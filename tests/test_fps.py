"""Testes do medidor de FPS (relógio injetável)."""

import unittest

from sentinela_solo.fps import MedidorFPS


class TestFPS(unittest.TestCase):
    def test_primeira_marca_e_zero(self):
        self.assertEqual(MedidorFPS().marcar(agora=0.0), 0.0)

    def test_um_frame_por_segundo(self):
        m = MedidorFPS()
        m.marcar(agora=0.0)
        self.assertAlmostEqual(m.marcar(agora=1.0), 1.0, places=6)

    def test_suavizacao_exponencial(self):
        m = MedidorFPS(suavizacao=0.9)
        m.marcar(agora=0.0)
        m.marcar(agora=1.0)            # fps = 1.0
        fps = m.marcar(agora=1.5)      # inst = 2.0 -> ema = 0.9*1 + 0.1*2 = 1.1
        self.assertAlmostEqual(fps, 1.1, places=6)


if __name__ == "__main__":
    unittest.main()
