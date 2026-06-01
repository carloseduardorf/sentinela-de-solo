"""Controle de ocupação do abrigo climático.

Combina duas fontes: a contagem por **eventos físicos** (sensor de proximidade
na porta e check-ins por RFID, vindos do Arduino) e a **estimativa por visão**
(pessoas/faces detectadas no frame). Lógica pura e testável.
"""

from __future__ import annotations

import math
from enum import Enum


class Nivel(Enum):
    OK = "ok"
    ALTA = "lotação alta"
    LOTADO = "lotado"


class Ocupacao:
    def __init__(self, capacidade: int = 20, fracao_alerta: float = 0.9) -> None:
        if capacidade <= 0:
            raise ValueError("capacidade deve ser > 0")
        self.capacidade = capacidade
        self.fracao_alerta = fracao_alerta
        self.contagem = 0            # por eventos de porta (proximidade/RFID)
        self.visao = 0               # estimativa por visão computacional
        self.checkins: set[str] = set()  # UIDs de RFID já registrados

    def entrada(self, n: int = 1) -> None:
        self.contagem = max(0, self.contagem + n)

    def saida(self, n: int = 1) -> None:
        self.contagem = max(0, self.contagem - n)

    def check_in_rfid(self, uid: str) -> bool:
        """Registra um check-in por RFID. Retorna True se for novo (conta como entrada)."""
        novo = uid not in self.checkins
        self.checkins.add(uid)
        if novo:
            self.entrada(1)
        return novo

    def atualizar_visao(self, n_pessoas: int) -> None:
        self.visao = max(0, int(n_pessoas))

    @property
    def estimativa(self) -> int:
        """Ocupação considerada = a maior entre contagem física e visão."""
        return max(self.contagem, self.visao)

    def nivel(self) -> Nivel:
        e = self.estimativa
        if e >= self.capacidade:
            return Nivel.LOTADO
        if e >= math.ceil(self.fracao_alerta * self.capacidade):
            return Nivel.ALTA
        return Nivel.OK
