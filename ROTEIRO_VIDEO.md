# 🎬 Roteiro do vídeo — Sentinela de Solo (50 pts)

Vídeo sugerido de **4 a 6 minutos**. Critérios cobertos: contextualização +
recursos visuais, explicação da arquitetura, **script em execução**, **FPS** e
**robustez** (iluminação, ruído, oclusão parcial).

> Dica: grave a tela mostrando a janela do programa (o HUD já mostra FPS, estado
> e ocupação). Tenha o `main.py` aberto ao lado para mostrar o código.

---

## Cena 1 — Contexto (≈45 s)
- Apresentem os integrantes (nome + RM).
- Problema: ondas de calor matam, sobretudo idosos em abrigos. Mostre 1–2 imagens
  de apoio (mapa de calor, abrigo climático).
- Ideia: **Sentinela de Solo**, o nó terrestre da **Sentinela Orbital** — a
  webcam vigia o abrigo e avisa quando alguém cai/desmaia.

## Cena 2 — Arquitetura (≈60 s)
- Mostre o **diagrama** do README (captura → MediaPipe Pose → postura → queda;
  faces → ocupação; serial → Arduino LED/buzzer).
- Explique o pipeline em 3 frases: "pegamos a pose com o MediaPipe, medimos a
  inclinação do tronco para saber se a pessoa está em pé ou caída, e só
  disparamos o alerta se ela continuar caída por alguns segundos".
- Mostre rapidamente a **estrutura de pastas** (modularização) e o
  `requirements.txt` (reprodutibilidade).

## Cena 3 — Script em execução + FPS (≈90 s)
- Rode `python main.py`. Mostre a janela com o **esqueleto**, o **FPS** no canto
  e o estado **NORMAL** (verde).
- Fique em pé → sente → **deite/desabe no chão**. Narre: "veja que ao deitar,
  entra em **SUSPEITA** (laranja) e, após o tempo de confirmação, dispara o
  **ALERTA: PESSOA CAÍDA** (vermelho)". Mostre a moldura vermelha e a faixa de
  alerta. (Se tiver Arduino: mostre o LED ficar vermelho e o buzzer apitar.)
- Levante-se → o sistema volta ao **NORMAL**.

## Cena 4 — Ocupação + Arduino (≈45 s)
- Chame outra pessoa para o quadro → mostre a **OCUPAÇÃO** subir e o nível mudar.
- (Com hardware) aproxime um **cartão RFID** → mostre o check-in; aproxime a mão
  do **sensor de proximidade** → mostre a contagem na porta.
- (Sem hardware) explique que o sistema usa o **fallback** e roda igual.

## Cena 5 — Robustez (intempéries) (≈60 s) — IMPORTANTE p/ nota
- **Iluminação:** apague parte das luzes / acenda uma lanterna; mostre que a
  pose continua sendo detectada.
- **Oclusão parcial:** passe um objeto na frente de parte do corpo por 1–2 s;
  destaque que, graças à **janela de carência**, o alerta **não pisca/cai** com
  um frame ruim.
- **Ruído:** aproxime-se/afaste-se rápido; mostre que não há falso positivo
  (a confirmação por tempo evita disparos indevidos).

## Cena 6 — Código + testes (≈40 s)
- Mostre 1 trecho de código bem comentado (ex.: `fall_detector.py` ou
  `video_source.py` com o tratamento de exceções do stream).
- Rode `python -m unittest discover -s tests -v` e mostre **27 testes passando**.

## Cena 7 — Fecho (≈20 s)
- Reforce o impacto: "do espaço ao chão, a Sentinela cuida das pessoas durante o
  calor extremo". Mostre o link do repositório.

---

### Checklist do que PRECISA aparecer no vídeo
- [ ] Nome dos integrantes
- [ ] Diagrama/arquitetura explicada
- [ ] Script **rodando** ao vivo
- [ ] **FPS** visível
- [ ] Detecção de queda funcionando (NORMAL → SUSPEITA → ALERTA)
- [ ] Robustez: **iluminação**, **oclusão** e/ou **ruído**
- [ ] (Bônus) Arduino reagindo (LED/buzzer) e/ou RFID/proximidade
- [ ] Testes passando
