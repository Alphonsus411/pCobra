from src.core.memoria.estrategia_memoria import EstrategiaMemoria
from src.core.memoria.gestor_memoria import GestorMemoriaGenetico


def test_asignacion_y_liberacion():
    estrategia = EstrategiaMemoria(10, 0.5)

    # Asignar un bloque de tamaño 10
    index = estrategia.asignar(10)
    assert index != -1, "Error: No se pudo asignar memoria correctamente"

    # Liberar el bloque
    estrategia.liberar(index, 10)
    assert all(bloque is None for bloque in
               estrategia.memoria[index:index + 10]), "Error: La memoria no se liberó correctamente"


def test_gestor_memoria_genetico():
    gestor = GestorMemoriaGenetico(poblacion_tam=10)

    # Realizamos varias generaciones
    for _ in range(5):
        gestor.evolucionar()

    # Verificamos que la población evolucione y no quede vacía
    assert len(gestor.poblacion) > 0, "Error: La población de estrategias es demasiado pequeña"
