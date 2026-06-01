"""Testes do controle de ocupação."""

import unittest

from sentinela_solo.occupancy import Nivel, Ocupacao


class TestOcupacao(unittest.TestCase):
    def setUp(self):
        self.o = Ocupacao(capacidade=10, fracao_alerta=0.9)

    def test_entrada_e_saida(self):
        self.o.entrada(); self.o.entrada()
        self.assertEqual(self.o.contagem, 2)
        self.o.saida()
        self.assertEqual(self.o.contagem, 1)
        self.o.saida(); self.o.saida()  # não fica negativo
        self.assertEqual(self.o.contagem, 0)

    def test_check_in_rfid_conta_uma_vez(self):
        self.assertTrue(self.o.check_in_rfid("CARD-1"))
        self.assertFalse(self.o.check_in_rfid("CARD-1"))  # repetido não conta
        self.assertEqual(self.o.contagem, 1)

    def test_estimativa_usa_maior_fonte(self):
        self.o.entrada(2)
        self.o.atualizar_visao(5)
        self.assertEqual(self.o.estimativa, 5)

    def test_niveis(self):
        self.o.atualizar_visao(3)
        self.assertEqual(self.o.nivel(), Nivel.OK)
        self.o.atualizar_visao(9)  # ceil(0.9*10)=9 -> ALTA
        self.assertEqual(self.o.nivel(), Nivel.ALTA)
        self.o.atualizar_visao(10)
        self.assertEqual(self.o.nivel(), Nivel.LOTADO)


if __name__ == "__main__":
    unittest.main()
