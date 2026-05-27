import typer
from rich.console import Console

app = typer.Typer(name="exp", help="Experimental commands for testing and development.")


@app.command("moo")
def moo() -> None:
    """Prints a colorful cow to the console."""

    console = Console()
    cow = [
        ("        (    )", "yellow"),
        ("       (      )", "yellow"),
        ("        (    )", "yellow"),
        ("  ^__^         ", "white"),
        ("  (oo)\\_______", "brown"),
        ("  (__)\\       )\\/\\/", "brown"),
        ("      ||----w |", "brown"),
        ("      ||     ||", "red"),
    ]
    for line, color in cow:
        console.print(f"[bold {color}]{line}[/bold {color}]")
    console.print("[bold green]Hello, Moo![/bold green]")


@app.command("table")
def print_table() -> None:
    """Prints a simple table to the console."""
    from rich.table import Table

    console = Console()
    table = Table(title="Sample Table")

    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Name", style="magenta")
    table.add_column("Description", style="green")

    table.add_row("1", "Item One", "This is the first item.")
    table.add_row("2", "Item Two", "This is the second item.")
    table.add_row("3", "Item Three", "This is the third item.")

    console.print(table)


@app.command("prompts")
def prompts() -> None:
    """Demonstrates the use of prompts for user input."""
    name = typer.prompt("What is your name?")
    age = typer.prompt("What is your age?", type=int)
    typer.echo(f"Hello, {name}! You are {age} years old.")


@app.command("progress")
def render_progress() -> None:
    """Demonstrates rendering a progress bar."""
    import time

    from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn()) as progress:
        task = progress.add_task("Processing...", total=100)
        for _ in range(100):
            time.sleep(0.05)  # Simulate work
            progress.update(task, advance=1)
    typer.echo("Processing complete!")
