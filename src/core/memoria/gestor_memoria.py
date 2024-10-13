import random


class EstrategiaMemoria:
    def __init__(self, tam_bloque, frecuencia_recoleccion):
        self.tam_bloque = tam_bloque  # Tamaño de los bloques de memoria
        self.frecuencia_recoleccion = frecuencia_recoleccion  # Frecuencia de la recolección de basura
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
                self.memoria[i:i + tam] = [True] * tam  # Se marca como True
                return i  # Retorna el índice donde se asignó
        return -1  # Si no hay espacio

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
            self.memoria = [block for block in self.memoria if block is not None] + [None] * self.memoria.count(None)


class GestorMemoriaGenetico:
    def __init__(self, poblacion_tam=10):
        """
        Inicializa el gestor de memoria con una población de estrategias de memoria.
        :param poblacion_tam: Tamaño de la población inicial de estrategias.
        """
        self.poblacion = [self.crear_estrategia_aleatoria() for _ in range(poblacion_tam)]
        self.generacion = 0

    def crear_estrategia_aleatoria(self):
        """
        Crea una estrategia de manejo de memoria con parámetros aleatorios.
        """
        tam_bloque = random.randint(1, 128)  # Tamaño del bloque de memoria
        frecuencia_recoleccion = random.uniform(0.0, 1.0)  # Probabilidad de recolección de basura
        return EstrategiaMemoria(tam_bloque, frecuencia_recoleccion)

    def evaluar(self, estrategia):
        """
        Evalúa la estrategia de memoria simulando un conjunto de operaciones de asignación y liberación de memoria.
        :param estrategia: La estrategia de memoria a evaluar.
        :return: Total de memoria asignada correctamente.
        """
        total_asignado = 0
        for _ in range(100):  # Simula 100 operaciones de memoria
            tam = random.randint(1, estrategia.tam_bloque)
            index = estrategia.asignar(tam)
            if index != -1:
                total_asignado += tam
                if random.random() < 0.5:  # Liberar memoria aleatoriamente
                    estrategia.liberar(index, tam)
            estrategia.recolectar_basura()
        return total_asignado

    def seleccionar(self):
        """
        Selecciona las mejores estrategias basadas en su desempeño.
        """
        fitness = [(self.evaluar(estrategia), estrategia) for estrategia in self.poblacion]
        fitness.sort(reverse=True, key=lambda x: x[0])  # Ordena por fitness en orden descendente
        self.poblacion = [estrategia for _, estrategia in fitness[:len(fitness) // 2]]  # Selecciona la mitad superior

    def cruzar(self):
        """
        Cruza las estrategias de la población para generar nuevas combinaciones.
        """
        nuevos_individuos = []
        for _ in range(len(self.poblacion)):
            padre1, padre2 = random.sample(self.poblacion, 2)
            nuevo_tam_bloque = random.choice([padre1.tam_bloque, padre2.tam_bloque])
            nueva_frecuencia_recoleccion = random.choice([padre1.frecuencia_recoleccion, padre2.frecuencia_recoleccion])
            nuevos_individuos.append(EstrategiaMemoria(nuevo_tam_bloque, nueva_frecuencia_recoleccion))
        self.poblacion += nuevos_individuos

    def mutar(self):
        """
        Introduce mutaciones en algunas estrategias de la población.
        """
        for estrategia in self.poblacion:
            if random.random() < 0.1:  # 10% de probabilidad de mutación
                estrategia.tam_bloque = random.randint(1, 128)
            if random.random() < 0.1:
                estrategia.frecuencia_recoleccion = random.uniform(0.0, 1.0)

    def evolucionar(self):
        """
        Realiza una generación completa: selección, cruce y mutación.
        """
        self.seleccionar()
        self.cruzar()
        self.mutar()
        self.generacion += 1
        print(f"Generación {self.generacion}: {len(self.poblacion)} estrategias de memoria activas")
