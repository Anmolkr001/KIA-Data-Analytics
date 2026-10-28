"""
Conversation memory manager for Ask Your Data.
Preserves multi-turn query history so contextual follow-ups work smoothly.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class ConversationTurn:
    question: str
    plan: str
    code: str
    result_preview: str
    business_summary: str
    recommendation: str
    chart_spec: Optional[Dict[str, Any]] = None


class ConversationMemory:
    """Manages conversational state and contextual history for dealership analytics."""

    def __init__(self, max_turns: int = 6):
        self.max_turns = max_turns
        self.history: List[ConversationTurn] = []

    def add_turn(
        self,
        question: str,
        plan: str,
        code: str,
        result_preview: str,
        business_summary: str,
        recommendation: str,
        chart_spec: Optional[Dict[str, Any]] = None,
    ) -> None:
        turn = ConversationTurn(
            question=question,
            plan=plan,
            code=code,
            result_preview=result_preview,
            business_summary=business_summary,
            recommendation=recommendation,
            chart_spec=chart_spec,
        )
        self.history.append(turn)
        if len(self.history) > self.max_turns:
            self.history.pop(0)

    def get_context_for_prompt(self) -> str:
        """Formats recent turns into a readable prompt segment for the LLM."""
        if not self.history:
            return "No previous conversation history."

        lines = ["Previous Conversation Context:"]
        for idx, turn in enumerate(self.history, start=1):
            lines.append(f"\n[Turn {idx}]")
            lines.append(f"Manager Question: {turn.question}")
            lines.append(f"Pandas Code Used: {turn.code.strip()}")
            lines.append(f"Key Findings: {turn.business_summary}")
        return "\n".join(lines)

    def get_last_turn(self) -> Optional[ConversationTurn]:
        """Returns the most recent conversation turn if available."""
        return self.history[-1] if self.history else None

    def clear(self) -> None:
        """Clears all conversation turns."""
        self.history.clear()
