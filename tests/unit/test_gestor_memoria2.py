from core.memoria.estrategia_memoria import EstrategiaMemoria
from core.memoria.gestor_memoria import GestorMemoriaGenetico


def test_asignacion_y_liberacion_intensiva():
    estrategia = EstrategiaMemoria(10, 0.5)

    # Asignar múltiples bloques de diferentes tamaños
    indices = []
    for tam in [5, 10, 15, 20]:
        index = estrategia.asignar(tam)
        indices.append((index, tam))
        assert index != -1, f"No se pudo asignar bloque de tamaño {tam}"

    # Liberar todos los bloques asignados
    for index, tam in indices:
        estrategia.liberar(index, tam)

    # Verificar que todos los bloques han sido liberados
    for i in range(1024):
        assert estrategia.memoria[i] is None, "Memoria no liberada correctamente"


def test_gestor_memoria_genetico_intensivo():
    gestor = GestorMemoriaGenetico(poblacion_tam=20)

    # Realizar 10 generaciones con mayor carga de trabajo
    for _ in range(10):
        gestor.evolucionar()

    # Comprobar que todas las generaciones se realizaron correctamente
    assert len(gestor.poblacion) > 0, "No hay estrategias activas después de 10 generaciones"
