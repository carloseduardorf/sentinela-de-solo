"""Testes da máquina de estados de queda (debounce + carência)."""

import unittest

from sentinela_solo.fall_detector import DetectorQueda, EstadoMonitor
from sentinela_solo.posture import Postura


class TestDetectorQueda(unittest.TestCase):
    def setUp(self):
        self.d = DetectorQueda(seg_confirmar_queda=2.0, grace=0.7)

    def test_em_pe_e_normal(self):
        self.assertEqual(self.d.atualizar(Postura.VERTICAL, agora=0.0), EstadoMonitor.NORMAL)

    def test_sem_leitura_e_sem_pessoa(self):
        self.assertEqual(self.d.atualizar(None, agora=0.0), EstadoMonitor.SEM_PESSOA)

    def test_queda_so_confirma_apos_o_tempo(self):
        # deitou agora -> apenas SUSPEITA
        self.assertEqual(self.d.atualizar(Postura.HORIZONTAL, agora=0.0), EstadoMonitor.SUSPEITA)
        self.assertEqual(self.d.atualizar(Postura.HORIZONTAL, agora=1.0), EstadoMonitor.SUSPEITA)
        # passou de 2 s deitado -> ALERTA
        self.assertEqual(self.d.atualizar(Postura.HORIZONTAL, agora=2.1), EstadoMonitor.ALERTA)

    def test_carencia_tolera_falha_breve_de_deteccao(self):
        self.d.atualizar(Postura.HORIZONTAL, agora=0.0)
        self.d.atualizar(Postura.HORIZONTAL, agora=1.0)
        # oclusão breve (sem leitura) dentro da carência: não zera o cronômetro
        self.d.atualizar(None, agora=1.2)
        self.assertEqual(self.d.atualizar(Postura.HORIZONTAL, agora=2.1), EstadoMonitor.ALERTA)

    def test_levantar_apos_a_carencia_reseta(self):
        self.d.atualizar(Postura.HORIZONTAL, agora=0.0)
        self.d.atualizar(Postura.HORIZONTAL, agora=2.1)  # ALERTA
        # ficou em pé bem depois da carência -> volta ao normal
        self.assertEqual(self.d.atualizar(Postura.VERTICAL, agora=5.0), EstadoMonitor.NORMAL)


if __name__ == "__main__":
    unittest.main()
