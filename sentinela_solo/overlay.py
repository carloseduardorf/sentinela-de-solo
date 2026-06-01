"""Desenho do HUD sobre o frame (FPS, estado, ocupação, esqueleto, alerta).

Observação técnica: as fontes do OpenCV (Hershey) não renderizam acentos, então
os rótulos na imagem são propositalmente em ASCII para sair limpos no vídeo.
"""

from __future__ import annotations

import cv2

from .fall_detector import EstadoMonitor
from .landmarks import (
    JOELHO_DIR, JOELHO_ESQ, OMBRO_DIR, OMBRO_ESQ, QUADRIL_DIR, QUADRIL_ESQ,
    TORNOZELO_DIR, TORNOZELO_ESQ,
)
from .occupancy import Nivel

_COR = {  # BGR
    EstadoMonitor.SEM_PESSOA: (130, 130, 130),
    EstadoMonitor.NORMAL: (0, 170, 0),
    EstadoMonitor.SUSPEITA: (0, 200, 255),
    EstadoMonitor.ALERTA: (0, 0, 255),
}
_ROTULO = {
    EstadoMonitor.SEM_PESSOA: "SEM PESSOA",
    EstadoMonitor.NORMAL: "NORMAL",
    EstadoMonitor.SUSPEITA: "SUSPEITA DE QUEDA",
    EstadoMonitor.ALERTA: "ALERTA: PESSOA CAIDA",
}
_NIVEL_COR = {Nivel.OK: (0, 170, 0), Nivel.ALTA: (0, 200, 255), Nivel.LOTADO: (0, 0, 255)}
_NIVEL_ROTULO = {Nivel.OK: "OK", Nivel.ALTA: "LOTACAO ALTA", Nivel.LOTADO: "LOTADO"}

_CONEXOES = [
    (OMBRO_ESQ, OMBRO_DIR), (OMBRO_ESQ, QUADRIL_ESQ), (OMBRO_DIR, QUADRIL_DIR),
    (QUADRIL_ESQ, QUADRIL_DIR), (QUADRIL_ESQ, JOELHO_ESQ), (JOELHO_ESQ, TORNOZELO_ESQ),
    (QUADRIL_DIR, JOELHO_DIR), (JOELHO_DIR, TORNOZELO_DIR),
]

_FONTE = cv2.FONT_HERSHEY_SIMPLEX


def _texto(frame, txt, org, escala=0.6, cor=(255, 255, 255), grossura=2, fundo=True):
    if fundo:
        (w, h), _ = cv2.getTextSize(txt, _FONTE, escala, grossura)
        x, y = org
        cv2.rectangle(frame, (x - 4, y - h - 6), (x + w + 4, y + 6), (0, 0, 0), -1)
    cv2.putText(frame, txt, org, _FONTE, escala, cor, grossura, cv2.LINE_AA)


def _desenhar_esqueleto(frame, landmarks, vis_min=0.3):
    h, w = frame.shape[:2]
    arr = landmarks.arr
    for a, b in _CONEXOES:
        if arr[a, 3] >= vis_min and arr[b, 3] >= vis_min:
            pa = (int(arr[a, 0] * w), int(arr[a, 1] * h))
            pb = (int(arr[b, 0] * w), int(arr[b, 1] * h))
            cv2.line(frame, pa, pb, (255, 200, 0), 2, cv2.LINE_AA)
    for i in range(arr.shape[0]):
        if arr[i, 3] >= vis_min:
            cv2.circle(frame, (int(arr[i, 0] * w), int(arr[i, 1] * h)), 3, (0, 255, 255), -1)


def desenhar_hud(
    frame,
    *,
    fps: float,
    estado: EstadoMonitor,
    segundos_caido: float,
    nivel: Nivel,
    ocupacao_estimativa: int,
    capacidade: int,
    landmarks=None,
    n_faces: int = 0,
    imovel: bool = False,
):
    h, w = frame.shape[:2]
    cor_estado = _COR[estado]

    if landmarks is not None:
        _desenhar_esqueleto(frame, landmarks)

    # barra de status no topo
    cv2.rectangle(frame, (0, 0), (w, 40), (20, 20, 20), -1)
    _texto(frame, f"FPS: {fps:4.1f}", (10, 28), 0.6, (255, 255, 255), 2, fundo=False)
    _texto(frame, _ROTULO[estado], (130, 28), 0.7, cor_estado, 2, fundo=False)
    _texto(
        frame,
        f"OCUPACAO: {ocupacao_estimativa}/{capacidade} [{_NIVEL_ROTULO[nivel]}]",
        (w - 360, 28), 0.6, _NIVEL_COR[nivel], 2, fundo=False,
    )

    if imovel and estado != EstadoMonitor.ALERTA:
        _texto(frame, "IMOVEL", (10, 70), 0.6, (0, 200, 255), 2)

    # alerta de queda: moldura vermelha + faixa inferior
    if estado == EstadoMonitor.ALERTA:
        cv2.rectangle(frame, (2, 2), (w - 2, h - 2), (0, 0, 255), 6)
        cv2.rectangle(frame, (0, h - 54), (w, h), (0, 0, 200), -1)
        _texto(frame, f"ALERTA: PESSOA CAIDA ({segundos_caido:0.1f}s) -> notificar Defesa Civil/Saude",
               (12, h - 18), 0.7, (255, 255, 255), 2, fundo=False)
    elif estado == EstadoMonitor.SUSPEITA:
        _texto(frame, f"verificando queda... {segundos_caido:0.1f}s", (12, h - 18), 0.6, (0, 200, 255), 2)

    return frame
