from .mcp_server import StravaCoachMCPServer


def main() -> None:
    StravaCoachMCPServer().serve()


if __name__ == "__main__":
    main()
