"""Smoke test de integração: roda o pipeline completo (MediaPipe + OpenCV)
sobre frames sintéticos, em modo headless, sem câmera nem Arduino.

Garante que captura -> pose -> postura -> queda -> ocupação -> atuação -> loop
se integram sem erro. Não precisa de hardware.
"""

import unittest

from sentinela_solo.app import App
from sentinela_solo.config import Config


class TestSmokePipeline(unittest.TestCase):
    def test_pipeline_roda_em_fonte_sintetica(self):
        cfg = Config(source="dummy", mostrar_video=False, serial_port=None)
        app = App(cfg)
        # não deve levantar exceção ao processar alguns frames
        app.run(max_frames=8)
        self.assertGreaterEqual(app._frame_idx, 8)


if __name__ == "__main__":
    unittest.main()
