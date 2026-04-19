from cobra.cli.services.command_factory import CommandFactory


def test_command_factory_resuelve_por_nombre():
    factory = CommandFactory()

    ejecutar = factory.create("ejecutar")
    compilar = factory.create("compilar")
    verificar = factory.create("verificar")
    modulos = factory.create("modulos")

    assert ejecutar.name == "ejecutar"
    assert compilar.name == "compilar"
    assert verificar.name == "verificar"
    assert modulos.name == "modulos"


def test_command_factory_resuelve_por_capacidad():
    factory = CommandFactory()

    execute_commands = factory.create_by_capability("execute")
    codegen_commands = factory.create_by_capability("codegen")

    assert [cmd.name for cmd in execute_commands] == ["ejecutar"]
    assert {cmd.name for cmd in codegen_commands} == {"compilar", "verificar"}
