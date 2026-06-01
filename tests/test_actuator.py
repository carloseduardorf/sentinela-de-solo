"""Testes do atuador (protocolo serial + fallback), sem hardware real."""

import unittest

from sentinela_solo.actuator import (ArduinoActuator, NullActuator, criar_atuador,
                                      montar_comando, parse_evento)


class FakeSerial:
    """Serial em memória para testar o ArduinoActuator sem hardware."""

    def __init__(self, entrada: bytes = b""):
        self.saida = b""
        self._entrada = entrada
        self.fechado = False

    def write(self, b):
        self.saida += b
        return len(b)

    def read(self, n):
        chunk, self._entrada = self._entrada[:n], self._entrada[n:]
        return chunk

    def close(self):
        self.fechado = True


class TestProtocolo(unittest.TestCase):
    def test_montar_comando(self):
        self.assertEqual(montar_comando("ALERTA", "ALTA"), b"CMD:ALERTA:ALTA\n")

    def test_parse_evento(self):
        self.assertEqual(parse_evento("EVT:RFID:ABC123"), ("RFID", "ABC123"))
        self.assertEqual(parse_evento("EVT:PROX:IN"), ("PROX", "IN"))
        self.assertIsNone(parse_evento("linha qualquer"))
        self.assertIsNone(parse_evento("EVT:DESCONHECIDO:x"))


class TestArduinoActuator(unittest.TestCase):
    def test_aplicar_envia_comando(self):
        fake = FakeSerial()
        ArduinoActuator(fake).aplicar("ALERTA", "OK")
        self.assertEqual(fake.saida, b"CMD:ALERTA:OK\n")

    def test_ler_eventos(self):
        fake = FakeSerial(entrada=b"EVT:RFID:CARD-1\nEVT:PROX:IN\n")
        eventos = ArduinoActuator(fake).ler_eventos()
        self.assertEqual(eventos, [("RFID", "CARD-1"), ("PROX", "IN")])

    def test_ler_eventos_linha_parcial_aguarda(self):
        # sem '\n' ainda: nada é entregue até a linha completar
        atu = ArduinoActuator(FakeSerial(entrada=b"EVT:RFID:PARC"))
        self.assertEqual(atu.ler_eventos(), [])


class TestFallback(unittest.TestCase):
    def test_sem_porta_usa_null_actuator(self):
        atu = criar_atuador(None)
        self.assertIsInstance(atu, NullActuator)
        atu.aplicar("NORMAL", "OK")
        self.assertEqual(atu.ultimo_comando, b"CMD:NORMAL:OK\n")
        self.assertEqual(atu.ler_eventos(), [])

    def test_porta_invalida_cai_para_null(self):
        # porta inexistente -> fábrica não quebra, devolve NullActuator
        atu = criar_atuador("PORTA_INEXISTENTE_999")
        self.assertIsInstance(atu, NullActuator)


if __name__ == "__main__":
    unittest.main()
