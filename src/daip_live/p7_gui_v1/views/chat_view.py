"""
Chat View

This module implements the chat view for the P7 GUI application using CustomTkinter.
It displays conversation messages and provides input functionality, binding to the ChatViewModel.
"""

import customtkinter as ctk
from typing import Dict, Any, List, Optional
from .base import View
from ..viewmodel.chat_viewmodel import ChatViewModel


class ChatView(View):
    """
    Chat view implementation for the P7 GUI application.
    
    This view handles:
    - Display of chat messages in a scrollable area
    - User input for sending new messages
    - Visual indicators for typing status
    - Message history management
    """
    
    def __init__(self, parent: ctk.CTkFrame, viewmodel: ChatViewModel):
        """
        Initialize the ChatView.
        
        Args:
            parent: Parent frame to contain this view
            viewmodel: ChatViewModel instance to bind to
        """
        self._parent = parent
        self._viewmodel = viewmodel
        self._visible = False
        
        # Component references
        self._scrollable_frame: Optional[ctk.CTkScrollableFrame] = None
        self._message_log: Optional[ctk.CTkTextbox] = None
        self._input_field: Optional[ctk.CTkEntry] = None
        self._send_button: Optional[ctk.CTkButton] = None
        self._typing_indicator: Optional[ctk.CTkLabel] = None
        self._message_labels: List[ctk.CTkLabel] = []
        
        # Initialize UI
        self._setup_components()
        self._bind_to_viewmodel()
    
    def _setup_components(self):
        """Create and arrange all chat view components."""
        # Configure the parent frame
        self._parent.grid_rowconfigure(0, weight=1)
        self._parent.grid_columnconfigure(0, weight=1)
        
        # Create main container frame
        container = ctk.CTkFrame(self._parent)
        container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        container.grid_rowconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=0)  # Input area doesn't expand
        container.grid_columnconfigure(0, weight=1)
        
        # Create scrollable frame for messages
        self._scrollable_frame = ctk.CTkScrollableFrame(container, label_text="Chat Messages")
        self._scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5))
        self._scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # Create input area frame
        input_frame = ctk.CTkFrame(container)
        input_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(5, 10))
        input_frame.grid_columnconfigure(0, weight=1)
        
        # Create input field
        self._input_field = ctk.CTkEntry(
            input_frame,
            placeholder_text="Type your message here...",
            height=40
        )
        self._input_field.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        # Bind Enter key to send message
        self._input_field.bind("<Return>", lambda event: self.submit_message())
        
        # Create send button
        self._send_button = ctk.CTkButton(
            input_frame,
            text="Send",
            command=self.submit_message,
            width=80,
            height=40
        )
        self._send_button.grid(row=0, column=1, sticky="e")
        
        # Create typing indicator
        self._typing_indicator = ctk.CTkLabel(
            container,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self._typing_indicator.grid(row=2, column=0, sticky="w", padx=15, pady=(0, 5))
        
        # Load initial messages
        self._update_messages_display()
    
    def _bind_to_viewmodel(self):
        """Bind view components to ViewModel properties."""
        # Subscribe to ViewModel property changes
        self._viewmodel.subscribe_property_change('messages', self._on_messages_changed)
        self._viewmodel.subscribe_property_change('is_typing', self._on_typing_changed)
        self._viewmodel.subscribe_property_change('input_text', self._on_input_changed)
        
        # Update initial state from ViewModel
        messages = self._viewmodel.get_property('messages', [])
        self._display_messages(messages)
        
        is_typing = self._viewmodel.get_property('is_typing', False)
        self._update_typing_indicator(is_typing)
        
        input_text = self._viewmodel.get_property('input_text', '')
        if input_text and self._input_field:
            self._input_field.delete(0, "end")
            self._input_field.insert(0, input_text)
    
    def _on_messages_changed(self, name: str, new_value: Any, old_value: Any):
        """
        Handle ViewModel messages property change.
        
        Args:
            name: Property name that changed
            new_value: New property value
            old_value: Previous property value
        """
        self._display_messages(new_value)
    
    def _on_typing_changed(self, name: str, new_value: Any, old_value: Any):
        """
        Handle ViewModel typing status change.
        
        Args:
            name: Property name that changed
            new_value: New property value
            old_value: Previous property value
        """
        self._update_typing_indicator(new_value)
    
    def _on_input_changed(self, name: str, new_value: Any, old_value: Any):
        """
        Handle ViewModel input text change.
        
        Args:
            name: Property name that changed
            new_value: New property value
            old_value: Previous property value
        """
        if self._input_field:
            self._input_field.delete(0, "end")
            self._input_field.insert(0, new_value)
    
    def _display_messages(self, messages: List[Dict[str, Any]]):
        """
        Display messages in the chat view.
        
        Args:
            messages: List of message dictionaries to display
        """
        if not self._scrollable_frame:
            return
        
        # Clear existing message labels
        for label in self._message_labels:
            label.destroy()
        self._message_labels.clear()
        
        # Display each message
        for msg in messages:
            sender = msg.get('sender', 'unknown')
            content = msg.get('content', '')
            timestamp = msg.get('timestamp', '')
            
            # Format the message differently based on sender
            if sender == 'user':
                bg_color = ("#2c8d48", "#2c8d48")  # Green for user messages
                align = "e"  # Right-align user messages
                prefix = "👤 You: "
            else:
                bg_color = ("gray70", "gray30")  # Different color for agent messages
                align = "w"  # Left-align agent messages
                prefix = "🤖 Agent: "
            
            # Create message label
            msg_text = f"{prefix}{content}"
            if timestamp:
                msg_text += f" [{timestamp}]"
            
            msg_label = ctk.CTkLabel(
                self._scrollable_frame,
                text=msg_text,
                wraplength=500,
                justify="left" if align == "w" else "right",
                bg_color=bg_color
            )
            
            # Grid the label with appropriate alignment
            msg_label.grid(
                row=len(self._message_labels), 
                column=0, 
                sticky=align,
                padx=(10 if align == "w" else 0, 10 if align == "e" else 0),
                pady=2,
                ipadx=10,
                ipady=5
            )
            
            self._message_labels.append(msg_label)
        
        # Scroll to bottom to show latest messages
        if self._scrollable_frame:
            self._scrollable_frame._parent_canvas.yview_moveto(1.0)
    
    def _update_messages_display(self):
        """Update the message display with current ViewModel state."""
        messages = self._viewmodel.get_messages()
        self._display_messages(messages)
    
    def _update_typing_indicator(self, is_typing: bool):
        """
        Update the typing indicator.
        
        Args:
            is_typing: Whether the agent is currently typing
        """
        if not self._typing_indicator:
            return
            
        if is_typing:
            self._typing_indicator.configure(text="Agent is typing...", text_color="gray60")
        else:
            self._typing_indicator.configure(text="", text_color="transparent")
    
    def display_message(self, message: Dict[str, Any]):
        """
        Display a single message in the chat view.
        
        Args:
            message: Message dictionary to display
        """
        # This method adds a single message to the existing display
        messages = self._viewmodel.get_property('messages', [])
        messages.append(message)
        self._viewmodel.set_property('messages', messages)
        # The binding will update the display automatically
    
    def submit_message(self):
        """Submit the current input as a message."""
        if not self._input_field:
            return
        
        message_text = self._input_field.get().strip()
        if not message_text:
            return
        
        # Update ViewModel with the input text
        self._viewmodel.set_property('input_text', message_text)
        
        # Clear the input field
        self._input_field.delete(0, "end")
        
        # Send the message via ViewModel
        # Note: In a real implementation, this would be an async call
        # For now, we'll just use the sync command execution
        try:
            # Send message command - this would typically be async
            result = self._viewmodel.execute_command('send_input')
            # In a real implementation, we would handle the async message sending
        except Exception as e:
            # Handle error in UI
            self._typing_indicator.configure(text=f"Error: {str(e)}", text_color="red")
    
    def get_input_text(self) -> str:
        """
        Get the current text from the input field.
        
        Returns:
            Current input field text
        """
        if self._input_field:
            return self._input_field.get()
        return ""
    
    def clear_input(self):
        """Clear the input field."""
        if self._input_field:
            self._input_field.delete(0, "end")
            self._viewmodel.set_property('input_text', '')
    
    def show(self):
        """Show the chat view."""
        if not self._visible:
            self._visible = True
            self._parent.grid(row=0, column=0, sticky="nsew")
    
    def hide(self):
        """Hide the chat view."""
        if self._visible:
            self._visible = False
            self._parent.grid_remove()
    
    def refresh(self):
        """Refresh the chat view display."""
        self._update_messages_display()
    
    def focus_input(self):
        """Focus the input field."""
        if self._input_field:
            self._input_field.focus()
    
    def scroll_to_bottom(self):
        """Scroll the message area to the bottom."""
        if self._scrollable_frame:
            self._scrollable_frame._parent_canvas.yview_moveto(1.0)
    
    def get_message_count(self) -> int:
        """
        Get the number of messages in the display.
        
        Returns:
            Number of messages
        """
        return len(self._message_labels)
    
    def enable_input(self):
        """Enable the input field."""
        if self._input_field:
            self._input_field.configure(state="normal")
    
    def disable_input(self):
        """Disable the input field."""
        if self._input_field:
            self._input_field.configure(state="disabled")
    
    def set_placeholder_text(self, text: str):
        """
        Set the placeholder text for the input field.
        
        Args:
            text: New placeholder text
        """
        # Note: CustomTkinter doesn't directly support changing placeholder text
        # So we'll store this for future reference or use a different approach
        pass
    
    def is_typing_indicator_visible(self) -> bool:
        """
        Check if the typing indicator is currently visible.
        
        Returns:
            True if typing indicator is visible, False otherwise
        """
        if self._typing_indicator:
            # Check if the text is not empty
            return bool(self._typing_indicator.cget("text"))
        return False