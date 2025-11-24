/*
 * Script de Testing para Arduino
 * Prueba todos los componentes del robot
 */

// ===== PINES =====
#define MOTOR_IZQ_A 5
#define MOTOR_IZQ_B 6
#define MOTOR_IZQ_PWM 9
#define MOTOR_DER_A 7
#define MOTOR_DER_B 8
#define MOTOR_DER_PWM 10

#define SENSOR_IZQ 2
#define SENSOR_CEN 3
#define SENSOR_DER 4

#define TRIGGER_PIN 11
#define ECHO_PIN 12

#define SENSOR_BORDE_IZQ A0
#define SENSOR_BORDE_DER A1

void setup() {
  Serial.begin(9600);
  
  // Configurar motores
  pinMode(MOTOR_IZQ_A, OUTPUT);
  pinMode(MOTOR_IZQ_B, OUTPUT);
  pinMode(MOTOR_IZQ_PWM, OUTPUT);
  pinMode(MOTOR_DER_A, OUTPUT);
  pinMode(MOTOR_DER_B, OUTPUT);
  pinMode(MOTOR_DER_PWM, OUTPUT);
  
  // Configurar sensores
  pinMode(SENSOR_IZQ, INPUT);
  pinMode(SENSOR_CEN, INPUT);
  pinMode(SENSOR_DER, INPUT);
  pinMode(TRIGGER_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(SENSOR_BORDE_IZQ, INPUT);
  pinMode(SENSOR_BORDE_DER, INPUT);
  
  Serial.println("========================================");
  Serial.println("   ROBOT TESTING - Arduino");
  Serial.println("========================================");
  Serial.println();
  
  mostrarMenu();
}

void loop() {
  if (Serial.available() > 0) {
    char opcion = Serial.read();
    
    switch(opcion) {
      case '1':
        testMotores();
        break;
      case '2':
        testSensoresIR();
        break;
      case '3':
        testUltrasonico();
        break;
      case '4':
        testSensoresBorde();
        break;
      case '5':
        testCompleto();
        break;
      case '0':
        Serial.println("Saliendo...");
        while(1);
        break;
      default:
        Serial.println("Opcion no valida");
    }
    
    Serial.println();
    Serial.println("Presiona Enter para continuar...");
    while(Serial.available() == 0);
    while(Serial.available() > 0) Serial.read();
    
    Serial.println("\n\n");
    mostrarMenu();
  }
}

void mostrarMenu() {
  Serial.println("MENU DE TESTING:");
  Serial.println("1. Test Motores");
  Serial.println("2. Test Sensores IR (Linea)");
  Serial.println("3. Test Sensor Ultrasonico");
  Serial.println("4. Test Sensores de Borde");
  Serial.println("5. Test Completo");
  Serial.println("0. Salir");
  Serial.println();
  Serial.print("Selecciona opcion: ");
}

// ===== TEST MOTORES =====
void testMotores() {
  Serial.println("\n========== TEST MOTORES ==========");
  
  // Motor Izquierdo Adelante
  Serial.println("Motor Izquierdo - Adelante (2 seg)");
  digitalWrite(MOTOR_IZQ_A, HIGH);
  digitalWrite(MOTOR_IZQ_B, LOW);
  analogWrite(MOTOR_IZQ_PWM, 150);
  delay(2000);
  analogWrite(MOTOR_IZQ_PWM, 0);
  delay(500);
  
  // Motor Izquierdo Atras
  Serial.println("Motor Izquierdo - Atras (2 seg)");
  digitalWrite(MOTOR_IZQ_A, LOW);
  digitalWrite(MOTOR_IZQ_B, HIGH);
  analogWrite(MOTOR_IZQ_PWM, 150);
  delay(2000);
  analogWrite(MOTOR_IZQ_PWM, 0);
  delay(500);
  
  // Motor Derecho Adelante
  Serial.println("Motor Derecho - Adelante (2 seg)");
  digitalWrite(MOTOR_DER_A, HIGH);
  digitalWrite(MOTOR_DER_B, LOW);
  analogWrite(MOTOR_DER_PWM, 150);
  delay(2000);
  analogWrite(MOTOR_DER_PWM, 0);
  delay(500);
  
  // Motor Derecho Atras
  Serial.println("Motor Derecho - Atras (2 seg)");
  digitalWrite(MOTOR_DER_A, LOW);
  digitalWrite(MOTOR_DER_B, HIGH);
  analogWrite(MOTOR_DER_PWM, 150);
  delay(2000);
  analogWrite(MOTOR_DER_PWM, 0);
  delay(500);
  
  // Ambos motores
  Serial.println("Ambos motores - Adelante (2 seg)");
  digitalWrite(MOTOR_IZQ_A, HIGH);
  digitalWrite(MOTOR_IZQ_B, LOW);
  digitalWrite(MOTOR_DER_A, HIGH);
  digitalWrite(MOTOR_DER_B, LOW);
  analogWrite(MOTOR_IZQ_PWM, 150);
  analogWrite(MOTOR_DER_PWM, 150);
  delay(2000);
  
  // Detener
  analogWrite(MOTOR_IZQ_PWM, 0);
  analogWrite(MOTOR_DER_PWM, 0);
  digitalWrite(MOTOR_IZQ_A, LOW);
  digitalWrite(MOTOR_IZQ_B, LOW);
  digitalWrite(MOTOR_DER_A, LOW);
  digitalWrite(MOTOR_DER_B, LOW);
  
  Serial.println("Test de motores completado");
}

// ===== TEST SENSORES IR =====
void testSensoresIR() {
  Serial.println("\n========== TEST SENSORES IR ==========");
  Serial.println("Leyendo sensores durante 10 segundos...");
  Serial.println("Formato: Izq | Centro | Der");
  Serial.println();
  
  unsigned long inicio = millis();
  while (millis() - inicio < 10000) {
    int izq = digitalRead(SENSOR_IZQ);
    int cen = digitalRead(SENSOR_CEN);
    int der = digitalRead(SENSOR_DER);
    
    Serial.print("  ");
    Serial.print(izq);
    Serial.print("  |   ");
    Serial.print(cen);
    Serial.print("    |  ");
    Serial.println(der);
    
    delay(200);
  }
  
  Serial.println("Test de sensores IR completado");
}

// ===== TEST ULTRASONICO =====
void testUltrasonico() {
  Serial.println("\n========== TEST ULTRASONICO ==========");
  Serial.println("Midiendo distancia durante 10 segundos...");
  Serial.println();
  
  unsigned long inicio = millis();
  while (millis() - inicio < 10000) {
    long distancia = medirDistancia();
    
    Serial.print("Distancia: ");
    if (distancia > 0 && distancia < 400) {
      Serial.print(distancia);
      Serial.println(" cm");
    } else {
      Serial.println("Fuera de rango");
    }
    
    delay(200);
  }
  
  Serial.println("Test de sensor ultrasonico completado");
}

long medirDistancia() {
  digitalWrite(TRIGGER_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIGGER_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIGGER_PIN, LOW);
  
  long duracion = pulseIn(ECHO_PIN, HIGH, 30000);
  long distancia = duracion * 0.034 / 2;
  
  return distancia;
}

// ===== TEST SENSORES BORDE =====
void testSensoresBorde() {
  Serial.println("\n========== TEST SENSORES BORDE ==========");
  Serial.println("Leyendo sensores durante 10 segundos...");
  Serial.println("Formato: Izq | Der");
  Serial.println();
  
  unsigned long inicio = millis();
  while (millis() - inicio < 10000) {
    int izq = analogRead(SENSOR_BORDE_IZQ);
    int der = analogRead(SENSOR_BORDE_DER);
    
    Serial.print(" ");
    Serial.print(izq);
    Serial.print("  |  ");
    Serial.println(der);
    
    delay(200);
  }
  
  Serial.println("Test de sensores de borde completado");
}

// ===== TEST COMPLETO =====
void testCompleto() {
  Serial.println("\n========== TEST COMPLETO ==========");
  Serial.println("Ejecutando todos los tests...");
  Serial.println();
  
  testMotores();
  delay(1000);
  
  testSensoresIR();
  delay(1000);
  
  testUltrasonico();
  delay(1000);
  
  testSensoresBorde();
  
  Serial.println("\n========== TESTS COMPLETADOS ==========");
}
