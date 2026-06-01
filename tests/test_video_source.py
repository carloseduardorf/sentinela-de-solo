"""Testes da fonte de vídeo sintética (sem câmera)."""

import unittest

import numpy as np

from sentinela_solo.video_source import (DummySource, FimDoVideo, criar_fonte)


class TestDummySource(unittest.TestCase):
    def test_gera_frames_no_formato_certo(self):
        fonte = DummySource(largura=320, altura=240, total=3)
        frame = fonte.ler()
        self.assertEqual(frame.shape, (240, 320, 3))
        self.assertEqual(frame.dtype, np.uint8)

    def test_fim_do_video_apos_total(self):
        fonte = DummySource(total=2)
        fonte.ler(); fonte.ler()
        with self.assertRaises(FimDoVideo):
            fonte.ler()

    def test_fabrica_dummy(self):
        self.assertIsInstance(criar_fonte("dummy"), DummySource)

    def test_context_manager_libera(self):
        with DummySource(total=1) as fonte:
            self.assertIsNotNone(fonte.ler())


if __name__ == "__main__":
    unittest.main()
