"""Atuação física no Arduino (camada de IoT / physical computing).

A Sentinela de Solo conversa com um Arduino por **serial**:

- Python -> Arduino:  ``CMD:<ESTADO>:<NIVEL>\\n``  (aciona LED RGB e buzzer)
- Arduino -> Python:  ``EVT:RFID:<uid>\\n`` · ``EVT:PROX:IN\\n`` · ``EVT:PROX:OUT\\n``

As funções de protocolo são puras (testáveis). ``ArduinoActuator`` recebe o
objeto serial por injeção (um ``FakeSerial`` é usado nos testes), e
``NullActuator`` é o fallback quando não há hardware — assim o sistema **nunca
quebra** por ausência de Arduino.
"""

from __future__ import annotations

from typing import Protocol


# ----- protocolo (funções puras) -----
def montar_comando(estado_nome: str, nivel_nome: str) -> bytes:
    """Monta a linha de comando enviada ao Arduino."""
    return f"CMD:{estado_nome}:{nivel_nome}\n".encode("ascii")


def parse_evento(linha: str) -> tuple[str, str] | None:
    """Interpreta uma linha vinda do Arduino. Retorna (tipo, valor) ou None."""
    linha = linha.strip()
    if not linha.startswith("EVT:"):
        return None
    partes = linha.split(":", 2)
    if len(partes) < 3:
        return None
    _, tipo, valor = partes
    if tipo in ("RFID", "PROX"):
        return tipo, valor
    return None


# ----- interface -----
class Atuador(Protocol):
    def aplicar(self, estado_nome: str, nivel_nome: str) -> None: ...
    def ler_eventos(self) -> list[tuple[str, str]]: ...
    def fechar(self) -> None: ...


class NullActuator:
    """Fallback sem hardware: registra o último comando, não emite eventos."""

    def __init__(self) -> None:
        self.ultimo_comando: bytes | None = None

    def aplicar(self, estado_nome: str, nivel_nome: str) -> None:
        self.ultimo_comando = montar_comando(estado_nome, nivel_nome)

    def ler_eventos(self) -> list[tuple[str, str]]:
        return []

    def fechar(self) -> None:
        pass


class ArduinoActuator:
    """Atuador real via serial. O objeto ``ser`` é injetado (pyserial ou fake)."""

    def __init__(self, ser) -> None:
        self._ser = ser
        self._buffer = b""

    @classmethod
    def abrir(cls, port: str, baud: int = 115200, timeout: float = 0.05) -> "ArduinoActuator":
        import serial  # import tardio: só exige pyserial quando há hardware
        return cls(serial.Serial(port, baud, timeout=timeout))

    def aplicar(self, estado_nome: str, nivel_nome: str) -> None:
        self._ser.write(montar_comando(estado_nome, nivel_nome))

    def ler_eventos(self) -> list[tuple[str, str]]:
        """Lê linhas disponíveis sem bloquear e devolve os eventos válidos."""
        dados = self._ser.read(256)
        if dados:
            self._buffer += dados
        eventos: list[tuple[str, str]] = []
        while b"\n" in self._buffer:
            linha, self._buffer = self._buffer.split(b"\n", 1)
            ev = parse_evento(linha.decode("ascii", errors="ignore"))
            if ev is not None:
                eventos.append(ev)
        return eventos

    def fechar(self) -> None:
        try:
            self._ser.close()
        except Exception:
            pass


def criar_atuador(serial_port: str | None, baud: int = 115200) -> Atuador:
    """Fábrica: tenta o Arduino; em qualquer falha, cai para o NullActuator."""
    if not serial_port:
        return NullActuator()
    try:
        return ArduinoActuator.abrir(serial_port, baud)
    except Exception as e:  # porta inexistente, pyserial ausente, etc.
        print(f"[atuador] Arduino indisponível ({e}); seguindo sem hardware.")
        return NullActuator()
