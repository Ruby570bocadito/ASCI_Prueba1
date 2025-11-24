# Robot ASTI Robotics Challenge 2025/26

Sistema completo de control para robot de competición ASTI con soporte para Arduino y Raspberry Pi, control por Bluetooth y WiFi, múltiples modos de competición, y funcionalidades de automatización industrial para el desafío "Automatiza el futuro".

## Características

### Funcionalidades Básicas
- **Múltiples Plataformas**: Arduino y Raspberry Pi
- **Control Dual**: Bluetooth y WiFi
- **Interfaz Web Responsive**: Optimizada para móvil y portátil
- **Control por Teclado**: Soporte WASD y flechas direccionales

### Modos de Competición
- 🎮 **Manual**: Control directo desde interfaz web o Bluetooth
- 📍 **Seguimiento de Línea PID**: Algoritmo mejorado con control PID para mayor velocidad y precisión
- ⚔️ **Sumo Mejorado**: Estrategia agresiva con búsqueda en espiral y ataque variable
- 🏭 **Logística (Automatización)**: Ciclo completo de clasificación y transporte de objetos

### Funcionalidades Avanzadas (Nuevas en v2.0)
- 📊 **Sistema de Telemetría**: Registro de eventos, estadísticas y generación de evidencias
- 🎛️ **Calibración Automática**: Adaptación a diferentes superficies de competición
- 🎨 **Sensor de Color**: Clasificación de objetos por color (automatización industrial)
- 🤏 **Control de Pinza**: Manipulación de objetos con servo
- 💡 **Indicadores LED RGB**: Comunicación visual de estado del robot
- 📈 **Dashboard Web**: Visualización de telemetría en tiempo real
- 💾 **Exportación de Datos**: Logs en JSON y CSV para análisis

## Instalación

### Arduino

1. **Conectar el hardware** según el diagrama de pines:

```
Motor Izquierdo:
  - IN1 → Pin 5
  - IN2 → Pin 6
  - ENA → Pin 9 (PWM)

Motor Derecho:
  - IN3 → Pin 7
  - IN4 → Pin 8
  - ENB → Pin 10 (PWM)

Sensores IR:
  - Izquierdo → Pin 2
  - Central → Pin 3
  - Derecho → Pin 4

Sensor Ultrasónico:
  - Trigger → Pin 11
  - Echo → Pin 12

Bluetooth HC-05:
  - TX → RX Arduino
  - RX → TX Arduino (con divisor de voltaje 5V→3.3V)
```

2. **Cargar el código**:
   - Abrir `robot_arduino/robot_arduino.ino` en Arduino IDE
   - Seleccionar placa y puerto
   - Subir el sketch

3. **Emparejar Bluetooth**:
   - Buscar dispositivo "HC-05" o similar
   - PIN por defecto: `1234` o `0000`
   - Conectar desde app de terminal Bluetooth

### Raspberry Pi

1. **Instalar dependencias**:

```bash
cd robot_rpi
pip3 install -r requirements.txt
```

2. **Conectar hardware** según pines GPIO:

```python
Motor Izquierdo: GPIO 17, 27, 22
Motor Derecho: GPIO 23, 24, 25
Sensores IR: GPIO 5, 6, 13
Ultrasónico: GPIO 20 (Trigger), 21 (Echo)
Sensores Borde: GPIO 16, 19
```

3. **Ejecutar servidor**:

```bash
sudo python3 robot_rpi.py
```

4. **Acceder a la interfaz web**:
   - El servidor mostrará la IP local
   - Abrir navegador en: `http://[IP_RASPBERRY]:5000`
   - Ejemplo: `http://192.168.1.100:5000`

## Uso

### Interfaz Web

1. **Conectar**: Abrir navegador y acceder a la IP del robot
2. **Seleccionar Modo**:
   - **Manual**: Usar botones direccionales o teclado
   - **Línea**: Robot sigue línea negra automáticamente
   - **Sumo**: Robot busca y empuja al oponente
3. **Ajustar Velocidad**: Usar slider (0-100%)
4. **Control por Teclado**:
   - `W/↑`: Adelante
   - `S/↓`: Atrás
   - `A/←`: Izquierda
   - `D/→`: Derecha
   - `Espacio`: Stop

### Control Bluetooth (Arduino)

Comandos disponibles por Serial/Bluetooth:

```
F  - Avanzar
B  - Retroceder
L  - Girar izquierda
R  - Girar derecha
S  - Detener
M1 - Modo Línea
M2 - Modo Sumo
M3 - Modo Manual
V[0-255] - Cambiar velocidad (ej: V200)
```

## Apps Recomendadas

### Android
- **Serial Bluetooth Terminal** (Play Store)
- **Bluetooth RC Controller** (Play Store)

### iOS
- **BLE Terminal** (App Store)
- Usar interfaz web (recomendado)

## 🔧 Configuración Avanzada

### Ajustar Sensores de Línea

En `robot_arduino.ino` o `robot_rpi.py`, modificar la lógica según tus sensores:

```cpp
// Arduino - Invertir lógica si es necesario
if (cen == 1) {  // Cambiar a 1 si sensor es activo-alto
    avanzar();
}
```

### Calibrar Velocidad

```cpp
// Arduino
int velocidadBase = 200;  // 0-255
int velocidadGiro = 150;
```

```python
# Raspberry Pi
velocidad_base = 80  # 0-100%
```

### Cambiar Pines

Modificar las constantes al inicio de cada archivo:

```cpp
// Arduino
#define MOTOR_IZQ_A 5  // Cambiar según tu conexión
```

```python
# Raspberry Pi
MOTOR_IZQ_A = 17  # Cambiar según tu GPIO
```

## Solución de Problemas

### Arduino no responde a Bluetooth
- Verificar conexión TX/RX (cruzados)
- Comprobar baudrate (9600 por defecto)
- Usar divisor de voltaje para RX del HC-05

### Raspberry Pi no inicia servidor
- Instalar dependencias: `pip3 install -r requirements.txt`
- Ejecutar con sudo: `sudo python3 robot_rpi.py`
- Verificar GPIO habilitado en `raspi-config`

### Motores no funcionan
- Verificar alimentación del driver L298N
- Comprobar conexiones de pines
- Probar con velocidad alta (>150 en Arduino, >70% en RPi)

### Sensores de línea no detectan
- Ajustar altura de sensores (2-5mm del suelo)
- Verificar lógica (activo-alto vs activo-bajo)
- Probar en Serial Monitor valores de sensores

### No se conecta a interfaz web
- Verificar IP con `hostname -I` en Raspberry Pi
- Comprobar firewall
- Asegurar que móvil/portátil está en misma red WiFi

## 📊 Diagrama de Conexión

```
┌─────────────────┐
│   Arduino/RPi   │
├─────────────────┤
│                 │
│  ┌───────────┐  │
│  │  L298N    │  │──► Motor Izquierdo
│  │  Driver   │  │──► Motor Derecho
│  └───────────┘  │
│                 │
│  Sensores IR    │──► Línea
│  HC-SR04        │──► Distancia
│  HC-05 (BT)     │──► Bluetooth
│  WiFi (RPi)     │──► Web Interface
└─────────────────┘
```

## 🏆 Consejos para Competición

### Seguimiento de Línea
- **Calibrar sensores antes de cada prueba** (ver `CALIBRACION.md`)
- Usar modo PID para mayor velocidad
- Ajustar parámetros Kp, Kd según el circuito
- Probar con diferentes superficies

### Sumo
- Maximizar peso del robot (dentro del reglamento)
- Usar ruedas con buena tracción
- Ajustar sensibilidad de borde según ring
- Modo sumo mejorado tiene estrategia más agresiva

### General
- Llevar baterías de repuesto cargadas
- Probar todos los modos antes de competir
- Tener cable USB para reprogramación rápida
- **Usar telemetría para análisis de rendimiento**
- **Calibrar en la superficie de competición**

---

## 🆕 Novedades Versión 2.0 (ASTI Challenge 2025/26)

### Sistema de Telemetría

Registra automáticamente todos los eventos del robot para análisis y documentación:

```bash
# Los logs se guardan automáticamente en robot_rpi/logs/
# Formato: YYYYMMDD_HHMMSS_telemetria.json
```

**Uso:**
- Descarga logs desde interfaz web (botón "Descargar Logs")
- Analiza rendimiento con datos JSON/CSV
- Genera gráficas para la memoria del proyecto

### Calibración Automática

Calibra sensores IR automáticamente:

```bash
cd robot_rpi
sudo python3 calibrador.py
```

Ver guía completa en [`CALIBRACION.md`](CALIBRACION.md)

### Modo Logística (Automatización)

Nuevo modo que simula automatización industrial:

1. **Ir a zona de recogida** (sigue línea)
2. **Detectar color** del objeto (sensor de color)
3. **Agarrar** objeto (pinza)
4. **Transportar** a zona de entrega
5. **Soltar** objeto
6. **Volver** a posición inicial

**Activar desde interfaz web:** Botón "Modo Logística" (M4)

### Indicadores LED

Estados visuales del robot:

| Color | Estado |
|-------|--------|
| 🔵 Azul | IDLE (esperando) |
| ⚪ Blanco | Manual |
| 🟢 Verde | Línea / Transportando |
| 🔴 Rojo | Sumo / Error |
| 🟡 Amarillo | Logística / Calibrando |
| 🟣 Magenta | Buscando |
| 🔷 Cian | Clasificando |

### Control PID

Seguimiento de línea mejorado con control PID:

- **Más rápido** en rectas
- **Más suave** en curvas
- **Menos oscilaciones**

Ajustar parámetros en `robot_rpi_mejorado.py`:

```python
pid = ControladorPID(kp=1.5, ki=0.1, kd=0.5)
```

---

## 📁 Estructura del Proyecto

```
Prueba/
├── robot_rpi/
│   ├── robot_rpi.py                 # Versión original
│   ├── robot_rpi_mejorado.py        # ⭐ Versión 2.0 mejorada
│   ├── telemetria.py                # Sistema de telemetría
│   ├── calibrador.py                # Calibración automática
│   ├── sensor_color.py              # Control sensor de color
│   ├── pinza.py                     # Control de pinza
│   ├── indicadores.py               # LEDs de estado
│   ├── requirements.txt             # Dependencias Python
│   ├── logs/                        # Logs de telemetría
│   └── calibracion.json             # Configuración de sensores
├── robot_arduino/
│   ├── robot_arduino.ino            # Código Arduino mejorado
│   └── test_arduino.ino             # Tests de hardware
├── web_interface/
│   ├── index.html                   # Interfaz web
│   ├── script.js                    # Lógica JavaScript
│   └── style.css                    # Estilos
├── README.md                        # Este archivo
├── MEJORAS_RECOMENDADAS.md          # Guía de mejoras
├── CALIBRACION.md                   # Guía de calibración
└── TESTING.md                       # Guía de testing
```

---

## 🚀 Inicio Rápido (Versión 2.0)

### Raspberry Pi

```bash
# 1. Instalar dependencias
cd robot_rpi
pip3 install -r requirements.txt

# 2. (Opcional) Calibrar sensores
sudo python3 calibrador.py

# 3. Ejecutar versión mejorada
sudo python3 robot_rpi_mejorado.py

# 4. Abrir navegador en http://[IP_RASPBERRY]:5000
```

### Características Automáticas

- ✅ Telemetría se inicia automáticamente
- ✅ LEDs muestran estado del robot
- ✅ Calibración se carga si existe
- ✅ Logs se guardan en `logs/`

---

## Documentación Adicional

- **[MEJORAS_RECOMENDADAS.md](MEJORAS_RECOMENDADAS.md)**: Guía completa de mejoras para ASTI Challenge
- **[CALIBRACION.md](CALIBRACION.md)**: Guía de calibración de todos los sensores
- **[TESTING.md](TESTING.md)**: Guía de pruebas y validación

---

## 🎯 Para el ASTI Robotics Challenge 2025/26

Este robot está optimizado para el desafío **"Automatiza el futuro"**:

### Funcionalidades Implementadas

✅ **Seguimiento de trayectorias** (modo línea PID)  
✅ **Reconocimiento de colores** (sensor TCS3200)  
✅ **Manipulación de objetos** (pinza con servo)  
✅ **Comunicación de estado** (LEDs RGB)  
✅ **Detección de obstáculos** (sensor ultrasónico)  
✅ **Optimización de energía** (telemetría de consumo)  
✅ **Sistema de telemetría** (evidencias para documentación)

### Documentación del Proyecto

El sistema de telemetría genera automáticamente:

- 📊 Estadísticas de rendimiento
- 📈 Datos para gráficas
- 📝 Evidencias para la memoria
- 🧪 Resultados de pruebas
