"""@Time: 2025-08-03
@Author: Claude Code
@File: conflict_resolution_system.py
@Description: Conflict resolution system for collaborative review environment with graceful degradation
"""

import asyncio
import logging
import threading
import time
import uuid
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from queue import Queue
from typing import Any, Optional

logger = logging.getLogger(__name__)


class ConflictType(Enum):
    """Types of conflicts that can occur in collaborative review"""
    CONCURRENT_EDIT = "concurrent_edit"
    COMMENT_CONFLICT = "comment_conflict"
    ANNOTATION_CONFLICT = "annotation_conflict"
    STATUS_CONFLICT = "status_conflict"
    VERSION_CONFLICT = "version_conflict"
    DIRECT_CONTRADICTION = "direct_contradiction"
    PARTIAL_OVERLAP = "partial_overlap"
    TEMPORAL_INCONSISTENCY = "temporal_inconsistency"
    SOURCE_DISAGREEMENT = "source_disagreement"


class ConflictPriority(Enum):
    """Priority levels for conflict resolution"""
    HIGH = "high"  # Immediate resolution required
    MEDIUM = "medium"  # Resolution within minutes
    LOW = "low"  # Resolution within hours


class ResolutionStrategy(Enum):
    """Strategies for resolving conflicts"""
    LAST_WRITE_WINS = "last_write_wins"
    FIRST_WRITE_WINS = "first_write_wins"
    MANUAL_REVIEW = "manual_review"
    MERGE = "merge"
    VOTING = "voting"
    PRIORITY_BASED = "priority_based"


@dataclass
class Conflict:
    """Represents a conflict in the review system"""
    conflict_id: str
    conflict_type: ConflictType
    priority: ConflictPriority
    affected_resources: list[str]
    conflicting_operations: list[dict[str, Any]]
    timestamp: datetime
    user_ids: set[str]
    context: dict[str, Any] = field(default_factory=dict)
    resolution_strategy: ResolutionStrategy = ResolutionStrategy.MANUAL_REVIEW
    
    def to_dict(self) -> dict[str, Any]:
        """Convert conflict to dictionary"""
        return {
            'conflict_id': self.conflict_id,
            'conflict_type': self.conflict_type.value,
            'priority': self.priority.value,
            'affected_resources': self.affected_resources,
            'conflicting_operations': self.conflicting_operations,
            'timestamp': self.timestamp.isoformat(),
            'user_ids': list(self.user_ids),
            'context': self.context,
            'resolution_strategy': self.resolution_strategy.value
        }


@dataclass
class ResolutionResult:
    """Result of conflict resolution"""
    conflict_id: str
    resolution_strategy: ResolutionStrategy
    resolved_operations: list[dict[str, Any]]
    resolution_time: datetime
    resolver_id: Optional[str]
    success: bool
    message: str
    fallback_used: bool = False
    
    def to_dict(self) -> dict[str, Any]:
        """Convert resolution result to dictionary"""
        return {
            'conflict_id': self.conflict_id,
            'resolution_strategy': self.resolution_strategy.value,
            'resolved_operations': self.resolved_operations,
            'resolution_time': self.resolution_time.isoformat(),
            'resolver_id': self.resolver_id,
            'success': self.success,
            'message': self.message,
            'fallback_used': self.fallback_used
        }


class ConflictResolutionSystem:
    """Conflict resolution system with graceful degradation
    Handles concurrent editing, comment conflicts, and review conflicts
    """
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.conflict_queue = Queue()
        self.resolved_conflicts: dict[str, ResolutionResult] = {}
        self.active_conflicts: dict[str, Conflict] = {}
        self.resolution_strategies: dict[ConflictType, list[ResolutionStrategy]] = {
            ConflictType.CONCURRENT_EDIT: [
                ResolutionStrategy.LAST_WRITE_WINS,
                ResolutionStrategy.MERGE,
                ResolutionStrategy.MANUAL_REVIEW
            ],
            ConflictType.COMMENT_CONFLICT: [
                ResolutionStrategy.VOTING,
                ResolutionStrategy.PRIORITY_BASED,
                ResolutionStrategy.MANUAL_REVIEW
            ],
            ConflictType.ANNOTATION_CONFLICT: [
                ResolutionStrategy.FIRST_WRITE_WINS,
                ResolutionStrategy.MANUAL_REVIEW
            ],
            ConflictType.STATUS_CONFLICT: [
                ResolutionStrategy.PRIORITY_BASED,
                ResolutionStrategy.LAST_WRITE_WINS
            ],
            ConflictType.VERSION_CONFLICT: [
                ResolutionStrategy.MANUAL_REVIEW,
                ResolutionStrategy.FIRST_WRITE_WINS
            ]
        }
        
        # Graceful degradation settings
        self.fallback_strategy = ResolutionStrategy.LAST_WRITE_WINS
        self.max_resolution_time = 30.0  # seconds
        self.max_queue_size = 1000
        
        # Performance monitoring
        self.resolution_times: list[float] = []
        self.conflict_counts: dict[ConflictType, int] = {}
        
        # Background processing
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._running = False
        self._lock = threading.Lock()
        
        # Event handlers
        self.conflict_handlers: dict[str, Callable] = {}
        self.resolution_handlers: dict[str, Callable] = {}
        
    async def start(self) -> None:
        """Start the conflict resolution system"""
        self._running = True
        logger.info("Conflict resolution system started")
        
        # Start background processor
        asyncio.create_task(self._process_conflicts())
        
    async def stop(self) -> None:
        """Stop the conflict resolution system"""
        self._running = False
        self.executor.shutdown(wait=True)
        logger.info("Conflict resolution system stopped")
        
    async def detect_conflict(self, operations: list[dict[str, Any]]) -> Optional[Conflict]:
        """Detect potential conflicts in operations
        Returns conflict if detected, None otherwise
        """
        try:
            # Check for concurrent editing conflicts
            concurrent_conflict = await self._detect_concurrent_edit_conflict(operations)
            if concurrent_conflict:
                return concurrent_conflict
                
            # Check for comment conflicts
            comment_conflict = await self._detect_comment_conflict(operations)
            if comment_conflict:
                return comment_conflict
                
            # Check for annotation conflicts
            annotation_conflict = await self._detect_annotation_conflict(operations)
            if annotation_conflict:
                return annotation_conflict
                
            # Check for status conflicts
            status_conflict = await self._detect_status_conflict(operations)
            if status_conflict:
                return status_conflict
                
            # Check for version conflicts
            version_conflict = await self._detect_version_conflict(operations)
            if version_conflict:
                return version_conflict
                
            return None
            
        except Exception as e:
            logger.error(f"Error detecting conflict: {e}")
            # Graceful degradation: return None to continue processing
            return None
            
    async def submit_conflict(self, conflict: Conflict) -> str:
        """Submit a conflict for resolution"""
        try:
            # Check queue size for graceful degradation
            if self.conflict_queue.qsize() >= self.max_queue_size:
                logger.warning(f"Conflict queue full, dropping low priority conflict: {conflict.conflict_id}")
                # Resolve immediately with fallback strategy
                return await self._resolve_immediate(conflict)
                
            with self._lock:
                self.active_conflicts[conflict.conflict_id] = conflict
                
            self.conflict_queue.put(conflict)
            
            # Track conflict statistics
            conflict_type = conflict.conflict_type
            self.conflict_counts[conflict_type] = self.conflict_counts.get(conflict_type, 0) + 1
            
            # Trigger conflict event
            await self._trigger_event('conflict_detected', conflict)
            
            logger.info(f"Conflict submitted: {conflict.conflict_id} ({conflict.conflict_type.value})")
            return conflict.conflict_id
            
        except Exception as e:
            logger.error(f"Error submitting conflict: {e}")
            # Graceful degradation: resolve immediately
            return await self._resolve_immediate(conflict)
            
    async def resolve_conflict(self, conflict_id: str, strategy: Optional[ResolutionStrategy] = None) -> ResolutionResult:
        """Manually resolve a specific conflict"""
        try:
            with self._lock:
                conflict = self.active_conflicts.get(conflict_id)
                
            if not conflict:
                raise ValueError(f"Conflict not found: {conflict_id}")
                
            if strategy:
                conflict.resolution_strategy = strategy
                
            result = await self._execute_resolution(conflict)
            
            with self._lock:
                self.resolved_conflicts[conflict_id] = result
                if conflict_id in self.active_conflicts:
                    del self.active_conflicts[conflict_id]
                    
            # Trigger resolution event
            await self._trigger_event('conflict_resolved', result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error resolving conflict {conflict_id}: {e}")
            # Graceful degradation: return fallback result
            return ResolutionResult(
                conflict_id=conflict_id,
                resolution_strategy=self.fallback_strategy,
                resolved_operations=[],
                resolution_time=datetime.now(),
                resolver_id='system',
                success=False,
                message=f"Resolution failed: {str(e)}",
                fallback_used=True
            )
            
    async def get_conflict_status(self, conflict_id: str) -> dict[str, Any]:
        """Get status of a conflict"""
        with self._lock:
            if conflict_id in self.active_conflicts:
                conflict = self.active_conflicts[conflict_id]
                return {
                    'status': 'active',
                    'conflict': conflict.to_dict()
                }
            elif conflict_id in self.resolved_conflicts:
                result = self.resolved_conflicts[conflict_id]
                return {
                    'status': 'resolved',
                    'resolution': result.to_dict()
                }
            else:
                return {'status': 'not_found'}
                
    async def get_system_stats(self) -> dict[str, Any]:
        """Get system statistics"""
        with self._lock:
            active_count = len(self.active_conflicts)
            resolved_count = len(self.resolved_conflicts)
            queue_size = self.conflict_queue.qsize()
            
        avg_resolution_time = (
            sum(self.resolution_times) / len(self.resolution_times)
            if self.resolution_times else 0.0
        )
        
        return {
            'active_conflicts': active_count,
            'resolved_conflicts': resolved_count,
            'queue_size': queue_size,
            'avg_resolution_time': avg_resolution_time,
            'conflict_counts': {ct.value: count for ct, count in self.conflict_counts.items()},
            'system_running': self._running,
            'fallback_strategy': self.fallback_strategy.value
        }
        
    def register_handler(self, event_type: str, handler: Callable) -> None:
        """Register event handler"""
        if event_type == 'conflict_detected':
            self.conflict_handlers[handler.__name__] = handler
        elif event_type == 'conflict_resolved':
            self.resolution_handlers[handler.__name__] = handler
            
    # Private methods for conflict detection
    async def _detect_concurrent_edit_conflict(self, operations: list[dict[str, Any]]) -> Optional[Conflict]:
        """Detect concurrent editing conflicts"""
        # Group operations by resource
        resource_ops = {}
        for op in operations:
            resource_id = op.get('resource_id')
            if resource_id:
                if resource_id not in resource_ops:
                    resource_ops[resource_id] = []
                resource_ops[resource_id].append(op)
                
        # Check for concurrent edits on same resource
        for resource_id, ops in resource_ops.items():
            if len(ops) > 1:
                # Check if operations overlap in time
                timestamps = [op.get('timestamp', datetime.now()) for op in ops]
                if self._check_time_overlap(timestamps):
                    return Conflict(
                        conflict_id=str(uuid.uuid4()),
                        conflict_type=ConflictType.CONCURRENT_EDIT,
                        priority=ConflictPriority.HIGH,
                        affected_resources=[resource_id],
                        conflicting_operations=ops,
                        timestamp=datetime.now(),
                        user_ids={op.get('user_id', 'unknown') for op in ops}
                    )
                    
        return None
        
    async def _detect_comment_conflict(self, operations: list[dict[str, Any]]) -> Optional[Conflict]:
        """Detect comment conflicts"""
        comment_ops = [op for op in operations if op.get('type') == 'comment']
        
        # Group by parent resource
        resource_comments = {}
        for op in comment_ops:
            resource_id = op.get('resource_id')
            if resource_id:
                if resource_id not in resource_comments:
                    resource_comments[resource_id] = []
                resource_comments[resource_id].append(op)
                
        # Check for conflicting comments
        for resource_id, comments in resource_comments.items():
            if len(comments) > 1:
                # Check for contradictory content
                if self._check_contradictory_comments(comments):
                    return Conflict(
                        conflict_id=str(uuid.uuid4()),
                        conflict_type=ConflictType.COMMENT_CONFLICT,
                        priority=ConflictPriority.MEDIUM,
                        affected_resources=[resource_id],
                        conflicting_operations=comments,
                        timestamp=datetime.now(),
                        user_ids={op.get('user_id', 'unknown') for op in comments}
                    )
                    
        return None
        
    async def _detect_annotation_conflict(self, operations: list[dict[str, Any]]) -> Optional[Conflict]:
        """Detect annotation conflicts"""
        annotation_ops = [op for op in operations if op.get('type') == 'annotation']
        
        # Group by annotated resource
        resource_annotations = {}
        for op in annotation_ops:
            resource_id = op.get('resource_id')
            if resource_id:
                if resource_id not in resource_annotations:
                    resource_annotations[resource_id] = []
                resource_annotations[resource_id].append(op)
                
        # Check for overlapping annotations
        for resource_id, annotations in resource_annotations.items():
            if len(annotations) > 1:
                # Check for spatial overlap
                if self._check_annotation_overlap(annotations):
                    return Conflict(
                        conflict_id=str(uuid.uuid4()),
                        conflict_type=ConflictType.ANNOTATION_CONFLICT,
                        priority=ConflictPriority.LOW,
                        affected_resources=[resource_id],
                        conflicting_operations=annotations,
                        timestamp=datetime.now(),
                        user_ids={op.get('user_id', 'unknown') for op in annotations}
                    )
                    
        return None
        
    async def _detect_status_conflict(self, operations: list[dict[str, Any]]) -> Optional[Conflict]:
        """Detect status conflicts"""
        status_ops = [op for op in operations if op.get('type') == 'status_change']
        
        # Group by resource
        resource_statuses = {}
        for op in status_ops:
            resource_id = op.get('resource_id')
            if resource_id:
                if resource_id not in resource_statuses:
                    resource_statuses[resource_id] = []
                resource_statuses[resource_id].append(op)
                
        # Check for conflicting status changes
        for resource_id, statuses in resource_statuses.items():
            if len(statuses) > 1:
                # Check for incompatible statuses
                if self._check_incompatible_statuses(statuses):
                    return Conflict(
                        conflict_id=str(uuid.uuid4()),
                        conflict_type=ConflictType.STATUS_CONFLICT,
                        priority=ConflictPriority.HIGH,
                        affected_resources=[resource_id],
                        conflicting_operations=statuses,
                        timestamp=datetime.now(),
                        user_ids={op.get('user_id', 'unknown') for op in statuses}
                    )
                    
        return None
        
    async def _detect_version_conflict(self, operations: list[dict[str, Any]]) -> Optional[Conflict]:
        """Detect version conflicts"""
        version_ops = [op for op in operations if op.get('type') == 'version_change']
        
        # Check for version conflicts
        if len(version_ops) > 1:
            versions = [op.get('version', 0) for op in version_ops]
            if len(set(versions)) > 1:
                return Conflict(
                    conflict_id=str(uuid.uuid4()),
                    conflict_type=ConflictType.VERSION_CONFLICT,
                    priority=ConflictPriority.HIGH,
                    affected_resources=[op.get('resource_id') for op in version_ops],
                    conflicting_operations=version_ops,
                    timestamp=datetime.now(),
                    user_ids={op.get('user_id', 'unknown') for op in version_ops}
                )
                
        return None
        
    # Private helper methods
    def _check_time_overlap(self, timestamps: list[datetime]) -> bool:
        """Check if timestamps overlap within a threshold"""
        if len(timestamps) < 2:
            return False
            
        # Sort timestamps
        sorted_times = sorted(timestamps)
        
        # Check if any two are within 5 seconds
        for i in range(len(sorted_times) - 1):
            diff = (sorted_times[i + 1] - sorted_times[i]).total_seconds()
            if diff < 5.0:
                return True
                
        return False
        
    def _check_contradictory_comments(self, comments: list[dict[str, Any]]) -> bool:
        """Check if comments are contradictory"""
        # Simple heuristic: check for opposing sentiment keywords
        positive_keywords = ['good', 'great', 'excellent', 'approve', 'agree']
        negative_keywords = ['bad', 'poor', 'terrible', 'reject', 'disagree']
        
        sentiments = []
        for comment in comments:
            content = comment.get('content', '').lower()
            if any(keyword in content for keyword in positive_keywords):
                sentiments.append('positive')
            elif any(keyword in content for keyword in negative_keywords):
                sentiments.append('negative')
                
        return len(set(sentiments)) > 1
        
    def _check_annotation_overlap(self, annotations: list[dict[str, Any]]) -> bool:
        """Check if annotations overlap spatially"""
        # Simple overlap detection
        for i, ann1 in enumerate(annotations):
            for j, ann2 in enumerate(annotations[i + 1:], i + 1):
                pos1 = ann1.get('position', {})
                pos2 = ann2.get('position', {})
                
                # Simple bounding box overlap
                if (pos1.get('start') <= pos2.get('end', pos2.get('start')) and
                    pos2.get('start') <= pos1.get('end', pos1.get('start'))):
                    return True
                    
        return False
        
    def _check_incompatible_statuses(self, statuses: list[dict[str, Any]]) -> bool:
        """Check if statuses are incompatible"""
        # Define incompatible status pairs
        incompatible_pairs = [
            ('approved', 'rejected'),
            ('active', 'closed'),
            ('draft', 'published')
        ]
        
        status_values = [status.get('status', '') for status in statuses]
        
        for pair in incompatible_pairs:
            if all(s in status_values for s in pair):
                return True
                
        return False
        
    async def _execute_resolution(self, conflict: Conflict) -> ResolutionResult:
        """Execute conflict resolution with timing and fallback"""
        start_time = time.time()
        
        try:
            # Choose resolution strategy
            strategy = conflict.resolution_strategy
            
            # Execute strategy with timeout
            result = await asyncio.wait_for(
                self._apply_resolution_strategy(conflict, strategy),
                timeout=self.max_resolution_time
            )
            
            resolution_time = time.time() - start_time
            self.resolution_times.append(resolution_time)
            
            return result
            
        except asyncio.TimeoutError:
            logger.warning(f"Resolution timeout for conflict {conflict.conflict_id}, using fallback")
            # Graceful degradation: use fallback strategy
            return await self._apply_resolution_strategy(conflict, self.fallback_strategy)
            
        except Exception as e:
            logger.error(f"Error in resolution execution: {e}")
            # Graceful degradation: use fallback strategy
            fallback_result = await self._apply_resolution_strategy(conflict, self.fallback_strategy)
            fallback_result.fallback_used = True
            fallback_result.message = f"Original strategy failed: {str(e)}. Used fallback: {fallback_result.message}"
            return fallback_result
            
    async def _apply_resolution_strategy(self, conflict: Conflict, strategy: ResolutionStrategy) -> ResolutionResult:
        """Apply specific resolution strategy"""
        try:
            if strategy == ResolutionStrategy.LAST_WRITE_WINS:
                return await self._resolve_last_write_wins(conflict)
            elif strategy == ResolutionStrategy.FIRST_WRITE_WINS:
                return await self._resolve_first_write_wins(conflict)
            elif strategy == ResolutionStrategy.MANUAL_REVIEW:
                return await self._resolve_manual_review(conflict)
            elif strategy == ResolutionStrategy.MERGE:
                return await self._resolve_merge(conflict)
            elif strategy == ResolutionStrategy.VOTING:
                return await self._resolve_voting(conflict)
            elif strategy == ResolutionStrategy.PRIORITY_BASED:
                return await self._resolve_priority_based(conflict)
            else:
                raise ValueError(f"Unknown resolution strategy: {strategy}")
                
        except Exception as e:
            logger.error(f"Error applying strategy {strategy}: {e}")
            # Last resort fallback
            return ResolutionResult(
                conflict_id=conflict.conflict_id,
                resolution_strategy=ResolutionStrategy.LAST_WRITE_WINS,
                resolved_operations=[conflict.conflicting_operations[-1]],  # Last operation
                resolution_time=datetime.now(),
                resolver_id='system',
                success=True,
                message="Fallback resolution applied due to strategy failure",
                fallback_used=True
            )
            
    async def _resolve_last_write_wins(self, conflict: Conflict) -> ResolutionResult:
        """Resolve using last write wins strategy"""
        # Sort by timestamp and take the latest
        sorted_ops = sorted(
            conflict.conflicting_operations,
            key=lambda x: x.get('timestamp', datetime.now()),
            reverse=True
        )
        
        return ResolutionResult(
            conflict_id=conflict.conflict_id,
            resolution_strategy=ResolutionStrategy.LAST_WRITE_WINS,
            resolved_operations=[sorted_ops[0]],
            resolution_time=datetime.now(),
            resolver_id='system',
            success=True,
            message="Resolved using last write wins strategy"
        )
        
    async def _resolve_first_write_wins(self, conflict: Conflict) -> ResolutionResult:
        """Resolve using first write wins strategy"""
        # Sort by timestamp and take the earliest
        sorted_ops = sorted(
            conflict.conflicting_operations,
            key=lambda x: x.get('timestamp', datetime.now())
        )
        
        return ResolutionResult(
            conflict_id=conflict.conflict_id,
            resolution_strategy=ResolutionStrategy.FIRST_WRITE_WINS,
            resolved_operations=[sorted_ops[0]],
            resolution_time=datetime.now(),
            resolver_id='system',
            success=True,
            message="Resolved using first write wins strategy"
        )
        
    async def _resolve_manual_review(self, conflict: Conflict) -> ResolutionResult:
        """Resolve using manual review (placeholder for UI integration)"""
        # In a real implementation, this would wait for user input
        # For now, use fallback strategy
        return await self._resolve_last_write_wins(conflict)
        
    async def _resolve_merge(self, conflict: Conflict) -> ResolutionResult:
        """Resolve using merge strategy"""
        # Simple merge: combine non-conflicting parts
        merged_ops = []
        
        # Group by operation type
        op_types = {}
        for op in conflict.conflicting_operations:
            op_type = op.get('type')
            if op_type not in op_types:
                op_types[op_type] = []
            op_types[op_type].append(op)
            
        # Take latest operation of each type
        for op_type, ops in op_types.items():
            latest_op = max(ops, key=lambda x: x.get('timestamp', datetime.now()))
            merged_ops.append(latest_op)
            
        return ResolutionResult(
            conflict_id=conflict.conflict_id,
            resolution_strategy=ResolutionStrategy.MERGE,
            resolved_operations=merged_ops,
            resolution_time=datetime.now(),
            resolver_id='system',
            success=True,
            message="Resolved using merge strategy"
        )
        
    async def _resolve_voting(self, conflict: Conflict) -> ResolutionResult:
        """Resolve using voting strategy"""
        # Simple majority voting based on user priorities
        user_votes = {}
        
        for op in conflict.conflicting_operations:
            user_id = op.get('user_id', 'unknown')
            # In a real implementation, this would consider user roles/permissions
            user_votes[user_id] = op
            
        # For now, just take the first operation (simplified voting)
        winning_op = list(user_votes.values())[0]
        
        return ResolutionResult(
            conflict_id=conflict.conflict_id,
            resolution_strategy=ResolutionStrategy.VOTING,
            resolved_operations=[winning_op],
            resolution_time=datetime.now(),
            resolver_id='system',
            success=True,
            message="Resolved using voting strategy"
        )
        
    async def _resolve_priority_based(self, conflict: Conflict) -> ResolutionResult:
        """Resolve using priority-based strategy"""
        # Sort by operation priority or user priority
        def get_priority(op):
            # Simple priority based on operation type
            type_priority = {
                'status_change': 3,
                'version_change': 2,
                'annotation': 1,
                'comment': 0
            }
            return type_priority.get(op.get('type'), 0)
            
        sorted_ops = sorted(
            conflict.conflicting_operations,
            key=get_priority,
            reverse=True
        )
        
        return ResolutionResult(
            conflict_id=conflict.conflict_id,
            resolution_strategy=ResolutionStrategy.PRIORITY_BASED,
            resolved_operations=[sorted_ops[0]],
            resolution_time=datetime.now(),
            resolver_id='system',
            success=True,
            message="Resolved using priority-based strategy"
        )
        
    async def _resolve_immediate(self, conflict: Conflict) -> str:
        """Resolve conflict immediately with fallback strategy"""
        try:
            result = await self._apply_resolution_strategy(conflict, self.fallback_strategy)
            
            with self._lock:
                self.resolved_conflicts[conflict.conflict_id] = result
                
            logger.info(f"Immediate resolution completed for conflict {conflict.conflict_id}")
            return conflict.conflict_id
            
        except Exception as e:
            logger.error(f"Error in immediate resolution: {e}")
            return conflict.conflict_id
            
    async def _process_conflicts(self) -> None:
        """Background conflict processing"""
        while self._running:
            try:
                # Get conflict from queue with timeout
                try:
                    conflict = self.conflict_queue.get(timeout=1.0)
                except:
                    continue
                    
                # Process conflict in background
                asyncio.create_task(self._process_single_conflict(conflict))
                
            except Exception as e:
                logger.error(f"Error in conflict processing loop: {e}")
                await asyncio.sleep(1.0)
                
    async def _process_single_conflict(self, conflict: Conflict) -> None:
        """Process a single conflict"""
        try:
            # Choose best strategy based on conflict type
            available_strategies = self.resolution_strategies.get(conflict.conflict_type, [self.fallback_strategy])
            
            # Use the first available strategy (could be enhanced with AI selection)
            strategy = available_strategies[0]
            
            # Execute resolution
            result = await self._execute_resolution(conflict)
            
            # Store result
            with self._lock:
                self.resolved_conflicts[conflict.conflict_id] = result
                if conflict.conflict_id in self.active_conflicts:
                    del self.active_conflicts[conflict.conflict_id]
                    
            # Trigger event
            await self._trigger_event('conflict_resolved', result)
            
            logger.info(f"Conflict {conflict.conflict_id} resolved using {strategy.value}")
            
        except Exception as e:
            logger.error(f"Error processing conflict {conflict.conflict_id}: {e}")
            # Ensure conflict is removed from active conflicts
            with self._lock:
                if conflict.conflict_id in self.active_conflicts:
                    del self.active_conflicts[conflict.conflict_id]
                    
    async def _trigger_event(self, event_type: str, data: Any) -> None:
        """Trigger event handlers"""
        try:
            if event_type == 'conflict_detected':
                for handler in self.conflict_handlers.values():
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(data)
                        else:
                            handler(data)
                    except Exception as e:
                        logger.error(f"Error in conflict handler: {e}")
                        
            elif event_type == 'conflict_resolved':
                for handler in self.resolution_handlers.values():
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(data)
                        else:
                            handler(data)
                    except Exception as e:
                        logger.error(f"Error in resolution handler: {e}")
                        
        except Exception as e:
            logger.error(f"Error triggering events: {e}")


# Singleton instance for global use
conflict_resolution_system = ConflictResolutionSystem()