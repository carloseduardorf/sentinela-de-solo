/*
 * Sentinela de Solo — firmware do nó físico (Arduino UNO)
 * ---------------------------------------------------------
 * Camada de physical computing da solução de visão computacional.
 *
 * Conversa com o Python por SERIAL (115200 bps):
 *   Recebe:  CMD:<ESTADO>:<NIVEL>\n
 *            ESTADO em {SEM_PESSOA, NORMAL, SUSPEITA, ALERTA}
 *            NIVEL  em {OK, ALTA, LOTADO}
 *   Envia:   EVT:RFID:<uid>\n        (check-in de pessoa cadastrada)
 *            EVT:PROX:IN\n           (alguém detectado na porta)
 *
 * Atuadores: LED RGB (estado do abrigo) + buzzer (alerta de queda).
 * Sensores:  RFID MFRC522 (check-in) + ultrassônico HC-SR04 (fluxo na porta).
 *
 * Ligações (sugestão):
 *   LED RGB:    R=9, G=10, B=11  (PWM, com resistores)
 *   Buzzer:     8
 *   HC-SR04:    TRIG=6, ECHO=7
 *   MFRC522:    SDA/SS=10? -> use SS=A0 p/ não colidir; RST=A1; SPI: 13/12/11
 *               (ajuste conforme seu shield)
 */

#include <SPI.h>
#include <MFRC522.h>

// ---- pinos ----
const uint8_t PIN_R = 9, PIN_G = 10, PIN_B = 11;   // LED RGB (PWM)
const uint8_t PIN_BUZZER = 8;
const uint8_t PIN_TRIG = 6, PIN_ECHO = 7;          // HC-SR04
const uint8_t PIN_SS = A0, PIN_RST = A1;           // MFRC522

MFRC522 rfid(PIN_SS, PIN_RST);

// ---- estado recebido do Python ----
String estado = "SEM_PESSOA";
String nivel  = "OK";

// ---- controle de presença (HC-SR04) ----
const float LIMIAR_CM = 80.0;   // < isso = alguém na porta
bool presencaAnterior = false;
unsigned long ultimaLeituraProx = 0;

void setRGB(uint8_t r, uint8_t g, uint8_t b) {
  analogWrite(PIN_R, r); analogWrite(PIN_G, g); analogWrite(PIN_B, b);
}

float medirDistanciaCm() {
  digitalWrite(PIN_TRIG, LOW);  delayMicroseconds(2);
  digitalWrite(PIN_TRIG, HIGH); delayMicroseconds(10);
  digitalWrite(PIN_TRIG, LOW);
  unsigned long dur = pulseIn(PIN_ECHO, HIGH, 30000UL); // timeout 30 ms
  if (dur == 0) return 9999.0;                          // sem eco
  return dur / 58.0;                                    // us -> cm
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_R, OUTPUT); pinMode(PIN_G, OUTPUT); pinMode(PIN_B, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);
  pinMode(PIN_TRIG, OUTPUT); pinMode(PIN_ECHO, INPUT);
  SPI.begin();
  rfid.PCD_Init();
  setRGB(0, 0, 0);
}

void aplicarAtuadores() {
  // Prioridade: ALERTA de queda > lotação > estado normal.
  if (estado == "ALERTA") {
    setRGB(255, 0, 0);                       // vermelho
    tone(PIN_BUZZER, 1000);                  // buzzer contínuo
  } else if (estado == "SUSPEITA") {
    setRGB(255, 120, 0);                     // laranja (verificando)
    noTone(PIN_BUZZER);
  } else if (nivel == "LOTADO") {
    setRGB(255, 0, 0); noTone(PIN_BUZZER);   // vermelho de lotação
  } else if (nivel == "ALTA") {
    setRGB(255, 200, 0); noTone(PIN_BUZZER); // amarelo
  } else if (estado == "NORMAL") {
    setRGB(0, 180, 0); noTone(PIN_BUZZER);   // verde
  } else {                                   // SEM_PESSOA
    setRGB(0, 0, 0); noTone(PIN_BUZZER);
  }
}

void lerComandoSerial() {
  // Formato: CMD:ESTADO:NIVEL
  String linha = Serial.readStringUntil('\n');
  linha.trim();
  if (!linha.startsWith("CMD:")) return;
  int p1 = linha.indexOf(':');
  int p2 = linha.indexOf(':', p1 + 1);
  if (p2 < 0) return;
  estado = linha.substring(p1 + 1, p2);
  nivel  = linha.substring(p2 + 1);
}

void checarProximidade() {
  if (millis() - ultimaLeituraProx < 120) return; // ~8 Hz
  ultimaLeituraProx = millis();
  bool presenca = medirDistanciaCm() < LIMIAR_CM;
  if (presenca && !presencaAnterior) {
    Serial.println("EVT:PROX:IN");            // borda de subida = alguém chegou
  }
  presencaAnterior = presenca;
}

void checarRFID() {
  if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) return;
  String uid = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    if (rfid.uid.uidByte[i] < 0x10) uid += "0";
    uid += String(rfid.uid.uidByte[i], HEX);
  }
  uid.toUpperCase();
  Serial.print("EVT:RFID:");
  Serial.println(uid);
  rfid.PICC_HaltA();
}

void loop() {
  if (Serial.available()) lerComandoSerial();
  checarProximidade();
  checarRFID();
  aplicarAtuadores();
}
