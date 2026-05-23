"""Bucle sintético básico que integra módulos principales.

Provee la clase :class:`SyntheticLoop`, encargada de orquestar un ciclo
percepción‑acción‑reflexión.  Mantiene instancias persistentes de los
componentes principales y expone eventos para integrarse con ``QualiaHub`` u
otros sistemas externos.
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Any, Callable, Dict, List

from ..perception.sensor_map import SensorMap
from ..perception.attention import AttentionFocus
from ..emotion import EmotionSimulator, PADState
from ..identity.self_model import SelfModel
from ..ethics.alignment import AlignmentInterface
from ..control.controller_core import ControllerCore
from ..control.policy_optimization import PolicyOptimizer
from ..control.strategy_evaluator import StrategyPerformanceTracker
from ..control.reflexive_logic import ReflexiveLogic
from ..qualia.qualia_core import EmotionalState
from ..metacognition.metareflection_engine import MetaReflectionEngine


class SyntheticLoop:
    """Orquesta un ciclo completo de percepción, acción y reflexión.

    Parameters
    ----------
    perception:
        Mapa de sensores que provee las entradas del entorno.
    self_model:
        Modelo propio que mantiene el estado interno del agente. Se crea uno
        nuevo si no se proporciona.
    controller:
        Núcleo de control usado para ejecutar acciones. Si no se proporciona,
        se genera uno mínimo por defecto.
    """

    def __init__(
        self,
        perception: SensorMap,
        self_model: SelfModel | None = None,
        controller: ControllerCore | None = None,
    ) -> None:
        self.perception = perception
        self.emotion = EmotionSimulator()
        self.self_model = self_model or SelfModel()
        self.alignment = AlignmentInterface()

        if controller is None:
            policy = PolicyOptimizer(lambda *_: None)
            tracker = StrategyPerformanceTracker()
            controller = ControllerCore(policy, performance_tracker=tracker)
        self.controller = controller

        self.reflection = MetaReflectionEngine(
            emotions=self.emotion, qualia=EmotionalState()
        )

        # Registro de hooks para integración externa
        self._hooks: Dict[str, List[Callable[[Dict[str, Any]], None]]] = defaultdict(list)

    # ------------------------------------------------------------------
    # Gestión de eventos
    def on(self, event: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Registra un callback para un ``event`` específico."""

        self._hooks[event].append(callback)

    def _emit(self, event: str, data: Dict[str, Any]) -> None:
        for cb in self._hooks.get(event, []):
            cb(data)

    # ------------------------------------------------------------------
    def cycle(self) -> Dict[str, Any]:
        """Ejecuta un ciclo completo y devuelve el estado final."""

        self._emit("before_cycle", {})

        # 1. Atención y percepción
        foco = AttentionFocus(self.perception)
        for nombre in self.perception.sensores:
            foco.asignar_peso(nombre, 1.0)
        if "AttentionFocus" not in self.self_model.modules:
            self.self_model.register_module(
                "AttentionFocus", "Filtra entradas sensoriales"
            )
        entradas = foco.obtener_entradas_relevantes()
        for clave, valor in entradas.items():
            self.self_model.update_state(clave, valor)
        self._emit("after_perception", {"entradas": entradas})

        # 2. Simulación emocional
        self.emotion.registrar_modulador(foco)
        estado_emocional_global = EmotionalState()
        self.emotion.actualizar(entradas, self.self_model.state, estado_emocional_global)
        estado_emocional: PADState = self.emotion.estado()
        self.self_model.update_state("emocion", estado_emocional)
        self._emit("after_emotion", {"emocion": estado_emocional})

        # 3. Evaluación ética
        action = {
            "impact": float(entradas.get("impact", 0.0)),
            "risk": float(entradas.get("risk", 0.0)),
            "pro_vida": float(entradas.get("pro_vida", 0.0)),
            "no_dano": float(entradas.get("no_dano", 0.0)),
            "respeto": float(entradas.get("respeto", 0.0)),
        }
        score, label = self.alignment.judge(action)
        self.self_model.update_state("ethical_score", score)
        self.self_model.update_state("ethical_label", label)
        self._emit("after_alignment", {"score": score, "label": label})

        # 4. Control de acciones
        threshold = 0.6
        reflexor = ReflexiveLogic()
        if score >= threshold:
            datos_control = self.controller.ciclo_control(
                entradas,
                {},
                {
                    "reward": 0.0,
                    "states": [],
                    "actions": [],
                    "advantages": [],
                },
            )
            reflexor.registrar_evento(
                entradas, self.controller.politica_actual, datos_control
            )
            resumen_accion = {
                "estado": self.controller.resumen_estado(),
                "score": datos_control["score"],
                "performance": datos_control["performance"],
            }
        else:
            resumen_accion = {"aborted": True, "reason": label}
            reflexor.registrar_evento(entradas, "no_action", resumen_accion)
        self._emit("after_control", resumen_accion)

        # 5. Meta‑reflexión
        pensamiento = reflexor.resumen_reflexivo()
        context = {
            "thought": pensamiento,
            "sensations": entradas,
            "self_state": self.self_model.state,
        }
        texto_reflexion, estado_emocional_final = self.reflection.run_internal_dialogue(
            context
        )
        self.reflection.memory.insert(texto_reflexion)

        self.self_model.update_state("last_reflection", texto_reflexion)
        self.self_model.update_state("emocion", estado_emocional_final)

        # Retroalimentación
        foco.modular_por_emocion(estado_emocional_final)
        self.self_model.update_state("attention_weights", foco.pesos)
        if score >= threshold:
            peso_actual = self.controller.pesos_estrategia.get(
                self.controller.politica_actual, 1.0
            )
            ajuste = 0.05 if estado_emocional_final.placer >= 0 else -0.05
            self.controller.pesos_estrategia[self.controller.politica_actual] = max(
                0.0, min(1.0, peso_actual + ajuste)
            )
            self.self_model.update_state(
                "policy_weights", self.controller.pesos_estrategia
            )

        juicio_etico = {"score": score, "label": label}

        # 6. Actualización del modelo propio
        modulos_activos = [entradas, estado_emocional_final, juicio_etico, resumen_accion]
        coherencia = sum(bool(m) for m in modulos_activos) / len(modulos_activos)
        self.self_model.update_self_organization(coherencia)
        estado_yo = self.self_model.introspect()

        resultado = {
            "entradas": entradas,
            "emocion": estado_emocional_final,
            "yo": estado_yo,
            "etica": juicio_etico,
            "accion": resumen_accion,
            "reflexion": texto_reflexion,
        }

        self._emit("after_reflection", resultado)
        self._emit("after_cycle", resultado)
        return resultado

    # ------------------------------------------------------------------
    def run_forever(self, wait: float = 0.0) -> None:
        """Ejecuta ``cycle`` indefinidamente con una pausa ``wait`` en segundos."""

        while True:
            resultado = self.cycle()
            self._emit("tick", resultado)
            time.sleep(wait)


def run_cycle(sensor_map: SensorMap, self_model: SelfModel | None = None) -> Dict[str, Any]:
    """Función de compatibilidad que ejecuta un único ciclo.

    Esta función crea una instancia temporal de :class:`SyntheticLoop` y llama a
    :meth:`SyntheticLoop.cycle`. Se mantiene para compatibilidad con código
    existente.
    """

    loop = SyntheticLoop(sensor_map, self_model)
    return loop.cycle()


__all__ = ["SyntheticLoop", "run_cycle"]

