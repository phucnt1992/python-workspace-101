import shlex

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from typer.testing import CliRunner

_SHELL_COMMANDS: tuple[tuple[str, str], ...] = (
    ("clear, cls", "Clear the terminal screen."),
    ("help [command]", "Show available commands or detailed help for one command."),
    ("exit, quit", "Leave the todo shell."),
)


class TodoShell:
    _PROMPT = "todo> "
    _EXIT_COMMANDS = frozenset({"exit", "quit"})
    _CLEAR_COMMANDS = frozenset({"clear", "cls"})

    def __init__(self, typer_app: typer.Typer) -> None:
        self._typer = typer_app
        self._runner = CliRunner()
        self._console = Console()

    def run(self) -> None:
        self._print_welcome()
        while True:
            try:
                line = input(self._PROMPT)
            except (EOFError, KeyboardInterrupt):
                typer.echo()
                break

            line = line.strip()
            if not line:
                continue
            if line in self._EXIT_COMMANDS:
                break
            if line in self._CLEAR_COMMANDS:
                self._clear_screen()
                continue
            if line == "help":
                self._print_help()
                continue
            if line.startswith("help "):
                self._print_command_help(line[5:].strip())
                continue

            self._run_command(line)

    def _print_welcome(self) -> None:
        typer.echo("Todo shell — run commands without the 'todo' prefix.")
        typer.echo("Use quotes for multi-word values, e.g. create \"Buy milk\" -d \"2 bottles\"")
        typer.echo("Type 'help' for commands, 'clear' to clean the screen, or 'exit' to quit.")

    def _print_help(self) -> None:
        self._echo_typer_help(["--help"])
        self._print_shell_commands_help()

    def _print_shell_commands_help(self) -> None:
        table = Table(show_header=True, header_style="bold")
        table.add_column("Command")
        table.add_column("Description")
        for names, description in _SHELL_COMMANDS:
            table.add_row(names, description)
        self._console.print(Panel(table, title="Shell commands", border_style="cyan"))

    def _print_shell_command_help(self, command: str, description: str) -> None:
        self._console.print(Panel(description, title=f"Shell command: {command}", border_style="cyan"))

    def _print_command_help(self, command: str) -> None:
        if not command:
            self._print_help()
            return
        if command in self._CLEAR_COMMANDS:
            self._print_shell_command_help(command, "Clear the terminal screen.")
            return
        if command in self._EXIT_COMMANDS:
            self._print_shell_command_help(command, "Leave the todo shell.")
            return
        if command == "help":
            self._print_shell_command_help(
                command,
                "Show available commands or detailed help for one command.",
            )
            return

        self._echo_typer_help([command, "--help"])

    def _echo_typer_help(self, args: list[str]) -> None:
        result = self._runner.invoke(self._typer, args)
        output = result.stdout or (result.output if result.exit_code != 0 else "")
        if output:
            typer.echo(output.rstrip("\n"))

    def _clear_screen(self) -> None:
        # Use Rich's clear so terminal state stays in sync with Panel rendering.
        self._console.clear()

    def _run_command(self, line: str) -> None:
        try:
            args = shlex.split(line)
        except ValueError as exc:
            typer.echo(f"Invalid input: {exc}")
            return

        result = self._runner.invoke(self._typer, args)
        output = result.output.rstrip("\n")
        if output:
            typer.echo(output)
