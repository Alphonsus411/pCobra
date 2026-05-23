# emotional_rnn.py

"""Red neuronal recurrente sencilla para modelar estados emocionales."""

from __future__ import annotations

import numpy as np
from typing import Literal


class EmotionalRNN:
    """Implementa una RNN o LSTM minimalista en ``numpy``."""

    def __init__(
        self,
        input_size: int,
        hidden_size: int = 8,
        rnn_type: Literal["rnn", "lstm"] = "rnn",
        learning_rate: float = 0.01,
    ) -> None:
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = input_size
        self.rnn_type = rnn_type
        self.learning_rate = learning_rate

        rng = np.random.default_rng(42)
        if rnn_type == "rnn":
            self.Wxh = rng.normal(0, 0.1, (hidden_size, input_size))
            self.Whh = rng.normal(0, 0.1, (hidden_size, hidden_size))
            self.bh = np.zeros(hidden_size)
        else:  # LSTM
            gate_dim = hidden_size
            self.Wf = rng.normal(0, 0.1, (gate_dim, input_size + hidden_size))
            self.Wi = rng.normal(0, 0.1, (gate_dim, input_size + hidden_size))
            self.Wc = rng.normal(0, 0.1, (gate_dim, input_size + hidden_size))
            self.Wo = rng.normal(0, 0.1, (gate_dim, input_size + hidden_size))
            self.bf = np.zeros(gate_dim)
            self.bi = np.zeros(gate_dim)
            self.bc = np.zeros(gate_dim)
            self.bo = np.zeros(gate_dim)
            self.c = np.zeros(hidden_size)
        self.Why = rng.normal(0, 0.1, (input_size, hidden_size))
        self.by = np.zeros(input_size)
        self.reset_state()

    # ------------------------------------------------------------------
    def reset_state(self) -> None:
        """Inicializa los estados ocultos."""
        self.h = np.zeros(self.hidden_size)
        if self.rnn_type == "lstm":
            self.c = np.zeros(self.hidden_size)

    # ------------------------------------------------------------------
    def _sigmoid(self, x: np.ndarray) -> np.ndarray:
        return 1 / (1 + np.exp(-x))

    # ------------------------------------------------------------------
    def forward(self, seq: np.ndarray) -> np.ndarray:
        """Procesa una secuencia de vectores de entrada."""
        outputs = []
        self.last_hs = []
        if self.rnn_type == "rnn":
            for x in seq:
                h_raw = np.dot(self.Wxh, x) + np.dot(self.Whh, self.h) + self.bh
                self.h = np.tanh(h_raw)
                y = np.dot(self.Why, self.h) + self.by
                outputs.append(y)
                self.last_hs.append(self.h.copy())
        else:  # LSTM
            for x in seq:
                z = np.concatenate([x, self.h])
                f = self._sigmoid(np.dot(self.Wf, z) + self.bf)
                i = self._sigmoid(np.dot(self.Wi, z) + self.bi)
                c_bar = np.tanh(np.dot(self.Wc, z) + self.bc)
                self.c = f * self.c + i * c_bar
                o = self._sigmoid(np.dot(self.Wo, z) + self.bo)
                self.h = o * np.tanh(self.c)
                y = np.dot(self.Why, self.h) + self.by
                outputs.append(y)
                self.last_hs.append(self.h.copy())
        return np.vstack(outputs)

    # ------------------------------------------------------------------
    def update(self, seq: np.ndarray, targets: np.ndarray) -> None:
        """Entrenamiento supervisado muy básico con MSE."""
        preds = self.forward(seq)
        error = preds - targets
        dWhy = np.dot(error.T, np.vstack(self.last_hs)) / len(seq)
        dby = error.mean(axis=0)
        self.Why -= self.learning_rate * dWhy
        self.by -= self.learning_rate * dby

    # ------------------------------------------------------------------
    def __call__(self, seq: np.ndarray) -> np.ndarray:
        return self.forward(seq)

