"""
Skill execution caching system with TTL support and LRU eviction.
"""

import hashlib
import json
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Optional

from .base import SkillInput, SkillOutput


@dataclass
class CacheEntry:
    """Represents a cached skill execution result."""

    output: SkillOutput
    skill_name: str
    timestamp: float
    access_count: int = 0
    last_access: float = 0.0

    def is_expired(self, ttl: Optional[float]) -> bool:
        """Check if the cache entry has expired."""
        if ttl is None:
            return False
        return time.time() - self.timestamp > ttl


@dataclass
class CacheStatistics:
    """Statistics about cache performance."""

    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_entries: int = 0

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


class SkillCache:
    """
    LRU cache for skill execution results with TTL support.

    Features:
    - Cache key generation from skill name and input
    - TTL (Time To Live) support
    - LRU eviction policy
    - Cache statistics
    - Manual cache invalidation
    """

    def __init__(
        self,
        max_size: int = 100,
        default_ttl: Optional[float] = None,
        enabled: bool = True,
    ):
        """
        Initialize the skill cache.

        Args:
            max_size: Maximum number of entries in the cache (LRU eviction)
            default_ttl: Default time-to-live for cache entries in seconds (None = no expiration)
            enabled: Whether caching is enabled
        """  # noqa: E501
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._enabled = enabled
        self._stats = CacheStatistics()

    @property
    def enabled(self) -> bool:
        """Check if caching is enabled."""
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool):
        """Enable or disable caching."""
        self._enabled = value

    @property
    def size(self) -> int:
        """Get current cache size."""
        return len(self._cache)

    @property
    def statistics(self) -> CacheStatistics:
        """Get cache statistics."""
        self._stats.total_entries = len(self._cache)
        return self._stats

    def _generate_cache_key(self, skill_name: str, input: SkillInput) -> str:
        """
        Generate a unique cache key from skill name and input.

        Args:
            skill_name: Name of the skill
            input: Skill input data

        Returns:
            MD5 hash string for the cache key
        """
        # Create a deterministic string representation of the input
        input_dict = {
            "data": input.data,
            "context": input.context,
            "metadata": input.metadata,
        }
        input_str = json.dumps(input_dict, sort_keys=True)
        key_string = f"{skill_name}:{input_str}"

        # Generate MD5 hash for efficient storage
        return hashlib.md5(key_string.encode("utf-8")).hexdigest()

    def get(
        self, skill_name: str, input: SkillInput, ttl: Optional[float] = None
    ) -> Optional[SkillOutput]:
        """
        Retrieve a cached result.

        Args:
            skill_name: Name of the skill
            input: Skill input data
            ttl: Optional override for TTL check

        Returns:
            Cached SkillOutput if found and valid, None otherwise
        """
        if not self._enabled:
            return None

        cache_key = self._generate_cache_key(skill_name, input)

        if cache_key in self._cache:
            entry = self._cache[cache_key]

            # Check if entry has expired
            effective_ttl = ttl if ttl is not None else self._default_ttl
            if entry.is_expired(effective_ttl):
                # Remove expired entry
                del self._cache[cache_key]
                self._stats.misses += 1
                return None

            # Update access information for LRU
            entry.access_count += 1
            entry.last_access = time.time()

            # Move to end (most recently used)
            self._cache.move_to_end(cache_key)

            self._stats.hits += 1
            return entry.output

        self._stats.misses += 1
        return None

    def put(
        self,
        skill_name: str,
        input: SkillInput,
        output: SkillOutput,
        ttl: Optional[float] = None,
    ) -> None:
        """
        Store a result in the cache.

        Args:
            skill_name: Name of the skill
            input: Skill input data
            output: Skill output to cache
            ttl: Optional TTL for this specific entry
        """
        if not self._enabled:
            return

        cache_key = self._generate_cache_key(skill_name, input)
        current_time = time.time()

        # Create new cache entry
        entry = CacheEntry(
            output=output,
            skill_name=skill_name,
            timestamp=current_time,
            access_count=0,
            last_access=current_time,
        )

        # If the key already exists, replace it (move to end)
        if cache_key in self._cache:
            self._cache.move_to_end(cache_key)
            self._cache[cache_key] = entry
        else:
            # Add new entry and enforce LRU eviction
            self._cache[cache_key] = entry

            # Evict oldest entries if over capacity
            while len(self._cache) > self._max_size:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                self._stats.evictions += 1

    def invalidate(self, skill_name: str, input: Optional[SkillInput] = None) -> int:
        """
        Invalidate cached results.

        Args:
            skill_name: Name of the skill (if input is None, invalidates all entries for this skill)
            input: Specific input to invalidate (if provided, invalidates only this specific entry)

        Returns:
            Number of entries invalidated
        """  # noqa: E501
        if not self._enabled:
            return 0

        invalidated = 0

        if input is None:
            # Invalidate all entries for the skill
            keys_to_remove = []
            for cache_key, entry in self._cache.items():
                if entry.skill_name == skill_name:
                    keys_to_remove.append(cache_key)

            for key in keys_to_remove:
                del self._cache[key]
                invalidated += 1
        else:
            # Invalidate specific entry
            cache_key = self._generate_cache_key(skill_name, input)
            if cache_key in self._cache:
                del self._cache[cache_key]
                invalidated += 1

        return invalidated

    def clear(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()
        self._stats = CacheStatistics()

    def cleanup_expired(self, ttl: Optional[float] = None) -> int:
        """
        Remove all expired entries from the cache.

        Args:
            ttl: Optional override for TTL check

        Returns:
            Number of entries removed
        """
        if not self._enabled:
            return 0

        effective_ttl = ttl if ttl is not None else self._default_ttl

        if effective_ttl is None:
            return 0  # No expiration if no TTL

        keys_to_remove = []
        for cache_key, entry in self._cache.items():
            if entry.is_expired(effective_ttl):
                keys_to_remove.append(cache_key)

        for key in keys_to_remove:
            del self._cache[key]

        return len(keys_to_remove)

    def get_entries_by_skill(self, skill_name: str) -> list[dict[str, Any]]:
        """
        Get all cached entries for a specific skill.

        Args:
            skill_name: Name of the skill

        Returns:
            List of cache entry information (excluding the output itself)
        """
        if not self._enabled:
            return []

        entries = []
        skill_hash_prefix = hashlib.md5(skill_name.encode()).hexdigest()[:8]

        for cache_key, entry in self._cache.items():
            if cache_key.startswith(skill_hash_prefix):
                entries.append(
                    {
                        "cache_key": cache_key,
                        "timestamp": entry.timestamp,
                        "last_access": entry.last_access,
                        "access_count": entry.access_count,
                        "is_expired": entry.is_expired(self._default_ttl),
                    }
                )

        return entries

    def reset_statistics(self) -> None:
        """Reset cache statistics."""
        self._stats = CacheStatistics()
