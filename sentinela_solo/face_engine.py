"""Wrapper do MediaPipe Face Detection — estimativa de ocupação por visão.

Conta rostos no frame como uma estimativa rápida de quantas pessoas estão no
ambiente. É leve (roda em CPU) e complementa a contagem física feita pelos
sensores do Arduino (proximidade/RFID) em ``occupancy``.
"""

from __future__ import annotations

import cv2
import mediapipe as mp


class MotorFaces:
    def __init__(self, *, min_deteccao: float = 0.5, modelo: int = 0) -> None:
        # model_selection=0: rostos próximos (até ~2 m), ideal para a porta do abrigo.
        self._fd = mp.solutions.face_detection.FaceDetection(
            model_selection=modelo, min_detection_confidence=min_deteccao
        )

    def contar(self, frame_bgr) -> int:
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        resultado = self._fd.process(rgb)
        return len(resultado.detections) if resultado.detections else 0

    def fechar(self) -> None:
        self._fd.close()

    def __enter__(self) -> "MotorFaces":
        return self

    def __exit__(self, *exc) -> None:
        self.fechar()
