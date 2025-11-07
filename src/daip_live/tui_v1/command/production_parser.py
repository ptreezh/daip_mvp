"""
Production-grade Command Parser for newP6 TUI

This module provides comprehensive command parsing capabilities including:
- Advanced tokenization with proper Unicode and quote handling
- Command validation and security checks
- Performance monitoring and metrics collection
- Extensible command definition system
- Error recovery and suggestion mechanisms
- Command history and auto-completion support
- Plugin command integration
- Detailed audit logging
"""

import re
import shlex
import time
import uuid
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Set, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
import sqlite3
from pathlib import Path
import threading
from collections import defaultdict, deque
import asyncio
from functools import lru_cache
import unicodedata

logger = logging.getLogger(__name__)


class CommandType(Enum):
    """Command types for routing and processing"""
    SYSTEM = "system"           # System management commands
    SESSION = "session"         # Session management
    KNOWLEDGE = "knowledge"     # Knowledge base operations
    DEBATE = "debate"          # Debate system
    MODEL = "model"            # Model management
    ASSISTANT = "assistant"    # Personal assistant
    UI = "ui"                  # User interface controls
    PLUGIN = "plugin"          # Plugin commands
    CUSTOM = "custom"          # User-defined commands


class ParameterType(Enum):
    """Parameter types for validation"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    FILE_PATH = "file_path"
    DIRECTORY_PATH = "directory_path"
    URL = "url"
    EMAIL = "email"
    DATE = "date"
    TIME = "time"
    JSON = "json"
    REGEX = "regex"


class SecurityLevel(Enum):
    """Security levels for command execution"""
    PUBLIC = "public"           # No authentication required
    USER = "user"             # User authentication required
    ADMIN = "admin"           # Admin privileges required
    SYSTEM = "system"         # System level privileges required
    SANDBOXED = "sandboxed"   # Execute in restricted environment


@dataclass
class ParameterDefinition:
    """Command parameter definition with validation rules"""
    name: str
    param_type: ParameterType
    required: bool = True
    default_value: Any = None
    description: str = ""
    validation_regex: Optional[str] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    allowed_values: Optional[Set[Any]] = None
    file_extensions: Optional[Set[str]] = None
    max_length: Optional[int] = None
    sensitive: bool = False  # For passwords, tokens, etc.
    deprecated: bool = False
    deprecation_message: str = ""

    def validate_value(self, value: Any) -> Tuple[bool, Optional[str]]:
        """Validate parameter value against definition"""
        # Type validation
        if self.param_type == ParameterType.STRING:
            if not isinstance(value, str):
                return False, f"Expected string, got {type(value).__name__}"
        elif self.param_type == ParameterType.INTEGER:
            if not isinstance(value, int):
                return False, f"Expected integer, got {type(value).__name__}"
        elif self.param_type == ParameterType.FLOAT:
            if not isinstance(value, (int, float)):
                return False, f"Expected number, got {type(value).__name__}"
        elif self.param_type == ParameterType.BOOLEAN:
            if not isinstance(value, bool):
                return False, f"Expected boolean, got {type(value).__name__}"
        elif self.param_type == ParameterType.ARRAY:
            if not isinstance(value, list):
                return False, f"Expected array, got {type(value).__name__}"
        elif self.param_type == ParameterType.OBJECT:
            if not isinstance(value, dict):
                return False, f"Expected object, got {type(value).__name__}"

        # Length validation
        if self.max_length is not None:
            if isinstance(value, (str, list, dict)):
                if len(value) > self.max_length:
                    return False, f"Value exceeds maximum length of {self.max_length}"

        # Range validation
        if self.min_value is not None and value < self.min_value:
            return False, f"Value must be >= {self.min_value}"
        if self.max_value is not None and value > self.max_value:
            return False, f"Value must be <= {self.max_value}"

        # Allowed values validation
        if self.allowed_values is not None and value not in self.allowed_values:
            return False, f"Value must be one of {list(self.allowed_values)}"

        # Regex validation
        if self.validation_regex is not None and isinstance(value, str):
            if not re.match(self.validation_regex, value):
                return False, f"Value does not match required pattern: {self.validation_regex}"

        # File path validation
        if self.param_type == ParameterType.FILE_PATH:
            if not isinstance(value, str):
                return False, "File path must be a string"
            path = Path(value)
            if self.file_extensions and path.suffix.lower() not in self.file_extensions:
                return False, f"File extension must be one of {list(self.file_extensions)}"

        return True, None


@dataclass
class CommandDefinition:
    """Comprehensive command definition"""
    name: str
    command_type: CommandType
    description: str = ""
    aliases: Set[str] = field(default_factory=set)
    parameters: List[ParameterDefinition] = field(default_factory=list)
    security_level: SecurityLevel = SecurityLevel.USER
    rate_limit: Optional[int] = None  # Max requests per minute
    timeout_seconds: Optional[int] = None
    deprecated: bool = False
    deprecation_message: str = ""
    examples: List[str] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set)
    version: str = "1.0.0"
    author: str = ""
    plugin_name: Optional[str] = None
    handler: Optional[Callable] = None


@dataclass
class ParsedCommand:
    """Parsed command with comprehensive metadata"""
    raw: str
    command: str
    action: Optional[str]
    args: List[str]
    options: Dict[str, Any]
    flags: Set[str]
    command_type: CommandType
    security_level: SecurityLevel
    parse_time_ms: float
    checksum: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    validation_errors: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


@dataclass
class CommandMetrics:
    """Command execution metrics"""
    total_parses: int = 0
    successful_parses: int = 0
    failed_parses: int = 0
    average_parse_time_ms: float = 0.0
    parse_errors: Dict[str, int] = field(default_factory=dict)
    command_frequency: Dict[str, int] = field(default_factory=dict)
    parameter_frequency: Dict[str, int] = field(default_factory=dict)
    security_violations: int = 0
    rate_limit_violations: int = 0


class ProductionCommandParser:
    """Production-grade command parser with comprehensive features"""

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = Path(storage_path) if storage_path else Path("data/command_parser.db")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Command registry
        self.commands: Dict[str, CommandDefinition] = {}
        self.aliases: Dict[str, str] = {}  # alias -> command_name
        self.command_tree: Dict[str, Dict[str, Any]] = {}  # For auto-completion

        # Security and validation
        self.security_policies: Dict[SecurityLevel, List[Callable]] = defaultdict(list)
        self.rate_limiters: Dict[str, Dict[str, Any]] = defaultdict(dict)

        # Performance tracking
        self.metrics = CommandMetrics()
        self.parse_times: deque = deque(maxlen=1000)
        self._lock = threading.RLock()

        # Input validation and sanitization
        self.max_command_length = 10000
        self.max_token_count = 1000
        self.dangerous_patterns = [
            r'\$\(',                    # Command substitution
            r'`[^`]*`',                 # Backtick execution
            r'\|\s*sh\b',               # Pipe to shell
            r'\|\s*bash\b',             # Pipe to bash
            r';\s*rm\s+',               # Remove files
            r';\s*dd\s+',               # Disk destroyer
            r';\s*mkfs',                # Filesystem format
            r';\s*fdisk',               # Disk partitioning
            r'>(?:\s*/dev/)',           # Redirect to device
        ]

        # Database initialization
        self._init_database()

        # Load command definitions
        self._register_builtin_commands()

        # Background tasks
        self._maintenance_active = True
        self._start_maintenance_tasks()

    def _init_database(self) -> None:
        """Initialize database for metrics and history"""
        try:
            with sqlite3.connect(self.storage_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS command_history (
                        id TEXT PRIMARY KEY,
                        raw_command TEXT NOT NULL,
                        parsed_command TEXT,
                        success BOOLEAN,
                        parse_time_ms REAL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        user_id TEXT,
                        session_id TEXT
                    )
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS command_metrics (
                        metric_name TEXT PRIMARY KEY,
                        metric_value REAL NOT NULL,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS command_errors (
                        id TEXT PRIMARY KEY,
                        command TEXT NOT NULL,
                        error_type TEXT NOT NULL,
                        error_message TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        frequency INTEGER DEFAULT 1
                    )
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS command_suggestions (
                        command TEXT PRIMARY KEY,
                        suggestions TEXT NOT NULL,
                        usage_count INTEGER DEFAULT 0,
                        last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Indexes
                conn.execute("CREATE INDEX IF NOT EXISTS idx_history_timestamp ON command_history (timestamp)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_history_command ON command_history (raw_command)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_errors_command ON command_errors (command)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_suggestions_usage ON command_suggestions (usage_count)")

                conn.commit()

        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")

    def _register_builtin_commands(self) -> None:
        """Register built-in command definitions"""
        # System commands
        self.register_command(CommandDefinition(
            name="help",
            command_type=CommandType.SYSTEM,
            description="Show help information",
            aliases={"h", "?"},
            parameters=[
                ParameterDefinition(
                    name="command",
                    param_type=ParameterType.STRING,
                    required=False,
                    description="Command to get help for"
                )
            ],
            examples=["help", "help list", "help --version"]
        ))

        self.register_command(CommandDefinition(
            name="exit",
            command_type=CommandType.SYSTEM,
            description="Exit the application",
            aliases={"quit", "q"},
            examples=["exit", "quit", "q"]
        ))

        self.register_command(CommandDefinition(
            name="clear",
            command_type=CommandType.UI,
            description="Clear the screen",
            aliases={"cls"},
            examples=["clear", "cls"]
        ))

        # Session commands
        self.register_command(CommandDefinition(
            name="session",
            command_type=CommandType.SESSION,
            description="Session management",
            parameters=[
                ParameterDefinition(
                    name="action",
                    param_type=ParameterType.STRING,
                    required=True,
                    allowed_values={"list", "create", "delete", "switch", "show"}
                ),
                ParameterDefinition(
                    name="session_id",
                    param_type=ParameterType.STRING,
                    required=False
                ),
                ParameterDefinition(
                    name="name",
                    param_type=ParameterType.STRING,
                    required=False
                )
            ],
            examples=["session list", "session create --name \"New Session\"", "session switch abc123"]
        ))

        # Knowledge commands
        self.register_command(CommandDefinition(
            name="knowledge",
            command_type=CommandType.KNOWLEDGE,
            description="Knowledge base operations",
            aliases={"kb", "knowledge-base"},
            parameters=[
                ParameterDefinition(
                    name="action",
                    param_type=ParameterType.STRING,
                    required=True,
                    allowed_values={"search", "add", "delete", "list", "stats"}
                ),
                ParameterDefinition(
                    name="query",
                    param_type=ParameterType.STRING,
                    required=False
                ),
                ParameterDefinition(
                    name="file",
                    param_type=ParameterType.FILE_PATH,
                    required=False,
                    file_extensions={".txt", ".md", ".pdf", ".docx"}
                )
            ],
            examples=["knowledge search \"AI agents\"", "knowledge add --file document.pdf", "knowledge list"]
        ))

        # Model commands
        self.register_command(CommandDefinition(
            name="model",
            command_type=CommandType.MODEL,
            description="Model management",
            parameters=[
                ParameterDefinition(
                    name="action",
                    param_type=ParameterType.STRING,
                    required=True,
                    allowed_values={"list", "switch", "info", "status"}
                ),
                ParameterDefinition(
                    name="model_name",
                    param_type=ParameterType.STRING,
                    required=False
                )
            ],
            examples=["model list", "model switch gpt-4", "model info"]
        ))

        # Debate commands
        self.register_command(CommandDefinition(
            name="debate",
            command_type=CommandType.DEBATE,
            description="Debate system operations",
            parameters=[
                ParameterDefinition(
                    name="action",
                    param_type=ParameterType.STRING,
                    required=True,
                    allowed_values={"start", "join", "list", "status", "end"}
                ),
                ParameterDefinition(
                    name="topic",
                    param_type=ParameterType.STRING,
                    required=False
                ),
                ParameterDefinition(
                    name="role",
                    param_type=ParameterType.STRING,
                    required=False
                )
            ],
            examples=["debate start \"AI Ethics\"", "debate join --role skeptic", "debate list"]
        ))

    def register_command(self, command_def: CommandDefinition) -> bool:
        """Register a new command definition"""
        with self._lock:
            if command_def.name in self.commands:
                logger.warning(f"Command '{command_def.name}' already registered, overwriting")

            self.commands[command_def.name] = command_def

            # Register aliases
            for alias in command_def.aliases:
                if alias in self.aliases:
                    logger.warning(f"Alias '{alias}' already mapped to '{self.aliases[alias]}'")
                self.aliases[alias] = command_def.name

            # Update command tree for auto-completion
            self._update_command_tree(command_def)

            logger.debug(f"Registered command: {command_def.name}")
            return True

    def _update_command_tree(self, command_def: CommandDefinition) -> None:
        """Update command tree for auto-completion"""
        parts = command_def.name.split()
        current = self.command_tree

        for i, part in enumerate(parts):
            if part not in current:
                current[part] = {"commands": {}, "params": []}
            if i == len(parts) - 1:
                current[part]["commands"][command_def.name] = command_def
                current[part]["params"] = [p.name for p in command_def.parameters]
            current = current[part]["commands"]

    async def parse(self, command_str: str, context: Optional[Dict[str, Any]] = None) -> ParsedCommand:
        """Parse command string with comprehensive validation and monitoring"""
        start_time = time.time()
        command_id = str(uuid.uuid4())

        try:
            # Input validation and sanitization
            sanitized_input = self._sanitize_input(command_str)
            if not sanitized_input:
                return self._create_empty_command(command_str, start_time)

            # Check security policies
            security_result = await self._check_security_policies(sanitized_input, context)
            if not security_result[0]:
                self.metrics.security_violations += 1
                return self._create_error_command(command_str, security_result[1], start_time)

            # Check rate limits
            if not self._check_rate_limits(sanitized_input, context):
                self.metrics.rate_limit_violations += 1
                return self._create_error_command(command_str, "Rate limit exceeded", start_time)

            # Tokenization with advanced handling
            tokens = self._tokenize(sanitized_input)
            if not tokens:
                return self._create_empty_command(command_str, start_time)

            # Parse tokens into structured command
            parsed = self._parse_tokens(tokens)
            if not parsed:
                return self._create_error_command(command_str, "Invalid command syntax", start_time)

            # Command lookup and validation
            command_def = self._lookup_command(parsed["command"])
            if not command_def:
                suggestions = self._generate_command_suggestions(parsed["command"])
                return self._create_suggestion_command(command_str, parsed, suggestions, start_time)

            # Validate parameters
            validation_errors = self._validate_parameters(parsed, command_def)
            if validation_errors:
                parsed["validation_errors"] = validation_errors

            # Create parsed command object
            parse_time = (time.time() - start_time) * 1000
            checksum = hashlib.sha256(command_str.encode()).hexdigest()

            result = ParsedCommand(
                raw=command_str,
                command=parsed["command"],
                action=parsed.get("action"),
                args=parsed.get("args", []),
                options=parsed.get("options", {}),
                flags=parsed.get("flags", set()),
                command_type=command_def.command_type,
                security_level=command_def.security_level,
                parse_time_ms=parse_time,
                checksum=checksum,
                metadata={
                    "command_id": command_id,
                    "command_def": command_def,
                    "tokens": tokens,
                    "context": context or {}
                }
            )

            # Update metrics
            self._update_metrics(result, True)

            # Log to database
            await self._log_command(result, True)

            return result

        except Exception as e:
            parse_time = (time.time() - start_time) * 1000
            error_msg = f"Parse error: {str(e)}"

            # Update metrics
            self._update_metrics(None, False, error_msg)

            # Log error
            await self._log_command_error(command_str, error_msg)

            return self._create_error_command(command_str, error_msg, parse_time)

    def _sanitize_input(self, command_str: str) -> str:
        """Sanitize and validate input command"""
        # Remove control characters
        sanitized = ''.join(char for char in command_str if unicodedata.category(char)[0] != 'C')

        # Check length
        if len(sanitized) > self.max_command_length:
            raise ValueError(f"Command too long (max {self.max_command_length} characters)")

        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if re.search(pattern, sanitized, re.IGNORECASE):
                raise ValueError(f"Potentially dangerous command pattern detected: {pattern}")

        # Normalize whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()

        return sanitized

    def _tokenize(self, command_str: str) -> List[str]:
        """Advanced tokenization with proper quote handling"""
        try:
            # Use shlex for proper quote handling
            tokens = shlex.split(command_str, posix=True)

            # Validate token count
            if len(tokens) > self.max_token_count:
                raise ValueError(f"Too many tokens (max {self.max_token_count})")

            return tokens

        except ValueError as e:
            # Fallback to simple tokenization if shlex fails
            logger.warning(f"shlex tokenization failed: {e}, using fallback")
            return command_str.split()

    def _parse_tokens(self, tokens: List[str]) -> Optional[Dict[str, Any]]:
        """Parse tokens into structured command data"""
        if not tokens:
            return None

        result = {
            "command": tokens[0],
            "action": None,
            "args": [],
            "options": {},
            "flags": set()
        }

        # Parse action (second token if not an option)
        if len(tokens) > 1 and not tokens[1].startswith('-'):
            result["action"] = tokens[1]
            remaining_tokens = tokens[2:]
        else:
            remaining_tokens = tokens[1:]

        # Parse options, flags, and arguments
        i = 0
        while i < len(remaining_tokens):
            token = remaining_tokens[i]

            if token.startswith('--'):
                # Long option
                if '=' in token:
                    # --option=value format
                    key, value = token[2:].split('=', 1)
                    result["options"][key] = self._parse_value(value)
                elif i + 1 < len(remaining_tokens) and not remaining_tokens[i + 1].startswith('-'):
                    # --option value format
                    key = token[2:]
                    value = remaining_tokens[i + 1]
                    result["options"][key] = self._parse_value(value)
                    i += 1
                else:
                    # Boolean flag
                    key = token[2:]
                    result["flags"].add(key)
                    result["options"][key] = True

            elif token.startswith('-'):
                # Short option(s)
                if len(token) == 2:
                    # Single short option
                    key = token[1]
                    if i + 1 < len(remaining_tokens) and not remaining_tokens[i + 1].startswith('-'):
                        value = remaining_tokens[i + 1]
                        result["options"][key] = self._parse_value(value)
                        i += 1
                    else:
                        result["flags"].add(key)
                        result["options"][key] = True
                else:
                    # Multiple short flags
                    for char in token[1:]:
                        result["flags"].add(char)
                        result["options"][char] = True
            else:
                # Regular argument
                result["args"].append(token)

            i += 1

        return result

    def _parse_value(self, value: str) -> Any:
        """Parse string value into appropriate Python type"""
        # Try JSON parsing first
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            pass

        # Try numeric types
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass

        # Try boolean
        if value.lower() in ('true', 'yes', 'on'):
            return True
        elif value.lower() in ('false', 'no', 'off'):
            return False

        # Return as string
        return value

    def _lookup_command(self, command_name: str) -> Optional[CommandDefinition]:
        """Look up command definition by name or alias"""
        # Direct command lookup
        if command_name in self.commands:
            return self.commands[command_name]

        # Alias lookup
        if command_name in self.aliases:
            actual_command = self.aliases[command_name]
            return self.commands.get(actual_command)

        return None

    def _validate_parameters(self, parsed: Dict[str, Any], command_def: CommandDefinition) -> List[str]:
        """Validate command parameters against definition"""
        errors = []
        provided_params = set(parsed["options"].keys()) | set(parsed["flags"])
        provided_args = set(parsed["args"])

        # Check required parameters
        for param_def in command_def.parameters:
            param_value = None

            # Check in options
            if param_def.name in parsed["options"]:
                param_value = parsed["options"][param_def.name]
            # Check in args (for positional parameters)
            elif param_def.name in provided_args:
                param_value = parsed["args"][list(provided_args).index(param_def.name)]

            # Required parameter check
            if param_def.required and param_value is None:
                if param_def.default_value is not None:
                    parsed["options"][param_def.name] = param_def.default_value
                else:
                    errors.append(f"Required parameter '{param_def.name}' is missing")

            # Validation if parameter is provided
            if param_value is not None and not param_def.deprecated:
                is_valid, error_msg = param_def.validate_value(param_value)
                if not is_valid:
                    errors.append(f"Parameter '{param_def.name}': {error_msg}")
                elif param_def.deprecated:
                    errors.append(f"Parameter '{param_def.name}' is deprecated: {param_def.deprecation_message}")

        return errors

    async def _check_security_policies(self, command_str: str, context: Optional[Dict[str, Any]]) -> Tuple[bool, str]:
        """Check security policies for command"""
        user_role = context.get("user_role", "user") if context else "user"

        # Basic security checks
        for level, policies in self.security_policies.items():
            for policy in policies:
                result = policy(command_str, context)
                if not result[0]:
                    return False, f"Security policy violation: {result[1]}"

        return True, ""

    def _check_rate_limits(self, command_str: str, context: Optional[Dict[str, Any]]) -> bool:
        """Check rate limits for command"""
        user_id = context.get("user_id", "anonymous") if context else "anonymous"
        command_name = command_str.split()[0] if command_str else ""

        if command_name in self.rate_limiters:
            limiter = self.rate_limiters[command_name]
            current_time = time.time()

            # Clean old entries
            cutoff_time = current_time - 60  # 1 minute window
            limiter["requests"] = [req_time for req_time in limiter.get("requests", []) if req_time > cutoff_time]

            # Check limit
            if len(limiter["requests"]) >= limiter.get("limit", 60):
                return False

            # Add current request
            limiter.setdefault("requests", []).append(current_time)

        return True

    def _generate_command_suggestions(self, command_name: str) -> List[str]:
        """Generate command suggestions for unknown commands"""
        suggestions = []

        # Find similar commands using Levenshtein distance
        for registered_name in self.commands.keys():
            if self._levenshtein_distance(command_name.lower(), registered_name.lower()) <= 2:
                suggestions.append(registered_name)

        # Check aliases too
        for alias, actual_name in self.aliases.items():
            if self._levenshtein_distance(command_name.lower(), alias.lower()) <= 2:
                suggestions.append(actual_name)

        return suggestions[:5]  # Limit to top 5 suggestions

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between strings"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def _create_empty_command(self, command_str: str, start_time: float) -> ParsedCommand:
        """Create empty command result"""
        parse_time = (time.time() - start_time) * 1000
        return ParsedCommand(
            raw=command_str,
            command="",
            action=None,
            args=[],
            options={},
            flags=set(),
            command_type=CommandType.SYSTEM,
            security_level=SecurityLevel.PUBLIC,
            parse_time_ms=parse_time,
            checksum=hashlib.sha256(command_str.encode()).hexdigest()
        )

    def _create_error_command(self, command_str: str, error_msg: str, start_time: float) -> ParsedCommand:
        """Create error command result"""
        parse_time = (time.time() - start_time) * 1000
        return ParsedCommand(
            raw=command_str,
            command="",
            action=None,
            args=[],
            options={},
            flags=set(),
            command_type=CommandType.SYSTEM,
            security_level=SecurityLevel.PUBLIC,
            parse_time_ms=parse_time,
            checksum=hashlib.sha256(command_str.encode()).hexdigest(),
            validation_errors=[error_msg]
        )

    def _create_suggestion_command(self, command_str: str, parsed: Dict[str, Any],
                                 suggestions: List[str], start_time: float) -> ParsedCommand:
        """Create suggestion command result"""
        parse_time = (time.time() - start_time) * 1000
        return ParsedCommand(
            raw=command_str,
            command=parsed["command"],
            action=parsed.get("action"),
            args=parsed.get("args", []),
            options=parsed.get("options", {}),
            flags=parsed.get("flags", set()),
            command_type=CommandType.SYSTEM,
            security_level=SecurityLevel.PUBLIC,
            parse_time_ms=parse_time,
            checksum=hashlib.sha256(command_str.encode()).hexdigest(),
            validation_errors=[f"Unknown command '{parsed['command']}'"],
            suggestions=suggestions
        )

    def _update_metrics(self, parsed_command: Optional[ParsedCommand], success: bool,
                       error_msg: str = "") -> None:
        """Update parsing metrics"""
        with self._lock:
            self.metrics.total_parses += 1

            if success and parsed_command:
                self.metrics.successful_parses += 1
                self.parse_times.append(parsed_command.parse_time_ms)
                self.metrics.command_frequency[parsed_command.command] = \
                    self.metrics.command_frequency.get(parsed_command.command, 0) + 1

                # Update parameter frequency
                for param_name in parsed_command.options.keys():
                    self.metrics.parameter_frequency[param_name] = \
                        self.metrics.parameter_frequency.get(param_name, 0) + 1
            else:
                self.metrics.failed_parses += 1
                if error_msg:
                    error_type = error_msg.split(':')[0] if ':' in error_msg else error_msg
                    self.metrics.parse_errors[error_type] = \
                        self.metrics.parse_errors.get(error_type, 0) + 1

            # Update average parse time
            if self.parse_times:
                self.metrics.average_parse_time_ms = sum(self.parse_times) / len(self.parse_times)

    async def _log_command(self, parsed_command: ParsedCommand, success: bool) -> None:
        """Log command to database"""
        try:
            with sqlite3.connect(self.storage_path) as conn:
                conn.execute(
                    "INSERT INTO command_history (id, raw_command, parsed_command, success, parse_time_ms) VALUES (?, ?, ?, ?, ?)",
                    (
                        str(uuid.uuid4()),
                        parsed_command.raw,
                        json.dumps({
                            "command": parsed_command.command,
                            "action": parsed_command.action,
                            "args": parsed_command.args,
                            "options": parsed_command.options,
                            "flags": list(parsed_command.flags)
                        }),
                        success,
                        parsed_command.parse_time_ms
                    )
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to log command: {e}")

    async def _log_command_error(self, command_str: str, error_msg: str) -> None:
        """Log command error to database"""
        try:
            with sqlite3.connect(self.storage_path) as conn:
                # Check if error already exists
                cursor = conn.execute(
                    "SELECT id, frequency FROM command_errors WHERE command = ? AND error_type = ?",
                    (command_str[:100], error_msg[:100])
                )
                existing = cursor.fetchone()

                if existing:
                    # Update frequency
                    conn.execute(
                        "UPDATE command_errors SET frequency = frequency + 1, timestamp = ? WHERE id = ?",
                        (datetime.now().isoformat(), existing[0])
                    )
                else:
                    # Insert new error
                    conn.execute(
                        "INSERT INTO command_errors (id, command, error_type, error_message) VALUES (?, ?, ?, ?)",
                        (str(uuid.uuid4()), command_str[:100], error_msg[:100], error_msg[:500])
                    )

                conn.commit()
        except Exception as e:
            logger.error(f"Failed to log command error: {e}")

    def _start_maintenance_tasks(self) -> None:
        """Start background maintenance tasks"""
        # This would typically run in a separate thread or async task
        # For now, we'll just initialize the maintenance flag
        pass

    async def get_command_suggestions(self, partial_command: str, limit: int = 10) -> List[str]:
        """Get command suggestions for auto-completion"""
        suggestions = []
        partial_lower = partial_command.lower()

        # Direct command matches
        for command_name in self.commands.keys():
            if command_name.startswith(partial_lower):
                suggestions.append(command_name)

        # Alias matches
        for alias, command_name in self.aliases.items():
            if alias.startswith(partial_lower):
                suggestions.append(command_name)

        # Fuzzy matches if no exact matches
        if not suggestions:
            for command_name in self.commands.keys():
                if partial_lower in command_name.lower():
                    suggestions.append(command_name)

        return suggestions[:limit]

    def get_command_statistics(self) -> Dict[str, Any]:
        """Get comprehensive command statistics"""
        with self._lock:
            return {
                "total_commands": len(self.commands),
                "total_aliases": len(self.aliases),
                "total_parses": self.metrics.total_parses,
                "successful_parses": self.metrics.successful_parses,
                "failed_parses": self.metrics.failed_parses,
                "success_rate": (self.metrics.successful_parses / self.metrics.total_parses
                               if self.metrics.total_parses > 0 else 0),
                "average_parse_time_ms": self.metrics.average_parse_time_ms,
                "security_violations": self.metrics.security_violations,
                "rate_limit_violations": self.metrics.rate_limit_violations,
                "most_used_commands": dict(sorted(
                    self.metrics.command_frequency.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]),
                "most_used_parameters": dict(sorted(
                    self.metrics.parameter_frequency.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]),
                "common_errors": dict(sorted(
                    self.metrics.parse_errors.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5])
            }

    def register_security_policy(self, security_level: SecurityLevel, policy: Callable) -> None:
        """Register a security policy for a security level"""
        self.security_policies[security_level].append(policy)

    def set_rate_limit(self, command_name: str, requests_per_minute: int) -> None:
        """Set rate limit for a command"""
        self.rate_limiters[command_name] = {"limit": requests_per_minute, "requests": []}

    async def shutdown(self) -> None:
        """Shutdown the parser gracefully"""
        self._maintenance_active = False
        logger.info("Command parser shutdown complete")