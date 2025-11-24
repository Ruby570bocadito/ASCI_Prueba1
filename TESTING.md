# 🧪 Guía de Testing - Robot ASTI Challenge v2.0

## 📋 Resumen

Se han creado **2 suites de testing** para validar todas las funcionalidades implementadas:

1. **`test_rapido.py`** - Validación rápida (5-10 segundos)
2. **`test_suite.py`** - Suite completa (1-2 minutos)

Ambos tests funcionan **sin hardware** usando simulación de GPIO.

---

## ✅ Tests Implementados

### Tests Unitarios (11)
- ✓ Telemetría - Creación
- ✓ Telemetría - Registro de eventos
- ✓ Telemetría - Estadísticas
- ✓ Telemetría - Exportar CSV
- ✓ Calibrador - Creación
- ✓ Sensor Color - Creación y lectura
- ✓ Pinza - Creación y movimiento
- ✓ Indicadores LED - Creación y estados

### Tests de Integración (3)
- ✓ Telemetría + Movimiento
- ✓ Sensor Color + Pinza
- ✓ LEDs + Telemetría

### Tests de Simulación (2)
- ✓ Modo Logística completo
- ✓ Calibración de sensores

### Tests de Rendimiento (1)
- ✓ Rendimiento de telemetría (>100 eventos/s)

---

## 🚀 Cómo Ejecutar los Tests

### Opción 1: Test Rápido (Recomendado)

```bash
cd robot_rpi
python test_rapido.py
```

**Duración:** ~10 segundos  
**Qué hace:** Verifica que todos los módulos se importen y funcionen básicamente

**Salida esperada:**
```
============================================================
TEST RÁPIDO DE VALIDACIÓN - ROBOT ASTI v2.0
============================================================

### TESTS DE IMPORTACIÓN ###
[TEST] Importar telemetria.py... ✓ OK
[TEST] Importar calibrador.py... ✓ OK
[TEST] Importar sensor_color.py... ✓ OK
[TEST] Importar pinza.py... ✓ OK
[TEST] Importar indicadores.py... ✓ OK

### TESTS FUNCIONALES ###
[TEST] Telemetría funcional... ✓ OK
[TEST] Sensor color - lectura... ✓ OK
[TEST] Pinza - movimiento... ✓ OK
[TEST] LEDs - estados... ✓ OK

### TEST DE INTEGRACIÓN ###
[TEST] Integración completa... ✓ OK

============================================================
REPORTE FINAL
============================================================
Tests ejecutados: 10
Tests exitosos:   10 ✓
Tests fallidos:   0 ✗

🎉 ¡TODOS LOS TESTS PASARON!
✅ El código está listo para usar con hardware
============================================================
```

### Opción 2: Suite Completa

```bash
cd robot_rpi
python test_suite.py
```

**Duración:** ~1-2 minutos  
**Qué hace:** Tests exhaustivos de todas las funcionalidades

---

## 🔧 Testing con Hardware Real

### Cambiar a Modo Hardware

Editar `test_suite.py` línea 15:

```python
# Cambiar de:
MODO_SIMULACION = True

# A:
MODO_SIMULACION = False
```

### Requisitos para Testing con Hardware

1. **Raspberry Pi** con GPIO configurado
2. **Hardware conectado** según pines definidos
3. **Ejecutar con sudo:**

```bash
sudo python3 test_suite.py
```

---

## 📊 Resultados Esperados

### Test Rápido
- **10 tests** deben pasar
- **0 fallos**
- Duración: ~10 segundos

### Suite Completa
- **17 tests** deben pasar
- **0 fallos**
- Duración: ~1-2 minutos

---

## 🐛 Solución de Problemas

### Error: "ModuleNotFoundError"

**Problema:** No encuentra los módulos

**Solución:**
```bash
cd robot_rpi
python test_rapido.py  # Asegúrate de estar en el directorio correcto
```

### Error: "RPi.GPIO not found"

**Problema:** Intentando ejecutar en modo hardware sin RPi.GPIO

**Solución:** Los tests usan simulación por defecto, no debería pasar

### Tests se cuelgan

**Problema:** Algún test está esperando indefinidamente

**Solución:**
1. Presiona `Ctrl+C` para cancelar
2. Usa `test_rapido.py` en lugar de `test_suite.py`
3. Revisa que no haya procesos previos colgados

---

## 📝 Testing Manual (Sin Scripts)

Si los scripts no funcionan, puedes probar manualmente:

### 1. Test de Telemetría

```python
from telemetria import SistemaTelemetria

tel = SistemaTelemetria()
tel.registrar_evento('TEST', {'valor': 123})
stats = tel.obtener_estadisticas()
print(stats)
```

### 2. Test de Sensor de Color

```python
# Mock GPIO primero
import sys
class MockGPIO:
    BCM = 'BCM'
    OUT = 'OUT'
    IN = 'IN'
    @staticmethod
    def setmode(m): pass
    @staticmethod
    def setwarnings(f): pass
    @staticmethod
    def setup(p, m, **k): pass
    @staticmethod
    def input(p): return 0
    class PWM:
        def __init__(self, p, f): pass
        def start(self, d): pass
        def ChangeDutyCycle(self, d): pass

sys.modules['RPi'] = type(sys)('RPi')
sys.modules['RPi.GPIO'] = MockGPIO()

# Ahora importar
from sensor_color import SensorColor
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
sensor = SensorColor(17, 27, 22, 23, 24)
r, g, b = sensor.leer_rgb()
print(f"RGB: {r}, {g}, {b}")
```

### 3. Test de Pinza

```python
# (Usar mismo mock de arriba)
from pinza import ControlPinza
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
pinza = ControlPinza(18)
pinza.abrir()
pinza.cerrar()
print("Pinza OK")
```

### 4. Test de LEDs

```python
# (Usar mismo mock de arriba)
from indicadores import SistemaIndicadores
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
leds = SistemaIndicadores(26, 19, 13)
leds.indicar_estado('IDLE')
leds.indicar_estado('LINEA')
print(f"Estado actual: {leds.estado_actual}")
```

---

## 🎯 Checklist de Validación

Antes de competir, verifica:

### Código
- [ ] `test_rapido.py` pasa todos los tests
- [ ] No hay errores de importación
- [ ] Todos los módulos se cargan correctamente

### Hardware (cuando lo tengas)
- [ ] Tests con `MODO_SIMULACION = False` pasan
- [ ] Motores responden correctamente
- [ ] Sensores IR leen valores
- [ ] Sensor ultrasónico mide distancias
- [ ] LEDs se encienden
- [ ] Servo de pinza se mueve
- [ ] Sensor de color detecta colores

### Funcionalidad
- [ ] Modo manual funciona
- [ ] Modo línea sigue la línea
- [ ] Modo sumo detecta oponente
- [ ] Modo logística completa ciclo
- [ ] Telemetría guarda logs
- [ ] Calibración se guarda/carga

---

## 📈 Próximos Pasos Después del Testing

### Si todos los tests pasan:

1. **Probar con hardware real**
   - Conectar componentes
   - Ejecutar `test_suite.py` en modo hardware
   - Calibrar sensores

2. **Optimizar parámetros**
   - Ajustar PID según circuito
   - Calibrar velocidades
   - Ajustar tiempos de ciclo

3. **Generar evidencias**
   - Ejecutar modos en condiciones reales
   - Descargar logs de telemetría
   - Crear gráficas para memoria

### Si hay fallos:

1. **Revisar errores**
   - Leer mensajes de error
   - Verificar importaciones
   - Comprobar sintaxis

2. **Debugging**
   - Ejecutar tests individuales
   - Usar `print()` para debug
   - Revisar logs de telemetría

3. **Solicitar ayuda**
   - Compartir mensaje de error
   - Indicar qué test falla
   - Mostrar código relevante

---

## 🔍 Interpretación de Resultados

### ✓ OK - Test Pasó
- El módulo funciona correctamente
- No se encontraron errores
- Listo para usar

### ✗ FALLO - Test Falló
- Hay un error en el código
- Revisar mensaje de error
- Corregir antes de continuar

### Ejemplos de Errores Comunes

**Error: "assert tel is not None"**
- Problema: El objeto no se creó
- Solución: Revisar constructor de la clase

**Error: "ModuleNotFoundError: No module named 'X'"**
- Problema: Falta un archivo
- Solución: Verificar que el archivo existe

**Error: "AttributeError: 'X' object has no attribute 'Y'"**
- Problema: Falta un método o propiedad
- Solución: Revisar implementación de la clase

---

## 📚 Archivos de Testing

```
robot_rpi/
├── test_rapido.py      # Test rápido de validación
├── test_suite.py       # Suite completa de tests
└── logs/               # Logs generados por tests (temporal)
```

---

## 💡 Consejos

1. **Ejecuta test_rapido.py primero** - Es más rápido y detecta problemas básicos
2. **No te preocupes por warnings** - Solo importan los errores
3. **Los tests limpian archivos temporales** - No dejan basura
4. **Usa modo simulación para desarrollo** - No necesitas hardware
5. **Cambia a modo hardware solo para validación final** - Cuando tengas todo conectado

---

## 🎉 Conclusión

Los tests están diseñados para:

✅ **Validar que el código funciona** sin hardware  
✅ **Detectar errores temprano** antes de competir  
✅ **Dar confianza** de que todo está bien  
✅ **Facilitar debugging** con mensajes claros

**Si `test_rapido.py` pasa todos los tests, el código está listo para usar con hardware.**

---

**Última actualización:** 2025-11-24  
**Versión:** 2.0
