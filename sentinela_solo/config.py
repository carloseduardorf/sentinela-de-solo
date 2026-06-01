"""Configuração central da Sentinela de Solo.

Reúne os parâmetros do pipeline num único objeto, evitando "números mágicos"
espalhados pelo código e facilitando o ajuste fino em campo.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Config:
    # ----- fonte de vídeo -----
    source: str = "0"            # "0".. = índice de webcam; caminho = arquivo; "dummy" = sintético
    largura: int = 640
    altura: int = 480
    max_reconexoes: int = 5      # tentativas de reabrir a webcam após falha

    # ----- detecção de postura / queda -----
    vis_min: float = 0.5         # visibilidade mínima do landmark para confiar nele
    limiar_vertical: float = 35.0    # graus: <= isso => pessoa em pé/sentada
    limiar_horizontal: float = 55.0  # graus: >= isso => pessoa deitada/caída
    seg_confirmar_queda: float = 2.0  # tempo deitado p/ confirmar QUEDA (anti-falso-positivo)
    seg_imovel: float = 8.0           # tempo imóvel (presente) p/ suspeitar de mal súbito
    limiar_movimento: float = 0.02    # deslocamento normalizado mínimo p/ contar como "movimento"

    # ----- ocupação -----
    capacidade: int = 20         # lotação do abrigo
    fracao_alerta_lotacao: float = 0.9  # >= 90% => nível ALTA

    # ----- Arduino (atuação física) -----
    serial_port: str | None = None   # ex.: "COM3"; None => sem hardware (fallback)
    baud: int = 115200

    # ----- execução -----
    mostrar_video: bool = True   # janela OpenCV; desligue em servidores headless
    espelhar: bool = True        # espelha a imagem (mais natural para o usuário)
