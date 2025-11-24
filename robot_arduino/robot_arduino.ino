/*
 * Robot de Competición - Control Arduino
 * Modos: Seguimiento de Línea, Sumo, Control Manual
 * Control: Bluetooth (HC-05/HC-06)
 */

// ===== CONFIGURACIÓN DE PINES =====
// Motor Izquierdo
#define MOTOR_IZQ_A 5   // IN1
#define MOTOR_IZQ_B 6   // IN2
#define MOTOR_IZQ_PWM 9 // ENA

// Motor Derecho
#define MOTOR_DER_A 7   // IN3
#define MOTOR_DER_B 8   // IN4
#define MOTOR_DER_PWM 10 // ENB

// Sensores IR para seguimiento de línea
#define SENSOR_IZQ 2
#define SENSOR_CEN 3
#define SENSOR_DER 4

// Sensor Ultrasónico para modo Sumo
#define TRIGGER_PIN 11
#define ECHO_PIN 12

// Sensor de borde (opcional para sumo)
#define SENSOR_BORDE_IZQ A0
#define SENSOR_BORDE_DER A1

// ===== VARIABLES GLOBALES =====
enum Modo {
  MANUAL,
  LINEA,
  SUMO
};

Modo modoActual = MANUAL;
int velocidadBase = 200;  // Velocidad base (0-255)
int velocidadGiro = 150;  // Velocidad para giros

// ===== SETUP =====
void setup() {
  // Inicializar comunicación serial (Bluetooth)
  Serial.begin(9600);
  
  // Configurar pines de motores
  pinMode(MOTOR_IZQ_A, OUTPUT);
  pinMode(MOTOR_IZQ_B, OUTPUT);
  pinMode(MOTOR_IZQ_PWM, OUTPUT);
  pinMode(MOTOR_DER_A, OUTPUT);
  pinMode(MOTOR_DER_B, OUTPUT);
  pinMode(MOTOR_DER_PWM, OUTPUT);
  
  // Configurar sensores IR
  pinMode(SENSOR_IZQ, INPUT);
  pinMode(SENSOR_CEN, INPUT);
  pinMode(SENSOR_DER, INPUT);
  
  // Configurar sensor ultrasónico
  pinMode(TRIGGER_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  
  // Configurar sensores de borde
  pinMode(SENSOR_BORDE_IZQ, INPUT);
  pinMode(SENSOR_BORDE_DER, INPUT);
  
  detenerMotores();
  
  Serial.println("Robot Iniciado - Modo Manual");
}

// ===== LOOP PRINCIPAL =====
void loop() {
  // Leer comandos Bluetooth
  if (Serial.available() > 0) {
    procesarComando();
  }
  
  // Ejecutar lógica según modo actual
  switch (modoActual) {
    case MANUAL:
      // En modo manual, solo responde a comandos
      break;
      
    case LINEA:
      seguirLinea();
      break;
      
    case SUMO:
      modoSumo();
      break;
  }
  
  delay(10);
}

// ===== PROCESAMIENTO DE COMANDOS =====
void procesarComando() {
  String comando = Serial.readStringUntil('\n');
  comando.trim();
  
  // Comandos de movimiento (modo manual)
  if (comando == "F") {
    avanzar();
    Serial.println("OK:Avanzar");
  }
  else if (comando == "B") {
    retroceder();
    Serial.println("OK:Retroceder");
  }
  else if (comando == "L") {
    girarIzquierda();
    Serial.println("OK:Izquierda");
  }
  else if (comando == "R") {
    girarDerecha();
    Serial.println("OK:Derecha");
  }
  else if (comando == "S") {
    detenerMotores();
    Serial.println("OK:Stop");
  }
  
  // Comandos de cambio de modo
  else if (comando == "M1") {
    modoActual = LINEA;
    Serial.println("OK:Modo Linea");
  }
  else if (comando == "M2") {
    modoActual = SUMO;
    Serial.println("OK:Modo Sumo");
  }
  else if (comando == "M3") {
    modoActual = MANUAL;
    detenerMotores();
    Serial.println("OK:Modo Manual");
  }
  
  // Comandos de configuración
  else if (comando.startsWith("V")) {
    // Cambiar velocidad: V150
    int vel = comando.substring(1).toInt();
    if (vel >= 0 && vel <= 255) {
      velocidadBase = vel;
      Serial.println("OK:Velocidad=" + String(vel));
    }
  }
  else {
    Serial.println("ERROR:Comando desconocido");
  }
}

// ===== FUNCIONES DE MOVIMIENTO =====
void avanzar() {
  // Motor izquierdo adelante
  digitalWrite(MOTOR_IZQ_A, HIGH);
  digitalWrite(MOTOR_IZQ_B, LOW);
  analogWrite(MOTOR_IZQ_PWM, velocidadBase);
  
  // Motor derecho adelante
  digitalWrite(MOTOR_DER_A, HIGH);
  digitalWrite(MOTOR_DER_B, LOW);
  analogWrite(MOTOR_DER_PWM, velocidadBase);
}

void retroceder() {
  // Motor izquierdo atrás
  digitalWrite(MOTOR_IZQ_A, LOW);
  digitalWrite(MOTOR_IZQ_B, HIGH);
  analogWrite(MOTOR_IZQ_PWM, velocidadBase);
  
  // Motor derecho atrás
  digitalWrite(MOTOR_DER_A, LOW);
  digitalWrite(MOTOR_DER_B, HIGH);
  analogWrite(MOTOR_DER_PWM, velocidadBase);
}

void girarIzquierda() {
  // Motor izquierdo atrás
  digitalWrite(MOTOR_IZQ_A, LOW);
  digitalWrite(MOTOR_IZQ_B, HIGH);
  analogWrite(MOTOR_IZQ_PWM, velocidadGiro);
  
  // Motor derecho adelante
  digitalWrite(MOTOR_DER_A, HIGH);
  digitalWrite(MOTOR_DER_B, LOW);
  analogWrite(MOTOR_DER_PWM, velocidadGiro);
}

void girarDerecha() {
  // Motor izquierdo adelante
  digitalWrite(MOTOR_IZQ_A, HIGH);
  digitalWrite(MOTOR_IZQ_B, LOW);
  analogWrite(MOTOR_IZQ_PWM, velocidadGiro);
  
  // Motor derecho atrás
  digitalWrite(MOTOR_DER_A, LOW);
  digitalWrite(MOTOR_DER_B, HIGH);
  analogWrite(MOTOR_DER_PWM, velocidadGiro);
}

void detenerMotores() {
  digitalWrite(MOTOR_IZQ_A, LOW);
  digitalWrite(MOTOR_IZQ_B, LOW);
  analogWrite(MOTOR_IZQ_PWM, 0);
  
  digitalWrite(MOTOR_DER_A, LOW);
  digitalWrite(MOTOR_DER_B, LOW);
  analogWrite(MOTOR_DER_PWM, 0);
}

// ===== MODO SEGUIMIENTO DE LÍNEA =====
void seguirLinea() {
  int izq = digitalRead(SENSOR_IZQ);
  int cen = digitalRead(SENSOR_CEN);
  int der = digitalRead(SENSOR_DER);
  
  // Lógica: 0 = línea negra detectada, 1 = superficie blanca
  
  if (cen == 0) {
    // Línea en el centro - avanzar recto
    avanzar();
  }
  else if (izq == 0) {
    // Línea a la izquierda - girar izquierda
    girarIzquierda();
  }
  else if (der == 0) {
    // Línea a la derecha - girar derecha
    girarDerecha();
  }
  else {
    // No detecta línea - buscar (girar lentamente)
    girarDerecha();
  }
}

// ===== MODO SUMO =====
void modoSumo() {
  // Verificar sensores de borde primero (evitar salir del ring)
  int bordeIzq = analogRead(SENSOR_BORDE_IZQ);
  int bordeDer = analogRead(SENSOR_BORDE_DER);
  
  // Si detecta borde blanco (valor alto), retroceder y girar
  if (bordeIzq > 500 || bordeDer > 500) {
    retroceder();
    delay(300);
    girarDerecha();
    delay(200);
    return;
  }
  
  // Medir distancia al oponente
  long distancia = medirDistancia();
  
  if (distancia > 0 && distancia < 50) {
    // Oponente detectado - atacar
    avanzar();
  }
  else {
    // Buscar oponente - girar lentamente
    digitalWrite(MOTOR_IZQ_A, HIGH);
    digitalWrite(MOTOR_IZQ_B, LOW);
    analogWrite(MOTOR_IZQ_PWM, 100);
    
    digitalWrite(MOTOR_DER_A, HIGH);
    digitalWrite(MOTOR_DER_B, LOW);
    analogWrite(MOTOR_DER_PWM, 80);
  }
}

// ===== SENSOR ULTRASÓNICO =====
long medirDistancia() {
  digitalWrite(TRIGGER_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIGGER_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIGGER_PIN, LOW);
  
  long duracion = pulseIn(ECHO_PIN, HIGH, 30000); // Timeout 30ms
  long distancia = duracion * 0.034 / 2; // Convertir a cm
  
  return distancia;
}
