"""@Time: 2025-08-03
@Author: Claude Code
@File: review_analytics.py
@Description: Review analytics system for analyzing collaborative review processes with graceful degradation
"""

import asyncio
import logging
import threading
import time
import uuid
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of analytics metrics"""
    PARTICIPATION = "participation"
    QUALITY = "quality"
    EFFICIENCY = "efficiency"
    COVERAGE = "coverage"
    CONFLICT = "conflict"
    SATISFACTION = "satisfaction"


class AnalysisScope(Enum):
    """Scope of analysis"""
    SESSION = "session"
    REVIEWER = "reviewer"
    RESOURCE = "resource"
    TEAM = "team"
    TEMPORAL = "temporal"


@dataclass
class ReviewMetric:
    """Represents a review metric"""
    metric_id: str
    metric_type: MetricType
    name: str
    value: float
    scope: AnalysisScope
    timestamp: datetime
    context: dict[str, Any] = field(default_factory=dict)
    threshold: Optional[float] = None
    unit: str = ""
    
    def to_dict(self) -> dict[str, Any]:
        """Convert metric to dictionary"""
        return {
            'metric_id': self.metric_id,
            'metric_type': self.metric_type.value,
            'name': self.name,
            'value': self.value,
            'scope': self.scope.value,
            'timestamp': self.timestamp.isoformat(),
            'context': self.context,
            'threshold': self.threshold,
            'unit': self.unit
        }


@dataclass
class ReviewInsight:
    """Represents an insight derived from analytics"""
    insight_id: str
    title: str
    description: str
    insight_type: str
    confidence: float
    impact_level: str
    actionable: bool
    recommendations: list[str]
    related_metrics: list[str]
    timestamp: datetime
    
    def to_dict(self) -> dict[str, Any]:
        """Convert insight to dictionary"""
        return {
            'insight_id': self.insight_id,
            'title': self.title,
            'description': self.description,
            'insight_type': self.insight_type,
            'confidence': self.confidence,
            'impact_level': self.impact_level,
            'actionable': self.actionable,
            'recommendations': self.recommendations,
            'related_metrics': self.related_metrics,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class AnalyticsReport:
    """Represents an analytics report"""
    report_id: str
    title: str
    scope: AnalysisScope
    time_period: tuple[datetime, datetime]
    metrics: list[ReviewMetric]
    insights: list[ReviewInsight]
    summary: str
    generated_at: datetime
    
    def to_dict(self) -> dict[str, Any]:
        """Convert report to dictionary"""
        return {
            'report_id': self.report_id,
            'title': self.title,
            'scope': self.scope.value,
            'time_period': (self.time_period[0].isoformat(), self.time_period[1].isoformat()),
            'metrics': [m.to_dict() for m in self.metrics],
            'insights': [i.to_dict() for i in self.insights],
            'summary': self.summary,
            'generated_at': self.generated_at.isoformat()
        }


class ReviewAnalytics:
    """Review analytics system with graceful degradation
    Analyzes collaborative review processes and provides insights
    """
    
    def __init__(self, max_history_size: int = 10000):
        self.max_history_size = max_history_size
        
        # Data storage
        self.metrics_history: deque = deque(maxlen=max_history_size)
        self.insights_history: deque = deque(maxlen=max_history_size)
        self.reports_history: deque = deque(maxlen=1000)
        
        # Performance tracking
        self.calculation_times: dict[str, list[float]] = defaultdict(list)
        self.last_calculation_time: dict[str, float] = {}
        
        # Graceful degradation settings
        self.max_calculation_time = 5.0  # seconds
        self.fallback_cache_size = 1000
        self.cache_ttl = 300  # seconds
        
        # Caching
        self.metric_cache: dict[str, tuple[float, datetime]] = {}
        self.insight_cache: dict[str, tuple[ReviewInsight, datetime]] = {}
        
        # Background processing
        self._running = False
        self._lock = threading.Lock()
        
        # Analytics processors
        self.metric_processors: dict[MetricType, Callable] = {}
        self.insight_generators: list[Callable] = []
        
        # Configuration
        self.metric_thresholds: dict[str, float] = {
            'participation_rate': 0.7,
            'quality_score': 0.8,
            'efficiency_ratio': 0.6,
            'coverage_completeness': 0.9,
            'conflict_resolution_rate': 0.8,
            'satisfaction_score': 0.7
        }
        
    async def start(self) -> None:
        """Start the analytics system"""
        self._running = True
        logger.info("Review analytics system started")
        
        # Start background processors
        asyncio.create_task(self._periodic_metric_calculation())
        asyncio.create_task(self._periodic_insight_generation())
        asyncio.create_task(self._cache_cleanup())
        
    async def stop(self) -> None:
        """Stop the analytics system"""
        self._running = False
        logger.info("Review analytics system stopped")
        
    async def record_metric(self, metric: ReviewMetric) -> str:
        """Record a review metric"""
        try:
            with self._lock:
                self.metrics_history.append(metric)
                
            # Update cache
            self.metric_cache[metric.metric_id] = (metric.value, datetime.now())
            
            logger.debug(f"Recorded metric: {metric.name} = {metric.value}")
            return metric.metric_id
            
        except Exception as e:
            logger.error(f"Error recording metric: {e}")
            # Graceful degradation: continue without recording
            return metric.metric_id
            
    async def calculate_session_metrics(self, session_id: str) -> list[ReviewMetric]:
        """Calculate metrics for a specific session"""
        try:
            start_time = time.time()
            
            # Get session data (would be from database in real implementation)
            session_data = await self._get_session_data(session_id)
            
            metrics = []
            
            # Calculate participation metrics
            participation_metrics = await self._calculate_participation_metrics(session_data)
            metrics.extend(participation_metrics)
            
            # Calculate quality metrics
            quality_metrics = await self._calculate_quality_metrics(session_data)
            metrics.extend(quality_metrics)
            
            # Calculate efficiency metrics
            efficiency_metrics = await self._calculate_efficiency_metrics(session_data)
            metrics.extend(efficiency_metrics)
            
            # Check timeout
            calculation_time = time.time() - start_time
            if calculation_time > self.max_calculation_time:
                logger.warning(f"Session metrics calculation timeout: {calculation_time:.2f}s")
                # Return partial results
                return metrics[:len(metrics)//2]  # Return half of metrics
                
            self.calculation_times['session_metrics'].append(calculation_time)
            self.last_calculation_time['session_metrics'] = calculation_time
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating session metrics: {e}")
            # Graceful degradation: return basic metrics
            return await self._get_basic_metrics(session_id)
            
    async def calculate_reviewer_metrics(self, reviewer_id: str) -> list[ReviewMetric]:
        """Calculate metrics for a specific reviewer"""
        try:
            start_time = time.time()
            
            # Get reviewer data
            reviewer_data = await self._get_reviewer_data(reviewer_id)
            
            metrics = []
            
            # Reviewer participation rate
            participation_rate = self._calculate_reviewer_participation(reviewer_data)
            metrics.append(ReviewMetric(
                metric_id=str(uuid.uuid4()),
                metric_type=MetricType.PARTICIPATION,
                name="reviewer_participation_rate",
                value=participation_rate,
                scope=AnalysisScope.REVIEWER,
                timestamp=datetime.now(),
                context={'reviewer_id': reviewer_id},
                threshold=self.metric_thresholds['participation_rate'],
                unit="percentage"
            ))
            
            # Reviewer quality score
            quality_score = self._calculate_reviewer_quality(reviewer_data)
            metrics.append(ReviewMetric(
                metric_id=str(uuid.uuid4()),
                metric_type=MetricType.QUALITY,
                name="reviewer_quality_score",
                value=quality_score,
                scope=AnalysisScope.REVIEWER,
                timestamp=datetime.now(),
                context={'reviewer_id': reviewer_id},
                threshold=self.metric_thresholds['quality_score'],
                unit="score"
            ))
            
            calculation_time = time.time() - start_time
            self.calculation_times['reviewer_metrics'].append(calculation_time)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating reviewer metrics: {e}")
            # Graceful degradation: return default metrics
            return [
                ReviewMetric(
                    metric_id=str(uuid.uuid4()),
                    metric_type=MetricType.PARTICIPATION,
                    name="reviewer_participation_rate",
                    value=0.5,
                    scope=AnalysisScope.REVIEWER,
                    timestamp=datetime.now(),
                    context={'reviewer_id': reviewer_id, 'error': str(e)},
                    threshold=self.metric_thresholds['participation_rate'],
                    unit="percentage"
                )
            ]
            
    async def generate_insights(self, scope: AnalysisScope, scope_id: str) -> list[ReviewInsight]:
        """Generate insights based on analytics data"""
        try:
            start_time = time.time()
            
            # Get relevant metrics
            metrics = await self._get_relevant_metrics(scope, scope_id)
            
            insights = []
            
            # Generate participation insights
            participation_insights = await self._generate_participation_insights(metrics)
            insights.extend(participation_insights)
            
            # Generate quality insights
            quality_insights = await self._generate_quality_insights(metrics)
            insights.extend(quality_insights)
            
            # Generate efficiency insights
            efficiency_insights = await self._generate_efficiency_insights(metrics)
            insights.extend(efficiency_insights)
            
            # Check timeout
            calculation_time = time.time() - start_time
            if calculation_time > self.max_calculation_time:
                logger.warning(f"Insight generation timeout: {calculation_time:.2f}s")
                # Return basic insights only
                return insights[:1] if insights else []
                
            with self._lock:
                for insight in insights:
                    self.insights_history.append(insight)
                    self.insight_cache[insight.insight_id] = (insight, datetime.now())
                    
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            # Graceful degradation: return empty list
            return []
            
    async def generate_report(self, scope: AnalysisScope, scope_id: str, 
                           time_period: tuple[datetime, datetime]) -> AnalyticsReport:
        """Generate comprehensive analytics report"""
        try:
            start_time = time.time()
            
            # Calculate metrics
            metrics = await self._calculate_report_metrics(scope, scope_id, time_period)
            
            # Generate insights
            insights = await self._generate_report_insights(metrics)
            
            # Generate summary
            summary = await self._generate_report_summary(metrics, insights)
            
            # Create report
            report = AnalyticsReport(
                report_id=str(uuid.uuid4()),
                title=f"{scope.value.title()} Analytics Report",
                scope=scope,
                time_period=time_period,
                metrics=metrics,
                insights=insights,
                summary=summary,
                generated_at=datetime.now()
            )
            
            with self._lock:
                self.reports_history.append(report)
                
            calculation_time = time.time() - start_time
            logger.info(f"Report generated in {calculation_time:.2f}s")
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            # Graceful degradation: return basic report
            return AnalyticsReport(
                report_id=str(uuid.uuid4()),
                title=f"{scope.value.title()} Analytics Report (Limited)",
                scope=scope,
                time_period=time_period,
                metrics=[],
                insights=[],
                summary=f"Report generation encountered errors: {str(e)}",
                generated_at=datetime.now()
            )
            
    async def get_system_stats(self) -> dict[str, Any]:
        """Get system statistics"""
        with self._lock:
            metrics_count = len(self.metrics_history)
            insights_count = len(self.insights_history)
            reports_count = len(self.reports_history)
            cache_size = len(self.metric_cache)
            
        # Calculate average calculation times
        avg_times = {}
        for metric_type, times in self.calculation_times.items():
            if times:
                avg_times[metric_type] = sum(times) / len(times)
                
        return {
            'metrics_recorded': metrics_count,
            'insights_generated': insights_count,
            'reports_generated': reports_count,
            'cache_size': cache_size,
            'avg_calculation_times': avg_times,
            'system_running': self._running,
            'max_history_size': self.max_history_size,
            'cache_ttl': self.cache_ttl
        }
        
    # Private methods for metric calculation
    async def _calculate_participation_metrics(self, session_data: dict[str, Any]) -> list[ReviewMetric]:
        """Calculate participation metrics"""
        metrics = []
        
        # Participation rate
        total_participants = session_data.get('total_participants', 0)
        active_participants = session_data.get('active_participants', 0)
        
        participation_rate = active_participants / total_participants if total_participants > 0 else 0.0
        
        metrics.append(ReviewMetric(
            metric_id=str(uuid.uuid4()),
            metric_type=MetricType.PARTICIPATION,
            name="participation_rate",
            value=participation_rate,
            scope=AnalysisScope.SESSION,
            timestamp=datetime.now(),
            context=session_data,
            threshold=self.metric_thresholds['participation_rate'],
            unit="percentage"
        ))
        
        # Comment frequency
        total_comments = session_data.get('total_comments', 0)
        session_duration = session_data.get('duration', 3600)  # seconds
        
        comment_frequency = total_comments / (session_duration / 3600) if session_duration > 0 else 0.0
        
        metrics.append(ReviewMetric(
            metric_id=str(uuid.uuid4()),
            metric_type=MetricType.PARTICIPATION,
            name="comment_frequency",
            value=comment_frequency,
            scope=AnalysisScope.SESSION,
            timestamp=datetime.now(),
            context=session_data,
            unit="comments_per_hour"
        ))
        
        return metrics
        
    async def _calculate_quality_metrics(self, session_data: dict[str, Any]) -> list[ReviewMetric]:
        """Calculate quality metrics"""
        metrics = []
        
        # Quality score based on various factors
        helpful_votes = session_data.get('helpful_votes', 0)
        total_votes = session_data.get('total_votes', 0)
        resolution_rate = session_data.get('resolution_rate', 0.0)
        
        quality_score = 0.0
        if total_votes > 0:
            quality_score += (helpful_votes / total_votes) * 0.5
        quality_score += resolution_rate * 0.5
        
        metrics.append(ReviewMetric(
            metric_id=str(uuid.uuid4()),
            metric_type=MetricType.QUALITY,
            name="quality_score",
            value=quality_score,
            scope=AnalysisScope.SESSION,
            timestamp=datetime.now(),
            context=session_data,
            threshold=self.metric_thresholds['quality_score'],
            unit="score"
        ))
        
        return metrics
        
    async def _calculate_efficiency_metrics(self, session_data: dict[str, Any]) -> list[ReviewMetric]:
        """Calculate efficiency metrics"""
        metrics = []
        
        # Efficiency ratio
        total_issues = session_data.get('total_issues', 0)
        resolved_issues = session_data.get('resolved_issues', 0)
        session_duration = session_data.get('duration', 3600)
        
        efficiency_ratio = resolved_issues / total_issues if total_issues > 0 else 0.0
        
        metrics.append(ReviewMetric(
            metric_id=str(uuid.uuid4()),
            metric_type=MetricType.EFFICIENCY,
            name="efficiency_ratio",
            value=efficiency_ratio,
            scope=AnalysisScope.SESSION,
            timestamp=datetime.now(),
            context=session_data,
            threshold=self.metric_thresholds['efficiency_ratio'],
            unit="ratio"
        ))
        
        # Resolution time
        avg_resolution_time = session_data.get('avg_resolution_time', 0.0)
        
        metrics.append(ReviewMetric(
            metric_id=str(uuid.uuid4()),
            metric_type=MetricType.EFFICIENCY,
            name="avg_resolution_time",
            value=avg_resolution_time,
            scope=AnalysisScope.SESSION,
            timestamp=datetime.now(),
            context=session_data,
            unit="seconds"
        ))
        
        return metrics
        
    async def _generate_participation_insights(self, metrics: list[ReviewMetric]) -> list[ReviewInsight]:
        """Generate participation-related insights"""
        insights = []
        
        # Find participation metrics
        participation_metrics = [m for m in metrics if m.metric_type == MetricType.PARTICIPATION]
        
        for metric in participation_metrics:
            if metric.threshold and metric.value < metric.threshold:
                insights.append(ReviewInsight(
                    insight_id=str(uuid.uuid4()),
                    title="Low Participation Detected",
                    description=f"Participation rate ({metric.value:.2f}) is below threshold ({metric.threshold})",
                    insight_type="participation_warning",
                    confidence=0.8,
                    impact_level="medium",
                    actionable=True,
                    recommendations=[
                        "Send reminders to inactive participants",
                        "Simplify the review process",
                        "Provide incentives for participation"
                    ],
                    related_metrics=[metric.metric_id],
                    timestamp=datetime.now()
                ))
                
        return insights
        
    async def _generate_quality_insights(self, metrics: list[ReviewMetric]) -> list[ReviewInsight]:
        """Generate quality-related insights"""
        insights = []
        
        # Find quality metrics
        quality_metrics = [m for m in metrics if m.metric_type == MetricType.QUALITY]
        
        for metric in quality_metrics:
            if metric.threshold and metric.value < metric.threshold:
                insights.append(ReviewInsight(
                    insight_id=str(uuid.uuid4()),
                    title="Quality Improvement Needed",
                    description=f"Quality score ({metric.value:.2f}) is below threshold ({metric.threshold})",
                    insight_type="quality_warning",
                    confidence=0.7,
                    impact_level="high",
                    actionable=True,
                    recommendations=[
                        "Provide reviewer training",
                        "Implement quality guidelines",
                        "Add peer review process"
                    ],
                    related_metrics=[metric.metric_id],
                    timestamp=datetime.now()
                ))
                
        return insights
        
    async def _generate_efficiency_insights(self, metrics: list[ReviewMetric]) -> list[ReviewInsight]:
        """Generate efficiency-related insights"""
        insights = []
        
        # Find efficiency metrics
        efficiency_metrics = [m for m in metrics if m.metric_type == MetricType.EFFICIENCY]
        
        for metric in efficiency_metrics:
            if metric.name == "avg_resolution_time" and metric.value > 3600:  # > 1 hour
                insights.append(ReviewInsight(
                    insight_id=str(uuid.uuid4()),
                    title="Slow Resolution Time",
                    description=f"Average resolution time ({metric.value:.0f}s) is high",
                    insight_type="efficiency_warning",
                    confidence=0.9,
                    impact_level="medium",
                    actionable=True,
                    recommendations=[
                        "Streamline decision process",
                        "Set clear deadlines",
                        "Automate routine tasks"
                    ],
                    related_metrics=[metric.metric_id],
                    timestamp=datetime.now()
                ))
                
        return insights
        
    # Helper methods
    async def _get_session_data(self, session_id: str) -> dict[str, Any]:
        """Get session data (placeholder)"""
        # In real implementation, this would query a database
        return {
            'session_id': session_id,
            'total_participants': 10,
            'active_participants': 7,
            'total_comments': 25,
            'duration': 7200,
            'helpful_votes': 18,
            'total_votes': 25,
            'resolution_rate': 0.8,
            'total_issues': 15,
            'resolved_issues': 12,
            'avg_resolution_time': 1800
        }
        
    async def _get_reviewer_data(self, reviewer_id: str) -> dict[str, Any]:
        """Get reviewer data (placeholder)"""
        # In real implementation, this would query a database
        return {
            'reviewer_id': reviewer_id,
            'sessions_participated': 15,
            'comments_made': 45,
            'helpful_votes_received': 30,
            'total_votes_received': 40,
            'issues_resolved': 12
        }
        
    def _calculate_reviewer_participation(self, reviewer_data: dict[str, Any]) -> float:
        """Calculate reviewer participation rate"""
        sessions_participated = reviewer_data.get('sessions_participated', 0)
        total_sessions = 20  # This would be from system config
        
        return sessions_participated / total_sessions if total_sessions > 0 else 0.0
        
    def _calculate_reviewer_quality(self, reviewer_data: dict[str, Any]) -> float:
        """Calculate reviewer quality score"""
        helpful_votes = reviewer_data.get('helpful_votes_received', 0)
        total_votes = reviewer_data.get('total_votes_received', 0)
        
        return helpful_votes / total_votes if total_votes > 0 else 0.5
        
    async def _get_basic_metrics(self, session_id: str) -> list[ReviewMetric]:
        """Get basic metrics for graceful degradation"""
        return [
            ReviewMetric(
                metric_id=str(uuid.uuid4()),
                metric_type=MetricType.PARTICIPATION,
                name="basic_participation_rate",
                value=0.5,
                scope=AnalysisScope.SESSION,
                timestamp=datetime.now(),
                context={'session_id': session_id, 'fallback': True},
                threshold=self.metric_thresholds['participation_rate'],
                unit="percentage"
            )
        ]
        
    async def _get_relevant_metrics(self, scope: AnalysisScope, scope_id: str) -> list[ReviewMetric]:
        """Get relevant metrics for insight generation"""
        with self._lock:
            # Filter metrics by scope and recent time period
            recent_metrics = []
            cutoff_time = datetime.now() - timedelta(days=7)
            
            for metric in self.metrics_history:
                if (metric.scope == scope and 
                    metric.timestamp > cutoff_time and
                    scope_id in str(metric.context.get(scope.value + '_id', ''))):
                    recent_metrics.append(metric)
                    
            return recent_metrics
            
    async def _calculate_report_metrics(self, scope: AnalysisScope, scope_id: str,
                                      time_period: tuple[datetime, datetime]) -> list[ReviewMetric]:
        """Calculate metrics for report"""
        # Get metrics within time period
        relevant_metrics = []
        with self._lock:
            for metric in self.metrics_history:
                if (time_period[0] <= metric.timestamp <= time_period[1] and
                    metric.scope == scope):
                    relevant_metrics.append(metric)
                    
        return relevant_metrics
        
    async def _generate_report_insights(self, metrics: list[ReviewMetric]) -> list[ReviewInsight]:
        """Generate insights for report"""
        all_insights = []
        
        # Generate insights by type
        participation_insights = await self._generate_participation_insights(metrics)
        all_insights.extend(participation_insights)
        
        quality_insights = await self._generate_quality_insights(metrics)
        all_insights.extend(quality_insights)
        
        efficiency_insights = await self._generate_efficiency_insights(metrics)
        all_insights.extend(efficiency_insights)
        
        return all_insights
        
    async def _generate_report_summary(self, metrics: list[ReviewMetric], insights: list[ReviewInsight]) -> str:
        """Generate report summary"""
        if not metrics:
            return "No metrics available for this time period."
            
        # Calculate overall metrics
        avg_quality = sum(m.value for m in metrics if m.metric_type == MetricType.QUALITY) / len([m for m in metrics if m.metric_type == MetricType.QUALITY])
        avg_efficiency = sum(m.value for m in metrics if m.metric_type == MetricType.EFFICIENCY) / len([m for m in metrics if m.metric_type == MetricType.EFFICIENCY])
        
        # Count issues
        warning_insights = [i for i in insights if i.impact_level in ["medium", "high"]]
        
        summary = "Report Summary:\n"
        summary += f"- Total metrics analyzed: {len(metrics)}\n"
        summary += f"- Average quality score: {avg_quality:.2f}\n"
        summary += f"- Average efficiency ratio: {avg_efficiency:.2f}\n"
        summary += f"- Actionable insights: {len([i for i in insights if i.actionable])}\n"
        summary += f"- Warnings identified: {len(warning_insights)}\n"
        
        return summary
        
    # Background tasks
    async def _periodic_metric_calculation(self) -> None:
        """Periodic metric calculation"""
        while self._running:
            try:
                # Calculate system-wide metrics
                await self._calculate_system_metrics()
                await asyncio.sleep(300)  # Every 5 minutes
            except Exception as e:
                logger.error(f"Error in periodic metric calculation: {e}")
                await asyncio.sleep(60)
                
    async def _periodic_insight_generation(self) -> None:
        """Periodic insight generation"""
        while self._running:
            try:
                # Generate system-wide insights
                await self._generate_system_insights()
                await asyncio.sleep(600)  # Every 10 minutes
            except Exception as e:
                logger.error(f"Error in periodic insight generation: {e}")
                await asyncio.sleep(120)
                
    async def _cache_cleanup(self) -> None:
        """Periodic cache cleanup"""
        while self._running:
            try:
                # Clean expired cache entries
                cutoff_time = datetime.now() - timedelta(seconds=self.cache_ttl)
                
                with self._lock:
                    # Clean metric cache
                    expired_metrics = [
                        key for key, (_, timestamp) in self.metric_cache.items()
                        if timestamp < cutoff_time
                    ]
                    for key in expired_metrics:
                        del self.metric_cache[key]
                        
                    # Clean insight cache
                    expired_insights = [
                        key for key, (_, timestamp) in self.insight_cache.items()
                        if timestamp < cutoff_time
                    ]
                    for key in expired_insights:
                        del self.insight_cache[key]
                        
                await asyncio.sleep(1800)  # Every 30 minutes
            except Exception as e:
                logger.error(f"Error in cache cleanup: {e}")
                await asyncio.sleep(300)
                
    async def _calculate_system_metrics(self) -> None:
        """Calculate system-wide metrics"""
        try:
            # System participation rate
            with self._lock:
                total_sessions = len(set(m.context.get('session_id') for m in self.metrics_history if 'session_id' in m.context))
                active_sessions = len([m for m in self.metrics_history if m.timestamp > datetime.now() - timedelta(hours=24)])
                
            if total_sessions > 0:
                system_participation = active_sessions / total_sessions
                
                metric = ReviewMetric(
                    metric_id=str(uuid.uuid4()),
                    metric_type=MetricType.PARTICIPATION,
                    name="system_participation_rate",
                    value=system_participation,
                    scope=AnalysisScope.TEAM,
                    timestamp=datetime.now(),
                    context={'total_sessions': total_sessions, 'active_sessions': active_sessions},
                    threshold=0.5,
                    unit="percentage"
                )
                
                await self.record_metric(metric)
                
        except Exception as e:
            logger.error(f"Error calculating system metrics: {e}")
            
    async def _generate_system_insights(self) -> None:
        """Generate system-wide insights"""
        try:
            # Get recent system metrics
            recent_metrics = []
            with self._lock:
                cutoff_time = datetime.now() - timedelta(days=1)
                recent_metrics = [m for m in self.metrics_history if m.timestamp > cutoff_time]
                
            # Generate insights
            insights = await self.generate_insights(AnalysisScope.TEAM, "system")
            
            logger.info(f"Generated {len(insights)} system insights")
            
        except Exception as e:
            logger.error(f"Error generating system insights: {e}")


# Singleton instance for global use
review_analytics = ReviewAnalytics()