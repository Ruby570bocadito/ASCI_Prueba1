#!/usr/bin/env python3
"""
Robot de Competición ASTI Challenge - Control Raspberry Pi 2 W MEJORADO
Modos: Seguimiento de Línea (PID), Sumo Mejorado, Logística, Control Manual
Control: WiFi (Web Interface)
Funcionalidades: Telemetría, Calibración, Sensor Color, Pinza, LEDs
Optimizado para Raspberry Pi 2 W (recursos limitados)
"""

import RPi.GPIO as GPIO
import time
import threading
from flask import Flask, render_template, jsonify, request, send_file
from flask_socketio import SocketIO, emit
import json
import gc  # Garbage collector para optimización de memoria
import os

# Importar módulos personalizados
try:
    from telemetria import SistemaTelemetria
    from calibrador import CalibradorSensores
    from sensor_color import SensorColor
    from pinza import ControlPinza
    from indicadores import SistemaIndicadores
    MODULOS_DISPONIBLES = True
except ImportError as e:
    print(f"[Advertencia] No se pudieron cargar todos los módulos: {e}")
    print("[Info] El robot funcionará en modo básico")
    MODULOS_DISPONIBLES = False

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

# Sensores de borde
SENSOR_BORDE_IZQ = 16
SENSOR_BORDE_DER = 19

# LEDs RGB (opcional)
LED_ROJO = 26
LED_VERDE = 19
LED_AZUL = 13

# Servo Pinza (opcional)
SERVO_PIN = 18

# Sensor de Color TCS3200 (opcional)
COLOR_S0 = 17
COLOR_S1 = 27
COLOR_S2 = 22
COLOR_S3 = 23
COLOR_OUT = 24

# ===== CONFIGURACIÓN =====
app = Flask(__name__, static_folder='../web_interface', template_folder='../web_interface')
app.config['SECRET_KEY'] = 'robot_asti_2025'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Variables globales
modo_actual = "manual"
velocidad_base = 80  # Porcentaje (0-100)
robot_activo = False

# Sistemas opcionales
telemetria = None
calibrador = None
sensor_color = None
pinza = None
leds = None

# ===== CLASE CONTROLADOR PID =====
class ControladorPID:
    """Control PID para seguimiento de línea suave"""
    
    def __init__(self, kp=1.5, ki=0.1, kd=0.5):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.error_anterior = 0
        self.integral = 0
        self.integral_max = 100  # Anti-windup
    
    def calcular(self, error):
        """Calcula la salida PID"""
        # Integral con anti-windup
        self.integral += error
        self.integral = max(-self.integral_max, min(self.integral_max, self.integral))
        
        # Derivada
        derivada = error - self.error_anterior
        
        # Salida PID
        salida = (self.kp * error) + (self.ki * self.integral) + (self.kd * derivada)
        
        self.error_anterior = error
        return salida
    
    def reset(self):
        """Resetea el controlador PID"""
        self.error_anterior = 0
        self.integral = 0

# ===== INICIALIZACIÓN GPIO =====
def inicializar_gpio():
    """Inicializa todos los pines GPIO"""
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
    pwm_izq = GPIO.PWM(MOTOR_IZQ_PWM, 500)
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
    
    print("[GPIO] Inicializado correctamente")

def inicializar_modulos():
    """Inicializa módulos opcionales (telemetría, LEDs, etc.)"""
    global telemetria, calibrador, sensor_color, pinza, leds
    
    if not MODULOS_DISPONIBLES:
        return
    
    try:
        # Telemetría
        telemetria = SistemaTelemetria()
        telemetria.registrar_evento('INICIO', {'version': '2.0_mejorado'})
        print("[Telemetría] Iniciada")
    except Exception as e:
        print(f"[Telemetría] Error: {e}")
    
    try:
        # Calibrador
        calibrador = CalibradorSensores(SENSOR_IZQ, SENSOR_CEN, SENSOR_DER)
        calibrador.cargar_calibracion()
        print("[Calibrador] Iniciado")
    except Exception as e:
        print(f"[Calibrador] Error: {e}")
    
    try:
        # LEDs
        leds = SistemaIndicadores(LED_ROJO, LED_VERDE, LED_AZUL)
        leds.secuencia_inicio()
        print("[LEDs] Iniciados")
    except Exception as e:
        print(f"[LEDs] Error: {e}")
    
    # Sensor de color y pinza solo si están conectados
    # (se inicializarán bajo demanda)

# ===== FUNCIONES DE MOVIMIENTO =====
def avanzar():
    """Mueve el robot hacia adelante"""
    if telemetria:
        telemetria.registrar_evento('MOVIMIENTO', {'accion': 'avanzar', 'velocidad': velocidad_base})
    
    GPIO.output(MOTOR_IZQ_A, GPIO.HIGH)
    GPIO.output(MOTOR_IZQ_B, GPIO.LOW)
    pwm_izq.ChangeDutyCycle(velocidad_base)
    
    GPIO.output(MOTOR_DER_A, GPIO.HIGH)
    GPIO.output(MOTOR_DER_B, GPIO.LOW)
    pwm_der.ChangeDutyCycle(velocidad_base)

def retroceder():
    """Mueve el robot hacia atrás"""
    if telemetria:
        telemetria.registrar_evento('MOVIMIENTO', {'accion': 'retroceder', 'velocidad': velocidad_base})
    
    GPIO.output(MOTOR_IZQ_A, GPIO.LOW)
    GPIO.output(MOTOR_IZQ_B, GPIO.HIGH)
    pwm_izq.ChangeDutyCycle(velocidad_base)
    
    GPIO.output(MOTOR_DER_A, GPIO.LOW)
    GPIO.output(MOTOR_DER_B, GPIO.HIGH)
    pwm_der.ChangeDutyCycle(velocidad_base)

def girar_izquierda():
    """Gira el robot a la izquierda"""
    if telemetria:
        telemetria.registrar_evento('MOVIMIENTO', {'accion': 'girar_izquierda', 'velocidad': velocidad_base})
    
    GPIO.output(MOTOR_IZQ_A, GPIO.LOW)
    GPIO.output(MOTOR_IZQ_B, GPIO.HIGH)
    pwm_izq.ChangeDutyCycle(velocidad_base * 0.7)
    
    GPIO.output(MOTOR_DER_A, GPIO.HIGH)
    GPIO.output(MOTOR_DER_B, GPIO.LOW)
    pwm_der.ChangeDutyCycle(velocidad_base * 0.7)

def girar_derecha():
    """Gira el robot a la derecha"""
    if telemetria:
        telemetria.registrar_evento('MOVIMIENTO', {'accion': 'girar_derecha', 'velocidad': velocidad_base})
    
    GPIO.output(MOTOR_IZQ_A, GPIO.HIGH)
    GPIO.output(MOTOR_IZQ_B, GPIO.LOW)
    pwm_izq.ChangeDutyCycle(velocidad_base * 0.7)
    
    GPIO.output(MOTOR_DER_A, GPIO.LOW)
    GPIO.output(MOTOR_DER_B, GPIO.HIGH)
    pwm_der.ChangeDutyCycle(velocidad_base * 0.7)

def detener():
    """Detiene el robot"""
    if telemetria:
        telemetria.registrar_evento('MOVIMIENTO', {'accion': 'detener'})
    
    GPIO.output(MOTOR_IZQ_A, GPIO.LOW)
    GPIO.output(MOTOR_IZQ_B, GPIO.LOW)
    pwm_izq.ChangeDutyCycle(0)
    
    GPIO.output(MOTOR_DER_A, GPIO.LOW)
    GPIO.output(MOTOR_DER_B, GPIO.LOW)
    pwm_der.ChangeDutyCycle(0)

def mover_motores_diferencial(vel_izq, vel_der):
    """
    Control diferencial de motores para PID
    
    Args:
        vel_izq, vel_der: Velocidad de cada motor (-100 a 100)
    """
    # Motor izquierdo
    if vel_izq >= 0:
        GPIO.output(MOTOR_IZQ_A, GPIO.HIGH)
        GPIO.output(MOTOR_IZQ_B, GPIO.LOW)
    else:
        GPIO.output(MOTOR_IZQ_A, GPIO.LOW)
        GPIO.output(MOTOR_IZQ_B, GPIO.HIGH)
    pwm_izq.ChangeDutyCycle(abs(vel_izq))
    
    # Motor derecho
    if vel_der >= 0:
        GPIO.output(MOTOR_DER_A, GPIO.HIGH)
        GPIO.output(MOTOR_DER_B, GPIO.LOW)
    else:
        GPIO.output(MOTOR_DER_A, GPIO.LOW)
        GPIO.output(MOTOR_DER_B, GPIO.HIGH)
    pwm_der.ChangeDutyCycle(abs(vel_der))

# ===== SENSOR ULTRASÓNICO =====
def medir_distancia():
    """Mide distancia con sensor ultrasónico"""
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

# ===== MODO SEGUIMIENTO DE LÍNEA CON PID =====
def seguir_linea_pid():
    """Seguimiento de línea con control PID mejorado"""
    if leds:
        leds.indicar_estado('LINEA')
    
    if telemetria:
        telemetria.registrar_evento('MODO', {'modo': 'linea_pid', 'iniciado': True})
    
    pid = ControladorPID(kp=1.5, ki=0.1, kd=0.5)
    
    while robot_activo and modo_actual == "linea":
        izq = GPIO.input(SENSOR_IZQ)
        cen = GPIO.input(SENSOR_CEN)
        der = GPIO.input(SENSOR_DER)
        
        if telemetria:
            telemetria.registrar_evento('SENSORES_IR', {'izq': izq, 'cen': cen, 'der': der})
        
        # Calcular error de posición
        # -1 = muy a la izquierda, 0 = centrado, 1 = muy a la derecha
        if cen == 0:
            error = 0
        elif izq == 0:
            error = -1
        elif der == 0:
            error = 1
        else:
            error = 0  # Perdió la línea - mantener dirección
        
        # Calcular corrección PID
        correccion = pid.calcular(error)
        
        # Aplicar corrección a motores
        vel_izq = velocidad_base - correccion * 20
        vel_der = velocidad_base + correccion * 20
        
        # Limitar velocidades
        vel_izq = max(0, min(100, vel_izq))
        vel_der = max(0, min(100, vel_der))
        
        # Aplicar velocidades
        mover_motores_diferencial(vel_izq, vel_der)
        
        time.sleep(0.05)
    
    detener()
    pid.reset()
    gc.collect()

# ===== MODO SEGUIMIENTO DE LÍNEA BÁSICO =====
def seguir_linea():
    """Seguimiento de línea básico (sin PID)"""
    if leds:
        leds.indicar_estado('LINEA')
    
    if telemetria:
        telemetria.registrar_evento('MODO', {'modo': 'linea_basico', 'iniciado': True})
    
    while robot_activo and modo_actual == "linea":
        izq = GPIO.input(SENSOR_IZQ)
        cen = GPIO.input(SENSOR_CEN)
        der = GPIO.input(SENSOR_DER)
        
        if telemetria:
            telemetria.registrar_evento('SENSORES_IR', {'izq': izq, 'cen': cen, 'der': der})
        
        # 0 = línea negra, 1 = superficie blanca
        if cen == 0:
            avanzar()
        elif izq == 0:
            girar_izquierda()
        elif der == 0:
            girar_derecha()
        else:
            girar_derecha()
        
        time.sleep(0.1)
    
    detener()
    gc.collect()

# ===== MODO SUMO MEJORADO =====
def modo_sumo_mejorado():
    """Modo sumo con estrategia mejorada"""
    if leds:
        leds.indicar_estado('SUMO')
    
    if telemetria:
        telemetria.registrar_evento('MODO', {'modo': 'sumo_mejorado', 'iniciado': True})
    
    estado = "BUSCAR"
    tiempo_sin_deteccion = 0
    
    while robot_activo and modo_actual == "sumo":
        # 1. PRIORIDAD: Verificar bordes
        borde_izq = GPIO.input(SENSOR_BORDE_IZQ)
        borde_der = GPIO.input(SENSOR_BORDE_DER)
        
        if borde_izq == 1 or borde_der == 1:
            # Detectó borde - maniobra de escape
            estado = "ESCAPAR"
            if telemetria:
                telemetria.registrar_evento('SUMO', {'estado': estado, 'borde_izq': borde_izq, 'borde_der': borde_der})
            
            retroceder()
            time.sleep(0.4)
            if borde_izq == 1:
                girar_derecha()
            else:
                girar_izquierda()
            time.sleep(0.3)
            estado = "BUSCAR"
            continue
        
        # 2. Buscar oponente
        distancia = medir_distancia()
        
        if 0 < distancia < 60:
            # Oponente detectado - ATACAR
            estado = "ATACAR"
            tiempo_sin_deteccion = 0
            
            if telemetria:
                telemetria.registrar_evento('SUMO', {'estado': estado, 'distancia': distancia})
            
            # Ajustar dirección según distancia
            if distancia < 20:
                # Muy cerca - máxima potencia
                velocidad_temp = velocidad_base
                velocidad_base = 100
                avanzar()
                velocidad_base = velocidad_temp
            else:
                # Acercarse rápido
                avanzar()
        else:
            # No detectado - buscar
            estado = "BUSCAR"
            tiempo_sin_deteccion += 1
            
            # Estrategia de búsqueda: giro en espiral
            if tiempo_sin_deteccion < 20:
                girar_derecha()
            else:
                # Cambiar dirección de búsqueda
                girar_izquierda()
                if tiempo_sin_deteccion > 40:
                    tiempo_sin_deteccion = 0
        
        time.sleep(0.05)
    
    detener()
    gc.collect()

# ===== MODO SUMO BÁSICO =====
def modo_sumo():
    """Modo sumo básico"""
    if leds:
        leds.indicar_estado('SUMO')
    
    if telemetria:
        telemetria.registrar_evento('MODO', {'modo': 'sumo_basico', 'iniciado': True})
    
    while robot_activo and modo_actual == "sumo":
        # Verificar bordes
        borde_izq = GPIO.input(SENSOR_BORDE_IZQ)
        borde_der = GPIO.input(SENSOR_BORDE_DER)
        
        if borde_izq == 1 or borde_der == 1:
            retroceder()
            time.sleep(0.3)
            girar_derecha()
            time.sleep(0.2)
            continue
        
        # Buscar oponente
        distancia = medir_distancia()
        
        if 0 < distancia < 50:
            avanzar()
        else:
            girar_derecha()
        
        time.sleep(0.1)
    
    detener()
    gc.collect()

# ===== MODO LOGÍSTICA (AUTOMATIZACIÓN INDUSTRIAL) =====
def modo_logistica():
    """
    Modo logística - Automatización industrial
    Ciclo: Ir a zona → Detectar color → Agarrar → Transportar → Soltar
    """
    if leds:
        leds.indicar_estado('LOGISTICA')
    
    if telemetria:
        telemetria.registrar_evento('MODO', {'modo': 'logistica', 'iniciado': True})
    
    print("[Logística] Iniciando modo automatización...")
    
    # Estados del ciclo logístico
    estados = ['IR_A_RECOGIDA', 'DETECTAR_COLOR', 'AGARRAR', 
               'IR_A_ENTREGA', 'SOLTAR', 'VOLVER']
    
    for estado in estados:
        if not robot_activo or modo_actual != "logistica":
            break
        
        print(f"[Logística] Estado: {estado}")
        if telemetria:
            telemetria.registrar_evento('LOGISTICA', {'estado': estado})
        
        if estado == 'IR_A_RECOGIDA':
            # Seguir línea hasta zona de recogida
            if leds:
                leds.indicar_estado('BUSCANDO')
            avanzar()
            time.sleep(2)  # Simular desplazamiento
            detener()
        
        elif estado == 'DETECTAR_COLOR':
            # Detectar color del objeto
            if leds:
                leds.indicar_estado('CLASIFICANDO')
            if sensor_color:
                color = sensor_color.leer_color()
                print(f"[Logística] Color detectado: {color}")
                if telemetria:
                    telemetria.registrar_evento('COLOR_DETECTADO', {'color': color})
            time.sleep(1)
        
        elif estado == 'AGARRAR':
            # Agarrar objeto con pinza
            if leds:
                leds.indicar_estado('TRANSPORTANDO')
            if pinza:
                pinza.agarrar_objeto()
            else:
                print("[Logística] Simulando agarre (pinza no disponible)")
                time.sleep(1)
        
        elif estado == 'IR_A_ENTREGA':
            # Transportar a zona de entrega
            avanzar()
            time.sleep(2)  # Simular transporte
            detener()
        
        elif estado == 'SOLTAR':
            # Soltar objeto
            if pinza:
                pinza.soltar_objeto()
            else:
                print("[Logística] Simulando liberación (pinza no disponible)")
                time.sleep(1)
        
        elif estado == 'VOLVER':
            # Volver a posición inicial
            retroceder()
            time.sleep(2)
            detener()
    
    if leds:
        leds.secuencia_exito()
    
    print("[Logística] ✓ Ciclo completado")
    if telemetria:
        telemetria.registrar_evento('LOGISTICA', {'estado': 'COMPLETADO'})
    
    gc.collect()

# ===== RUTAS WEB =====
@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/api/status')
def status():
    """Estado actual del robot"""
    stats = {}
    if telemetria:
        stats = telemetria.obtener_estadisticas()
    
    return jsonify({
        'modo': modo_actual,
        'velocidad': velocidad_base,
        'activo': robot_activo,
        'telemetria': stats
    })

@app.route('/api/descargar_logs')
def descargar_logs():
    """Descarga archivo de logs"""
    if telemetria:
        telemetria.guardar()
        return send_file(telemetria.archivo, as_attachment=True)
    return jsonify({'error': 'Telemetría no disponible'}), 404

@app.route('/api/calibrar', methods=['POST'])
def calibrar():
    """Inicia calibración de sensores"""
    if calibrador:
        threading.Thread(target=calibrador.calibrar_sensores_ir, daemon=True).start()
        return jsonify({'status': 'Calibración iniciada'})
    return jsonify({'error': 'Calibrador no disponible'}), 404

# ===== WEBSOCKET EVENTOS =====
@socketio.on('connect')
def handle_connect():
    """Cliente conectado"""
    print('[WebSocket] Cliente conectado')
    emit('status', {
        'modo': modo_actual,
        'velocidad': velocidad_base,
        'activo': robot_activo
    })

@socketio.on('comando')
def handle_comando(data):
    """Maneja comandos desde interfaz web"""
    global modo_actual, velocidad_base, robot_activo
    
    cmd = data.get('cmd', '')
    print(f'[Comando] Recibido: {cmd}')
    
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
    elif cmd == 'M1':  # Modo Línea
        modo_actual = 'linea'
        robot_activo = True
        threading.Thread(target=seguir_linea_pid, daemon=True).start()
    elif cmd == 'M2':  # Modo Sumo
        modo_actual = 'sumo'
        robot_activo = True
        threading.Thread(target=modo_sumo_mejorado, daemon=True).start()
    elif cmd == 'M3':  # Modo Manual
        robot_activo = False
        modo_actual = 'manual'
        detener()
        if leds:
            leds.indicar_estado('MANUAL')
    elif cmd == 'M4':  # Modo Logística
        modo_actual = 'logistica'
        robot_activo = True
        threading.Thread(target=modo_logistica, daemon=True).start()
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
        print("\n" + "="*60)
        print("ROBOT ASTI CHALLENGE - VERSIÓN MEJORADA 2.0")
        print("="*60)
        
        inicializar_gpio()
        inicializar_modulos()
        
        # Obtener IP local
        import socket
        hostname = socket.gethostname()
        ip_local = socket.gethostbyname(hostname)
        
        print(f"\n{'='*60}")
        print(f"✓ Servidor iniciado correctamente")
        print(f"✓ Optimizado para Raspberry Pi 2 W")
        print(f"✓ Telemetría: {'Activa' if telemetria else 'Desactivada'}")
        print(f"✓ LEDs: {'Activos' if leds else 'Desactivados'}")
        print(f"\nAccede desde tu navegador a:")
        print(f"  → http://{ip_local}:5000")
        print(f"  → http://localhost:5000 (solo local)")
        print(f"{'='*60}\n")
        
        # Usar eventlet para mejor rendimiento en RPi 2 W
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, 
                     allow_unsafe_werkzeug=True)
        
    except KeyboardInterrupt:
        print("\n\n[Sistema] Deteniendo servidor...")
    finally:
        detener()
        if telemetria:
            telemetria.guardar()
            print(f"[Telemetría] Logs guardados en: {telemetria.archivo}")
        if leds:
            leds.apagar()
        GPIO.cleanup()
        print("[Sistema] GPIO limpiado. ¡Adiós!")
