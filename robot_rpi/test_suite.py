#!/usr/bin/env python3
"""
Suite de Testing Completa para Robot ASTI Challenge
Incluye tests unitarios, de integración y simulación
"""

import sys
import time
from pathlib import Path

# Añadir directorio robot_rpi al path
sys.path.insert(0, str(Path(__file__).parent))

# Modo de testing (cambiar a False para testing con hardware real)
MODO_SIMULACION = True

if MODO_SIMULACION:
    print("[TEST] Modo SIMULACIÓN activado (sin hardware)")
    # Mock de RPi.GPIO para testing sin hardware
    class MockGPIO:
        BCM = 'BCM'
        OUT = 'OUT'
        IN = 'IN'
        HIGH = 1
        LOW = 0
        PUD_UP = 'PUD_UP'
        
        @staticmethod
        def setmode(mode):
            pass
        
        @staticmethod
        def setwarnings(flag):
            pass
        
        @staticmethod
        def setup(pin, mode, **kwargs):
            pass
        
        @staticmethod
        def output(pin, value):
            pass
        
        @staticmethod
        def input(pin):
            return 0
        
        @staticmethod
        def cleanup():
            pass
        
        class PWM:
            def __init__(self, pin, freq):
                self.pin = pin
                self.freq = freq
            
            def start(self, duty):
                pass
            
            def ChangeDutyCycle(self, duty):
                pass
            
            def stop(self):
                pass
    
    sys.modules['RPi'] = type(sys)('RPi')
    sys.modules['RPi.GPIO'] = MockGPIO()
else:
    print("[TEST] Modo HARDWARE activado")
    import RPi.GPIO as GPIO

# Importar módulos a testear
try:
    from telemetria import SistemaTelemetria
    from calibrador import CalibradorSensores
    from sensor_color import SensorColor
    from pinza import ControlPinza
    from indicadores import SistemaIndicadores
    MODULOS_DISPONIBLES = True
except ImportError as e:
    print(f"[ERROR] No se pudieron importar módulos: {e}")
    MODULOS_DISPONIBLES = False
    sys.exit(1)


class TestRunner:
    """Ejecutor de tests con reporte"""
    
    def __init__(self):
        self.tests_ejecutados = 0
        self.tests_exitosos = 0
        self.tests_fallidos = 0
        self.resultados = []
    
    def ejecutar_test(self, nombre, funcion):
        """Ejecuta un test y registra el resultado"""
        self.tests_ejecutados += 1
        print(f"\n{'='*60}")
        print(f"TEST {self.tests_ejecutados}: {nombre}")
        print('='*60)
        
        try:
            funcion()
            print(f"✓ ÉXITO: {nombre}")
            self.tests_exitosos += 1
            self.resultados.append((nombre, True, None))
        except Exception as e:
            print(f"✗ FALLO: {nombre}")
            print(f"  Error: {e}")
            self.tests_fallidos += 1
            self.resultados.append((nombre, False, str(e)))
    
    def generar_reporte(self):
        """Genera reporte final de tests"""
        print("\n" + "="*60)
        print("REPORTE FINAL DE TESTING")
        print("="*60)
        print(f"Tests ejecutados: {self.tests_ejecutados}")
        print(f"Tests exitosos:   {self.tests_exitosos} ({self.tests_exitosos/self.tests_ejecutados*100:.1f}%)")
        print(f"Tests fallidos:   {self.tests_fallidos} ({self.tests_fallidos/self.tests_ejecutados*100:.1f}%)")
        print("\nDetalle:")
        
        for nombre, exito, error in self.resultados:
            simbolo = "✓" if exito else "✗"
            print(f"  {simbolo} {nombre}")
            if error:
                print(f"    └─ Error: {error}")
        
        print("="*60)
        
        return self.tests_fallidos == 0


# ===== TESTS UNITARIOS =====

def test_telemetria_creacion():
    """Test: Crear sistema de telemetría"""
    tel = SistemaTelemetria(archivo_log="test_telemetria.json")
    assert tel is not None
    assert len(tel.datos) == 1  # Evento de inicio
    print("  - Sistema de telemetría creado correctamente")

def test_telemetria_registro():
    """Test: Registrar eventos en telemetría"""
    tel = SistemaTelemetria(archivo_log="test_telemetria.json")
    
    tel.registrar_evento('TEST', {'valor': 123})
    tel.registrar_evento('MOVIMIENTO', {'accion': 'avanzar'})
    
    assert len(tel.datos) >= 2
    print(f"  - {len(tel.datos)} eventos registrados")

def test_telemetria_estadisticas():
    """Test: Generar estadísticas de telemetría"""
    tel = SistemaTelemetria(archivo_log="test_telemetria.json")
    
    for i in range(10):
        tel.registrar_evento('TEST', {'iteracion': i})
    
    stats = tel.obtener_estadisticas()
    assert stats['total_eventos'] >= 10
    assert 'TEST' in stats['eventos_por_tipo']
    print(f"  - Estadísticas generadas: {stats['total_eventos']} eventos")

def test_telemetria_exportar_csv():
    """Test: Exportar telemetría a CSV"""
    tel = SistemaTelemetria(archivo_log="test_telemetria.json")
    
    tel.registrar_evento('TEST', {'valor': 1})
    tel.registrar_evento('TEST', {'valor': 2})
    
    resultado = tel.exportar_csv("test_export.csv")
    assert resultado == True
    print("  - Exportación a CSV exitosa")

def test_calibrador_creacion():
    """Test: Crear calibrador de sensores"""
    if MODO_SIMULACION:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
    
    cal = CalibradorSensores(5, 6, 13)
    assert cal is not None
    print("  - Calibrador creado correctamente")

def test_sensor_color_creacion():
    """Test: Crear sensor de color"""
    if MODO_SIMULACION:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
    
    sensor = SensorColor(17, 27, 22, 23, 24)
    assert sensor is not None
    print("  - Sensor de color creado correctamente")

def test_sensor_color_lectura():
    """Test: Leer valores RGB del sensor"""
    if MODO_SIMULACION:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
    
    sensor = SensorColor(17, 27, 22, 23, 24)
    r, g, b = sensor.leer_rgb()
    
    assert isinstance(r, int)
    assert isinstance(g, int)
    assert isinstance(b, int)
    print(f"  - Lectura RGB: R={r}, G={g}, B={b}")

def test_pinza_creacion():
    """Test: Crear control de pinza"""
    if MODO_SIMULACION:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
    
    pinza = ControlPinza(18)
    assert pinza is not None
    print("  - Control de pinza creado correctamente")

def test_pinza_movimiento():
    """Test: Mover pinza a diferentes ángulos"""
    if MODO_SIMULACION:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
    
    pinza = ControlPinza(18, angulo_abierto=90, angulo_cerrado=0)
    
    pinza.abrir()
    assert pinza.angulo_actual == 90
    
    pinza.cerrar()
    assert pinza.angulo_actual == 0
    
    print("  - Movimientos de pinza correctos")

def test_indicadores_creacion():
    """Test: Crear sistema de indicadores LED"""
    if MODO_SIMULACION:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
    
    leds = SistemaIndicadores(26, 19, 13)
    assert leds is not None
    print("  - Sistema de indicadores creado correctamente")

def test_indicadores_estados():
    """Test: Cambiar estados de LEDs"""
    if MODO_SIMULACION:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
    
    leds = SistemaIndicadores(26, 19, 13)
    
    estados = ['IDLE', 'MANUAL', 'LINEA', 'SUMO', 'LOGISTICA']
    for estado in estados:
        leds.indicar_estado(estado)
        assert leds.estado_actual == estado
    
    print(f"  - {len(estados)} estados probados correctamente")


# ===== TESTS DE INTEGRACIÓN =====

def test_integracion_telemetria_movimiento():
    """Test: Integración telemetría + movimiento simulado"""
    tel = SistemaTelemetria(archivo_log="test_integracion.json")
    
    # Simular secuencia de movimientos
    movimientos = ['avanzar', 'girar_izquierda', 'avanzar', 'detener']
    for mov in movimientos:
        tel.registrar_evento('MOVIMIENTO', {'accion': mov})
        time.sleep(0.1)
    
    stats = tel.obtener_estadisticas()
    assert stats['eventos_por_tipo']['MOVIMIENTO'] == len(movimientos)
    print(f"  - {len(movimientos)} movimientos registrados correctamente")

def test_integracion_sensor_color_pinza():
    """Test: Integración sensor color + pinza"""
    if MODO_SIMULACION:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
    
    sensor = SensorColor(17, 27, 22, 23, 24)
    pinza = ControlPinza(18)
    tel = SistemaTelemetria(archivo_log="test_color_pinza.json")
    
    # Simular ciclo: detectar color → agarrar
    color = sensor.leer_color()
    tel.registrar_evento('COLOR_DETECTADO', {'color': color})
    
    pinza.agarrar_objeto()
    tel.registrar_evento('OBJETO_AGARRADO', {})
    
    stats = tel.obtener_estadisticas()
    assert stats['total_eventos'] >= 2
    print("  - Ciclo detección + agarre simulado correctamente")

def test_integracion_leds_telemetria():
    """Test: Integración LEDs + telemetría"""
    if MODO_SIMULACION:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
    
    leds = SistemaIndicadores(26, 19, 13)
    tel = SistemaTelemetria(archivo_log="test_leds.json")
    
    estados = ['IDLE', 'BUSCANDO', 'TRANSPORTANDO', 'EXITO']
    for estado in estados:
        leds.indicar_estado(estado)
        tel.registrar_evento('CAMBIO_ESTADO', {'estado': estado})
    
    stats = tel.obtener_estadisticas()
    assert stats['eventos_por_tipo']['CAMBIO_ESTADO'] == len(estados)
    print(f"  - {len(estados)} cambios de estado registrados")


# ===== TESTS DE SIMULACIÓN =====

def test_simulacion_modo_logistica():
    """Test: Simulación completa del modo logística"""
    if MODO_SIMULACION:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
    
    tel = SistemaTelemetria(archivo_log="test_logistica.json")
    sensor = SensorColor(17, 27, 22, 23, 24)
    pinza = ControlPinza(18)
    leds = SistemaIndicadores(26, 19, 13)
    
    print("  - Iniciando simulación de modo logística...")
    
    # Estado 1: IR_A_RECOGIDA
    leds.indicar_estado('BUSCANDO')
    tel.registrar_evento('LOGISTICA', {'estado': 'IR_A_RECOGIDA'})
    time.sleep(0.5)
    
    # Estado 2: DETECTAR_COLOR
    leds.indicar_estado('CLASIFICANDO')
    color = sensor.leer_color()
    tel.registrar_evento('LOGISTICA', {'estado': 'DETECTAR_COLOR', 'color': color})
    time.sleep(0.5)
    
    # Estado 3: AGARRAR
    leds.indicar_estado('TRANSPORTANDO')
    pinza.agarrar_objeto(pausa_antes=0.2, pausa_despues=0.2)
    tel.registrar_evento('LOGISTICA', {'estado': 'AGARRAR'})
    
    # Estado 4: IR_A_ENTREGA
    tel.registrar_evento('LOGISTICA', {'estado': 'IR_A_ENTREGA'})
    time.sleep(0.5)
    
    # Estado 5: SOLTAR
    pinza.soltar_objeto(pausa_antes=0.2, pausa_despues=0.2)
    tel.registrar_evento('LOGISTICA', {'estado': 'SOLTAR'})
    
    # Estado 6: VOLVER
    tel.registrar_evento('LOGISTICA', {'estado': 'VOLVER'})
    leds.secuencia_exito()
    
    stats = tel.obtener_estadisticas()
    eventos_logistica = stats['eventos_por_tipo'].get('LOGISTICA', 0)
    assert eventos_logistica >= 6
    
    print(f"  - Ciclo logística completado: {eventos_logistica} estados")

def test_simulacion_calibracion():
    """Test: Simulación de calibración de sensores"""
    if MODO_SIMULACION:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
    
    cal = CalibradorSensores(5, 6, 13)
    tel = SistemaTelemetria(archivo_log="test_calibracion.json")
    
    print("  - Simulando calibración de sensores IR...")
    
    # Simular valores de calibración
    cal.umbral_linea = {
        'izq': 0.5,
        'cen': 0.5,
        'der': 0.5,
        'blanco': {'izq': 1.0, 'cen': 1.0, 'der': 1.0},
        'negro': {'izq': 0.0, 'cen': 0.0, 'der': 0.0}
    }
    
    cal._guardar_calibracion()
    tel.registrar_evento('CALIBRACION', {'umbrales': cal.umbral_linea})
    
    # Verificar que se guardó
    cal2 = CalibradorSensores(5, 6, 13)
    resultado = cal2.cargar_calibracion()
    
    assert resultado is not None
    assert 'izq' in resultado
    print("  - Calibración guardada y cargada correctamente")


# ===== TESTS DE RENDIMIENTO =====

def test_rendimiento_telemetria():
    """Test: Rendimiento del sistema de telemetría"""
    tel = SistemaTelemetria(archivo_log="test_rendimiento.json")
    
    n_eventos = 1000
    inicio = time.time()
    
    for i in range(n_eventos):
        tel.registrar_evento('RENDIMIENTO', {'iteracion': i})
    
    duracion = time.time() - inicio
    eventos_por_segundo = n_eventos / duracion
    
    print(f"  - {n_eventos} eventos en {duracion:.2f}s")
    print(f"  - Rendimiento: {eventos_por_segundo:.0f} eventos/segundo")
    
    assert eventos_por_segundo > 100  # Mínimo 100 eventos/s


# ===== MAIN =====

def main():
    """Ejecuta todos los tests"""
    print("\n" + "="*60)
    print("SUITE DE TESTING - ROBOT ASTI CHALLENGE v2.0")
    print("="*60)
    print(f"Modo: {'SIMULACIÓN' if MODO_SIMULACION else 'HARDWARE'}")
    print("="*60)
    
    runner = TestRunner()
    
    # Tests Unitarios
    print("\n### TESTS UNITARIOS ###")
    runner.ejecutar_test("Telemetría - Creación", test_telemetria_creacion)
    runner.ejecutar_test("Telemetría - Registro de eventos", test_telemetria_registro)
    runner.ejecutar_test("Telemetría - Estadísticas", test_telemetria_estadisticas)
    runner.ejecutar_test("Telemetría - Exportar CSV", test_telemetria_exportar_csv)
    runner.ejecutar_test("Calibrador - Creación", test_calibrador_creacion)
    runner.ejecutar_test("Sensor Color - Creación", test_sensor_color_creacion)
    runner.ejecutar_test("Sensor Color - Lectura RGB", test_sensor_color_lectura)
    runner.ejecutar_test("Pinza - Creación", test_pinza_creacion)
    runner.ejecutar_test("Pinza - Movimiento", test_pinza_movimiento)
    runner.ejecutar_test("Indicadores - Creación", test_indicadores_creacion)
    runner.ejecutar_test("Indicadores - Estados", test_indicadores_estados)
    
    # Tests de Integración
    print("\n### TESTS DE INTEGRACIÓN ###")
    runner.ejecutar_test("Integración - Telemetría + Movimiento", test_integracion_telemetria_movimiento)
    runner.ejecutar_test("Integración - Sensor Color + Pinza", test_integracion_sensor_color_pinza)
    runner.ejecutar_test("Integración - LEDs + Telemetría", test_integracion_leds_telemetria)
    
    # Tests de Simulación
    print("\n### TESTS DE SIMULACIÓN ###")
    runner.ejecutar_test("Simulación - Modo Logística Completo", test_simulacion_modo_logistica)
    runner.ejecutar_test("Simulación - Calibración", test_simulacion_calibracion)
    
    # Tests de Rendimiento
    print("\n### TESTS DE RENDIMIENTO ###")
    runner.ejecutar_test("Rendimiento - Telemetría", test_rendimiento_telemetria)
    
    # Generar reporte final
    exito = runner.generar_reporte()
    
    # Limpiar archivos de test
    import os
    archivos_test = [
        'test_telemetria.json', 'test_export.csv', 'test_integracion.json',
        'test_color_pinza.json', 'test_leds.json', 'test_logistica.json',
        'test_calibracion.json', 'test_rendimiento.json', 'calibracion.json'
    ]
    
    for archivo in archivos_test:
        try:
            if os.path.exists(archivo):
                os.remove(archivo)
        except:
            pass
    
    return 0 if exito else 1


if __name__ == "__main__":
    sys.exit(main())
