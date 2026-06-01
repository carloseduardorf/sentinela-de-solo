"""Estrutura leve dos pontos de pose.

Encapsula os 33 landmarks do MediaPipe Pose num objeto simples (array NumPy),
de modo que o restante do código (classificação de postura, detecção de queda)
**não dependa** do MediaPipe e seja facilmente testável com dados sintéticos.
"""

from __future__ import annotations

import numpy as np

# Índices dos landmarks do MediaPipe Pose que usamos.
NARIZ = 0
OMBRO_ESQ = 11
OMBRO_DIR = 12
QUADRIL_ESQ = 23
QUADRIL_DIR = 24
JOELHO_ESQ = 25
JOELHO_DIR = 26
TORNOZELO_ESQ = 27
TORNOZELO_DIR = 28

N_LANDMARKS = 33


class PoseLandmarks:
    """Pontos de pose normalizados (x, y em 0..1; y cresce para baixo)."""

    __slots__ = ("arr",)

    def __init__(self, arr: np.ndarray) -> None:
        arr = np.asarray(arr, dtype=float)
        if arr.shape != (N_LANDMARKS, 4):
            raise ValueError(f"esperado array {(N_LANDMARKS, 4)} (x,y,z,visibilidade), recebido {arr.shape}")
        self.arr = arr

    def ponto(self, i: int) -> tuple[float, float]:
        return float(self.arr[i, 0]), float(self.arr[i, 1])

    def visibilidade(self, i: int) -> float:
        return float(self.arr[i, 3])

    def visivel(self, i: int, vis_min: float) -> bool:
        return self.visibilidade(i) >= vis_min

    def medio(self, i: int, j: int) -> tuple[float, float]:
        return (
            (self.arr[i, 0] + self.arr[j, 0]) / 2.0,
            (self.arr[i, 1] + self.arr[j, 1]) / 2.0,
        )

    def centro(self, vis_min: float = 0.0) -> tuple[float, float] | None:
        """Centro médio dos pontos visíveis (para medir movimento)."""
        mask = self.arr[:, 3] >= vis_min
        if not mask.any():
            return None
        pts = self.arr[mask]
        return float(pts[:, 0].mean()), float(pts[:, 1].mean())

    def aspecto_bbox(self, vis_min: float) -> float | None:
        """Razão largura/altura da caixa que envolve os pontos visíveis."""
        mask = self.arr[:, 3] >= vis_min
        if mask.sum() < 2:
            return None
        pts = self.arr[mask]
        largura = float(pts[:, 0].max() - pts[:, 0].min())
        altura = float(pts[:, 1].max() - pts[:, 1].min())
        if altura <= 1e-6:
            return float("inf")
        return largura / altura

    @classmethod
    def from_mediapipe(cls, landmark_list) -> "PoseLandmarks":
        """Converte o resultado do MediaPipe Pose nesta estrutura."""
        arr = np.array(
            [[lm.x, lm.y, lm.z, lm.visibility] for lm in landmark_list.landmark],
            dtype=float,
        )
        return cls(arr)
