#!/usr/bin/env python3
"""
Robot de Competición - Control Raspberry Pi 2 W
Modos: Seguimiento de Línea, Sumo, Control Manual
Control: WiFi (Web Interface)
Optimizado para Raspberry Pi 2 W (recursos limitados)
"""

import RPi.GPIO as GPIO
import time
import threading
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import json
import gc  # Garbage collector para optimización de memoria

# ===== CONFIGURACIÓN DE PINES GPIO =====
# Motor Izquierdo
MOTOR_IZQ_A = 17
MOTOR_IZQ_B = 27
MOTOR_IZQ_PWM = 22

# Motor Derecho
MOTOR_DER_A = 23
MOTOR_DER_B = 24
MOTOR_DER_PWM = 25

# Sensores IR para seguimiento de línea
SENSOR_IZQ = 5
SENSOR_CEN = 6
SENSOR_DER = 13

# Sensor Ultrasónico
TRIGGER_PIN = 20
ECHO_PIN = 21

# Sensores de borde (opcional)
SENSOR_BORDE_IZQ = 16
SENSOR_BORDE_DER = 19

# ===== CONFIGURACIÓN =====
app = Flask(__name__, static_folder='../web_interface', template_folder='../web_interface')
app.config['SECRET_KEY'] = 'robot_secret_2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Variables globales
modo_actual = "manual"
velocidad_base = 80  # Porcentaje (0-100)
robot_activo = False

# ===== INICIALIZACIÓN GPIO =====
def inicializar_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # Configurar motores
    GPIO.setup(MOTOR_IZQ_A, GPIO.OUT)
    GPIO.setup(MOTOR_IZQ_B, GPIO.OUT)
    GPIO.setup(MOTOR_IZQ_PWM, GPIO.OUT)
    GPIO.setup(MOTOR_DER_A, GPIO.OUT)
    GPIO.setup(MOTOR_DER_B, GPIO.OUT)
    GPIO.setup(MOTOR_DER_PWM, GPIO.OUT)
    
    # PWM para control de velocidad (500Hz para RPi 2 W)
    global pwm_izq, pwm_der
    pwm_izq = GPIO.PWM(MOTOR_IZQ_PWM, 500)  # 500Hz optimizado para RPi 2 W
    pwm_der = GPIO.PWM(MOTOR_DER_PWM, 500)
    pwm_izq.start(0)
    pwm_der.start(0)
    
    # Configurar sensores
    GPIO.setup(SENSOR_IZQ, GPIO.IN)
    GPIO.setup(SENSOR_CEN, GPIO.IN)
    GPIO.setup(SENSOR_DER, GPIO.IN)
    GPIO.setup(TRIGGER_PIN, GPIO.OUT)
    GPIO.setup(ECHO_PIN, GPIO.IN)
    GPIO.setup(SENSOR_BORDE_IZQ, GPIO.IN)
    GPIO.setup(SENSOR_BORDE_DER, GPIO.IN)
    
    print("GPIO inicializado correctamente")

# ===== FUNCIONES DE MOVIMIENTO =====
def avanzar():
    GPIO.output(MOTOR_IZQ_A, GPIO.HIGH)
    GPIO.output(MOTOR_IZQ_B, GPIO.LOW)
    pwm_izq.ChangeDutyCycle(velocidad_base)
    
    GPIO.output(MOTOR_DER_A, GPIO.HIGH)
    GPIO.output(MOTOR_DER_B, GPIO.LOW)
    pwm_der.ChangeDutyCycle(velocidad_base)

def retroceder():
    GPIO.output(MOTOR_IZQ_A, GPIO.LOW)
    GPIO.output(MOTOR_IZQ_B, GPIO.HIGH)
    pwm_izq.ChangeDutyCycle(velocidad_base)
    
    GPIO.output(MOTOR_DER_A, GPIO.LOW)
    GPIO.output(MOTOR_DER_B, GPIO.HIGH)
    pwm_der.ChangeDutyCycle(velocidad_base)

def girar_izquierda():
    GPIO.output(MOTOR_IZQ_A, GPIO.LOW)
    GPIO.output(MOTOR_IZQ_B, GPIO.HIGH)
    pwm_izq.ChangeDutyCycle(velocidad_base * 0.7)
    
    GPIO.output(MOTOR_DER_A, GPIO.HIGH)
    GPIO.output(MOTOR_DER_B, GPIO.LOW)
    pwm_der.ChangeDutyCycle(velocidad_base * 0.7)

def girar_derecha():
    GPIO.output(MOTOR_IZQ_A, GPIO.HIGH)
    GPIO.output(MOTOR_IZQ_B, GPIO.LOW)
    pwm_izq.ChangeDutyCycle(velocidad_base * 0.7)
    
    GPIO.output(MOTOR_DER_A, GPIO.LOW)
    GPIO.output(MOTOR_DER_B, GPIO.HIGH)
    pwm_der.ChangeDutyCycle(velocidad_base * 0.7)

def detener():
    GPIO.output(MOTOR_IZQ_A, GPIO.LOW)
    GPIO.output(MOTOR_IZQ_B, GPIO.LOW)
    pwm_izq.ChangeDutyCycle(0)
    
    GPIO.output(MOTOR_DER_A, GPIO.LOW)
    GPIO.output(MOTOR_DER_B, GPIO.LOW)
    pwm_der.ChangeDutyCycle(0)

# ===== SENSOR ULTRASÓNICO =====
def medir_distancia():
    try:
        GPIO.output(TRIGGER_PIN, GPIO.LOW)
        time.sleep(0.00001)
        GPIO.output(TRIGGER_PIN, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(TRIGGER_PIN, GPIO.LOW)
        
        timeout = time.time() + 0.1
        while GPIO.input(ECHO_PIN) == 0 and time.time() < timeout:
            inicio = time.time()
        
        timeout = time.time() + 0.1
        while GPIO.input(ECHO_PIN) == 1 and time.time() < timeout:
            fin = time.time()
        
        duracion = fin - inicio
        distancia = (duracion * 34300) / 2
        return distancia
    except:
        return -1

# ===== MODO SEGUIMIENTO DE LÍNEA =====
def seguir_linea():
    while robot_activo and modo_actual == "linea":
        izq = GPIO.input(SENSOR_IZQ)
        cen = GPIO.input(SENSOR_CEN)
        der = GPIO.input(SENSOR_DER)
        
        # 0 = línea negra, 1 = superficie blanca
        if cen == 0:
            avanzar()
        elif izq == 0:
            girar_izquierda()
        elif der == 0:
            girar_derecha()
        else:
            girar_derecha()
        
        time.sleep(0.1)  # Aumentado para RPi 2 W
    
    detener()
    gc.collect()  # Liberar memoria

# ===== MODO SUMO =====
def modo_sumo():
    while robot_activo and modo_actual == "sumo":
        # Verificar bordes
        borde_izq = GPIO.input(SENSOR_BORDE_IZQ)
        borde_der = GPIO.input(SENSOR_BORDE_DER)
        
        if borde_izq == 1 or borde_der == 1:
            # Detectó borde blanco - retroceder
            retroceder()
            time.sleep(0.3)
            girar_derecha()
            time.sleep(0.2)
            continue
        
        # Buscar oponente
        distancia = medir_distancia()
        
        if 0 < distancia < 50:
            # Oponente detectado - atacar
            avanzar()
        else:
            # Buscar - girar lentamente
            girar_derecha()
        
        time.sleep(0.1)  # Aumentado para RPi 2 W
    
    detener()
    gc.collect()  # Liberar memoria

# ===== RUTAS WEB =====
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def status():
    return jsonify({
        'modo': modo_actual,
        'velocidad': velocidad_base,
        'activo': robot_activo
    })

# ===== WEBSOCKET EVENTOS =====
@socketio.on('connect')
def handle_connect():
    print('Cliente conectado')
    emit('status', {
        'modo': modo_actual,
        'velocidad': velocidad_base,
        'activo': robot_activo
    })

@socketio.on('comando')
def handle_comando(data):
    global modo_actual, velocidad_base, robot_activo
    
    cmd = data.get('cmd', '')
    
    if cmd == 'F':
        avanzar()
    elif cmd == 'B':
        retroceder()
    elif cmd == 'L':
        girar_izquierda()
    elif cmd == 'R':
        girar_derecha()
    elif cmd == 'S':
        detener()
    elif cmd == 'M1':
        modo_actual = 'linea'
        robot_activo = True
        threading.Thread(target=seguir_linea, daemon=True).start()
    elif cmd == 'M2':
        modo_actual = 'sumo'
        robot_activo = True
        threading.Thread(target=modo_sumo, daemon=True).start()
    elif cmd == 'M3':
        robot_activo = False
        modo_actual = 'manual'
        detener()
    elif cmd.startswith('V'):
        try:
            vel = int(cmd[1:])
            if 0 <= vel <= 100:
                velocidad_base = vel
        except:
            pass
    
    emit('status', {
        'modo': modo_actual,
        'velocidad': velocidad_base,
        'activo': robot_activo
    }, broadcast=True)

# ===== MAIN =====
if __name__ == '__main__':
    try:
        print("Iniciando Robot Control Server...")
        inicializar_gpio()
        
        # Obtener IP local
        import socket
        hostname = socket.gethostname()
        ip_local = socket.gethostbyname(hostname)
        
        print(f"\n{'='*50}")
        print(f"Servidor iniciado correctamente")
        print(f"Optimizado para Raspberry Pi 2 W")
        print(f"Accede desde tu navegador a:")
        print(f"  http://{ip_local}:5000")
        print(f"  http://localhost:5000 (solo local)")
        print(f"{'='*50}\n")
        
        # Usar eventlet para mejor rendimiento en RPi 2 W
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, 
                     async_mode='eventlet', log_output=False)
        
    except KeyboardInterrupt:
        print("\nDeteniendo servidor...")
    finally:
        detener()
        GPIO.cleanup()
        print("GPIO limpiado. Adiós!")
