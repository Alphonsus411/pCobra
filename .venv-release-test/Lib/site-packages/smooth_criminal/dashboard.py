from rich.table import Table
from rich.console import Console
from smooth_criminal.memory import get_execution_history, build_summary

console = Console()

def render_dashboard():
    """
    Muestra un panel con el historial de funciones ejecutadas,
    decoradores aplicados y rendimiento medio.
    """
    all_logs = get_execution_history()
    if not all_logs:
        console.print("[yellow]No hay historial de ejecuciones todavía.[/yellow]")
        return

    stats = build_summary(all_logs)

    table = Table(title="🧠 Smooth Criminal — Function Dashboard", header_style="bold magenta")
    table.add_column("Function", style="cyan", no_wrap=True)
    table.add_column("Decorator(s)", style="green")
    table.add_column("Runs", justify="right")
    table.add_column("Avg Time (s)", justify="right")

    for name, info in stats.items():
        count = len(info["durations"])
        avg_time = sum(info["durations"]) / count
        table.add_row(
            name,
            ", ".join(sorted(info["decorators"])),
            str(count),
            f"{avg_time:.6f}"
        )

    console.print(table)
