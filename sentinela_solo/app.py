"""Loop principal — integra captura, visão, lógica e atuação.

Responsável pela **eficiência** (faces a cada N frames, atuação só na mudança de
estado) e pela **robustez** do stream: quedas de frame e falhas de hardware são
tratadas com reconexão; Ctrl+C encerra liberando todos os recursos.
"""

from __future__ import annotations

import time

import cv2

from .actuator import criar_atuador
from .config import Config
from .face_engine import MotorFaces
from .fall_detector import DetectorQueda, EstadoMonitor
from .fps import MedidorFPS
from .occupancy import Ocupacao
from .overlay import desenhar_hud
from .pose_engine import MotorPose
from .posture import classificar
from .video_source import (ErroCamera, FimDoVideo, QuedaDeFrame, criar_fonte)

INTERVALO_FACES = 5  # roda detecção de faces a cada N frames (economia de CPU)


class App:
    def __init__(self, config: Config) -> None:
        self.cfg = config
        self.fonte = criar_fonte(config.source, config.largura, config.altura)
        self.motor_pose = MotorPose()
        self.motor_faces = MotorFaces()
        self.detector = DetectorQueda(
            seg_confirmar_queda=config.seg_confirmar_queda,
            seg_imovel=config.seg_imovel,
            limiar_movimento=config.limiar_movimento,
        )
        self.ocupacao = Ocupacao(config.capacidade, config.fracao_alerta_lotacao)
        self.atuador = criar_atuador(config.serial_port, config.baud)
        self.fps = MedidorFPS()
        self._ultimo_cmd: tuple[str, str] | None = None
        self._n_faces = 0
        self._falhas = 0
        self._frame_idx = 0

    # ---- captura robusta ----
    def _tentar_reabrir(self) -> bool:
        for tentativa in range(1, self.cfg.max_reconexoes + 1):
            print(f"[captura] reabrindo o stream ({tentativa}/{self.cfg.max_reconexoes})...")
            try:
                self.fonte.reabrir()
                return True
            except ErroCamera:
                time.sleep(0.5)
        return False

    def _capturar(self):
        """Lê um frame tratando queda de frame e falha de hardware. None => pular."""
        try:
            frame = self.fonte.ler()
            self._falhas = 0
            return frame
        except QuedaDeFrame:
            self._falhas += 1
            print(f"[captura] queda de frame ({self._falhas}/{self.cfg.max_reconexoes})")
            if self._falhas >= self.cfg.max_reconexoes and not self._tentar_reabrir():
                raise ErroCamera("stream irrecuperável após várias quedas")
            return None
        except ErroCamera as e:
            print(f"[captura] falha de hardware: {e}")
            if not self._tentar_reabrir():
                raise
            return None

    # ---- processamento de um frame ----
    def _processar(self, frame):
        if self.cfg.espelhar:
            frame = cv2.flip(frame, 1)

        pose = self.motor_pose.processar(frame)
        if pose is not None:
            rp = classificar(
                pose, limiar_vertical=self.cfg.limiar_vertical,
                limiar_horizontal=self.cfg.limiar_horizontal, vis_min=self.cfg.vis_min,
            )
            postura, centro = rp.postura, pose.centro(self.cfg.vis_min)
        else:
            postura, centro = None, None

        estado = self.detector.atualizar(postura, centro=centro)

        # ocupação: visão (a cada N frames) + eventos físicos do Arduino
        if self._frame_idx % INTERVALO_FACES == 0:
            try:
                self._n_faces = self.motor_faces.contar(frame)
            except Exception:
                pass
        self.ocupacao.atualizar_visao(self._n_faces)
        for tipo, valor in self.atuador.ler_eventos():
            if tipo == "RFID":
                self.ocupacao.check_in_rfid(valor)
            elif tipo == "PROX":
                self.ocupacao.entrada() if valor == "IN" else self.ocupacao.saida()

        nivel = self.ocupacao.nivel()

        # atua só quando o estado muda (não inunda a serial)
        cmd = (estado.name, nivel.name)
        if cmd != self._ultimo_cmd:
            self.atuador.aplicar(estado.name, nivel.name)
            self._ultimo_cmd = cmd
            if estado == EstadoMonitor.ALERTA:
                print(f"[ALERTA] pessoa caida ha {self.detector.segundos_caido:.1f}s -> acionando alerta")

        fps = self.fps.marcar()
        if self.cfg.mostrar_video:
            desenhar_hud(
                frame, fps=fps, estado=estado, segundos_caido=self.detector.segundos_caido,
                nivel=nivel, ocupacao_estimativa=self.ocupacao.estimativa,
                capacidade=self.cfg.capacidade, landmarks=pose, n_faces=self._n_faces,
                imovel=self.detector.imovel,
            )
            cv2.imshow("Sentinela de Solo", frame)
            if (cv2.waitKey(1) & 0xFF) in (ord("q"), 27):
                return False
        return True

    # ---- loop ----
    def run(self, max_frames: int | None = None) -> None:
        print("[app] Sentinela de Solo iniciada. (q/ESC para sair)")
        try:
            while True:
                self._frame_idx += 1
                if max_frames is not None and self._frame_idx > max_frames:
                    break
                try:
                    frame = self._capturar()
                except ErroCamera as e:
                    print(f"[app] encerrando: {e}")
                    break
                if frame is None:
                    continue
                try:
                    if self._processar(frame) is False:
                        break
                except FimDoVideo:
                    break
                except Exception as e:  # robustez: um frame ruim não derruba o serviço
                    print(f"[app] erro ao processar frame {self._frame_idx}: {e}")
                    continue
        except KeyboardInterrupt:
            print("\n[app] interrompido pelo usuario (Ctrl+C).")
        finally:
            self._encerrar()

    def _encerrar(self) -> None:
        print("[app] liberando recursos...")
        try:
            self.atuador.aplicar(EstadoMonitor.SEM_PESSOA.name, "OK")  # apaga LED/buzzer
        except Exception:
            pass
        self.fonte.liberar()
        self.motor_pose.fechar()
        self.motor_faces.fechar()
        self.atuador.fechar()
        if self.cfg.mostrar_video:
            cv2.destroyAllWindows()
        print("[app] finalizado.")
