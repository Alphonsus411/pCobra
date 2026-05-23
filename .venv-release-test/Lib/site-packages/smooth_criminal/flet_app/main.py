import flet as ft
from smooth_criminal.memory import (
    get_execution_history,
    score_function,
    clear_execution_history,
    export_execution_history,
    build_summary,
)
from datetime import datetime

def mostrar_grafico(e, page, dropdown_func, msg):
    import matplotlib.pyplot as plt
    import tempfile
    from flet import Image

    history = get_execution_history()
    if not history:
        msg.value = "⚠️ No hay datos para graficar."
        page.update()
        return

    func = dropdown_func.value if dropdown_func.value else history[0]["function"]
    times = [entry["duration"] for entry in history if entry["function"] == func]

    if not times:
        msg.value = "⚠️ No hay datos para graficar."
        page.update()
        return

    fig, ax = plt.subplots()
    ax.plot(times, marker='o')
    ax.set_title(f"Historial de tiempos: {func}")
    ax.set_xlabel("Ejecución")
    ax.set_ylabel("Duración (s)")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        fig.savefig(tmp.name)
        graph_path = tmp.name

    plt.close(fig)

    page.dialog = ft.AlertDialog(
        title=ft.Text(f"Gráfico de: {func}"),
        content=Image(src=graph_path, width=500, height=300),
        open=True
    )
    page.update()

def main(page: ft.Page):
    page.title = "Smooth Criminal Dashboard"
    page.theme_mode = "light"
    page.padding = 20
    page.scroll = "auto"

    title = ft.Text("🎩 Smooth Criminal Dashboard", size=26, weight="bold", color="purple")

    dropdown_func = ft.Dropdown(label="Selecciona función",
                                options=[],
                                width=300)

    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Function")),
            ft.DataColumn(ft.Text("Decorator(s)")),
            ft.DataColumn(ft.Text("Runs")),
            ft.DataColumn(ft.Text("Avg Time (s)")),
            ft.DataColumn(ft.Text("Score")),
        ],
        rows=[]
    )

    msg = ft.Text("")

    def refresh_table(e=None):
        history = get_execution_history()
        summary = build_summary(history)

        table.rows = []
        for name, data in summary.items():
            avg_time = sum(data["durations"]) / len(data["durations"])
            score = score_function(name)[0]
            row = ft.DataRow(cells=[
                ft.DataCell(ft.Text(name)),
                ft.DataCell(ft.Text(", ".join(sorted(data["decorators"])))),
                ft.DataCell(ft.Text(str(len(data["durations"])))),
                ft.DataCell(ft.Text(f"{avg_time:.6f}")),
                ft.DataCell(ft.Text(f"{score}/100" if score is not None else "N/A")),
            ])
            table.rows.append(row)

        dropdown_func.options = [ft.dropdown.Option(f) for f in summary.keys()]
        page.update()

    def clear_history(e):
        if clear_execution_history():
            msg.value = "🧼 Historial borrado exitosamente."
            refresh_table()
        else:
            msg.value = "⚠️ No hay historial para borrar."
        page.update()

    def export_data(e):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = f"smooth_export_{timestamp}.csv"
        if export_execution_history(csv_file, format="csv"):
            msg.value = f"💾 Historial exportado a {csv_file}"
        else:
            msg.value = "⚠️ No hay historial para exportar."
        page.update()

    graph_button = ft.ElevatedButton(
        "📈 Ver gráfico",
        on_click=lambda e: mostrar_grafico(e, page, dropdown_func, msg),
        icon=ft.icons.INSERT_CHART
    )

    refresh_button = ft.ElevatedButton("🔄 Refresh", on_click=refresh_table, icon=ft.icons.REFRESH)
    clean_button = ft.ElevatedButton("🧼 Limpiar historial", on_click=clear_history, icon=ft.icons.DELETE)
    export_button = ft.ElevatedButton("💾 Exportar CSV", on_click=export_data, icon=ft.icons.DOWNLOAD)

    buttons = ft.Row([refresh_button, clean_button, export_button, graph_button], spacing=15)

    page.add(title, dropdown_func, buttons, msg, table)
    refresh_table()

if __name__ == "__main__":
    ft.app(target=main)
