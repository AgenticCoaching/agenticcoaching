from __future__ import annotations

import json
import os
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


DEFAULT_STREAM_KEYS = [
    "time",
    "distance",
    "latlng",
    "altitude",
    "velocity_smooth",
    "grade_smooth",
    "heartrate",
    "cadence",
    "watts",
    "temp",
    "moving",
]




def _default_ssl_context() -> ssl.SSLContext:
    cert_file = os.getenv("SSL_CERT_FILE")
    if cert_file and os.path.exists(cert_file):
        return ssl.create_default_context(cafile=cert_file)

    for candidate in ("/etc/ssl/cert.pem", "/etc/ssl/certs/ca-certificates.crt"):
        if os.path.exists(candidate):
            return ssl.create_default_context(cafile=candidate)

    return ssl.create_default_context()

class StravaApiError(RuntimeError):
    def __init__(self, status: int, message: str, payload: Optional[Any] = None) -> None:
        super().__init__(message)
        self.status = status
        self.payload = payload


@dataclass
class StravaCredentials:
    access_token: str
    expires_at: Optional[int] = None
    refresh_token: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None

    @classmethod
    def from_env(cls) -> "StravaCredentials":
        access_token = os.getenv("STRAVA_ACCESS_TOKEN")
        if not access_token:
            raise ValueError("STRAVA_ACCESS_TOKEN is required to use the Strava MCP server.")

        expires_at = os.getenv("STRAVA_ACCESS_TOKEN_EXPIRES_AT")
        return cls(
            access_token=access_token,
            expires_at=int(expires_at) if expires_at else None,
            refresh_token=os.getenv("STRAVA_REFRESH_TOKEN"),
            client_id=os.getenv("STRAVA_CLIENT_ID"),
            client_secret=os.getenv("STRAVA_CLIENT_SECRET"),
        )

    def needs_refresh(self) -> bool:
        if self.expires_at is None:
            return False
        return self.expires_at <= int(time.time()) + 300

    def can_refresh(self) -> bool:
        return bool(self.refresh_token and self.client_id and self.client_secret)


class StravaApiClient:
    api_base_url = "https://www.strava.com/api/v3"
    oauth_token_url = "https://www.strava.com/api/v3/oauth/token"

    def __init__(self, credentials: Optional[StravaCredentials] = None) -> None:
        self.credentials = credentials or StravaCredentials.from_env()

    def _refresh_access_token(self) -> None:
        if not self.credentials.can_refresh():
            return

        form = urllib.parse.urlencode(
            {
                "client_id": self.credentials.client_id,
                "client_secret": self.credentials.client_secret,
                "grant_type": "refresh_token",
                "refresh_token": self.credentials.refresh_token,
            }
        ).encode("utf-8")
        request = urllib.request.Request(self.oauth_token_url, method="POST", data=form)
        request.add_header("Content-Type", "application/x-www-form-urlencoded")

        try:
            with urllib.request.urlopen(request, timeout=30, context=_default_ssl_context()) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise StravaApiError(exc.code, f"Unable to refresh Strava access token: {body}")

        self.credentials.access_token = payload["access_token"]
        self.credentials.refresh_token = payload.get("refresh_token", self.credentials.refresh_token)
        self.credentials.expires_at = payload.get("expires_at", self.credentials.expires_at)

    def _request(
        self,
        method: str,
        path: str,
        *,
        query: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        want_json: bool = True,
    ) -> Any:
        if self.credentials.needs_refresh():
            self._refresh_access_token()

        query = {key: value for key, value in (query or {}).items() if value is not None}
        url = f"{self.api_base_url}{path}"
        if query:
            url = f"{url}?{urllib.parse.urlencode(query, doseq=True)}"

        data = None
        request = urllib.request.Request(url, method=method.upper())
        request.add_header("Authorization", f"Bearer {self.credentials.access_token}")
        request.add_header("Accept", "application/json" if want_json else "*/*")

        if json_body is not None:
            data = json.dumps(json_body).encode("utf-8")
            request.data = data
            request.add_header("Content-Type", "application/json")

        try:
            with urllib.request.urlopen(request, timeout=30, context=_default_ssl_context()) as response:
                raw = response.read()
                if not raw:
                    return None
                if want_json:
                    return json.loads(raw.decode("utf-8"))
                return raw.decode("utf-8")
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            payload: Any = body
            try:
                payload = json.loads(body)
            except json.JSONDecodeError:
                pass
            raise StravaApiError(exc.code, f"Strava API request failed with HTTP {exc.code}", payload)

    def get_profile(self) -> Dict[str, Any]:
        return self._request("GET", "/athlete")

    def get_zones(self) -> Dict[str, Any]:
        return self._request("GET", "/athlete/zones")

    def get_stats(self, athlete_id: int) -> Dict[str, Any]:
        return self._request("GET", f"/athletes/{athlete_id}/stats")

    def update_athlete(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("PUT", "/athlete", json_body=payload)

    def list_activities(
        self,
        *,
        before: Optional[int] = None,
        after: Optional[int] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        return self._request(
            "GET",
            "/athlete/activities",
            query={"before": before, "after": after, "page": page, "per_page": per_page},
        )

    def get_activity(self, activity_id: int, include_all_efforts: bool = False) -> Dict[str, Any]:
        return self._request(
            "GET",
            f"/activities/{activity_id}",
            query={"include_all_efforts": str(include_all_efforts).lower() if include_all_efforts else None},
        )

    def get_activity_laps(self, activity_id: int) -> List[Dict[str, Any]]:
        return self._request("GET", f"/activities/{activity_id}/laps")

    def get_activity_zones(self, activity_id: int) -> List[Dict[str, Any]]:
        return self._request("GET", f"/activities/{activity_id}/zones")

    def get_activity_streams(self, activity_id: int, keys: Optional[List[str]] = None) -> Dict[str, Any]:
        return self._request(
            "GET",
            f"/activities/{activity_id}/streams",
            query={"keys": keys or DEFAULT_STREAM_KEYS, "key_by_type": "true"},
        )

    def update_activity(self, activity_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("PUT", f"/activities/{activity_id}", json_body=payload)

    def get_gear(self, gear_id: str) -> Dict[str, Any]:
        return self._request("GET", f"/gear/{gear_id}")

    def list_routes(self, athlete_id: int, page: Optional[int] = None, per_page: Optional[int] = None) -> List[Dict[str, Any]]:
        return self._request(
            "GET",
            f"/athletes/{athlete_id}/routes",
            query={"page": page, "per_page": per_page},
        )

    def get_route(self, route_id: int) -> Dict[str, Any]:
        return self._request("GET", f"/routes/{route_id}")

    def download_route_gpx(self, route_id: int) -> str:
        return self._request("GET", f"/routes/{route_id}/export_gpx", want_json=False)

    def download_route_tcx(self, route_id: int) -> str:
        return self._request("GET", f"/routes/{route_id}/export_tcx", want_json=False)
