from __future__ import annotations

import argparse
import sys
import time
from collections.abc import Sequence

import argcomplete
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory, Suggestion
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.document import Document
from prompt_toolkit.styles import Style as PStyle
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

# Setup Rich Console
console = Console()

# Define slash commands and their descriptions
COMMANDS = {
    "/reset": "Restart the session context",
    "/clear": "Clear the screen",
    "/model": "Switch AI models",
    "/help": "Show available commands",
    "/quit": "Exit the application",
    "/exit": "Exit the application",
}

# Available models for autocomplete and /model command
AVAILABLE_MODELS = [
    "gpt-4",
    "gpt-4-turbo",
    "gpt-3.5-turbo",
    "claude-3-opus",
    "claude-3-sonnet",
    "claude-3-haiku",
]

# Create the autocompleter
completer = WordCompleter(list(COMMANDS.keys()), ignore_case=True)


class CustomAutoSuggest(AutoSuggestFromHistory):
    """Auto-suggester combining history with slash command suggestions."""

    def __init__(self, special_suggestions: list[str] | None = None):
        super().__init__()
        self.special_suggestions = special_suggestions or []

    def get_suggestion(self, buffer: Buffer, document: Document) -> Suggestion | None:
        # Try history-based suggestions first
        suggestion = super().get_suggestion(buffer, document)

        # Check for slash command suggestions
        text = document.text_before_cursor.strip()
        for special in self.special_suggestions:
            if special.startswith(text) and len(text) > 0:
                return Suggestion(special[len(text) :])

        return suggestion


# Custom style for the prompt input (matching Rich's cyan/purple vibe)
style = PStyle.from_dict(
    {
        "completion-menu.completion": "bg:#008888 #ffffff",
        "completion-menu.completion.current": "bg:#00aaaa #000000",
        "scrollbar.background": "bg:#88aaaa",
        "scrollbar.button": "bg:#222222",
    }
)


def create_parser(prog_name: str = "selfheal") -> argparse.ArgumentParser:
    """Create and configure the argument parser with argcomplete support."""
    parser = argparse.ArgumentParser(
        prog=prog_name,
        description="A self improving coding agent CLI.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Optional positional for one-shot mode
    parser.add_argument(
        "prompt",
        nargs="?",
        help="AI prompt for one-shot mode. If omitted, starts interactive mode.",
    )

    # Model selection with autocomplete
    model_arg = parser.add_argument(
        "-m",
        "--model",
        default="gpt-4",
        help='Initial model to use. Defaults to "gpt-4".',
    )
    model_arg.completer = argcomplete.ChoicesCompleter(AVAILABLE_MODELS)  # type: ignore

    return parser


def print_header():
    grid = Panel.fit(
        "[bold cyan] selfheal CLI[/] [dim]v0.1.0[/] | Type [bold magenta]/[/] for commands",
        border_style="cyan",
        padding=(0, 2),
    )
    console.print(grid)


def handle_model_command(command: str, current_model: str, console: Console) -> str:
    """Handle /model slash command for runtime model switching.

    Usage:
        /model              - Show current model and available options
        /model <name>       - Switch to specified model

    Returns:
        New model name (or current if unchanged)
    """
    parts = command.split()

    # Show current model and options
    if len(parts) == 1:
        console.print(f"\n[cyan]Current model:[/] [bold]{current_model}[/bold]")
        console.print("\n[cyan]Available models:[/]")
        for model in AVAILABLE_MODELS:
            marker = " [green]✓[/]" if model == current_model else ""
            console.print(f"  • {model}{marker}")
        console.print("\n[dim]Usage: /model <model-name>[/]\n")
        return current_model

    # Switch to new model
    new_model = parts[1]
    if new_model in AVAILABLE_MODELS:
        console.print(f"[green]✓[/] Switched to [bold]{new_model}[/bold]")
        return new_model
    else:
        console.print(f"[red]✗[/] Unknown model: [bold]{new_model}[/bold]")
        console.print(f"[dim]Available: {', '.join(AVAILABLE_MODELS)}[/dim]")
        return current_model


def run_interactive(
    model: str,
    console: Console,
) -> int:
    """Run the interactive chat loop.

    Returns:
        Exit code (0 for success)
    """
    print_header()

    # Track mutable model state
    current_model = model

    # Create a session to keep history
    auto_suggest = CustomAutoSuggest(list(COMMANDS.keys()))
    session = PromptSession(completer=completer, style=style, auto_suggest=auto_suggest)

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
                    console.print(
                        Panel(
                            "\n".join(
                                [f"[bold cyan]{k}[/]: {v}" for k, v in COMMANDS.items()]
                            ),
                            title="Commands",
                        )
                    )
                    continue

                elif cmd == "/reset":
                    console.print("[yellow]↺ Context reset.[/]")
                    time.sleep(0.5)
                    continue

                elif cmd == "/model":
                    current_model = handle_model_command(
                        user_input, current_model, console
                    )
                    continue

                else:
                    console.print(f"[red]Unknown command: {cmd}[/]")
                    continue

            # Handle Normal Chat
            if not user_input:
                continue

            # Simulate "thinking"
            console.print()
            with console.status(
                f"[dim]Sending to {current_model}...[/]", spinner="dots"
            ):
                time.sleep(1)

            # Response
            console.print(
                Panel(
                    Markdown(f"I processed: **{user_input}**"),
                    title=f"[bold purple]{current_model}[/]",
                    border_style="purple",
                )
            )
            console.print()

        except KeyboardInterrupt:
            break
        except EOFError:
            break

    return 0


def cli(args_list: Sequence[str] | None = None, *, prog_name: str = "selfheal") -> int:
    """Run the CLI and return the exit code.

    Main entry point for testing and programmatic use.

    Args:
        args_list: Command-line arguments (None = sys.argv[1:])
        prog_name: Program name for help text

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = create_parser(prog_name)

    # Enable argcomplete BEFORE parsing
    argcomplete.autocomplete(parser)

    # Parse arguments
    args = parser.parse_args(args_list)

    # Create console
    console_instance = Console()

    # One-shot mode if prompt provided
    if args.prompt:
        console_instance.print(f"\n[dim]Using model: {args.model}[/]\n")
        console_instance.print(
            Panel(
                Markdown(f"I processed: **{args.prompt}**"),
                title=f"[bold purple]{args.model}[/]",
                border_style="purple",
            )
        )
        return 0

    # Interactive mode
    return run_interactive(args.model, console_instance)


def cli_exit(prog_name: str = "selfheal") -> None:
    """Run the CLI and exit with the returned code.

    Entry point for installed script.
    """
    sys.exit(cli(prog_name=prog_name))


if __name__ == "__main__":
    cli_exit()
