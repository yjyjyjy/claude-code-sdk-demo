#!/usr/bin/env python3
"""
Logging utility for Claude Code SDK responses
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class ResponseLogger:
    """Utility class to log Claude Code SDK responses to files"""
    
    def __init__(self, log_dir: str = "logs", session_prefix: str = "claude_responses"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.session_prefix = session_prefix
        self.session_id = None
        self.log_file = None
        self.responses = []
        
    def init_session(self, session_id: str = None):
        """Initialize a new logging session"""
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"{self.session_prefix}_{timestamp}_{self.session_id}.jsonl"
        self.responses = []
        
        # Write session header
        self._write_log_entry({
            "event_type": "session_start",
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "log_file": str(self.log_file)
        })
        
    def log_response(self, message: Any, turn: int = None, context: Dict[str, Any] = None):
        """Log a response message to file
        
        Args:
            message: The response message object from Claude Code SDK
            turn: Optional turn number for context
            context: Additional context data
        """
        if not self.log_file:
            self.init_session()
            
        # Convert message to serializable dict
        response_data = self._serialize_message(message)
        
        log_entry = {
            "event_type": "response",
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "turn": turn,
            "message_type": type(message).__name__,
            "response_data": response_data,
            "context": context or {}
        }
        
        self.responses.append(log_entry)
        self._write_log_entry(log_entry)
        
    def log_query(self, query: str, turn: int = None, attachments: List[str] = None):
        """Log a query being sent
        
        Args:
            query: The query text
            turn: Optional turn number
            attachments: List of attachment file paths
        """
        if not self.log_file:
            self.init_session()
            
        log_entry = {
            "event_type": "query",
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "turn": turn,
            "query": query,
            "attachments": attachments or []
        }
        
        self._write_log_entry(log_entry)
        
    def log_execution(self, code: str, result: Any, turn: int = None, success: bool = True, error: str = None):
        """Log code execution results
        
        Args:
            code: The executed code
            result: Execution result
            turn: Optional turn number
            success: Whether execution was successful
            error: Error message if failed
        """
        if not self.log_file:
            self.init_session()
            
        log_entry = {
            "event_type": "execution",
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "turn": turn,
            "code": code,
            "result": self._serialize_object(result),
            "success": success,
            "error": error
        }
        
        self._write_log_entry(log_entry)
        
    def close_session(self, final_result: Dict[str, Any] = None):
        """Close the current logging session"""
        if not self.log_file:
            return
            
        log_entry = {
            "event_type": "session_end",
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "total_responses": len(self.responses),
            "final_result": final_result or {}
        }
        
        self._write_log_entry(log_entry)
        
        # Also write a complete session summary
        summary_file = self.log_file.with_suffix('.json')
        summary = {
            "session_id": self.session_id,
            "start_time": self.responses[0]["timestamp"] if self.responses else None,
            "end_time": datetime.now().isoformat(),
            "total_responses": len(self.responses),
            "responses": self.responses,
            "final_result": final_result or {}
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
            
    def _serialize_message(self, message: Any) -> Dict[str, Any]:
        """Convert a message object to a serializable dictionary"""
        data = {}
        
        # Get all attributes of the message
        for attr in dir(message):
            if not attr.startswith('_'):
                try:
                    value = getattr(message, attr)
                    if not callable(value):
                        data[attr] = self._serialize_object(value)
                except Exception as e:
                    data[f"{attr}_error"] = str(e)
        
        return data
        
    def _serialize_object(self, obj: Any) -> Any:
        """Serialize any object to JSON-compatible format"""
        try:
            # Try direct JSON serialization first
            json.dumps(obj)
            return obj
        except (TypeError, ValueError):
            # Handle non-serializable objects
            if hasattr(obj, '__dict__'):
                return {k: self._serialize_object(v) for k, v in obj.__dict__.items()}
            elif hasattr(obj, '_asdict'):  # namedtuple
                return obj._asdict()
            elif isinstance(obj, (list, tuple)):
                return [self._serialize_object(item) for item in obj]
            elif isinstance(obj, dict):
                return {k: self._serialize_object(v) for k, v in obj.items()}
            else:
                return str(obj)
                
    def _write_log_entry(self, entry: Dict[str, Any]):
        """Write a log entry to the JSONL file"""
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry, default=str) + '\n')


# Global logger instance
_logger = None

def get_logger(log_dir: str = "logs", session_prefix: str = "claude_responses") -> ResponseLogger:
    """Get or create a global logger instance"""
    global _logger
    if _logger is None:
        _logger = ResponseLogger(log_dir, session_prefix)
    return _logger

def init_logging(session_id: str = None, log_dir: str = "logs"):
    """Initialize logging for a new session"""
    logger = get_logger(log_dir)
    logger.init_session(session_id)
    return logger