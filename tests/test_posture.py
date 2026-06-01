"""Testes da classificação de postura (lógica pura)."""

import unittest

from sentinela_solo.posture import Postura, classificar
from tests import helpers


class TestPostura(unittest.TestCase):
    def test_pessoa_em_pe_e_vertical(self):
        r = classificar(helpers.verticais())
        self.assertEqual(r.postura, Postura.VERTICAL)
        self.assertLess(r.inclinacao_graus, 35.0)

    def test_pessoa_caida_e_horizontal(self):
        r = classificar(helpers.horizontais())
        self.assertEqual(r.postura, Postura.HORIZONTAL)
        self.assertGreater(r.inclinacao_graus, 55.0)

    def test_sem_pontos_visiveis_e_indefinido(self):
        r = classificar(helpers.invisiveis())
        self.assertEqual(r.postura, Postura.INDEFINIDO)
        self.assertIsNone(r.inclinacao_graus)


if __name__ == "__main__":
    unittest.main()
