# Sentinela de Solo — Visão Computacional (GS Physical Computing · IoT & IoB)

## Integrantes do grupo

| Nome | RM |
|---|---|
| Carlos Eduardo | 556785 |
| Giulia Rocha | 558084 |
| Caio Rossini | 555084 |
| Gabriel Danius | 555747 |

---

**Sentinela de Solo** é o **nó terrestre (edge)** da plataforma **Sentinela Orbital**
(nossa GS de monitoramento de ondas de calor extremo). Enquanto a Sentinela
Orbital enxerga o calor **do espaço**, a Sentinela de Solo cuida das **pessoas no
chão**: instalada em **abrigos climáticos / pontos de hidratação** durante uma
onda de calor, usa uma **webcam** + **visão computacional** para detectar quem
precisa de ajuda e acionar um **alerta físico** (Arduino).

> Pipeline de inferência 100% em **Python**, com **MediaPipe** + **OpenCV**, e
> integração física via **Arduino** (RFID, proximidade, buzzer/LED).

---

## 🎯 Objetivo

**De negócio:** ondas de calor matam de forma silenciosa, sobretudo idosos e
pessoas vulneráveis em abrigos. A Sentinela de Solo dá **olhos** ao abrigo:
avisa em segundos quando alguém **cai/desmaia** (possível insolação) e mede a
**ocupação** do espaço — reduzindo tempo de socorro e apoiando a Defesa Civil.

**Técnico:** demonstrar um pipeline de **visão computacional em tempo real**
robusto e eficiente, que (1) estima a **pose** humana, (2) classifica **postura**
e detecta **queda** com anti-falso-positivo, (3) **conta pessoas** para ocupação,
e (4) integra **sensores/atuadores físicos** (IoT) com tratamento de falhas.

---

## 🧠 Lógica da solução (arquitetura)

```
            +-------------------- SENTINELA DE SOLO (edge) --------------------+
  WEBCAM -->| Captura (OpenCV)  ->  MediaPipe Pose  ->  Postura  ->  Queda     |
            |        |                    |              (ângulo)   (estados)  |
            |        |              MediaPipe Faces  ->  Ocupação              |
            |        |                                      ^                  |
            |   tratamento de                               | eventos         |
            |   exceções no stream                          |                 |
            +----------------------------|------------------|-----------------+
                                          |  serial (USB)    |
                                          v                  |
                            ARDUINO: LED RGB + buzzer   <-----+----- RFID + HC-SR04
                            (verde/amarelo/vermelho)        (check-in / fluxo na porta)
                                          |
                                          v
                            Alerta -> Defesa Civil / Saúde (plataforma Sentinela)
```

**Estados do monitor:** `SEM_PESSOA → NORMAL → SUSPEITA → ALERTA`
**Níveis de ocupação:** `OK → LOTAÇÃO ALTA → LOTADO`

---

## 🔬 Pipeline de Visão Computacional (passo a passo)

1. **Captura** (`video_source.py`): `cv2.VideoCapture` lê frames da webcam. Há
   tratamento explícito de **queda de frame** e **falha de hardware** (reconexão).
2. **Pré-processamento**: espelhamento e conversão BGR→RGB.
3. **Estimativa de pose** (`pose_engine.py`): **MediaPipe Pose** devolve 33
   landmarks normalizados (x, y, z, visibilidade).
4. **Desacoplamento** (`landmarks.py`): os landmarks viram uma estrutura própria
   — o resto do código não depende do MediaPipe (e fica testável).
5. **Classificação de postura** (`posture.py`): mede a **inclinação do tronco**
   (vetor ombros→quadril) em relação à vertical. ~0° = em pé/sentado; ~90° =
   deitado/caído. A razão da caixa delimitadora desempata a faixa intermediária.
6. **Detecção de queda** (`fall_detector.py`): máquina de estados com **debounce
   temporal** — uma queda só é confirmada se a postura horizontal **persistir**
   (`seg_confirmar_queda`); uma **janela de carência** tolera oclusão/ruído sem
   gerar falso positivo nem perder o alerta. Também monitora **imobilidade**.
7. **Ocupação** (`face_engine.py` + `occupancy.py`): **MediaPipe Face Detection**
   conta rostos (a cada N frames, por eficiência) e combina com a contagem
   física dos sensores (RFID/proximidade) → nível de lotação.
8. **Atuação + HUD** (`actuator.py`, `overlay.py`): o estado vira comando serial
   para o Arduino (LED/buzzer) e um HUD com **FPS**, estado, ocupação e esqueleto
   é desenhado no frame.

### Robustez e eficiência (critérios do vídeo)
- **Iluminação:** o MediaPipe Pose é robusto a variações de luz; testado em
  ambiente claro e escuro.
- **Oclusão parcial / ruído:** a **carência temporal** do detector evita que um
  frame ruim derrube o alerta; a confirmação por tempo evita falsos positivos.
- **FPS exibido** no HUD; detecção de faces a cada *N* frames e atuação **só na
  mudança de estado** mantêm o loop leve.

---

## 🧰 Stack (bibliotecas)

| Biblioteca | Versão | Para quê |
|---|---|---|
| **mediapipe** | 0.10.21 | Pose (33 landmarks) e Face Detection |
| **opencv-contrib-python** | 4.11.0.86 | Captura, conversão e desenho do HUD |
| **numpy** | 1.26.4 | Operações com os landmarks |
| **pyserial** | 3.5 | Comunicação serial com o Arduino |

> Dependências **exatas** (incl. transitivas) estão em [`requirements.txt`](requirements.txt).
> Usamos `opencv-contrib-python` (não `opencv-python`) para evitar conflito de
> versão do NumPy com o MediaPipe 0.10.21.

**Hardware (físico):** Arduino UNO · módulo **RFID-RC522** · sensor ultrassônico
**HC-SR04** · LED RGB · buzzer. Firmware em [`arduino/sentinela_solo.ino`](arduino/sentinela_solo.ino).

---

## 📁 Estrutura

```
sentinela-de-solo/
├── main.py                     ponto de entrada (argparse)
├── requirements.txt            dependências exatas (reprodutibilidade)
├── sentinela_solo/
│   ├── config.py               parâmetros do pipeline
│   ├── video_source.py         captura robusta (webcam/arquivo/dummy) + exceções
│   ├── pose_engine.py          wrapper MediaPipe Pose
│   ├── face_engine.py          wrapper MediaPipe Face Detection
│   ├── landmarks.py            estrutura de pose (desacopla do MediaPipe)
│   ├── posture.py              classificação de postura (lógica pura)
│   ├── fall_detector.py        máquina de estados de queda (debounce)
│   ├── occupancy.py            ocupação (visão + sensores)
│   ├── actuator.py             Arduino via serial (+ fallback sem hardware)
│   ├── fps.py                  medidor de FPS
│   ├── overlay.py              HUD desenhado no frame
│   └── app.py                  loop principal (integra tudo)
├── arduino/sentinela_solo.ino  firmware (RFID + proximidade + LED/buzzer)
└── tests/                      27 testes (unittest) — lógica + smoke do pipeline
```

---

## ▶️ Instruções de execução

> Requer **Python 3.12** e uma **webcam**. (Sem webcam? Use `--source dummy`.)

```bash
# 1) Clonar
git clone https://github.com/carloseduardorf/sentinela-de-solo.git
cd sentinela-de-solo

# 2) Ambiente virtual + dependências (reprodutível)
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt        # Windows
# source .venv/bin/activate && pip install -r requirements.txt # Linux/Mac

# 3) Rodar (webcam padrão, janela com HUD)
.venv\Scripts\python main.py

# Outras opções:
python main.py --source dummy --no-video --max-frames 30   # sem câmera (teste)
python main.py --serial-port COM3                          # com Arduino
python main.py --source video.mp4 --capacidade 30          # a partir de um vídeo
```

Atalhos na janela: **q** ou **ESC** encerram.

### Testes
```bash
.venv\Scripts\python -m unittest discover -s tests -v
```
Resultado esperado: **27 testes passando** (lógica de postura/queda/ocupação/
atuador/FPS/captura + smoke test do pipeline completo, tudo **sem hardware**).

---

## 🔌 Ligações do Arduino (resumo)

| Componente | Pinos (sugestão) |
|---|---|
| LED RGB | R=9, G=10, B=11 (PWM) |
| Buzzer | 8 |
| HC-SR04 (proximidade) | TRIG=6, ECHO=7 |
| RFID-RC522 | SS=A0, RST=A1, SPI (13/12/11) |

Protocolo serial: Python envia `CMD:<ESTADO>:<NIVEL>`; Arduino envia
`EVT:RFID:<uid>` e `EVT:PROX:IN`. Sem Arduino, o sistema roda igual (fallback).

## Link do Vídeo

https://youtu.be/q5bWXM_OX5E

---

## 🛰️ Relação com a Sentinela Orbital
Este projeto é a camada de **borda** da nossa GS de monitoramento de ondas de
calor: os dados de ocupação e os alertas de emergência alimentam a mesma
plataforma que processa os dados orbitais — do espaço ao chão.

## 📄 Licença
MIT — ver [LICENSE](LICENSE).
