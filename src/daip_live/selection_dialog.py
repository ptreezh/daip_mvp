"""Selection dialog components for interactive list selection."""

from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Button, Label, ListView, ListItem, Static


class SelectionDialog(Screen):
    """A dialog for selecting items from a list."""
    
    def __init__(self, title: str, items: list, item_formatter=None, on_select=None):
        super().__init__()
        self.title = title
        self.items = items
        self.item_formatter = item_formatter or (lambda x: str(x))
        self.on_select = on_select
        self.selected_item = None
    
    def compose(self) -> ComposeResult:
        with Container(id="selection-dialog"):
            yield Label(self.title, id="selection-title")
            
            # Create list items
            list_items = []
            for item in self.items:
                display_text = self.item_formatter(item)
                list_items.append(ListItem(Static(display_text)))
            
            yield ListView(*list_items, id="selection-list")
            
            with Container(id="selection-buttons"):
                yield Button("选择", id="select-btn", variant="primary")
                yield Button("取消", id="cancel-btn")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "select-btn":
            list_view = self.query_one(ListView)
            if list_view.index is not None and list_view.index < len(self.items):
                self.selected_item = self.items[list_view.index]
                if self.on_select:
                    self.on_select(self.selected_item)
            self.app.pop_screen()
        elif event.button.id == "cancel-btn":
            self.app.pop_screen()
    
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle list selection with Enter key."""
        try:
            list_view = self.query_one(ListView)
            if list_view.index is not None and list_view.index < len(self.items):
                self.selected_item = self.items[list_view.index]
                if self.on_select:
                    self.on_select(self.selected_item)
                self.app.pop_screen()
        except Exception as e:
            # If there's an error, just pop the screen without selection
            self.app.pop_screen()


class SessionSelectionDialog(SelectionDialog):
    """Dialog for selecting sessions."""
    
    def __init__(self, sessions, on_select):
        def format_session(session):
            return f"{session.session_id} | {session.status.name} | {session.goal[:50]}..."
        
        super().__init__(
            title="选择会话 (Session)",
            items=sessions,
            item_formatter=format_session,
            on_select=on_select
        )


class RoleSelectionDialog(SelectionDialog):
    """Dialog for selecting roles."""
    
    def __init__(self, roles, on_select):
        def format_role(role):
            return f"{role.name}: {role.persona[:50]}..."
        
        super().__init__(
            title="选择角色 (Role)",
            items=roles,
            item_formatter=format_role,
            on_select=on_select
        )


class ModelSelectionDialog(SelectionDialog):
    """Dialog for selecting models."""
    
    def __init__(self, models, on_select):
        def format_model(model):
            return f"{model['name']} ({model['provider']}) - {model['size']}"
        
        super().__init__(
            title="选择模型 (Model)",
            items=models,
            item_formatter=format_model,
            on_select=on_select
        )