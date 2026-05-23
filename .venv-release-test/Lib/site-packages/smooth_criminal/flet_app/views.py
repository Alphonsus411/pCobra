import flet as ft
from smooth_criminal.memory import (
    get_execution_history,
    clear_execution_history,
    export_execution_history,
    build_summary,
    calcular_score,
)
from smooth_criminal.flet_app.components import (
    info_panel,
    function_table,
    action_buttons,
    moonwalk_animation,
)
from smooth_criminal.flet_app.utils import formatear_tiempo, export_filename

def main_view(page: ft.Page):
    table = function_table()
    msg = ft.Text()

    def refresh(_=None):
        history = get_execution_history()
        summary = build_summary(history)

        table.rows.clear()
        for fn, data in summary.items():
            avg = sum(data["durations"]) / len(data["durations"])
            score = calcular_score(data["durations"], data["decorators"])
            table.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(fn)),
                ft.DataCell(ft.Text(", ".join(sorted(data["decorators"])))),
                ft.DataCell(ft.Text(str(len(data["durations"])))),
                ft.DataCell(ft.Text(formatear_tiempo(avg))),
                ft.DataCell(ft.Text(f"{score}/100")),
            ]))
        page.update()

    def clear(_):
        if clear_execution_history():
            msg.value = "Historial borrado."
            table.rows.clear()
        else:
            msg.value = "No hay historial para borrar."
        page.update()

    def export(fmt: str):
        filepath = export_filename(ext=fmt)
        if export_execution_history(filepath, format=fmt):
            msg.value = f"Historial exportado a {filepath}"
        else:
            msg.value = "No hay historial para exportar."
        page.update()

    def trigger_moonwalk(e):
        moonwalk_animation(page)
        moonwalk_switch.value = False
        page.update()

    btns = action_buttons(refresh, clear, export, lambda e: None)
    moonwalk_switch = ft.Switch(label="Moonwalk", on_change=trigger_moonwalk)
    btns.controls.append(moonwalk_switch)

    page.add(
        ft.Text("🎩 Smooth Criminal Dashboard", size=28, weight="bold", color="purple"),
        btns,
        msg,
        table
    )

    refresh()
