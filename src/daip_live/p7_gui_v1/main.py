"""
DAIP-LIVE P7 GUI Main Application Entry Point

This is the main entry point for the P7 GUI application following the newP7 MVVM specification.
It creates the complete application with all services and launches the GUI.
"""

import asyncio
import sys
import os
import customtkinter as ctk
from pathlib import Path
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

# Import all required components
from .viewmodel.main_viewmodel import MainViewModel
from .views.main_window import MainWindow
from .container import ServiceContainer
from .api_client.base import APIClient
from .models.interaction_layer import FastAPIInteractionAdapter
from .theme.theme_manager import ThemeManager
from .platform_adapters.base import get_current_platform_adapter


def main():
    """
    Main entry point for the DAIP-LIVE P7 GUI application.
    
    This function initializes all services, creates the application window,
    and runs the main event loop.
    """
    print("🚀 Starting DAIP-LIVE P7 GUI Application (newP7 Specification)")
    print("="*60)
    
    try:
        # Initialize CustomTkinter appearance settings
        ctk.set_appearance_mode("dark")  # Default to dark mode
        ctk.set_default_color_theme("blue")  # Use blue theme as default
        
        print("🎨 GUI framework initialized (CustomTkinter)")
        
        # Create service container and register all services
        print("🏗️  Setting up service container...")
        container = ServiceContainer()
        
        # Create API client for backend communication
        api_client = APIClient(base_url="http://localhost:8000")
        print("🔗 API client created")
        
        # Create interaction adapter
        interaction_adapter = FastAPIInteractionAdapter(api_client)
        print("🔄 Interaction layer adapter created")
        
        # Create theme manager
        theme_manager = ThemeManager(config_dir=os.path.join(os.path.expanduser("~"), ".daip_live", "themes"))
        print("🎨 Theme manager created")
        
        # Create platform adapter
        platform_adapter = get_current_platform_adapter()
        print(f"🌍 Platform adapter created: {platform_adapter.get_platform_name()}")
        
        # Register services in container
        container.register_service('api_client', api_client)
        container.register_service('interaction_adapter', interaction_adapter)
        container.register_service('theme_manager', theme_manager)
        container.register_service('platform_adapter', platform_adapter)
        
        print("📦 All services registered in container")
        
        # Create the main ViewModel with interaction layer
        print("🧠 Creating Main ViewModel...")
        main_vm = MainViewModel(interaction_adapter)
        
        # Create root window
        print("🖥️  Creating main application window...")
        root = ctk.CTk()
        root.geometry("1200x800")
        root.minsize(800, 600)
        root.title("DAIP-LIVE P7 GUI - Advanced Assistant Platform")
        
        # Create and show main window
        main_window = MainWindow(root, main_vm)
        print("📱 Main window created and configured")
        
        print("\n✨ DAIP-LIVE P7 GUI Application Ready!")
        print("📋 Features Available:")
        print("   • Multi-role AI assistance")
        print("   • Real-time conversation interface")
        print("   • Session management system")
        print("   • Knowledge base integration")
        print("   • Debate system with multiple participants")
        print("   • Cross-platform theming support")
        print("   • Customizable UI components")
        print("")
        print("💡 Use the sidebar navigation to explore different features")
        print("⚙️  Press Ctrl+C in terminal to exit gracefully")
        print("="*60)
        
        # Start the application
        print("🎬 Application starting...")
        root.mainloop()
        
    except KeyboardInterrupt:
        print("\n👋 DAIP-LIVE P7 GUI application terminated by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting DAIP-LIVE P7 GUI application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def create_application():
    """
    Factory function to create the DAIP-LIVE P7 GUI application without running it.
    
    Returns:
        tuple: (root_window, main_window, viewmodel) for manual control
    """
    # Initialize appearance
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Create services
    container = ServiceContainer()
    api_client = APIClient(base_url="http://localhost:8000")
    interaction_adapter = FastAPIInteractionAdapter(api_client)
    theme_manager = ThemeManager()
    platform_adapter = get_current_platform_adapter()
    
    # Register services
    container.register_service('api_client', api_client)
    container.register_service('interaction_adapter', interaction_adapter)
    container.register_service('theme_manager', theme_manager)
    container.register_service('platform_adapter', platform_adapter)
    
    # Create ViewModel
    main_vm = MainViewModel(interaction_adapter)
    
    # Create root window
    root = ctk.CTk()
    root.geometry("1200x800")
    root.minsize(800, 600)
    root.title("DAIP-LIVE P7 GUI - Factory Created Instance")
    
    # Create main window
    main_window = MainWindow(root, main_vm, theme_manager)
    
    return root, main_window, main_vm


if __name__ == "__main__":
    main()