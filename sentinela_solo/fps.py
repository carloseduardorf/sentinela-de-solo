"""Medidor de FPS do loop de captura.

Usa média móvel exponencial (EMA) para uma leitura estável — exigida na
demonstração do vídeo. O relógio é injetável (parâmetro ``agora``) para
permitir testes determinísticos.
"""

from __future__ import annotations

import time


class MedidorFPS:
    def __init__(self, suavizacao: float = 0.9) -> None:
        if not 0.0 <= suavizacao < 1.0:
            raise ValueError("suavizacao deve estar em [0, 1)")
        self.suavizacao = suavizacao
        self._fps: float = 0.0
        self._ultimo: float | None = None

    def marcar(self, *, agora: float | None = None) -> float:
        """Registra um frame e devolve o FPS suavizado."""
        agora = time.monotonic() if agora is None else float(agora)
        if self._ultimo is not None:
            dt = agora - self._ultimo
            if dt > 0:
                inst = 1.0 / dt
                self._fps = inst if self._fps == 0.0 else (
                    self.suavizacao * self._fps + (1.0 - self.suavizacao) * inst
                )
        self._ultimo = agora
        return self._fps

    @property
    def fps(self) -> float:
        return self._fps
