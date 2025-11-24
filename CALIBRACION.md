# 📐 Guía de Calibración - Robot ASTI Challenge

## 🎯 Objetivo

Esta guía te ayudará a calibrar todos los sensores del robot para obtener el máximo rendimiento en competición.

---

## 1. Calibración de Sensores IR (Seguimiento de Línea)

### ¿Cuándo calibrar?
- **Antes de cada competición**
- Cuando cambies de superficie (diferente color/material)
- Si el robot no sigue bien la línea

### Proceso Automático

```bash
cd robot_rpi
sudo python3 calibrador.py
```

El script te guiará paso a paso:

1. **Superficie Blanca:**
   - Coloca el robot sobre superficie blanca
   - Espera 5 segundos
   - El sistema leerá los valores automáticamente

2. **Línea Negra:**
   - Coloca el robot sobre la línea negra
   - Espera 5 segundos
   - El sistema calculará los umbrales óptimos

3. **Guardado:**
   - La calibración se guarda en `calibracion.json`
   - Se carga automáticamente al iniciar el robot

### Verificación

```python
# Desde Python
from calibrador import CalibradorSensores
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
calibrador = CalibradorSensores(5, 6, 13)
calibrador.cargar_calibracion()
calibrador.verificar_calibracion(duracion=10)
```

---

## 2. Calibración de Sensor de Color

### ¿Cuándo calibrar?
- **Antes de usar el modo logística**
- Cuando cambies la iluminación del entorno
- Si el sensor no detecta bien los colores

### Proceso

```bash
cd robot_rpi
sudo python3 sensor_color.py
```

O desde el código:

```python
from sensor_color import SensorColor
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
sensor = SensorColor(17, 27, 22, 23, 24)

# Calibrar colores básicos
sensor.calibrar_colores_basicos()

# O calibrar un color específico
sensor.calibrar_color("ROJO", n_muestras=10)
sensor.calibrar_color("VERDE", n_muestras=10)
sensor.calibrar_color("AZUL", n_muestras=10)
```

### Consejos
- Usa objetos con colores sólidos y uniformes
- Calibra con la misma iluminación que usarás en competición
- Mantén el sensor a 2-3 cm del objeto

---

## 3. Calibración de Pinza/Servo

### ¿Cuándo calibrar?
- **Al montar la pinza por primera vez**
- Si cambias el servo
- Si la pinza no agarra bien

### Proceso

```bash
cd robot_rpi
sudo python3 pinza.py
```

Esto ejecutará un test completo de movimiento.

### Ajuste Manual

Edita `pinza.py` y ajusta los ángulos:

```python
pinza = ControlPinza(
    pin_servo=18,
    angulo_abierto=90,   # Ajustar según tu pinza
    angulo_cerrado=0     # Ajustar según tu pinza
)
```

**Cómo encontrar los ángulos correctos:**

1. Empieza con `angulo_abierto=90` y `angulo_cerrado=0`
2. Ejecuta el test
3. Observa si la pinza abre/cierra completamente
4. Ajusta los valores en incrementos de 10 grados
5. Repite hasta que funcione perfectamente

---

## 4. Calibración de Sensor Ultrasónico

### ¿Cuándo calibrar?
- Generalmente **no requiere calibración**
- Solo verificar funcionamiento

### Verificación

```python
from robot_rpi_mejorado import medir_distancia
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
# Configurar pines...

while True:
    dist = medir_distancia()
    print(f"Distancia: {dist:.1f} cm")
    time.sleep(0.5)
```

### Solución de Problemas

- **Lecturas erráticas:** Verifica conexiones
- **Siempre -1:** Revisa pines TRIGGER y ECHO
- **Valores muy altos:** Aumenta timeout en código

---

## 5. Calibración de Sensores de Borde

### ¿Cuándo calibrar?
- Al cambiar de ring de sumo
- Si el robot no detecta los bordes

### Proceso

Los sensores de borde son digitales (0 o 1):
- **0 (LOW):** Superficie negra (dentro del ring)
- **1 (HIGH):** Superficie blanca (borde del ring)

### Verificación

```python
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
BORDE_IZQ = 16
BORDE_DER = 19

GPIO.setup(BORDE_IZQ, GPIO.IN)
GPIO.setup(BORDE_DER, GPIO.IN)

while True:
    izq = GPIO.input(BORDE_IZQ)
    der = GPIO.input(BORDE_DER)
    print(f"Izq: {izq} | Der: {der}")
    time.sleep(0.2)
```

### Ajuste

Si los valores están invertidos, modifica en `robot_rpi_mejorado.py`:

```python
# Cambiar:
if borde_izq == 1 or borde_der == 1:
# Por:
if borde_izq == 0 or borde_der == 0:
```

---

## 6. Calibración de Parámetros PID

### ¿Cuándo calibrar?
- **Para optimizar velocidad en siguelíneas**
- Si el robot oscila mucho o es muy lento

### Parámetros Actuales

En `robot_rpi_mejorado.py`:

```python
pid = ControladorPID(kp=1.5, ki=0.1, kd=0.5)
```

### Método de Ajuste

1. **Kp (Proporcional):**
   - Empieza con `kp=1.0`
   - Aumenta hasta que el robot siga la línea
   - Si oscila mucho, reduce
   - Valor típico: 1.0 - 2.0

2. **Kd (Derivativo):**
   - Empieza con `kd=0.5`
   - Aumenta para reducir oscilaciones
   - Valor típico: 0.3 - 1.0

3. **Ki (Integral):**
   - Empieza con `ki=0.0`
   - Aumenta solo si hay error constante
   - Valor típico: 0.0 - 0.2

### Proceso de Ajuste

```python
# 1. Solo P
pid = ControladorPID(kp=1.5, ki=0.0, kd=0.0)
# Prueba y ajusta kp

# 2. Añadir D
pid = ControladorPID(kp=1.5, ki=0.0, kd=0.5)
# Ajusta kd para suavizar

# 3. Añadir I (opcional)
pid = ControladorPID(kp=1.5, ki=0.1, kd=0.5)
# Solo si hay error persistente
```

---

## 7. Calibración de Velocidades

### Velocidad Base

En `robot_rpi_mejorado.py`:

```python
velocidad_base = 80  # 0-100%
```

### Ajuste por Modo

```python
# Siguelíneas: Equilibrio velocidad/precisión
velocidad_linea = 75  # Más lento en curvas cerradas

# Sumo: Máxima potencia
velocidad_sumo = 100

# Logística: Velocidad moderada
velocidad_logistica = 70
```

### Encontrar Velocidad Óptima

1. Empieza con 50%
2. Aumenta de 10 en 10 hasta que:
   - Siguelíneas: El robot empiece a salirse
   - Sumo: Los motores patinen
3. Reduce 10-20% para margen de seguridad

---

## 8. Checklist de Calibración Pre-Competición

### 1 Semana Antes
- [ ] Calibrar sensores IR en superficie de práctica
- [ ] Ajustar parámetros PID
- [ ] Calibrar sensor de color (si aplica)
- [ ] Verificar pinza (si aplica)

### 1 Día Antes
- [ ] Verificar todas las calibraciones
- [ ] Probar en condiciones similares a competición
- [ ] Guardar backup de `calibracion.json`

### El Día de la Competición
- [ ] Llegar temprano para calibrar en pista real
- [ ] Calibrar sensores IR en superficie de competición
- [ ] Probar velocidades óptimas
- [ ] Verificar sensores de borde en ring de sumo
- [ ] Guardar calibración final

---

## 9. Solución de Problemas Comunes

### El robot no sigue bien la línea
1. Recalibrar sensores IR
2. Verificar altura de sensores (2-5mm del suelo)
3. Ajustar parámetros PID
4. Comprobar que los sensores están limpios

### El sensor de color no detecta bien
1. Recalibrar con iluminación actual
2. Verificar distancia al objeto (2-3cm)
3. Usar objetos con colores sólidos
4. Aumentar número de muestras en calibración

### La pinza no agarra bien
1. Ajustar ángulos de apertura/cierre
2. Verificar fuerza del servo
3. Comprobar que el objeto está centrado
4. Ajustar tiempos de pausa

### El robot se sale del ring en sumo
1. Verificar sensores de borde
2. Reducir velocidad de ataque
3. Aumentar tiempo de retroceso al detectar borde
4. Comprobar que los sensores están a ras del suelo

---

## 10. Archivos de Calibración

### Ubicación
```
robot_rpi/
├── calibracion.json          # Sensores IR
├── calibracion_color.json    # Sensor de color (si se implementa guardado)
└── logs/                     # Telemetría de pruebas
```

### Backup

```bash
# Hacer backup
cp calibracion.json calibracion_backup.json

# Restaurar backup
cp calibracion_backup.json calibracion.json
```

---

