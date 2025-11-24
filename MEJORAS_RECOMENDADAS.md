# 🚀 Mejoras Recomendadas para ASTI Robotics Challenge 2025/26

## 📋 Análisis de Requisitos del Desafío "Automatiza el futuro"

Basado en las bases del ASTI Robotics Challenge 2025/26, he identificado las mejoras prioritarias para maximizar vuestras posibilidades de éxito.

---

## 🎯 PRIORIDADES CRÍTICAS

### ✅ Lo que ya tenéis bien implementado:
- ✓ Control dual (manual y autónomo)
- ✓ Interfaz web responsive
- ✓ Modos de competición (línea, sumo, manual)
- ✓ Sensores básicos (IR, ultrasónico, borde)
- ✓ Control por WiFi y Bluetooth
- ✓ Presupuesto dentro del límite (250€)

### ⚠️ Áreas críticas que necesitan mejora:

1. **Funcionalidades del desafío "Automatiza el futuro"** (CRÍTICO)
2. **Optimización de algoritmos de competición**
3. **Sistema de telemetría y logging**
4. **Calibración automática de sensores**
5. **Documentación del proyecto**

---

## 🔧 MEJORAS TÉCNICAS PRIORITARIAS

### 1. 🏭 Funcionalidades de Automatización Industrial (CRÍTICO)

El desafío requiere que el robot simule funciones de automatización industrial. **Actualmente faltan estas capacidades:**

#### A. Reconocimiento de colores/formas/señales
```python
# AÑADIR: Sensor de color TCS3200 o similar
# Permite clasificar objetos por color (simulando clasificación industrial)

class SensorColor:
    def __init__(self, s0, s1, s2, s3, out):
        self.s0 = s0
        self.s1 = s1
        self.s2 = s2
        self.s3 = s3
        self.out = out
        self._setup()
    
    def _setup(self):
        GPIO.setup([self.s0, self.s1, self.s2, self.s3], GPIO.OUT)
        GPIO.setup(self.out, GPIO.IN)
    
    def leer_color(self):
        # Leer frecuencia RGB
        r = self._leer_frecuencia('R')
        g = self._leer_frecuencia('G')
        b = self._leer_frecuencia('B')
        
        # Clasificar color
        return self._clasificar_color(r, g, b)
    
    def _clasificar_color(self, r, g, b):
        # Lógica de clasificación
        if r > g and r > b:
            return "ROJO"
        elif g > r and g > b:
            return "VERDE"
        elif b > r and b > g:
            return "AZUL"
        return "DESCONOCIDO"
```

**Aplicación práctica:** Clasificar objetos por color en la Gran Final (simula clasificación de productos en almacén).

#### B. Manipulación de objetos (brazo/pinza)
```cpp
// AÑADIR: Servo para pinza o brazo simple
#include <Servo.h>

Servo pinza;
#define SERVO_PIN 13

void setup() {
    pinza.attach(SERVO_PIN);
}

void abrirPinza() {
    pinza.write(90);  // Ajustar según tu servo
}

void cerrarPinza() {
    pinza.write(0);
}

void agarrarObjeto() {
    abrirPinza();
    delay(500);
    avanzar();
    delay(1000);
    detener();
    cerrarPinza();
    delay(500);
}
```

**Aplicación práctica:** Transportar objetos entre zonas (simula logística interna).

#### C. Comunicación de estado (LEDs/Display)
```python
# AÑADIR: LEDs de estado o display I2C
class SistemaIndicadores:
    def __init__(self):
        self.led_rojo = 26
        self.led_verde = 19
        self.led_azul = 13
        GPIO.setup([self.led_rojo, self.led_verde, self.led_azul], GPIO.OUT)
    
    def indicar_estado(self, estado):
        estados = {
            'IDLE': (0, 0, 1),      # Azul
            'BUSCANDO': (1, 1, 0),  # Amarillo
            'TRANSPORTANDO': (0, 1, 0),  # Verde
            'ERROR': (1, 0, 0)      # Rojo
        }
        
        r, g, b = estados.get(estado, (0, 0, 0))
        GPIO.output(self.led_rojo, r)
        GPIO.output(self.led_verde, g)
        GPIO.output(self.led_azul, b)
```

**Aplicación práctica:** Mostrar estado del robot al jurado (profesionalismo).

---

### 2. 📊 Sistema de Telemetría y Logging (IMPORTANTE)

Para la documentación del proyecto y debugging:

```python
import json
import datetime
import os

class SistemaTelemetria:
    def __init__(self, archivo_log="telemetria.json"):
        self.archivo = archivo_log
        self.datos = []
        self.inicio_sesion = datetime.datetime.now()
    
    def registrar_evento(self, tipo, datos):
        evento = {
            'timestamp': datetime.datetime.now().isoformat(),
            'tiempo_transcurrido': (datetime.datetime.now() - self.inicio_sesion).total_seconds(),
            'tipo': tipo,
            'datos': datos
        }
        self.datos.append(evento)
        
        # Guardar cada 10 eventos (optimizado para RPi 2 W)
        if len(self.datos) % 10 == 0:
            self.guardar()
    
    def guardar(self):
        with open(self.archivo, 'w') as f:
            json.dump(self.datos, f, indent=2)
    
    def obtener_estadisticas(self):
        return {
            'total_eventos': len(self.datos),
            'tiempo_total': (datetime.datetime.now() - self.inicio_sesion).total_seconds(),
            'eventos_por_tipo': self._contar_por_tipo()
        }
    
    def _contar_por_tipo(self):
        conteo = {}
        for evento in self.datos:
            tipo = evento['tipo']
            conteo[tipo] = conteo.get(tipo, 0) + 1
        return conteo

# Uso en robot_rpi.py
telemetria = SistemaTelemetria()

def avanzar():
    telemetria.registrar_evento('MOVIMIENTO', {'accion': 'avanzar', 'velocidad': velocidad_base})
    # ... código existente ...

def seguir_linea():
    telemetria.registrar_evento('MODO', {'modo': 'linea', 'iniciado': True})
    while robot_activo and modo_actual == "linea":
        izq, cen, der = GPIO.input(SENSOR_IZQ), GPIO.input(SENSOR_CEN), GPIO.input(SENSOR_DER)
        telemetria.registrar_evento('SENSORES_IR', {'izq': izq, 'cen': cen, 'der': der})
        # ... código existente ...
```

**Beneficios:**
- Datos para el apartado "Testing – Validaciones" del proyecto
- Análisis de rendimiento para optimización
- Evidencias para la memoria (gráficas, estadísticas)

---

### 3. 🎛️ Calibración Automática de Sensores

```python
class CalibradorSensores:
    def __init__(self):
        self.valores_ir = {'izq': [], 'cen': [], 'der': []}
        self.umbral_linea = None
    
    def calibrar_sensores_ir(self, duracion=5):
        """
        Calibración automática de sensores IR
        Mueve el robot sobre línea negra y superficie blanca
        """
        print("Iniciando calibración de sensores IR...")
        print("Coloca el robot sobre SUPERFICIE BLANCA")
        time.sleep(3)
        
        # Leer valores en blanco
        valores_blanco = self._leer_sensores_multiple(50)
        
        print("Ahora coloca el robot sobre LÍNEA NEGRA")
        time.sleep(3)
        
        # Leer valores en negro
        valores_negro = self._leer_sensores_multiple(50)
        
        # Calcular umbrales
        self.umbral_linea = {
            'izq': (valores_blanco['izq'] + valores_negro['izq']) / 2,
            'cen': (valores_blanco['cen'] + valores_negro['cen']) / 2,
            'der': (valores_blanco['der'] + valores_negro['der']) / 2
        }
        
        print(f"Calibración completada: {self.umbral_linea}")
        self._guardar_calibracion()
        return self.umbral_linea
    
    def _leer_sensores_multiple(self, n_lecturas):
        valores = {'izq': 0, 'cen': 0, 'der': 0}
        for _ in range(n_lecturas):
            valores['izq'] += GPIO.input(SENSOR_IZQ)
            valores['cen'] += GPIO.input(SENSOR_CEN)
            valores['der'] += GPIO.input(SENSOR_DER)
            time.sleep(0.01)
        
        return {k: v/n_lecturas for k, v in valores.items()}
    
    def _guardar_calibracion(self):
        with open('calibracion.json', 'w') as f:
            json.dump(self.umbral_linea, f)
```

**Beneficio:** Adaptación automática a diferentes superficies de competición.

---

### 4. 🏁 Optimización de Algoritmos de Competición

#### A. Siguelíneas mejorado (PID básico)

```python
class ControladorPID:
    def __init__(self, kp=1.0, ki=0.0, kd=0.0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.error_anterior = 0
        self.integral = 0
    
    def calcular(self, error):
        self.integral += error
        derivada = error - self.error_anterior
        salida = (self.kp * error) + (self.ki * self.integral) + (self.kd * derivada)
        self.error_anterior = error
        return salida

def seguir_linea_pid():
    """Seguimiento de línea con control PID para mayor suavidad"""
    pid = ControladorPID(kp=1.5, ki=0.1, kd=0.5)
    
    while robot_activo and modo_actual == "linea":
        izq = GPIO.input(SENSOR_IZQ)
        cen = GPIO.input(SENSOR_CEN)
        der = GPIO.input(SENSOR_DER)
        
        # Calcular error de posición
        # -1 = muy a la izquierda, 0 = centrado, 1 = muy a la derecha
        if cen == 0:
            error = 0
        elif izq == 0:
            error = -1
        elif der == 0:
            error = 1
        else:
            error = 0  # Perdió la línea
        
        # Calcular corrección
        correccion = pid.calcular(error)
        
        # Aplicar corrección a motores
        vel_izq = velocidad_base - correccion
        vel_der = velocidad_base + correccion
        
        # Limitar velocidades
        vel_izq = max(0, min(100, vel_izq))
        vel_der = max(0, min(100, vel_der))
        
        # Aplicar velocidades
        mover_motores_diferencial(vel_izq, vel_der)
        
        time.sleep(0.05)

def mover_motores_diferencial(vel_izq, vel_der):
    """Control diferencial de motores"""
    GPIO.output(MOTOR_IZQ_A, GPIO.HIGH if vel_izq > 0 else GPIO.LOW)
    GPIO.output(MOTOR_IZQ_B, GPIO.LOW if vel_izq > 0 else GPIO.HIGH)
    pwm_izq.ChangeDutyCycle(abs(vel_izq))
    
    GPIO.output(MOTOR_DER_A, GPIO.HIGH if vel_der > 0 else GPIO.LOW)
    GPIO.output(MOTOR_DER_B, GPIO.LOW if vel_der > 0 else GPIO.HIGH)
    pwm_der.ChangeDutyCycle(abs(vel_der))
```

**Beneficio:** Seguimiento más suave y rápido de líneas con curvas.

---

## 📝 MEJORAS EN DOCUMENTACIÓN DEL PROYECTO

### Parte 1: Diseño y desarrollo del robot

#### 2. Planificación y cronograma
```markdown
**Ejemplo de cronograma mejorado:**

| Fase | Actividad | Responsable | Fecha | Estado |
|------|-----------|-------------|-------|--------|
| Diseño | Selección de componentes | [Nombre] | 15/01 | ✅ |
| Diseño | Modelado 3D chasis | [Nombre] | 20/01 | ✅ |
| Construcción | Montaje mecánico | [Nombre] | 25/01 | ✅ |
| Programación | Código base Arduino | [Nombre] | 30/01 | ✅ |
| Programación | Interfaz web | [Nombre] | 05/02 | 🔄 |
| Testing | Pruebas siguelíneas | Equipo | 10/02 | ⏳ |
| Testing | Pruebas sumo | Equipo | 15/02 | ⏳ |
| Optimización | Ajuste PID | [Nombre] | 20/02 | ⏳ |
| Documentación | Memoria proyecto | Equipo | 25/02 | ⏳ |
```

#### 6. Presupuesto
```markdown
**Ejemplo detallado:**

| Componente | Cantidad | Precio Unit. | Total | Proveedor | Justificante |
|------------|----------|--------------|-------|-----------|--------------|
| Raspberry Pi 2 W | 1 | 35€ | 35€ | Amazon | ✅ |
| Arduino Nano | 1 | 8€ | 8€ | AliExpress | ✅ |
| L298N Driver | 2 | 3€ | 6€ | AliExpress | ✅ |
| Motores DC | 2 | 5€ | 10€ | Local | ✅ |
| Sensores IR | 3 | 2€ | 6€ | Amazon | ✅ |
| HC-SR04 | 1 | 3€ | 3€ | Amazon | ✅ |
| Batería LiPo | 1 | 25€ | 25€ | Hobbyking | ✅ |
| Chasis acrílico | 1 | 15€ | 15€ | Corte láser local | ✅ |
| Ruedas | 4 | 3€ | 12€ | Amazon | ✅ |
| Varios (cables, tornillos) | - | - | 20€ | Local | ✅ |
| **TOTAL** | | | **140€** | | |
| **Margen restante** | | | **110€** | | |
```

---

## 🏆 ESTRATEGIAS PARA LA GRAN FINAL

### Preparación de la presentación

#### Estructura recomendada (10-15 min):

1. **Introducción (1 min)**
   - Presentación del equipo
   - Eslogan/lema del proyecto
   - Problema que resuelve el robot

2. **Demostración en vivo (3 min)**
   - Video del robot en acción (modo logística)
   - Si es posible, demo en vivo

3. **Diseño técnico (3 min)**
   - Arquitectura del robot (diagrama)
   - Componentes clave y su función
   - Decisiones de diseño innovadoras

4. **Desarrollo del desafío "Automatiza el futuro" (4 min)**
   - Problema industrial identificado
   - Solución propuesta
   - Impacto esperado (educativo, social, industrial)
   - Evidencias de pruebas

5. **Aprendizajes y reflexión (2 min)**
   - Principales desafíos superados
   - Aprendizajes del equipo
   - Próximos pasos / mejoras futuras

6. **Cierre (1 min)**
   - Mensaje final
   - Agradecimientos

---

## 📊 CHECKLIST FINAL ANTES DE COMPETIR

### Hardware:
- [ ] Todos los sensores calibrados
- [ ] Motores funcionando correctamente
- [ ] Baterías completamente cargadas (+ 2 de repuesto)
- [ ] Conexiones soldadas (no solo cables sueltos)
- [ ] Robot dentro de dimensiones (250x250x250mm)
- [ ] Peso optimizado (máximo permitido)
- [ ] Ruedas con buena tracción
- [ ] Estructura robusta (resistente a impactos)

### Software:
- [ ] Código probado en todos los modos
- [ ] Sistema de telemetría funcionando
- [ ] Interfaz web accesible
- [ ] Calibración automática implementada
- [ ] Logs guardándose correctamente
- [ ] Código respaldado en GitHub/USB

### Documentación:
- [ ] Memoria completa (Parte 1 + Parte 2)
- [ ] Todos los apartados obligatorios incluidos
- [ ] Justificantes de gastos adjuntos
- [ ] Evidencias visuales (fotos, videos)
- [ ] Presentación preparada (PDF/PPT)
- [ ] Ensayo de presentación realizado

---

## 🎯 RESUMEN DE PRIORIDADES

### CRÍTICO (hacer antes de semifinales):
1. ✅ **Implementar funcionalidades de automatización** (sensor color, pinza, LEDs)
2. ✅ **Sistema de telemetría** para documentación
3. ✅ **Completar Parte 1 de la memoria** (apartados 1-6)
4. ✅ **Optimizar algoritmo siguelíneas** (PID básico)

### IMPORTANTE (hacer antes de la Gran Final):
5. ✅ **Completar Parte 2 de la memoria** (desafío "Automatiza el futuro")
6. ✅ **Preparar presentación** para el jurado
7. ✅ **Optimizar modo sumo**
8. ✅ **Calibración automática de sensores**

### OPCIONAL (mejoras adicionales):
9. ⭐ Dashboard web con gráficas en tiempo real
10. ⭐ Sistema de visión (cámara + OpenCV)
11. ⭐ Comunicación entre múltiples robots
12. ⭐ App móvil nativa (Android/iOS)

---

## 💡 CONSEJOS FINALES

### Técnicos:
- **Simplicidad > Complejidad:** Es mejor un robot simple que funcione bien que uno complejo que falle
- **Probar, probar, probar:** Cada cambio debe probarse exhaustivamente
- **Documentar todo:** Fotos, videos, logs → útil para la memoria
- **Backup siempre:** Código en GitHub, baterías de repuesto, plan B para demos

### De equipo:
- **Comunicación constante:** Reuniones semanales obligatorias
- **Roles claros:** Cada miembro debe saber qué hace
- **Aprender de errores:** Cada fallo es una oportunidad de mejora
- **Disfrutar el proceso:** ¡Es una experiencia única!

### De competición:
- **Conocer el reglamento:** Leer las bases varias veces
- **Visitar la pista antes:** Si es posible, familiarizarse con el entorno
- **Mantener la calma:** Los nervios son normales, respirar profundo
- **Espíritu ARC:** Colaboración, pasión, valentía, humildad, diversión

---

## 🚀 PRÓXIMOS PASOS INMEDIATOS

1. **Esta semana:**
   - [ ] Revisar este documento con todo el equipo
   - [ ] Priorizar mejoras según tiempo disponible
   - [ ] Asignar tareas a cada miembro
   - [ ] Crear cronograma detallado hasta semifinales

2. **Próximas 2 semanas:**
   - [ ] Implementar sistema de telemetría
   - [ ] Añadir sensor de color y pinza
   - [ ] Optimizar algoritmo siguelíneas
   - [ ] Completar apartados 1-6 de la memoria

3. **Antes de semifinales:**
   - [ ] Probar robot en condiciones de competición
   - [ ] Enviar preentrega del proyecto
   - [ ] Preparar baterías y herramientas
   - [ ] Ensayar presentación (si clasifican a final)

---

**¡Mucho éxito en el ASTI Robotics Challenge 2025/26!** 🏆🤖

*Recuerda: Lo importante no es solo ganar, sino aprender, disfrutar y conectar con otros apasionados de la robótica.*

---

**Documento creado:** 2025-11-24
**Versión:** 1.0
**Basado en:** Bases ASTI Robotics Challenge 2025/26 + Análisis de código actual
