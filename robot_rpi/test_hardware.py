#!/usr/bin/env python3
"""
Script de Testing de Hardware para Robot
Prueba todos los componentes: motores, sensores IR, ultrasónico, etc.
Compatible con Raspberry Pi 2 W
"""

import RPi.GPIO as GPIO
import time
import sys

# ===== CONFIGURACIÓN DE PINES =====
# Motor Izquierdo
MOTOR_IZQ_A = 17
MOTOR_IZQ_B = 27
MOTOR_IZQ_PWM = 22

# Motor Derecho
MOTOR_DER_A = 23
MOTOR_DER_B = 24
MOTOR_DER_PWM = 25

# Sensores IR
SENSOR_IZQ = 5
SENSOR_CEN = 6
SENSOR_DER = 13

# Sensor Ultrasónico
TRIGGER_PIN = 20
ECHO_PIN = 21

# Sensores de borde
SENSOR_BORDE_IZQ = 16
SENSOR_BORDE_DER = 19

# ===== COLORES PARA TERMINAL =====
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*50}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^50}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*50}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.YELLOW}ℹ {text}{Colors.END}")

# ===== INICIALIZACIÓN =====
def inicializar_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # Motores
    GPIO.setup(MOTOR_IZQ_A, GPIO.OUT)
    GPIO.setup(MOTOR_IZQ_B, GPIO.OUT)
    GPIO.setup(MOTOR_IZQ_PWM, GPIO.OUT)
    GPIO.setup(MOTOR_DER_A, GPIO.OUT)
    GPIO.setup(MOTOR_DER_B, GPIO.OUT)
    GPIO.setup(MOTOR_DER_PWM, GPIO.OUT)
    
    # Sensores
    GPIO.setup(SENSOR_IZQ, GPIO.IN)
    GPIO.setup(SENSOR_CEN, GPIO.IN)
    GPIO.setup(SENSOR_DER, GPIO.IN)
    GPIO.setup(TRIGGER_PIN, GPIO.OUT)
    GPIO.setup(ECHO_PIN, GPIO.IN)
    GPIO.setup(SENSOR_BORDE_IZQ, GPIO.IN)
    GPIO.setup(SENSOR_BORDE_DER, GPIO.IN)
    
    print_success("GPIO inicializado correctamente")

# ===== TEST 1: MOTORES =====
def test_motores():
    print_header("TEST 1: MOTORES")
    
    pwm_izq = GPIO.PWM(MOTOR_IZQ_PWM, 1000)
    pwm_der = GPIO.PWM(MOTOR_DER_PWM, 1000)
    pwm_izq.start(0)
    pwm_der.start(0)
    
    try:
        # Motor Izquierdo Adelante
        print_info("Motor Izquierdo - Adelante (2 seg)")
        GPIO.output(MOTOR_IZQ_A, GPIO.HIGH)
        GPIO.output(MOTOR_IZQ_B, GPIO.LOW)
        pwm_izq.ChangeDutyCycle(50)
        time.sleep(2)
        pwm_izq.ChangeDutyCycle(0)
        
        time.sleep(1)
        
        # Motor Izquierdo Atrás
        print_info("Motor Izquierdo - Atrás (2 seg)")
        GPIO.output(MOTOR_IZQ_A, GPIO.LOW)
        GPIO.output(MOTOR_IZQ_B, GPIO.HIGH)
        pwm_izq.ChangeDutyCycle(50)
        time.sleep(2)
        pwm_izq.ChangeDutyCycle(0)
        
        time.sleep(1)
        
        # Motor Derecho Adelante
        print_info("Motor Derecho - Adelante (2 seg)")
        GPIO.output(MOTOR_DER_A, GPIO.HIGH)
        GPIO.output(MOTOR_DER_B, GPIO.LOW)
        pwm_der.ChangeDutyCycle(50)
        time.sleep(2)
        pwm_der.ChangeDutyCycle(0)
        
        time.sleep(1)
        
        # Motor Derecho Atrás
        print_info("Motor Derecho - Atrás (2 seg)")
        GPIO.output(MOTOR_DER_A, GPIO.LOW)
        GPIO.output(MOTOR_DER_B, GPIO.HIGH)
        pwm_der.ChangeDutyCycle(50)
        time.sleep(2)
        pwm_der.ChangeDutyCycle(0)
        
        # Ambos motores
        print_info("Ambos motores - Adelante (2 seg)")
        GPIO.output(MOTOR_IZQ_A, GPIO.HIGH)
        GPIO.output(MOTOR_IZQ_B, GPIO.LOW)
        GPIO.output(MOTOR_DER_A, GPIO.HIGH)
        GPIO.output(MOTOR_DER_B, GPIO.LOW)
        pwm_izq.ChangeDutyCycle(50)
        pwm_der.ChangeDutyCycle(50)
        time.sleep(2)
        
        # Detener
        pwm_izq.ChangeDutyCycle(0)
        pwm_der.ChangeDutyCycle(0)
        GPIO.output(MOTOR_IZQ_A, GPIO.LOW)
        GPIO.output(MOTOR_IZQ_B, GPIO.LOW)
        GPIO.output(MOTOR_DER_A, GPIO.LOW)
        GPIO.output(MOTOR_DER_B, GPIO.LOW)
        
        print_success("Test de motores completado")
        
    except Exception as e:
        print_error(f"Error en test de motores: {e}")
    finally:
        pwm_izq.stop()
        pwm_der.stop()

# ===== TEST 2: SENSORES IR =====
def test_sensores_ir():
    print_header("TEST 2: SENSORES IR (LÍNEA)")
    print_info("Coloca el robot sobre superficie blanca/negra")
    print_info("Presiona Ctrl+C para terminar\n")
    
    try:
        for i in range(30):
            izq = GPIO.input(SENSOR_IZQ)
            cen = GPIO.input(SENSOR_CEN)
            der = GPIO.input(SENSOR_DER)
            
            print(f"Izq: {izq}  Centro: {cen}  Der: {der}", end='\r')
            time.sleep(0.2)
        
        print()
        print_success("Test de sensores IR completado")
        
    except KeyboardInterrupt:
        print()
        print_info("Test interrumpido por usuario")

# ===== TEST 3: SENSOR ULTRASÓNICO =====
def test_ultrasonico():
    print_header("TEST 3: SENSOR ULTRASÓNICO")
    print_info("Coloca objetos a diferentes distancias")
    print_info("Presiona Ctrl+C para terminar\n")
    
    def medir_distancia():
        try:
            GPIO.output(TRIGGER_PIN, GPIO.LOW)
            time.sleep(0.00001)
            GPIO.output(TRIGGER_PIN, GPIO.HIGH)
            time.sleep(0.00001)
            GPIO.output(TRIGGER_PIN, GPIO.LOW)
            
            timeout = time.time() + 0.1
            inicio = time.time()
            while GPIO.input(ECHO_PIN) == 0 and time.time() < timeout:
                inicio = time.time()
            
            timeout = time.time() + 0.1
            fin = time.time()
            while GPIO.input(ECHO_PIN) == 1 and time.time() < timeout:
                fin = time.time()
            
            duracion = fin - inicio
            distancia = (duracion * 34300) / 2
            return distancia
        except:
            return -1
    
    try:
        for i in range(30):
            dist = medir_distancia()
            if dist > 0 and dist < 400:
                print(f"Distancia: {dist:.1f} cm     ", end='\r')
            else:
                print(f"Distancia: Fuera de rango", end='\r')
            time.sleep(0.2)
        
        print()
        print_success("Test de sensor ultrasónico completado")
        
    except KeyboardInterrupt:
        print()
        print_info("Test interrumpido por usuario")

# ===== TEST 4: SENSORES DE BORDE =====
def test_sensores_borde():
    print_header("TEST 4: SENSORES DE BORDE")
    print_info("Coloca el robot sobre superficie blanca/negra")
    print_info("Presiona Ctrl+C para terminar\n")
    
    try:
        for i in range(30):
            izq = GPIO.input(SENSOR_BORDE_IZQ)
            der = GPIO.input(SENSOR_BORDE_DER)
            
            print(f"Borde Izq: {izq}  Borde Der: {der}", end='\r')
            time.sleep(0.2)
        
        print()
        print_success("Test de sensores de borde completado")
        
    except KeyboardInterrupt:
        print()
        print_info("Test interrumpido por usuario")

# ===== TEST 5: TEST COMPLETO =====
def test_completo():
    print_header("TEST COMPLETO DEL SISTEMA")
    
    print_info("Iniciando secuencia de pruebas completa...")
    time.sleep(2)
    
    test_motores()
    time.sleep(1)
    
    test_sensores_ir()
    time.sleep(1)
    
    test_ultrasonico()
    time.sleep(1)
    
    test_sensores_borde()
    
    print_header("TESTS COMPLETADOS")
    print_success("Todos los tests finalizados correctamente")

# ===== MENÚ PRINCIPAL =====
def mostrar_menu():
    print_header("ROBOT TESTING - Raspberry Pi 2 W")
    print("1. Test Motores")
    print("2. Test Sensores IR (Línea)")
    print("3. Test Sensor Ultrasónico")
    print("4. Test Sensores de Borde")
    print("5. Test Completo")
    print("0. Salir")
    print()

def main():
    try:
        inicializar_gpio()
        
        while True:
            mostrar_menu()
            opcion = input("Selecciona una opción: ").strip()
            
            if opcion == '1':
                test_motores()
            elif opcion == '2':
                test_sensores_ir()
            elif opcion == '3':
                test_ultrasonico()
            elif opcion == '4':
                test_sensores_borde()
            elif opcion == '5':
                test_completo()
            elif opcion == '0':
                print_info("Saliendo...")
                break
            else:
                print_error("Opción no válida")
            
            input("\nPresiona Enter para continuar...")
            print("\n" * 2)
    
    except KeyboardInterrupt:
        print("\n")
        print_info("Programa interrumpido por usuario")
    
    finally:
        GPIO.cleanup()
        print_success("GPIO limpiado. Adiós!")

if __name__ == '__main__':
    main()
