"""
AI Chat Engine for App Rationalization Pro

Sophisticated conversational AI for portfolio rationalization consulting.
Manages conversation state, context injection, and response enhancement.
"""

import uuid
import json
import logging
from typing import Dict, List, Any, Optional, Generator
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from .claude_client import ClaudeClient, get_claude_client

logger = logging.getLogger(__name__)


class ConversationMode(Enum):
    """Chat conversation modes for app rationalization"""
    GENERAL = "general"
    PORTFOLIO_ANALYSIS = "portfolio_analysis"
    TIME_DISCUSSION = "time_discussion"
    RECOMMENDATION_REVIEW = "recommendation_review"
    ROADMAP_PLANNING = "roadmap_planning"


@dataclass
class ChatSession:
    """Active chat session with portfolio context"""
    session_id: str
    organization_name: str
    mode: ConversationMode = ConversationMode.GENERAL
    portfolio_data: Optional[Dict] = None
    conversation_history: List[Dict] = field(default_factory=list)
    context_data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)


class AIChatEngine:
    """
    AI-powered chat engine for application rationalization consulting.

    Features:
    - Context-aware responses based on portfolio data
    - Multiple conversation modes (TIME, recommendations, roadmap)
    - Suggested questions and prompts
    - Session management
    """

    # Suggested prompts by mode
    SUGGESTED_PROMPTS = {
        ConversationMode.GENERAL: [
            "What is application rationalization?",
            "Explain the TIME framework",
            "How can we reduce IT costs?",
            "What are the benefits of portfolio optimization?"
        ],
        ConversationMode.PORTFOLIO_ANALYSIS: [
            "Analyze our application portfolio health",
            "Which applications need immediate attention?",
            "What's our overall portfolio score?",
            "Identify consolidation opportunities"
        ],
        ConversationMode.TIME_DISCUSSION: [
            "Explain why apps are marked for ELIMINATE",
            "What should we INVEST in first?",
            "Which apps should we MIGRATE vs TOLERATE?",
            "How is the TIME category determined?"
        ],
        ConversationMode.RECOMMENDATION_REVIEW: [
            "Explain the recommended actions",
            "What are the highest priority actions?",
            "Which apps should we RETIRE first?",
            "What's the risk of these recommendations?"
        ],
        ConversationMode.ROADMAP_PLANNING: [
            "Create a 12-month rationalization roadmap",
            "What resources do we need for Phase 1?",
            "How should we sequence the retirements?",
            "What milestones should we target?"
        ]
    }

    # Mode-specific system context additions
    MODE_CONTEXTS = {
        ConversationMode.PORTFOLIO_ANALYSIS: """
You are currently analyzing the user's application portfolio.
Help them understand their portfolio health, identify problem areas,
and recognize patterns across their applications.
Reference specific applications and scores from the context data.""",

        ConversationMode.TIME_DISCUSSION: """
You are explaining the TIME framework categorization for the portfolio.
TIME stands for: Tolerate (keep as-is), Invest (enhance), Migrate (modernize), Eliminate (retire).
Help the user understand why each application is categorized the way it is.
Be specific about the business value and technical quality factors.""",

        ConversationMode.RECOMMENDATION_REVIEW: """
You are reviewing the action recommendations for each application.
Explain the rationale behind each recommendation (RETAIN, INVEST, MAINTAIN,
TOLERATE, MIGRATE, CONSOLIDATE, RETIRE, IMMEDIATE_ACTION).
Help them prioritize which actions to take first.""",

        ConversationMode.ROADMAP_PLANNING: """
You are helping create an application rationalization roadmap.
Consider dependencies, risks, and resource requirements.
Provide realistic timelines and clear milestones.
Suggest a phased approach starting with quick wins."""
    }

    def __init__(self, claude_client: Optional[ClaudeClient] = None):
        """Initialize chat engine"""
        self.claude = claude_client or get_claude_client()
        self.sessions: Dict[str, ChatSession] = {}

    def create_session(
        self,
        organization_name: str,
        portfolio_data: Optional[Dict] = None,
        mode: ConversationMode = ConversationMode.GENERAL
    ) -> ChatSession:
        """
        Create a new chat session.

        Args:
            organization_name: Name of the organization
            portfolio_data: Optional portfolio summary for context
            mode: Initial conversation mode

        Returns:
            New ChatSession
        """
        session_id = str(uuid.uuid4())

        session = ChatSession(
            session_id=session_id,
            organization_name=organization_name,
            mode=mode,
            portfolio_data=portfolio_data
        )

        # Build context for Claude
        context = self._build_context(session)
        self.claude.create_conversation(session_id, "consultant", context)

        self.sessions[session_id] = session
        logger.info(f"Created chat session {session_id} for {organization_name}")

        return session

    def _build_context(self, session: ChatSession) -> Dict[str, Any]:
        """Build context dictionary for Claude"""
        context = {
            "organization_name": session.organization_name,
            "conversation_mode": session.mode.value
        }

        if session.portfolio_data:
            context["portfolio_summary"] = {
                "total_applications": session.portfolio_data.get("total_applications"),
                "total_cost": session.portfolio_data.get("total_cost"),
                "average_score": session.portfolio_data.get("average_score"),
                "time_distribution": session.portfolio_data.get("time_distribution"),
                "recommendation_distribution": session.portfolio_data.get("recommendation_distribution"),
                "applications": session.portfolio_data.get("applications", [])[:20]  # Top 20 apps for context
            }

        # Add mode-specific context
        if session.mode in self.MODE_CONTEXTS:
            context["mode_instructions"] = self.MODE_CONTEXTS[session.mode]

        return context

    def chat(
        self,
        session_id: str,
        user_message: str,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Process a chat message.

        Args:
            session_id: Session ID
            user_message: User's message
            stream: Whether to stream response

        Returns:
            Response with message and metadata
        """
        if session_id not in self.sessions:
            return {
                "error": "Session not found",
                "message": "Please start a new conversation."
            }

        session = self.sessions[session_id]
        session.last_activity = datetime.now()

        # Add to conversation history
        session.conversation_history.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })

        # Get response from Claude
        response = self.claude.chat(session_id, user_message, stream=stream)

        # Add assistant response to history
        session.conversation_history.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })

        return {
            "message": response,
            "session_id": session_id,
            "mode": session.mode.value,
            "suggested_prompts": self.get_suggested_prompts(session_id),
            "timestamp": datetime.now().isoformat()
        }

    def stream_chat(
        self,
        session_id: str,
        user_message: str
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Stream a chat response token by token.

        Args:
            session_id: Session ID
            user_message: User's message

        Yields:
            Dict with type ('token', 'done', 'error') and content
        """
        if session_id not in self.sessions:
            yield {
                "type": "error",
                "content": "Session not found. Please start a new conversation."
            }
            return

        session = self.sessions[session_id]
        session.last_activity = datetime.now()

        # Add user message to history
        session.conversation_history.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })

        # Check if Claude is available
        if not self.claude.is_available():
            fallback = self.claude._fallback_response(
                user_message,
                self.claude.conversations.get(session_id)
            )
            # Simulate streaming for fallback
            words = fallback.split(' ')
            for i, word in enumerate(words):
                yield {"type": "token", "content": word + (' ' if i < len(words) - 1 else '')}

            session.conversation_history.append({
                "role": "assistant",
                "content": fallback,
                "timestamp": datetime.now().isoformat()
            })

            yield {
                "type": "done",
                "suggested_prompts": self.get_suggested_prompts(session_id)
            }
            return

        # Stream from Claude
        try:
            full_response = ""
            conversation = self.claude.conversations.get(session_id)

            if not conversation:
                context = self._build_context(session)
                conversation = self.claude.create_conversation(session_id, "consultant", context)

            conversation.add_message("user", user_message)

            with self.claude.client.messages.stream(
                model=self.claude.model,
                max_tokens=self.claude.MAX_TOKENS,
                system=conversation.system_prompt,
                messages=conversation.get_messages_for_api()
            ) as stream:
                for text in stream.text_stream:
                    full_response += text
                    yield {"type": "token", "content": text}

            # Save to conversation history
            conversation.add_message("assistant", full_response)
            session.conversation_history.append({
                "role": "assistant",
                "content": full_response,
                "timestamp": datetime.now().isoformat()
            })

            yield {
                "type": "done",
                "suggested_prompts": self.get_suggested_prompts(session_id)
            }

        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield {
                "type": "error",
                "content": f"An error occurred: {str(e)}"
            }

    def change_mode(self, session_id: str, new_mode: ConversationMode) -> bool:
        """Change conversation mode for a session"""
        if session_id not in self.sessions:
            return False

        session = self.sessions[session_id]
        session.mode = new_mode

        # Update Claude context
        context = self._build_context(session)
        self.claude.create_conversation(session_id, "consultant", context)

        # Preserve conversation history
        for msg in session.conversation_history:
            self.claude.conversations[session_id].add_message(
                msg["role"], msg["content"]
            )

        logger.info(f"Changed session {session_id} to mode {new_mode.value}")
        return True

    def get_suggested_prompts(self, session_id: str) -> List[str]:
        """Get suggested prompts based on current mode and portfolio data"""
        if session_id not in self.sessions:
            return self.SUGGESTED_PROMPTS[ConversationMode.GENERAL]

        session = self.sessions[session_id]
        base_prompts = self.SUGGESTED_PROMPTS.get(
            session.mode,
            self.SUGGESTED_PROMPTS[ConversationMode.GENERAL]
        )

        # Add context-aware prompts if we have portfolio data
        if session.portfolio_data:
            time_dist = session.portfolio_data.get("time_distribution", {})
            eliminate_count = time_dist.get("ELIMINATE", 0)

            if eliminate_count > 0 and session.mode == ConversationMode.TIME_DISCUSSION:
                base_prompts = [
                    f"Why are {eliminate_count} apps marked for ELIMINATE?",
                    "What's the risk of keeping these apps?",
                ] + base_prompts[:2]

        return base_prompts

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get session by ID"""
        return self.sessions.get(session_id)

    def update_portfolio_data(self, session_id: str, portfolio_data: Dict) -> bool:
        """Update portfolio data for a session"""
        if session_id not in self.sessions:
            return False

        session = self.sessions[session_id]
        session.portfolio_data = portfolio_data

        # Rebuild context
        context = self._build_context(session)
        if session_id in self.claude.conversations:
            self.claude.conversations[session_id].context = context

        return True

    def get_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary of conversation"""
        if session_id not in self.sessions:
            return {"error": "Session not found"}

        session = self.sessions[session_id]

        return {
            "session_id": session_id,
            "organization_name": session.organization_name,
            "mode": session.mode.value,
            "message_count": len(session.conversation_history),
            "has_portfolio": session.portfolio_data is not None,
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat()
        }

    def export_conversation(self, session_id: str) -> Dict[str, Any]:
        """Export full conversation for saving/reporting"""
        if session_id not in self.sessions:
            return {"error": "Session not found"}

        session = self.sessions[session_id]

        return {
            "session_id": session_id,
            "organization_name": session.organization_name,
            "portfolio_app_count": session.portfolio_data.get("total_applications") if session.portfolio_data else None,
            "conversation": session.conversation_history,
            "exported_at": datetime.now().isoformat()
        }


# Singleton instance
_engine: Optional[AIChatEngine] = None


def get_chat_engine() -> AIChatEngine:
    """Get or create singleton chat engine"""
    global _engine
    if _engine is None:
        _engine = AIChatEngine()
    return _engine
