# 🎬 Roteiro do vídeo — Sentinela de Solo (máx. 3 min)

Vídeo de **até 3 minutos (180s)**. Demo **só com webcam + Python** (Arduino é
opcional — apenas mencione). O HUD já mostra **FPS**, estado e ocupação.

> Antes de gravar: deixe o programa pronto (`python main.py`) e o `main.py`/
> `fall_detector.py` abertos para um flash do código. Grave a tela + narre.

| ⏱️ Tempo | Cena | O que mostrar / narrar |
|---|---|---|
| **0:00–0:20** | **Abertura** | Integrantes (nome + RM). "Sentinela de Solo: o nó terrestre da Sentinela Orbital. Ondas de calor matam, sobretudo idosos em abrigos — a webcam avisa quando alguém cai/desmaia." |
| **0:20–0:45** | **Arquitetura** | Mostre o diagrama do README. Em 2 frases: "MediaPipe dá a pose; medimos a inclinação do tronco para saber se a pessoa caiu; só disparamos o ALERTA se ela ficar caída por alguns segundos. Rostos contam a ocupação." Cite o `requirements.txt` (reprodutível). |
| **0:45–1:40** | **Demo ao vivo + FPS** | Rode `python main.py`. Mostre o esqueleto e o **FPS** no canto, estado **NORMAL** (verde). Fique em pé → sente → **deite no chão**: aparece **SUSPEITA** (laranja) e depois **ALERTA: PESSOA CAÍDA** (moldura vermelha). Levante → volta a **NORMAL**. Chame outra pessoa → a **OCUPAÇÃO** sobe. |
| **1:40–2:25** | **Robustez** (vale nota!) | (a) **Iluminação**: reduza a luz / use lanterna — segue detectando. (b) **Oclusão**: passe um objeto na frente por 1–2 s — graças à **carência temporal**, o alerta não pisca nem cai. (c) Mencione que a confirmação por tempo evita **falso positivo**. |
| **2:25–2:50** | **Código + testes** | Flash de 1 trecho comentado (ex.: tratamento de exceção do stream em `video_source.py`). Rode `python -m unittest discover -s tests -v` → **27 testes passando**. |
| **2:50–3:00** | **Fecho** | "Do espaço ao chão, a Sentinela cuida das pessoas no calor extremo." Mostre o link do repositório. |

---

### Precisa aparecer (checklist)
- [ ] Integrantes · [ ] Arquitetura · [ ] Script **rodando** · [ ] **FPS** visível
- [ ] Queda: NORMAL → SUSPEITA → ALERTA · [ ] Robustez (luz/oclusão)
- [ ] Testes passando

### Dicas para caber em 3 min
- Ensaie a queda 1×: deite e **conte 2–3 s** parado para confirmar o ALERTA.
- Deixe `seg_confirmar_queda` em ~2 s (padrão) para o alerta sair rápido na gravação.
- Corte tempos mortos na edição; narre por cima da tela.
- Arduino é opcional: se não for usar, diga "em produção, esse estado aciona o LED/buzzer e recebe RFID/proximidade".
