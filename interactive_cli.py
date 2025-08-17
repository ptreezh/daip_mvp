# interactive_cli.py

import sys
from rich.console import Console
from rich.panel import Panel

from src.personal_assistant.intent_classifier import IntentClassifier
from src.personal_assistant.casual_chat import CasualChat
from src.personal_assistant.complex_task_handler import ComplexTaskHandler

def show_main_menu(console: Console):
    """Displays the main menu."""
    menu_text = """
[1] 个人助手 (Personal Assistant)
[2] 辩论大厅 (Debate Hall)
[3] 实时聊天室 (Chat Room)
[4] 知识维基 (Knowledge Wiki)
[5] 角色管理 (Role Management)
[6] 工作流与制度原语 (Workflows & Primitives)
[0] 退出 (Exit)
    """
    panel = Panel(
        menu_text.strip(),
        title="DAIP-LIVE 交互式指挥中心",
        border_style="bold blue"
    )
    console.print(panel)

def create_personal_assistant_components():
    """Creates and wires the components for the Personal Assistant."""
    llm_manager = IntegratedLLMManager()
    intent_classifier = IntentClassifier(llm_manager=llm_manager)
    casual_chat = CasualChat(llm_manager=llm_manager)
    
    # In a real scenario, this would be retrieved from a registry
    api_list = ["search_weather(city: str)", "create_travel_plan(duration: str, activities: list[str])"]
    
    secretary = Secretary(llm_manager=llm_manager)
    planner = Planner(llm_manager=llm_manager)
    task_manager = TaskManager()
    executor = Executor()
    
    complex_task_handler = ComplexTaskHandler(
        secretary=secretary,
        planner=planner,
        task_manager=task_manager,
        executor=executor,
        api_list=api_list
    )
    
    return intent_classifier, casual_chat, complex_task_handler

def start_personal_assistant():
    """Main loop for the Personal Assistant."""
    console = Console()
    console.print("[bold green]个人助手已启动。输入 'exit' 退出。[/bold green]")
    
    intent_classifier, casual_chat, complex_task_handler = create_personal_assistant_components()
    
    history = []

    while True:
        try:
            user_input = input("> ")
            if user_input.lower() == 'exit':
                break
            
            intent = intent_classifier.classify(user_input)
            
            if intent == "闲聊":
                response = casual_chat.handle(history, user_input)
                console.print(f"[cyan]AI:[/cyan] {response}")
                history.append(f"用户: {user_input}")
                history.append(f"AI: {response}")
            else:
                complex_task_handler.handle(history, user_input)
                console.print("[yellow]复杂任务已分派处理...[/yellow]")


        except (EOFError, KeyboardInterrupt):
            break
    
    console.print("[bold green]个人助手已退出。[/bold green]")

def start_debate_hall():
    """Placeholder for Debate Hall functionality."""
    print("Starting Debate Hall...")

def start_chat_room():
    """Placeholder for Chat Room functionality."""
    print("Starting Chat Room...")

def start_wiki_service():
    """Placeholder for Knowledge Wiki functionality."""
    print("Starting Knowledge Wiki...")

def start_role_management():
    """Placeholder for Role Management functionality."""
    print("Starting Role Management...")

def start_workflow_management():
    """Placeholder for Workflow Management functionality."""
    print("Starting Workflow Management...")


def handle_main_menu_input(choice_str: str, console: Console):
    """Handles the user's input from the main menu."""
    try:
        choice = int(choice_str)
        if choice == 1:
            start_personal_assistant()
        elif choice == 2:
            start_debate_hall()
        elif choice == 3:
            start_chat_room()
        elif choice == 4:
            start_wiki_service()
        elif choice == 5:
            start_role_management()
        elif choice == 6:
            start_workflow_management()
        elif choice == 0:
            print("再见！")
            sys.exit(0)
        else:
            console.print("[bold red]无效的选项，请重新输入。[/bold red]")
    except ValueError:
        console.print("[bold red]无效的输入，请输入一个数字。[/bold red]")

def main():
    """Main entry point for the interactive CLI."""
    console = Console()
    
    while True:
        show_main_menu(console)
        try:
            choice_str = input("> 请输入选项: ")
            handle_main_menu_input(choice_str, console)
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            sys.exit(0)

if __name__ == "__main__":
    main()

