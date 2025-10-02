"""
Session management for chat conversations.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class ChatSession:
    """Represents a single chat conversation."""
    
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.messages: List[Dict] = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.metadata: Dict = {}
    
    def add_message(self, role: str, content: str, **kwargs) -> None:
        """Add a message to the conversation."""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            **kwargs
        })
        self.updated_at = datetime.now()
    
    def get_messages(self) -> List[Dict]:
        """Get all messages in API format."""
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in self.messages
        ]
    
    def to_dict(self) -> Dict:
        """Convert session to dictionary."""
        return {
            "session_id": self.session_id,
            "messages": self.messages,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "ChatSession":
        """Create session from dictionary."""
        session = cls(data["session_id"])
        session.messages = data["messages"]
        session.created_at = datetime.fromisoformat(data["created_at"])
        session.updated_at = datetime.fromisoformat(data["updated_at"])
        session.metadata = data.get("metadata", {})
        return session
    
    def export_markdown(self) -> str:
        """Export conversation as Markdown."""
        lines = [
            f"# Chat Session: {self.session_id}",
            "",
            f"**Created**: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Messages**: {len(self.messages)}",
            "",
            "---",
            "",
        ]
        
        for msg in self.messages:
            role = "👤 User" if msg["role"] == "user" else "🤖 LLM"
            timestamp = msg.get("timestamp", "")
            if timestamp:
                time_str = datetime.fromisoformat(timestamp).strftime("%H:%M:%S")
                lines.append(f"## {role} [{time_str}]")
            else:
                lines.append(f"## {role}")
            lines.append("")
            lines.append(msg["content"])
            lines.append("")
        
        return "\n".join(lines)


class SessionManager:
    """Manages multiple chat sessions with persistence."""
    
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or (Path.home() / ".ai_cli" / "sessions")
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, session: ChatSession) -> Path:
        """Save session to disk."""
        file_path = self.base_dir / f"{session.session_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(session.to_dict(), f, ensure_ascii=False, indent=2)
        return file_path
    
    def load(self, session_id: str) -> Optional[ChatSession]:
        """Load session from disk."""
        file_path = self.base_dir / f"{session_id}.json"
        if not file_path.exists():
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return ChatSession.from_dict(data)
    
    def list_sessions(self, limit: Optional[int] = None) -> List[Dict]:
        """List all saved sessions."""
        sessions = []
        for file_path in self.base_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    sessions.append({
                        "id": data["session_id"],
                        "messages": len(data["messages"]),
                        "created_at": data["created_at"],
                        "updated_at": data["updated_at"],
                    })
            except Exception:
                continue
        
        # Sort by update time (newest first)
        sessions.sort(key=lambda x: x["updated_at"], reverse=True)
        
        if limit:
            return sessions[:limit]
        return sessions
    
    def delete(self, session_id: str) -> bool:
        """Delete a session."""
        file_path = self.base_dir / f"{session_id}.json"
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    
    def export_markdown(self, session_id: str) -> Optional[Path]:
        """Export session as Markdown file."""
        session = self.load(session_id)
        if not session:
            return None
        
        md_path = self.base_dir / f"{session_id}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(session.export_markdown())
        
        return md_path
