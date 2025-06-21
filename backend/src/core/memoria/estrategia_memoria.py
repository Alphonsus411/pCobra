import random


class EstrategiaMemoria:
    """Simula la gestión de memoria para programas Cobra."""
    def __init__(self, tam_bloque, frecuencia_recoleccion):
        """Inicializa la estrategia de manejo de memoria.

        :param tam_bloque: Tamaño del bloque de memoria que se asigna.
        :param frecuencia_recoleccion: Frecuencia de recolección de basura
            (entre 0.0 y 1.0).
        """
        self.tam_bloque = tam_bloque  # Tamaño de los bloques de memoria
        # Frecuencia de la recolección de basura
        self.frecuencia_recoleccion = frecuencia_recoleccion
        self.memoria = [None] * 1024  # Simulamos un espacio de memoria con 1024 bloques

    def asignar(self, tam):
        """
        Intenta asignar un bloque de memoria.
        :param tam: Tamaño del bloque a asignar.
        :return: Índice del bloque asignado o -1 si no se pudo asignar.
        """
        for i in range(len(self.memoria) - tam):
            # Verifica si todos los bloques en el rango son None
            if all(block is None for block in self.memoria[i:i + tam]):
                # Asignar el bloque
                # Se marca como True (bloque asignado)
                self.memoria[i:i + tam] = [True] * tam
                return i  # Retorna el índice donde se asignó
        return -1  # Si no hay espacio suficiente para asignar

    def liberar(self, index, tam):
        """
        Libera un bloque de memoria.
        :param index: Índice de inicio del bloque.
        :param tam: Tamaño del bloque a liberar.
        """
        self.memoria[index:index + tam] = [None] * tam  # Se marca como libre (None)

    def recolectar_basura(self):
        """
        Simulación de recolección de basura.
        """
        if random.random() < self.frecuencia_recoleccion:
            # Compactar memoria eliminando bloques vacíos
            self.memoria = [block for block in self.memoria if block is not None]
            self.memoria += [None] * self.memoria.count(None)

    def mostrar_estado(self):
        """
        Muestra el estado actual de la memoria para propósitos de depuración.
        """
        estado = ''.join(['X' if block else '.' for block in self.memoria])
        print(f"Estado de la memoria: {estado}")
