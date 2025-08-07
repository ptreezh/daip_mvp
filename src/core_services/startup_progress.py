# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-05 15:45:00
@Author  : DAIP-LIVE Team
@File    : startup_progress.py
@Description:
    Progressive startup feedback system for providing real-time initialization progress.
"""

import logging
import time
import threading
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import sys

logger = logging.getLogger(__name__)


class StartupPhase(Enum):
    """Startup phase enumeration"""
    PRE_INITIALIZATION = "pre_initialization"
    CRITICAL_SERVICES = "critical_services"
    CORE_SERVICES = "core_services"
    OPTIONAL_SERVICES = "optional_services"
    SCENARIO_SERVICES = "scenario_services"
    FINALIZATION = "finalization"
    COMPLETE = "complete"


class StepStatus(Enum):
    """Step status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class StartupStep:
    """Individual startup step information"""
    name: str
    description: str
    phase: StartupPhase
    is_critical: bool = True
    estimated_duration: float = 1.0
    status: StepStatus = StepStatus.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    error_message: Optional[str] = None
    progress_callback: Optional[Callable] = None


@dataclass
class StartupProgress:
    """Overall startup progress information"""
    current_step: int = 0
    total_steps: int = 0
    completed_steps: int = 0
    failed_steps: int = 0
    skipped_steps: int = 0
    start_time: float = field(default_factory=time.time)
    current_phase: StartupPhase = StartupPhase.PRE_INITIALIZATION
    overall_progress: float = 0.0
    estimated_remaining_time: float = 0.0
    steps: List[StartupStep] = field(default_factory=list)


class StartupProgressTracker:
    """Tracks and reports startup progress"""
    
    def __init__(self, enable_progress_bar: bool = True, enable_logging: bool = True):
        self.enable_progress_bar = enable_progress_bar
        self.enable_logging = enable_logging
        self.progress = StartupProgress()
        self.current_step_index = 0
        self.phase_step_counts: Dict[StartupPhase, int] = {}
        self.lock = threading.Lock()
        
        # Define startup steps
        self._define_startup_steps()
        
        # Progress bar thread
        self.progress_bar_thread: Optional[threading.Thread] = None
        self.stop_progress_bar = False
        
    def _define_startup_steps(self):
        """Define all startup steps"""
        steps = [
            # Pre-initialization
            StartupStep(
                name="configuration_loading",
                description="Loading configuration",
                phase=StartupPhase.PRE_INITIALIZATION,
                is_critical=True,
                estimated_duration=0.5
            ),
            StartupStep(
                name="path_setup",
                description="Setting up directories and paths",
                phase=StartupPhase.PRE_INITIALIZATION,
                is_critical=True,
                estimated_duration=0.2
            ),
            StartupStep(
                name="logging_setup",
                description="Configuring logging system",
                phase=StartupPhase.PRE_INITIALIZATION,
                is_critical=False,
                estimated_duration=0.1
            ),
            
            # Critical services
            StartupStep(
                name="token_management",
                description="Initializing token management",
                phase=StartupPhase.CRITICAL_SERVICES,
                is_critical=True,
                estimated_duration=0.3
            ),
            StartupStep(
                name="llm_interface",
                description="Setting up LLM interface",
                phase=StartupPhase.CRITICAL_SERVICES,
                is_critical=True,
                estimated_duration=2.0
            ),
            StartupStep(
                name="vector_database",
                description="Initializing vector database",
                phase=StartupPhase.CRITICAL_SERVICES,
                is_critical=True,
                estimated_duration=1.0
            ),
            StartupStep(
                name="memory_service",
                description="Starting memory service",
                phase=StartupPhase.CRITICAL_SERVICES,
                is_critical=True,
                estimated_duration=0.5
            ),
            StartupStep(
                name="wiki_service",
                description="Initializing wiki service",
                phase=StartupPhase.CRITICAL_SERVICES,
                is_critical=True,
                estimated_duration=0.3
            ),
            
            # Core services
            StartupStep(
                name="synthesis_engine",
                description="Starting synthesis engine",
                phase=StartupPhase.CORE_SERVICES,
                is_critical=False,
                estimated_duration=0.8
            ),
            StartupStep(
                name="expert_service",
                description="Loading expert service",
                phase=StartupPhase.CORE_SERVICES,
                is_critical=False,
                estimated_duration=0.4
            ),
            StartupStep(
                name="task_manager",
                description="Initializing task manager",
                phase=StartupPhase.CORE_SERVICES,
                is_critical=False,
                estimated_duration=0.3
            ),
            StartupStep(
                name="user_profile_service",
                description="Starting user profile service",
                phase=StartupPhase.CORE_SERVICES,
                is_critical=False,
                estimated_duration=0.2
            ),
            StartupStep(
                name="session_management",
                description="Initializing session management",
                phase=StartupPhase.CORE_SERVICES,
                is_critical=False,
                estimated_duration=0.2
            ),
            StartupStep(
                name="universal_context",
                description="Setting up universal context",
                phase=StartupPhase.CORE_SERVICES,
                is_critical=False,
                estimated_duration=0.4
            ),
            
            # Optional services
            StartupStep(
                name="enhanced_memory",
                description="Loading enhanced memory management",
                phase=StartupPhase.OPTIONAL_SERVICES,
                is_critical=False,
                estimated_duration=0.6
            ),
            StartupStep(
                name="knowledge_visualization",
                description="Initializing knowledge visualization",
                phase=StartupPhase.OPTIONAL_SERVICES,
                is_critical=False,
                estimated_duration=0.5
            ),
            StartupStep(
                name="role_definitions",
                description="Loading role definitions",
                phase=StartupPhase.OPTIONAL_SERVICES,
                is_critical=False,
                estimated_duration=1.5
            ),
            
            # Scenario services
            StartupStep(
                name="expert_consultation_scenario",
                description="Starting expert consultation scenario",
                phase=StartupPhase.SCENARIO_SERVICES,
                is_critical=False,
                estimated_duration=0.4
            ),
            StartupStep(
                name="academic_research_scenario",
                description="Loading academic research scenario",
                phase=StartupPhase.SCENARIO_SERVICES,
                is_critical=False,
                estimated_duration=0.4
            ),
            StartupStep(
                name="industry_analysis_scenario",
                description="Starting industry analysis scenario",
                phase=StartupPhase.SCENARIO_SERVICES,
                is_critical=False,
                estimated_duration=0.4
            ),
            
            # Finalization
            StartupStep(
                name="api_registration",
                description="Registering API endpoints",
                phase=StartupPhase.FINALIZATION,
                is_critical=True,
                estimated_duration=0.2
            ),
            StartupStep(
                name="health_check",
                description="Performing final health check",
                phase=StartupPhase.FINALIZATION,
                is_critical=True,
                estimated_duration=0.3
            ),
            StartupStep(
                name="startup_complete",
                description="Startup complete",
                phase=StartupPhase.FINALIZATION,
                is_critical=True,
                estimated_duration=0.1
            ),
        ]
        
        self.progress.steps = steps
        self.progress.total_steps = len(steps)
        
        # Count steps per phase
        for step in steps:
            self.phase_step_counts[step.phase] = self.phase_step_counts.get(step.phase, 0) + 1
    
    def start_step(self, step_name: str) -> bool:
        """Start a specific step"""
        with self.lock:
            step = self._find_step(step_name)
            if not step:
                logger.warning(f"Step not found: {step_name}")
                return False
            
            if step.status != StepStatus.PENDING:
                logger.warning(f"Step {step_name} already started or completed")
                return False
            
            step.status = StepStatus.IN_PROGRESS
            step.start_time = time.time()
            self.progress.current_phase = step.phase
            
            if self.enable_logging:
                logger.info(f"🔄 {step.description}")
            
            self._update_progress()
            return True
    
    def complete_step(self, step_name: str, success: bool = True, error_message: Optional[str] = None):
        """Complete a specific step"""
        with self.lock:
            step = self._find_step(step_name)
            if not step:
                logger.warning(f"Step not found: {step_name}")
                return
            
            if step.status != StepStatus.IN_PROGRESS:
                logger.warning(f"Step {step_name} not in progress")
                return
            
            step.end_time = time.time()
            
            if success:
                step.status = StepStatus.COMPLETED
                self.progress.completed_steps += 1
                
                if self.enable_logging:
                    duration = step.end_time - step.start_time
                    logger.info(f"✅ {step.description} ({duration:.3f}s)")
            else:
                step.status = StepStatus.FAILED
                step.error_message = error_message
                self.progress.failed_steps += 1
                
                if step.is_critical:
                    logger.error(f"❌ {step.description}: {error_message}")
                else:
                    logger.warning(f"⚠️ {step.description}: {error_message}")
            
            self._update_progress()
    
    def skip_step(self, step_name: str, reason: str):
        """Skip a non-critical step"""
        with self.lock:
            step = self._find_step(step_name)
            if not step:
                logger.warning(f"Step not found: {step_name}")
                return
            
            if step.is_critical:
                logger.warning(f"Cannot skip critical step: {step_name}")
                return
            
            step.status = StepStatus.SKIPPED
            step.error_message = reason
            self.progress.skipped_steps += 1
            
            if self.enable_logging:
                logger.info(f"⏭️ {step.description} (skipped: {reason})")
            
            self._update_progress()
    
    def _find_step(self, step_name: str) -> Optional[StartupStep]:
        """Find a step by name"""
        for step in self.progress.steps:
            if step.name == step_name:
                return step
        return None
    
    def _update_progress(self):
        """Update overall progress calculations"""
        # Calculate overall progress
        total_weight = 0
        completed_weight = 0
        
        for step in self.progress.steps:
            weight = 1.0 if step.is_critical else 0.5
            total_weight += weight
            
            if step.status == StepStatus.COMPLETED:
                completed_weight += weight
            elif step.status == StepStatus.SKIPPED:
                completed_weight += weight * 0.5  # Partial credit for skipped
        
        self.progress.overall_progress = completed_weight / total_weight if total_weight > 0 else 0.0
        
        # Calculate estimated remaining time
        if self.progress.completed_steps > 0:
            avg_time_per_step = (time.time() - self.progress.start_time) / self.progress.completed_steps
            remaining_steps = self.progress.total_steps - self.progress.completed_steps
            self.progress.estimated_remaining_time = avg_time_per_step * remaining_steps
        else:
            self.progress.estimated_remaining_time = sum(step.estimated_duration for step in self.progress.steps)
    
    def get_progress(self) -> StartupProgress:
        """Get current progress information"""
        with self.lock:
            return self.progress
    
    def get_progress_summary(self) -> Dict:
        """Get a summary of current progress"""
        with self.lock:
            return {
                "overall_progress": self.progress.overall_progress,
                "current_phase": self.progress.current_phase.value,
                "completed_steps": self.progress.completed_steps,
                "total_steps": self.progress.total_steps,
                "failed_steps": self.progress.failed_steps,
                "skipped_steps": self.progress.skipped_steps,
                "estimated_remaining_time": self.progress.estimated_remaining_time,
                "elapsed_time": time.time() - self.progress.start_time,
                "current_step": self.progress.steps[self.current_step_index].description if self.current_step_index < len(self.progress.steps) else "Complete"
            }
    
    def start_progress_bar(self):
        """Start the progress bar in a separate thread"""
        if not self.enable_progress_bar:
            return
        
        self.stop_progress_bar = False
        self.progress_bar_thread = threading.Thread(target=self._progress_bar_loop)
        self.progress_bar_thread.daemon = True
        self.progress_bar_thread.start()
    
    def stop_progress_bar_thread(self):
        """Stop the progress bar thread"""
        self.stop_progress_bar = True
        if self.progress_bar_thread:
            self.progress_bar_thread.join(timeout=1.0)
    
    def _progress_bar_loop(self):
        """Progress bar display loop"""
        import sys
        
        try:
            while not self.stop_progress_bar:
                summary = self.get_progress_summary()
                
                # Create progress bar
                progress = summary["overall_progress"]
                bar_length = 40
                filled_length = int(bar_length * progress)
                bar = "█" * filled_length + "░" * (bar_length - filled_length)
                
                # Format status line
                status_line = f"\r[{bar}] {progress*100:5.1f}% | {summary['current_step']}"
                
                if summary["estimated_remaining_time"] > 0:
                    status_line += f" | ETA: {summary['estimated_remaining_time']:.1f}s"
                
                status_line += " | " + self._get_phase_icon(summary["current_phase"])
                
                sys.stdout.write(status_line)
                sys.stdout.flush()
                
                time.sleep(0.1)
            
            # Clear the line when done
            sys.stdout.write("\r" + " " * 120 + "\r")
            sys.stdout.flush()
            
        except KeyboardInterrupt:
            pass
        except Exception as e:
            logger.error(f"Progress bar error: {e}")
    
    def _get_phase_icon(self, phase: str) -> str:
        """Get icon for current phase"""
        phase_icons = {
            "pre_initialization": "🔧",
            "critical_services": "⚡",
            "core_services": "🔧",
            "optional_services": "🔍",
            "scenario_services": "🎯",
            "finalization": "✅",
            "complete": "🎉"
        }
        return phase_icons.get(phase, "🔄")
    
    def print_startup_summary(self):
        """Print a summary of the startup process"""
        if not self.enable_logging:
            return
        
        summary = self.get_progress_summary()
        elapsed_time = summary["elapsed_time"]
        
        print("\n" + "="*60)
        print("🎉 DAIP-LIVE STARTUP COMPLETE")
        print("="*60)
        print(f"⏱️  Total startup time: {elapsed_time:.2f}s")
        print(f"📊 Progress: {summary['completed_steps']}/{summary['total_steps']} steps completed")
        print(f"✅ Successful: {summary['completed_steps']}")
        print(f"⚠️  Failed: {summary['failed_steps']}")
        print(f"⏭️  Skipped: {summary['skipped_steps']}")
        
        if summary["failed_steps"] > 0:
            print("\n❌ Failed Steps:")
            for step in self.progress.steps:
                if step.status == StepStatus.FAILED:
                    print(f"   • {step.description}: {step.error_message}")
        
        if summary["skipped_steps"] > 0:
            print("\n⏭️ Skipped Steps:")
            for step in self.progress.steps:
                if step.status == StepStatus.SKIPPED:
                    print(f"   • {step.description}: {step.error_message}")
        
        print("\n" + "="*60)
    
    def __enter__(self):
        """Context manager entry"""
        self.start_progress_bar()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop_progress_bar_thread()
        self.print_startup_summary()


# Global progress tracker instance
_progress_tracker: Optional[StartupProgressTracker] = None


def get_progress_tracker() -> StartupProgressTracker:
    """Get the global progress tracker instance"""
    global _progress_tracker
    if _progress_tracker is None:
        _progress_tracker = StartupProgressTracker()
    return _progress_tracker


def startup_step(step_name: str):
    """Decorator for startup steps"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            tracker = get_progress_tracker()
            
            # Start the step
            tracker.start_step(step_name)
            
            try:
                result = func(*args, **kwargs)
                tracker.complete_step(step_name, success=True)
                return result
            except Exception as e:
                tracker.complete_step(step_name, success=False, error_message=str(e))
                raise
        return wrapper
    return decorator


def optional_startup_step(step_name: str):
    """Decorator for optional startup steps"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            tracker = get_progress_tracker()
            
            # Start the step
            tracker.start_step(step_name)
            
            try:
                result = func(*args, **kwargs)
                tracker.complete_step(step_name, success=True)
                return result
            except Exception as e:
                tracker.skip_step(step_name, reason=str(e))
                return None  # Return None for optional steps that fail
        return wrapper
    return decorator


if __name__ == "__main__":
    # Test the startup progress tracker
    import logging
    
    logging.basicConfig(level=logging.INFO)
    
    print("Testing Startup Progress Tracker")
    print("=" * 40)
    
    with StartupProgressTracker() as tracker:
        # Simulate startup process
        import time
        
        # Test some steps
        tracker.start_step("configuration_loading")
        time.sleep(0.5)
        tracker.complete_step("configuration_loading")
        
        tracker.start_step("path_setup")
        time.sleep(0.2)
        tracker.complete_step("path_setup")
        
        tracker.start_step("llm_interface")
        time.sleep(1.0)
        tracker.complete_step("llm_interface")
        
        tracker.start_step("memory_service")
        time.sleep(0.3)
        tracker.complete_step("memory_service")
        
        # Test a failed step
        tracker.start_step("expert_service")
        time.sleep(0.1)
        tracker.complete_step("expert_service", success=False, error_message="Test failure")
        
        # Test a skipped step
        tracker.start_step("enhanced_memory")
        time.sleep(0.1)
        tracker.skip_step("enhanced_memory", reason="Not available")
        
        # Complete the rest
        for step in ["wiki_service", "synthesis_engine", "startup_complete"]:
            tracker.start_step(step)
            time.sleep(0.2)
            tracker.complete_step(step)
    
    print("Startup progress tracker test completed!")