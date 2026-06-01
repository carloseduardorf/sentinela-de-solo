"""Detecção de queda — máquina de estados com debounce e imobilidade.

Lógica **pura** e determinística (relógio injetável), portanto testável sem
câmera. Robustez a intempéries: uma queda só é confirmada se a postura
HORIZONTAL persistir por ``seg_confirmar_queda``; falhas breves de detecção
(oclusão/ruído) são toleradas por uma janela de carência (``grace``), evitando
tanto falsos positivos quanto a perda do alerta por um frame ruim.
"""

from __future__ import annotations

import math
import time
from enum import Enum

from .posture import Postura


class EstadoMonitor(Enum):
    SEM_PESSOA = "sem pessoa"
    NORMAL = "normal"
    SUSPEITA = "suspeita de queda"
    ALERTA = "ALERTA — pessoa caída"


class DetectorQueda:
    def __init__(
        self,
        *,
        seg_confirmar_queda: float = 2.0,
        seg_imovel: float = 8.0,
        limiar_movimento: float = 0.02,
        grace: float = 0.7,
    ) -> None:
        self.seg_confirmar_queda = seg_confirmar_queda
        self.seg_imovel = seg_imovel
        self.limiar_movimento = limiar_movimento
        self.grace = grace  # tolera oclusão/ruído sem zerar o cronômetro de queda

        self.estado = EstadoMonitor.SEM_PESSOA
        self.segundos_caido = 0.0
        self.imovel = False
        self._t_inicio_horizontal: float | None = None
        self._t_ultima_horizontal: float | None = None
        self._ultimo_centro: tuple[float, float] | None = None
        self._t_movimento: float | None = None

    def atualizar(
        self,
        postura: Postura | None,
        *,
        centro: tuple[float, float] | None = None,
        agora: float | None = None,
    ) -> EstadoMonitor:
        agora = time.monotonic() if agora is None else float(agora)
        horizontal = postura == Postura.HORIZONTAL
        presente = postura in (Postura.VERTICAL, Postura.HORIZONTAL, Postura.INCLINADO)

        # --- imobilidade: mede deslocamento do centro do corpo ---
        if centro is not None:
            if self._ultimo_centro is None:
                self._ultimo_centro = centro
                self._t_movimento = agora
            else:
                dist = math.hypot(centro[0] - self._ultimo_centro[0], centro[1] - self._ultimo_centro[1])
                if dist >= self.limiar_movimento:
                    self._t_movimento = agora
                    self._ultimo_centro = centro

        # --- janela horizontal com carência (debounce temporal) ---
        if horizontal:
            self._t_ultima_horizontal = agora
            if self._t_inicio_horizontal is None:
                self._t_inicio_horizontal = agora
        elif self._t_inicio_horizontal is not None:
            if (agora - (self._t_ultima_horizontal or agora)) > self.grace:
                self._t_inicio_horizontal = None  # saiu da horizontal de verdade

        # --- estado resultante ---
        if self._t_inicio_horizontal is not None:
            self.segundos_caido = agora - self._t_inicio_horizontal
            self.estado = (
                EstadoMonitor.ALERTA
                if self.segundos_caido >= self.seg_confirmar_queda
                else EstadoMonitor.SUSPEITA
            )
        else:
            self.segundos_caido = 0.0
            self.estado = EstadoMonitor.NORMAL if presente else EstadoMonitor.SEM_PESSOA

        self.imovel = (
            presente
            and self._t_movimento is not None
            and (agora - self._t_movimento) >= self.seg_imovel
        )
        return self.estado
