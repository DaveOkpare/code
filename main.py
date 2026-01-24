import sys
import time
import typer
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style as PStyle

# 1. Setup Typer, Rich, and Prompt Toolkit
app = typer.Typer(help="A self improving coding agent CLI.", add_completion=False)
console = Console()

# Define slash commands and their descriptions
COMMANDS = {
    "/reset": "Restart the session context",
    "/clear": "Clear the screen",
    "/model": "Switch AI models",
    "/help": "Show available commands",
    "/quit": "Exit the application",
    "/exit": "Exit the application"
}

# Create the autocompleter
completer = WordCompleter(list(COMMANDS.keys()), ignore_case=True)

# Custom style for the prompt input (matching Rich's cyan/purple vibe)
style = PStyle.from_dict({
    'completion-menu.completion': 'bg:#008888 #ffffff',
    'completion-menu.completion.current': 'bg:#00aaaa #000000',
    'scrollbar.background': 'bg:#88aaaa',
    'scrollbar.button': 'bg:#222222',
})

def print_header():
    grid = Panel.fit(
        "[bold cyan] selfheal CLI[/] [dim]v0.1.0[/] | Type [bold magenta]/[/] for commands",
        border_style="cyan",
        padding=(0, 2),
    )
    console.print(grid)

@app.command()
def chat(
    model: str = typer.Option("gpt-4", "--model", "-m", help="Initial model."),
):
    """Start the interactive chat with slash commands."""
    print_header()

    # Create a session to keep history
    session = PromptSession(completer=completer, style=style)

    while True:
        try:
            # 2. Interactive Input Loop
            user_input = session.prompt("You > ").strip()

            # Handle Slash Commands
            if user_input.startswith("/"):
                cmd = user_input.split(" ")[0].lower()

                if cmd in ("/exit", "/quit"):
                    console.print("[dim]Goodbye![/]")
                    break

                elif cmd == "/clear":
                    console.clear()
                    print_header()
                    continue

                elif cmd == "/help":
                    console.print(Panel("\n".join([f"[bold cyan]{k}[/]: {v}" for k,v in COMMANDS.items()]), title="Commands"))
                    continue

                elif cmd == "/reset":
                    console.print("[yellow]↺ Context reset.[/]")
                    time.sleep(0.5)
                    continue

                else:
                    console.print(f"[red]Unknown command: {cmd}[/]")
                    continue

            # Handle Normal Chat
            if not user_input: continue

            # Simulate "thinking"
            console.print()
            with console.status(f"[dim]Sending to {model}...[/]", spinner="dots"):
                time.sleep(1)

            # Response
            console.print(Panel(Markdown(f"I processed: **{user_input}**"), title=f"[bold purple]{model}[/]", border_style="purple"))
            console.print()

        except KeyboardInterrupt:
            break
        except EOFError:
            break

if __name__ == "__main__":
    app()
