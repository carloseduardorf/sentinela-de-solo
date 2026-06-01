"""Classificação de postura a partir dos landmarks de pose.

Lógica **pura** (sem MediaPipe/OpenCV) e portanto 100% testável: recebe um
``PoseLandmarks`` e devolve se a pessoa está VERTICAL (em pé/sentada),
HORIZONTAL (deitada/caída) ou em transição.

Método: mede a inclinação do tronco (vetor ombros→quadril) em relação ao eixo
vertical. ~0° = ereto; ~90° = deitado. A razão da caixa delimitadora serve de
desempate na faixa intermediária.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum

from .landmarks import OMBRO_DIR, OMBRO_ESQ, QUADRIL_DIR, QUADRIL_ESQ, PoseLandmarks


class Postura(Enum):
    VERTICAL = "em pé / sentado"
    HORIZONTAL = "deitado / caído"
    INCLINADO = "inclinado"
    INDEFINIDO = "indefinido"


@dataclass
class ResultadoPostura:
    postura: Postura
    inclinacao_graus: float | None
    aspecto: float | None


def classificar(
    lm: PoseLandmarks,
    *,
    limiar_vertical: float = 35.0,
    limiar_horizontal: float = 55.0,
    vis_min: float = 0.5,
) -> ResultadoPostura:
    """Classifica a postura. Retorna INDEFINIDO se faltarem pontos confiáveis."""
    essenciais = (OMBRO_ESQ, OMBRO_DIR, QUADRIL_ESQ, QUADRIL_DIR)
    if not all(lm.visivel(i, vis_min) for i in essenciais):
        return ResultadoPostura(Postura.INDEFINIDO, None, None)

    sx, sy = lm.medio(OMBRO_ESQ, OMBRO_DIR)
    hx, hy = lm.medio(QUADRIL_ESQ, QUADRIL_DIR)
    dx = sx - hx
    dy = sy - hy
    # Inclinação do tronco em relação à vertical: 0° ereto, 90° deitado.
    inclinacao = math.degrees(math.atan2(abs(dx), abs(dy) + 1e-9))
    aspecto = lm.aspecto_bbox(vis_min)

    if inclinacao <= limiar_vertical:
        postura = Postura.VERTICAL
    elif inclinacao >= limiar_horizontal:
        postura = Postura.HORIZONTAL
    else:
        # Faixa de transição: a caixa "deitada" (mais larga que alta) confirma queda.
        postura = Postura.HORIZONTAL if (aspecto is not None and aspecto > 1.3) else Postura.INCLINADO

    return ResultadoPostura(postura, inclinacao, aspecto)
