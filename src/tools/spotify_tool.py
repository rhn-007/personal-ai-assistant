class SpotifyTool:

    def __init__(self):
        self.name = "spotify"

    def can_handle(self, query: str):
        q = query.lower()
        return any(k in q for k in ["spotify", "play", "song", "music"])

    def execute(self, payload):

        # ---------------- STRING MODE (fallback) ----------------
        if isinstance(payload, str):
            return f"Spotify received: {payload}"

        # ---------------- STRUCTURED MODE ----------------
        if isinstance(payload, dict):

            action = payload.get("action")

            if action == "play":
                song = payload.get("input", {}).get("song", "unknown")
                return f"🎵 Playing song: {song}"

            if action == "pause":
                return "⏸ Spotify paused"

            if action == "resume":
                return "▶ Spotify resumed"

            if action == "next":
                return "⏭ Next track"

            return f"Unknown Spotify action: {action}"

        return "Invalid Spotify payload"
