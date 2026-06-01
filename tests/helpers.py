"""Geração de landmarks sintéticos para os testes (sem MediaPipe)."""

import numpy as np

from sentinela_solo.landmarks import (OMBRO_DIR, OMBRO_ESQ, QUADRIL_DIR, QUADRIL_ESQ, PoseLandmarks)


def _base() -> np.ndarray:
    return np.zeros((33, 4), dtype=float)


def _set(a, i, x, y, vis=1.0):
    a[i] = [x, y, 0.0, vis]


def verticais() -> PoseLandmarks:
    """Pessoa em pé: ombros acima dos quadris (tronco ~vertical)."""
    a = _base()
    _set(a, OMBRO_ESQ, 0.45, 0.30); _set(a, OMBRO_DIR, 0.55, 0.30)
    _set(a, QUADRIL_ESQ, 0.45, 0.62); _set(a, QUADRIL_DIR, 0.55, 0.62)
    return PoseLandmarks(a)


def horizontais() -> PoseLandmarks:
    """Pessoa caída: ombros e quadris na mesma altura (tronco ~horizontal)."""
    a = _base()
    _set(a, OMBRO_ESQ, 0.30, 0.48); _set(a, OMBRO_DIR, 0.30, 0.52)
    _set(a, QUADRIL_ESQ, 0.62, 0.48); _set(a, QUADRIL_DIR, 0.62, 0.52)
    return PoseLandmarks(a)


def invisiveis() -> PoseLandmarks:
    """Sem pontos confiáveis (visibilidade 0)."""
    return PoseLandmarks(_base())
