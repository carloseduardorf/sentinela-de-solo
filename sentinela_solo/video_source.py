"""Captura de vídeo robusta (webcam / arquivo / sintética).

Trata explicitamente as falhas exigidas pela GS: **falha de hardware da webcam**
(``ErroCamera``) e **queda de frame** (``QuedaDeFrame``). A ``DummySource``
gera frames sintéticos para rodar testes e demonstrações sem nenhuma câmera —
o que também ajuda na reprodutibilidade.
"""

from __future__ import annotations

import cv2
import numpy as np


class ErroCamera(Exception):
    """Falha ao abrir/reabrir o dispositivo de captura."""


class QuedaDeFrame(Exception):
    """Um frame não pôde ser lido (queda momentânea do stream)."""


class FimDoVideo(Exception):
    """Fonte finita (arquivo/dummy) chegou ao fim."""


class FonteVideo:
    """Interface comum + uso como context manager (libera o recurso ao sair)."""

    def ler(self) -> np.ndarray:
        raise NotImplementedError

    def reabrir(self) -> None:
        pass

    def liberar(self) -> None:
        pass

    def __enter__(self) -> "FonteVideo":
        return self

    def __exit__(self, *exc) -> None:
        self.liberar()


class WebcamSource(FonteVideo):
    def __init__(self, indice: int = 0, largura: int = 640, altura: int = 480) -> None:
        self.indice = indice
        self.largura = largura
        self.altura = altura
        self.cap: cv2.VideoCapture | None = None
        self._abrir()

    def _abrir(self) -> None:
        # CAP_DSHOW acelera a abertura da webcam no Windows.
        cap = cv2.VideoCapture(self.indice, cv2.CAP_DSHOW)
        if cap is None or not cap.isOpened():
            raise ErroCamera(f"não foi possível abrir a webcam {self.indice}")
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.largura)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.altura)
        self.cap = cap

    def ler(self) -> np.ndarray:
        if self.cap is None:
            raise ErroCamera("webcam não inicializada")
        ok, frame = self.cap.read()
        if not ok or frame is None:
            raise QuedaDeFrame("falha ao capturar frame da webcam")
        return frame

    def reabrir(self) -> None:
        self.liberar()
        self._abrir()

    def liberar(self) -> None:
        if self.cap is not None:
            self.cap.release()
            self.cap = None


class FileSource(FonteVideo):
    def __init__(self, caminho: str) -> None:
        self.caminho = caminho
        cap = cv2.VideoCapture(caminho)
        if not cap.isOpened():
            raise ErroCamera(f"não foi possível abrir o vídeo: {caminho}")
        self.cap = cap

    def ler(self) -> np.ndarray:
        ok, frame = self.cap.read()
        if not ok or frame is None:
            raise FimDoVideo("fim do arquivo de vídeo")
        return frame

    def liberar(self) -> None:
        if self.cap is not None:
            self.cap.release()
            self.cap = None


class DummySource(FonteVideo):
    """Fonte sintética: fundo + um bloco em movimento. Sem hardware."""

    def __init__(self, largura: int = 640, altura: int = 480, total: int = 100) -> None:
        self.largura = largura
        self.altura = altura
        self.total = total
        self.i = 0

    def ler(self) -> np.ndarray:
        if self.i >= self.total:
            raise FimDoVideo("fim da fonte dummy")
        self.i += 1
        frame = np.full((self.altura, self.largura, 3), (40, 30, 20), dtype=np.uint8)
        x = int((self.i * 7) % max(1, self.largura - 60))
        frame[self.altura // 2 - 30 : self.altura // 2 + 30, x : x + 60] = (200, 200, 200)
        return frame


def criar_fonte(source: str, largura: int = 640, altura: int = 480) -> FonteVideo:
    """Fábrica: ``"dummy"`` -> sintética; dígito -> webcam; caso contrário -> arquivo."""
    if source == "dummy":
        return DummySource(largura, altura)
    if source.isdigit():
        return WebcamSource(int(source), largura, altura)
    return FileSource(source)
