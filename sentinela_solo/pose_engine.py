"""Wrapper do MediaPipe Pose.

Isola toda a dependência do MediaPipe: recebe um frame BGR (OpenCV) e devolve
um ``PoseLandmarks`` (nossa estrutura desacoplada) ou ``None`` quando não há
pessoa detectada. Mantém o resto do código testável e independente do MediaPipe.
"""

from __future__ import annotations

import cv2
import mediapipe as mp

from .landmarks import PoseLandmarks


class MotorPose:
    def __init__(
        self,
        *,
        model_complexity: int = 1,
        min_deteccao: float = 0.5,
        min_rastreio: float = 0.5,
    ) -> None:
        self._pose = mp.solutions.pose.Pose(
            static_image_mode=False,
            model_complexity=model_complexity,
            enable_segmentation=False,
            min_detection_confidence=min_deteccao,
            min_tracking_confidence=min_rastreio,
        )

    def processar(self, frame_bgr) -> PoseLandmarks | None:
        # Converte para RGB e marca como somente-leitura (otimização do MediaPipe).
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        resultado = self._pose.process(rgb)
        if not resultado.pose_landmarks:
            return None
        return PoseLandmarks.from_mediapipe(resultado.pose_landmarks)

    def fechar(self) -> None:
        self._pose.close()

    def __enter__(self) -> "MotorPose":
        return self

    def __exit__(self, *exc) -> None:
        self.fechar()
