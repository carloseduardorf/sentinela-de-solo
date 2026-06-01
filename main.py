"""Ponto de entrada da Sentinela de Solo.

Exemplos:
    python main.py                          # webcam 0, janela com HUD
    python main.py --source dummy --no-video --max-frames 30   # teste sem câmera
    python main.py --serial-port COM3       # com Arduino conectado
    python main.py --source video.mp4 --capacidade 30
"""

from __future__ import annotations

import argparse

from sentinela_solo.app import App
from sentinela_solo.config import Config


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Sentinela de Solo — monitor de abrigo climático (visão computacional).")
    p.add_argument("--source", default="0", help='índice da webcam (ex.: "0"), caminho de vídeo, ou "dummy"')
    p.add_argument("--serial-port", default=None, help='porta do Arduino (ex.: "COM3"); omitido = sem hardware')
    p.add_argument("--baud", type=int, default=115200)
    p.add_argument("--capacidade", type=int, default=20, help="lotação do abrigo")
    p.add_argument("--largura", type=int, default=640)
    p.add_argument("--altura", type=int, default=480)
    p.add_argument("--no-video", action="store_true", help="não abre a janela (modo headless)")
    p.add_argument("--no-espelhar", action="store_true", help="não espelha a imagem")
    p.add_argument("--max-frames", type=int, default=None, help="encerra após N frames (útil em teste)")
    return p.parse_args()


def main() -> None:
    a = parse_args()
    config = Config(
        source=a.source,
        serial_port=a.serial_port,
        baud=a.baud,
        capacidade=a.capacidade,
        largura=a.largura,
        altura=a.altura,
        mostrar_video=not a.no_video,
        espelhar=not a.no_espelhar,
    )
    App(config).run(max_frames=a.max_frames)


if __name__ == "__main__":
    main()
