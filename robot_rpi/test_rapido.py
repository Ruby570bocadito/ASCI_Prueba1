#!/usr/bin/env python3
"""
Test Rápido de Validación - Robot ASTI Challenge
Verifica que todos los módulos se importen y funcionen correctamente
"""

import sys
import time
from pathlib import Path

print("="*60)
print("TEST RÁPIDO DE VALIDACIÓN - ROBOT ASTI v2.0")
print("="*60)

# Mock de RPi.GPIO para testing sin hardware
class MockGPIO:
    BCM = 'BCM'
    OUT = 'OUT'
    IN = 'IN'
    HIGH = 1
    LOW = 0
    PUD_UP = 'PUD_UP'
    
    @staticmethod
    def setmode(mode): pass
    
    @staticmethod
    def setwarnings(flag): pass
    
    @staticmethod
    def setup(pin, mode, **kwargs): pass
    
    @staticmethod
    def output(pin, value): pass
    
    @staticmethod
    def input(pin): return 0
    
    @staticmethod
    def cleanup(): pass
    
    class PWM:
        def __init__(self, pin, freq): pass
        def start(self, duty): pass
        def ChangeDutyCycle(self, duty): pass
        def stop(self): pass

sys.modules['RPi'] = type(sys)('RPi')
sys.modules['RPi.GPIO'] = MockGPIO()

# Cambiar al directorio robot_rpi
import os
os.chdir(Path(__file__).parent)

tests_ok = 0
tests_fail = 0

def test(nombre, funcion):
    """Ejecuta un test"""
    global tests_ok, tests_fail
    try:
        print(f"\n[TEST] {nombre}...", end=" ")
        funcion()
        print("✓ OK")
        tests_ok += 1
    except Exception as e:
        print(f"✗ FALLO: {e}")
        tests_fail += 1

# ===== TESTS =====

def test_import_telemetria():
    from telemetria import SistemaTelemetria
    tel = SistemaTelemetria()
    assert tel is not None

def test_import_calibrador():
    from calibrador import CalibradorSensores
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    cal = CalibradorSensores(5, 6, 13)
    assert cal is not None

def test_import_sensor_color():
    from sensor_color import SensorColor
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    sensor = SensorColor(17, 27, 22, 23, 24)
    assert sensor is not None

def test_import_pinza():
    from pinza import ControlPinza
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    pinza = ControlPinza(18)
    assert pinza is not None

def test_import_indicadores():
    from indicadores import SistemaIndicadores
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    leds = SistemaIndicadores(26, 19, 13)
    assert leds is not None

def test_telemetria_funcional():
    from telemetria import SistemaTelemetria
    tel = SistemaTelemetria()
    tel.registrar_evento('TEST', {'valor': 123})
    stats = tel.obtener_estadisticas()
    assert stats['total_eventos'] >= 1

def test_sensor_color_lectura():
    from sensor_color import SensorColor
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    sensor = SensorColor(17, 27, 22, 23, 24)
    r, g, b = sensor.leer_rgb()
    assert isinstance(r, int) and isinstance(g, int) and isinstance(b, int)

def test_pinza_movimiento():
    from pinza import ControlPinza
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    pinza = ControlPinza(18)
    pinza.abrir()
    pinza.cerrar()
    assert True

def test_leds_estados():
    from indicadores import SistemaIndicadores
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    leds = SistemaIndicadores(26, 19, 13)
    leds.indicar_estado('IDLE')
    leds.indicar_estado('LINEA')
    assert leds.estado_actual == 'LINEA'

def test_integracion_completa():
    """Test de integración de todos los módulos"""
    from telemetria import SistemaTelemetria
    from sensor_color import SensorColor
    from pinza import ControlPinza
    from indicadores import SistemaIndicadores
    import RPi.GPIO as GPIO
    
    GPIO.setmode(GPIO.BCM)
    
    tel = SistemaTelemetria()
    sensor = SensorColor(17, 27, 22, 23, 24)
    pinza = ControlPinza(18)
    leds = SistemaIndicadores(26, 19, 13)
    
    # Simular ciclo logística
    leds.indicar_estado('BUSCANDO')
    tel.registrar_evento('INICIO_CICLO', {})
    
    color = sensor.leer_color()
    tel.registrar_evento('COLOR_DETECTADO', {'color': color})
    
    pinza.agarrar_objeto(pausa_antes=0.1, pausa_despues=0.1)
    tel.registrar_evento('OBJETO_AGARRADO', {})
    
    pinza.soltar_objeto(pausa_antes=0.1, pausa_despues=0.1)
    tel.registrar_evento('OBJETO_LIBERADO', {})
    
    leds.indicar_estado('EXITO')
    
    stats = tel.obtener_estadisticas()
    assert stats['total_eventos'] >= 4

# ===== EJECUTAR TESTS =====

print("\n### TESTS DE IMPORTACIÓN ###")
test("Importar telemetria.py", test_import_telemetria)
test("Importar calibrador.py", test_import_calibrador)
test("Importar sensor_color.py", test_import_sensor_color)
test("Importar pinza.py", test_import_pinza)
test("Importar indicadores.py", test_import_indicadores)

print("\n### TESTS FUNCIONALES ###")
test("Telemetría funcional", test_telemetria_funcional)
test("Sensor color - lectura", test_sensor_color_lectura)
test("Pinza - movimiento", test_pinza_movimiento)
test("LEDs - estados", test_leds_estados)

print("\n### TEST DE INTEGRACIÓN ###")
test("Integración completa", test_integracion_completa)

# ===== REPORTE FINAL =====

print("\n" + "="*60)
print("REPORTE FINAL")
print("="*60)
print(f"Tests ejecutados: {tests_ok + tests_fail}")
print(f"Tests exitosos:   {tests_ok} ✓")
print(f"Tests fallidos:   {tests_fail} ✗")

if tests_fail == 0:
    print("\n🎉 ¡TODOS LOS TESTS PASARON!")
    print("✅ El código está listo para usar con hardware")
else:
    print(f"\n⚠️  {tests_fail} tests fallaron")
    print("❌ Revisar errores antes de usar con hardware")

print("="*60)

# Limpiar archivos temporales
import os
for archivo in ['test_export.csv', 'calibracion.json']:
    try:
        if os.path.exists(archivo):
            os.remove(archivo)
    except:
        pass

# Limpiar directorio logs de tests
import shutil
if os.path.exists('logs'):
    try:
        shutil.rmtree('logs')
    except:
        pass

sys.exit(0 if tests_fail == 0 else 1)
