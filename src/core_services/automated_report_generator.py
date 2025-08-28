"""@Time: 2025-08-03
@Author: Claude Code
@File: automated_report_generator.py
@Description: Automated report generator for collaborative review processes with graceful degradation
"""

import asyncio
import json
import logging
import threading
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from jinja2 import BaseLoader, Environment

logger = logging.getLogger(__name__)


class ReportFormat(Enum):
    """Supported report formats"""
    HTML = "html"
    PDF = "pdf"
    MARKDOWN = "markdown"
    JSON = "json"
    CSV = "csv"


class ReportType(Enum):
    """Types of reports"""
    SESSION_SUMMARY = "session_summary"
    REVIEWER_PERFORMANCE = "reviewer_performance"
    TEAM_ANALYTICS = "team_analytics"
    QUALITY_ASSESSMENT = "quality_assessment"
    EFFICIENCY_REPORT = "efficiency_report"
    COMPREHENSIVE = "comprehensive"


class ReportStatus(Enum):
    """Report generation status"""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ReportTemplate:
    """Report template definition"""
    template_id: str
    name: str
    description: str
    template_type: ReportType
    template_format: ReportFormat
    template_content: str
    required_data: list[str]
    created_at: datetime
    version: str = "1.0"
    
    def to_dict(self) -> dict[str, Any]:
        """Convert template to dictionary"""
        return {
            'template_id': self.template_id,
            'name': self.name,
            'description': self.description,
            'template_type': self.template_type.value,
            'template_format': self.template_format.value,
            'template_content': self.template_content,
            'required_data': self.required_data,
            'created_at': self.created_at.isoformat(),
            'version': self.version
        }


@dataclass
class ReportRequest:
    """Report generation request"""
    request_id: str
    report_type: ReportType
    report_format: ReportFormat
    template_id: Optional[str]
    data_sources: dict[str, Any]
    parameters: dict[str, Any]
    requested_by: str
    requested_at: datetime
    priority: str = "normal"
    callback_url: Optional[str] = None
    
    def to_dict(self) -> dict[str, Any]:
        """Convert request to dictionary"""
        return {
            'request_id': self.request_id,
            'report_type': self.report_type.value,
            'report_format': self.report_format.value,
            'template_id': self.template_id,
            'data_sources': self.data_sources,
            'parameters': self.parameters,
            'requested_by': self.requested_by,
            'requested_at': self.requested_at.isoformat(),
            'priority': self.priority,
            'callback_url': self.callback_url
        }


@dataclass
class ReportResult:
    """Report generation result"""
    request_id: str
    report_id: str
    status: ReportStatus
    generated_at: datetime
    file_path: Optional[str]
    file_size: Optional[int]
    download_url: Optional[str]
    error_message: Optional[str]
    generation_time: float
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary"""
        return {
            'request_id': self.request_id,
            'report_id': self.report_id,
            'status': self.status.value,
            'generated_at': self.generated_at.isoformat(),
            'file_path': self.file_path,
            'file_size': self.file_size,
            'download_url': self.download_url,
            'error_message': self.error_message,
            'generation_time': self.generation_time,
            'metadata': self.metadata
        }


class AutomatedReportGenerator:
    """Automated report generator with graceful degradation
    Generates various types of reports from review data
    """
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Background processing
        self._running = False
        self._lock = threading.Lock()
        self.workers: list[asyncio.Task] = []
        
        # Templates storage
        self.templates: dict[str, ReportTemplate] = {}
        self._initialize_default_templates()
        
        # Request processing
        self.active_requests: dict[str, ReportRequest] = {}
        self.completed_reports: dict[str, ReportResult] = {}
        self.request_queue = asyncio.Queue()
        
        # Performance tracking
        self.generation_times: dict[str, list[float]] = {}
        self.success_rates: dict[str, float] = {}
        
        # Graceful degradation settings
        self.max_generation_time = 30.0  # seconds
        self.max_queue_size = 100
        self.fallback_template_id = "basic_summary"
        
        # Jinja2 environment for templating
        self.jinja_env = Environment(loader=BaseLoader())
        
        # Event handlers
        self.completion_handlers: dict[str, Callable] = {}
        
    async def start(self) -> None:
        """Start the report generator"""
        self._running = True
        logger.info("Automated report generator started")
        
        # Start worker tasks
        for i in range(3):  # 3 workers
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self.workers.append(worker)
            
    async def stop(self) -> None:
        """Stop the report generator"""
        self._running = False
        
        # Cancel all workers
        for worker in self.workers:
            worker.cancel()
            
        # Wait for workers to finish
        await asyncio.gather(*self.workers, return_exceptions=True)
        
        logger.info("Automated report generator stopped")
        
    async def generate_report(self, request: ReportRequest) -> str:
        """Generate a report from request"""
        try:
            # Check queue size for graceful degradation
            if self.request_queue.qsize() >= self.max_queue_size:
                logger.warning(f"Report queue full, rejecting request: {request.request_id}")
                raise Exception("Report generation queue is full")
                
            with self._lock:
                self.active_requests[request.request_id] = request
                
            await self.request_queue.put(request)
            
            logger.info(f"Report generation requested: {request.request_id} ({request.report_type.value})")
            return request.request_id
            
        except Exception as e:
            logger.error(f"Error submitting report request: {e}")
            # Graceful degradation: create failed result
            result = ReportResult(
                request_id=request.request_id,
                report_id=str(uuid.uuid4()),
                status=ReportStatus.FAILED,
                generated_at=datetime.now(),
                file_path=None,
                file_size=None,
                download_url=None,
                error_message=str(e),
                generation_time=0.0,
                metadata={'queue_full': True}
            )
            
            with self._lock:
                self.completed_reports[request.report_id] = result
                
            return request.request_id
            
    async def get_report_status(self, request_id: str) -> dict[str, Any]:
        """Get report generation status"""
        with self._lock:
            if request_id in self.active_requests:
                request = self.active_requests[request_id]
                return {
                    'status': 'active',
                    'request': request.to_dict()
                }
            else:
                # Search in completed reports by request_id
                for report_id, result in self.completed_reports.items():
                    if result.request_id == request_id:
                        return {
                            'status': 'completed',
                            'result': result.to_dict()
                        }
                return {'status': 'not_found'}
                
    async def download_report(self, report_id: str) -> Optional[str]:
        """Download report content"""
        with self._lock:
            result = self.completed_reports.get(report_id)
            
        if result and result.file_path:
            try:
                with open(result.file_path, encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Error reading report file: {e}")
                
        return None
        
    async def create_template(self, template: ReportTemplate) -> str:
        """Create a new report template"""
        try:
            with self._lock:
                self.templates[template.template_id] = template
                
            logger.info(f"Template created: {template.template_id}")
            return template.template_id
            
        except Exception as e:
            logger.error(f"Error creating template: {e}")
            raise
            
    async def get_template(self, template_id: str) -> Optional[ReportTemplate]:
        """Get template by ID"""
        with self._lock:
            return self.templates.get(template_id)
            
    async def list_templates(self) -> list[dict[str, Any]]:
        """List all available templates"""
        with self._lock:
            return [template.to_dict() for template in self.templates.values()]
            
    async def get_system_stats(self) -> dict[str, Any]:
        """Get system statistics"""
        with self._lock:
            active_requests = len(self.active_requests)
            completed_reports = len(self.completed_reports)
            queue_size = self.request_queue.qsize()
            template_count = len(self.templates)
            
        # Calculate average generation times
        avg_times = {}
        for report_type, times in self.generation_times.items():
            if times:
                avg_times[report_type] = sum(times) / len(times)
                
        return {
            'active_requests': active_requests,
            'completed_reports': completed_reports,
            'queue_size': queue_size,
            'available_templates': template_count,
            'avg_generation_times': avg_times,
            'success_rates': self.success_rates,
            'system_running': self._running,
            'worker_count': len(self.workers)
        }
        
    def register_completion_handler(self, handler: Callable) -> None:
        """Register report completion handler"""
        self.completion_handlers[handler.__name__] = handler
        
    # Private methods
    async def _worker(self, worker_id: str) -> None:
        """Worker task for processing report requests"""
        logger.info(f"Report worker {worker_id} started")
        
        while self._running:
            try:
                # Get request from queue with timeout
                try:
                    request = await asyncio.wait_for(
                        self.request_queue.get(),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                    
                # Process request
                try:
                    result = await self._process_request(request)
                    
                    # Store result
                    with self._lock:
                        self.completed_reports[result.report_id] = result
                        if request.request_id in self.active_requests:
                            del self.active_requests[request.request_id]
                            
                    # Trigger completion handlers
                    await self._trigger_completion_handlers(result)
                    
                    logger.info(f"Report {result.report_id} generated by {worker_id}")
                    
                except Exception as e:
                    logger.error(f"Error processing request {request.request_id}: {e}")
                    
                    # Create failed result
                    result = ReportResult(
                        request_id=request.request_id,
                        report_id=str(uuid.uuid4()),
                        status=ReportStatus.FAILED,
                        generated_at=datetime.now(),
                        file_path=None,
                        file_size=None,
                        download_url=None,
                        error_message=str(e),
                        generation_time=0.0
                    )
                    
                    with self._lock:
                        self.completed_reports[result.report_id] = result
                        if request.request_id in self.active_requests:
                            del self.active_requests[request.request_id]
                            
                finally:
                    # Mark task as done
                    self.request_queue.task_done()
                    
            except Exception as e:
                logger.error(f"Error in worker {worker_id}: {e}")
                await asyncio.sleep(1.0)
                
        logger.info(f"Report worker {worker_id} stopped")
        
    async def _process_request(self, request: ReportRequest) -> ReportResult:
        """Process a single report request"""
        start_time = time.time()
        
        try:
            # Get template
            template = await self._get_template_for_request(request)
            
            # Collect data
            data = await self._collect_report_data(request)
            
            # Generate report
            report_content = await self._generate_report_content(request, template, data)
            
            # Save report
            file_path = await self._save_report(request, report_content)
            
            # Calculate metrics
            generation_time = time.time() - start_time
            file_size = len(report_content.encode('utf-8'))
            
            # Update performance tracking
            report_type = request.report_type.value
            if report_type not in self.generation_times:
                self.generation_times[report_type] = []
            self.generation_times[report_type].append(generation_time)
            
            # Update success rate
            if report_type not in self.success_rates:
                self.success_rates[report_type] = 0.0
            self.success_rates[report_type] = (
                self.success_rates[report_type] * 0.9 + 0.1  # Moving average
            )
            
            return ReportResult(
                request_id=request.request_id,
                report_id=str(uuid.uuid4()),
                status=ReportStatus.COMPLETED,
                generated_at=datetime.now(),
                file_path=str(file_path),
                file_size=file_size,
                download_url=f"/api/reports/{file_path.name}",
                error_message=None,
                generation_time=generation_time,
                metadata={
                    'template_id': template.template_id if template else None,
                    'data_sources': list(data.keys()),
                    'generation_method': 'template'
                }
            )
            
        except asyncio.TimeoutError:
            logger.error(f"Report generation timeout: {request.request_id}")
            # Graceful degradation: use fallback template
            return await self._generate_fallback_report(request, "Generation timeout")
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            # Graceful degradation: use fallback template
            return await self._generate_fallback_report(request, str(e))
            
    async def _get_template_for_request(self, request: ReportRequest) -> Optional[ReportTemplate]:
        """Get template for request"""
        if request.template_id:
            template = await self.get_template(request.template_id)
            if template:
                return template
                
        # Find default template for report type
        with self._lock:
            for template in self.templates.values():
                if (template.template_type == request.report_type and 
                    template.template_format == request.report_format):
                    return template
                    
        # Use fallback template
        return await self.get_template(self.fallback_template_id)
        
    async def _collect_report_data(self, request: ReportRequest) -> dict[str, Any]:
        """Collect data for report generation"""
        try:
            data = {}
            
            # Collect data from sources
            for source_name, source_config in request.data_sources.items():
                try:
                    source_data = await self._collect_from_source(source_name, source_config)
                    data[source_name] = source_data
                except Exception as e:
                    logger.error(f"Error collecting data from {source_name}: {e}")
                    # Graceful degradation: continue with empty data
                    data[source_name] = {'error': str(e)}
                    
            # Add metadata
            data['metadata'] = {
                'request_id': request.request_id,
                'generated_at': datetime.now().isoformat(),
                'report_type': request.report_type.value,
                'report_format': request.report_format.value,
                'parameters': request.parameters
            }
            
            return data
            
        except Exception as e:
            logger.error(f"Error collecting report data: {e}")
            # Return minimal data
            return {
                'metadata': {
                    'request_id': request.request_id,
                    'generated_at': datetime.now().isoformat(),
                    'error': str(e)
                }
            }
            
    async def _collect_from_source(self, source_name: str, source_config: dict[str, Any]) -> dict[str, Any]:
        """Collect data from a specific source"""
        # This would integrate with various data sources in a real implementation
        # For now, return mock data
        
        if source_name == "review_analytics":
            return {
                'total_sessions': 25,
                'active_reviewers': 15,
                'avg_quality_score': 0.85,
                'completion_rate': 0.92,
                'total_comments': 342,
                'resolution_time_avg': 2.5
            }
        elif source_name == "session_data":
            return {
                'session_id': source_config.get('session_id', 'unknown'),
                'participants': 8,
                'duration': 3600,
                'comments': 45,
                'resolutions': 12
            }
        elif source_name == "reviewer_data":
            return {
                'reviewer_id': source_config.get('reviewer_id', 'unknown'),
                'sessions_participated': 12,
                'comments_made': 67,
                'helpful_votes': 45,
                'quality_score': 0.88
            }
        else:
            return {'message': f'Unknown source: {source_name}'}
            
    async def _generate_report_content(self, request: ReportRequest, template: Optional[ReportTemplate], 
                                     data: dict[str, Any]) -> str:
        """Generate report content using template"""
        try:
            if not template:
                # Use basic template
                return await self._generate_basic_report(request, data)
                
            # Use Jinja2 template
            jinja_template = self.jinja_env.from_string(template.template_content)
            
            # Add helper functions
            jinja_template.globals.update({
                'format_datetime': self._format_datetime,
                'format_duration': self._format_duration,
                'calculate_percentage': self._calculate_percentage
            })
            
            # Render template
            content = jinja_template.render(data=data)
            
            return content
            
        except Exception as e:
            logger.error(f"Error generating report content: {e}")
            # Graceful degradation: use basic template
            return await self._generate_basic_report(request, data)
            
    async def _generate_basic_report(self, request: ReportRequest, data: dict[str, Any]) -> str:
        """Generate basic report without template"""
        if request.report_format == ReportFormat.HTML:
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Report: {request.report_type.value}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .header {{ background: #f0f0f0; padding: 20px; margin-bottom: 20px; }}
                    .section {{ margin-bottom: 20px; }}
                    .metric {{ background: #e8f4f8; padding: 10px; margin: 5px 0; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>{request.report_type.value.replace('_', ' ').title()}</h1>
                    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                <div class="section">
                    <h2>Report Data</h2>
                    <pre>{json.dumps(data, indent=2, default=str)}</pre>
                </div>
            </body>
            </html>
            """
        elif request.report_format == ReportFormat.MARKDOWN:
            return f"""# {request.report_type.value.replace('_', ' ').title()}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Report Data

```json
{json.dumps(data, indent=2, default=str)}
```
"""
        elif request.report_format == ReportFormat.JSON:
            return json.dumps({
                'report_type': request.report_type.value,
                'generated_at': datetime.now().isoformat(),
                'data': data
            }, indent=2, default=str)
        else:
            return str(data)
            
    async def _save_report(self, request: ReportRequest, content: str) -> Path:
        """Save report to file"""
        try:
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{request.report_type.value}_{timestamp}_{request.request_id[:8]}"
            
            # Add extension based on format
            if request.report_format == ReportFormat.HTML:
                filename += ".html"
            elif request.report_format == ReportFormat.MARKDOWN:
                filename += ".md"
            elif request.report_format == ReportFormat.JSON:
                filename += ".json"
            elif request.report_format == ReportFormat.CSV:
                filename += ".csv"
            else:
                filename += ".txt"
                
            # Create directory if needed
            report_dir = self.output_dir / request.report_type.value
            report_dir.mkdir(exist_ok=True)
            
            # Save file
            file_path = report_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            logger.info(f"Report saved to: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving report: {e}")
            raise
            
    async def _generate_fallback_report(self, request: ReportRequest, error_message: str) -> ReportResult:
        """Generate fallback report when normal generation fails"""
        try:
            # Create minimal report
            fallback_data = {
                'error': error_message,
                'request_id': request.request_id,
                'fallback': True,
                'timestamp': datetime.now().isoformat()
            }
            
            content = await self._generate_basic_report(request, fallback_data)
            file_path = await self._save_report(request, content)
            
            return ReportResult(
                request_id=request.request_id,
                report_id=str(uuid.uuid4()),
                status=ReportStatus.COMPLETED,
                generated_at=datetime.now(),
                file_path=str(file_path),
                file_size=len(content.encode('utf-8')),
                download_url=f"/api/reports/{file_path.name}",
                error_message=None,
                generation_time=0.0,
                metadata={
                    'fallback': True,
                    'original_error': error_message
                }
            )
            
        except Exception as e:
            logger.error(f"Error generating fallback report: {e}")
            # Last resort: return failed result
            return ReportResult(
                request_id=request.request_id,
                report_id=str(uuid.uuid4()),
                status=ReportStatus.FAILED,
                generated_at=datetime.now(),
                file_path=None,
                file_size=None,
                download_url=None,
                error_message=f"Fallback generation failed: {str(e)}",
                generation_time=0.0,
                metadata={'critical_failure': True}
            )
            
    async def _trigger_completion_handlers(self, result: ReportResult) -> None:
        """Trigger completion handlers"""
        for handler in self.completion_handlers.values():
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(result)
                else:
                    handler(result)
            except Exception as e:
                logger.error(f"Error in completion handler: {e}")
                
    # Template helper functions
    def _format_datetime(self, dt: Any) -> str:
        """Format datetime for template"""
        if isinstance(dt, datetime):
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(dt, str):
            try:
                # Attempt to parse ISO format string
                parsed_dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
                return parsed_dt.strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                return dt # Return original string if parsing fails
        return str(dt) # Fallback for other types
        
    def _format_duration(self, seconds: float) -> str:
        """Format duration for template"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            return f"{seconds/60:.1f}m"
        else:
            return f"{seconds/3600:.1f}h"
            
    def _calculate_percentage(self, value: float, total: float) -> float:
        """Calculate percentage for template"""
        if total == 0:
            return 0.0
        return (value / total) * 100
        
    def _initialize_default_templates(self) -> None:
        """Initialize default report templates"""
        # Basic summary template
        basic_template = ReportTemplate(
            template_id="basic_summary",
            name="Basic Summary",
            description="Basic report template for fallback use",
            template_type=ReportType.COMPREHENSIVE,
            template_format=ReportFormat.HTML,
            template_content="""
<!DOCTYPE html>
<html>
<head>
    <title>Report: {{ data.metadata.report_type }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { background: #f0f0f0; padding: 20px; margin-bottom: 20px; }
        .section { margin-bottom: 20px; }
        .metric { background: #e8f4f8; padding: 10px; margin: 5px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ data.metadata.report_type.replace('_', ' ').title() }}</h1>
        <p>Generated: {{ format_datetime(data.metadata.generated_at) }}</p>
    </div>
    <div class="section">
        <h2>Report Data</h2>
        {% for key, value in data.items() %}
        <div class="metric">
            <strong>{{ key }}:</strong> {{ value }}
        </div>
        {% endfor %}
    </div>
</body>
</html>
            """,
            required_data=["metadata"],
            created_at=datetime.now()
        )
        
        # Session summary template
        session_template = ReportTemplate(
            template_id="session_summary",
            name="Session Summary",
            description="Summary of a review session",
            template_type=ReportType.SESSION_SUMMARY,
            template_format=ReportFormat.HTML,
            template_content="""
<!DOCTYPE html>
<html>
<head>
    <title>Session Summary</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { background: #f0f0f0; padding: 20px; margin-bottom: 20px; }
        .stats { display: flex; gap: 20px; margin-bottom: 20px; }
        .stat { background: #e8f4f8; padding: 15px; border-radius: 5px; flex: 1; }
        .stat-value { font-size: 24px; font-weight: bold; color: #2c3e50; }
        .stat-label { font-size: 14px; color: #7f8c8d; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Session Summary</h1>
        <p>Session ID: {{ data.session_data.session_id }}</p>
        <p>Generated: {{ format_datetime(data.metadata.generated_at) }}</p>
    </div>
    
    <div class="stats">
        <div class="stat">
            <div class="stat-value">{{ data.session_data.participants }}</div>
            <div class="stat-label">Participants</div>
        </div>
        <div class="stat">
            <div class="stat-value">{{ data.session_data.comments }}</div>
            <div class="stat-label">Comments</div>
        </div>
        <div class="stat">
            <div class="stat-value">{{ format_duration(data.session_data.duration) }}</div>
            <div class="stat-label">Duration</div>
        </div>
        <div class="stat">
            <div class="stat-value">{{ data.session_data.resolutions }}</div>
            <div class="stat-label">Resolutions</div>
        </div>
    </div>
    
    <div class="section">
        <h2>Session Details</h2>
        <p>This session had {{ data.session_data.participants }} participants who generated {{ data.session_data.comments }} comments over {{ format_duration(data.session_data.duration) }}.</p>
        <p>{{ data.session_data.resolutions }} issues were successfully resolved during this session.</p>
    </div>
</body>
</html>
            """,
            required_data=["session_data", "metadata"],
            created_at=datetime.now()
        )
        
        # Add templates
        with self._lock:
            self.templates[basic_template.template_id] = basic_template
            self.templates[session_template.template_id] = session_template
            
        logger.info(f"Initialized {len(self.templates)} default templates")


# Singleton instance for global use
automated_report_generator = AutomatedReportGenerator()