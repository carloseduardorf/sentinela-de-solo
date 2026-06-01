"""Sentinela de Solo — nó terrestre (edge) da rede Sentinela Orbital.

Visão computacional via webcam para abrigos climáticos durante ondas de calor:
detecta **pessoa caída/imóvel** (possível insolação), estima **ocupação** e
aciona alertas físicos (Arduino: RFID, proximidade, buzzer/LED).

Organização (modular):
- ``landmarks``      estrutura leve dos pontos de pose (desacopla do MediaPipe)
- ``posture``        classificação de postura (lógica pura, testável)
- ``fall_detector``  máquina de estados de queda (debounce + imobilidade)
- ``occupancy``      contagem de ocupação (CV + sensores)
- ``fps``            medidor de FPS do loop
- ``actuator``       atuação no Arduino (serial) com fallback sem hardware
- ``video_source``   captura robusta (webcam/arquivo/dummy) com reconexão
- ``pose_engine`` / ``face_engine``  wrappers do MediaPipe
- ``overlay``        HUD desenhado no frame
- ``app``            loop principal que integra tudo
"""

__version__ = "1.0.0"
