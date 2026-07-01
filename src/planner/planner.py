class Planner:
    """
    Planner V2:
    - Intent-based routing (NOT keyword spam)
    - Confidence scoring
    - Safe tool selection
    """

    def __init__(self, tool_manager):
        self.tool_manager = tool_manager

    # =========================================================
    # OPTIONAL direct tool execution (fast path)
    # =========================================================
    def execute(self, user_input: str):
        tool = self.tool_manager.get_tool(user_input)

        if tool:
            return tool.execute(user_input)

        return None

    # =========================================================
    # 🧠 INTENT CLASSIFIER (CORE OF V2)
    # =========================================================
    def _classify_intent(self, text: str):

        t = text.lower()

        # EMAIL INTENT
        email_keywords = [
            "email", "inbox", "unread", "mail",
            "from:", "send email", "gmail"
        ]

        # DEFAULT CHAT INTENT
        chat_keywords = [
            "hi", "hello", "how are you", "what is", "explain", "who is"
        ]

        # TOOL INTENTS
        if any(k in t for k in email_keywords):
            return "email", 0.95

        if any(k in t for k in chat_keywords):
            return "chat", 0.60

        # fallback
        return "chat", 0.40

    # =========================================================
    # 🧠 PLAN GENERATION (V2 LOGIC)
    # =========================================================
    def create_plan(self, query: str):

        intent, confidence = self._classify_intent(query)

        plan = []

        # LOW CONFIDENCE → NO TOOL (important fix)
        if confidence < 0.75:
            return []

        # EMAIL TOOL ONLY IF HIGH CONFIDENCE
        if intent == "email":
            plan.append({
                "tool": "email",
                "input": query
            })
            return plan

        # CHAT → no tool execution
        return []
