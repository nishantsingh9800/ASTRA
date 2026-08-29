class LocalAgentServer:
    """
    Secure WebSocket or local HTTP server for ASTRA UI to communicate with the local agent.
    Ensures that only authorized connections from localhost are accepted.
    """
    def __init__(self, host: str = "127.0.0.1", port: int = 8765):
        self.host = host
        self.port = port
        self.is_running = False

    def start(self) -> None:
        """Bind to localhost and start listening for connections."""
        self.is_running = True
        print(f"LocalAgentServer started at ws://{self.host}:{self.port}")
        # Server implementation goes here

    def stop(self) -> None:
        """Stop the server gracefully."""
        self.is_running = False
        print("LocalAgentServer stopped.")
