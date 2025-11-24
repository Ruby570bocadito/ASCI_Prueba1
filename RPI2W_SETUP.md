# 🔧 Raspberry Pi 2 W - Guía de Configuración

Esta guía específica te ayudará a configurar y optimizar el robot para **Raspberry Pi 2 W**.

## 📌 Especificaciones RPi 2 W

- **CPU**: Single-core 1GHz ARMv7
- **RAM**: 512MB
- **WiFi**: 802.11n integrado
- **GPIO**: 40 pines (compatible con RPi 3/4)

> [!IMPORTANT]
> La RPi 2 W tiene menos recursos que modelos superiores. El código ha sido optimizado específicamente para este modelo.

---

## 🚀 Instalación Inicial

### 1. Preparar Sistema Operativo

```bash
# Actualizar sistema
sudo apt update
sudo apt upgrade -y

# Instalar dependencias del sistema
sudo apt install -y python3-pip python3-dev python3-rpi.gpio
```

### 2. Instalar Dependencias Python

```bash
cd robot_rpi

# Instalar con pip3
pip3 install -r requirements.txt

# Si hay problemas de memoria, instalar una por una:
pip3 install Flask==2.3.0
pip3 install flask-socketio==5.3.0
pip3 install RPi.GPIO==0.7.1
pip3 install python-socketio==5.9.0
pip3 install eventlet==0.33.3
```

### 3. Habilitar GPIO

```bash
# Configurar Raspberry Pi
sudo raspi-config

# Navegar a:
# 3. Interface Options → I4 SPI → Enable
# 3. Interface Options → I5 I2C → Enable (opcional)
```

---

## ⚙️ Optimizaciones para RPi 2 W

El código `robot_rpi.py` incluye las siguientes optimizaciones:

### 1. PWM Reducido
```python
# 500Hz en lugar de 1000Hz para reducir carga CPU
pwm_izq = GPIO.PWM(MOTOR_IZQ_PWM, 500)
pwm_der = GPIO.PWM(MOTOR_DER_PWM, 500)
```

### 2. Delays Aumentados
```python
# 0.1s en lugar de 0.05s en loops autónomos
time.sleep(0.1)  # Reduce uso de CPU
```

### 3. Garbage Collection
```python
import gc
# Libera memoria después de cada modo
gc.collect()
```

### 4. Eventlet Async
```python
# Mejor rendimiento para WebSocket
socketio.run(app, async_mode='eventlet', log_output=False)
```

---

## 🔋 Gestión de Energía

### Configurar para Máximo Rendimiento

```bash
# Editar config.txt
sudo nano /boot/config.txt

# Añadir al final:
# Overclock moderado (opcional, bajo tu responsabilidad)
arm_freq=1000
core_freq=500
sdram_freq=450
over_voltage=2

# Guardar: Ctrl+O, Enter, Ctrl+X
sudo reboot
```

> [!WARNING]
> El overclock puede causar inestabilidad. Probar bien antes de competición.

### Reducir Consumo en Idle

```bash
# Deshabilitar servicios innecesarios
sudo systemctl disable bluetooth
sudo systemctl disable avahi-daemon
```

---

## 📡 Configuración WiFi

### Conectar a Red WiFi

```bash
# Editar configuración WiFi
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf

# Añadir:
network={
    ssid="TU_RED_WIFI"
    psk="TU_CONTRASEÑA"
}

# Guardar y reiniciar WiFi
sudo systemctl restart dhcpcd
```

### Crear Punto de Acceso (Modo AP)

Para control directo sin router:

```bash
# Instalar hostapd y dnsmasq
sudo apt install -y hostapd dnsmasq

# Configurar hostapd
sudo nano /etc/hostapd/hostapd.conf
```

Contenido:
```
interface=wlan0
driver=nl80211
ssid=Robot_ASTI
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=robot2024
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
```

```bash
# Habilitar hostapd
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl start hostapd
```

Ahora el robot creará su propia red WiFi: `Robot_ASTI` (contraseña: `robot2024`)

---

## 🏃 Ejecución Automática al Inicio

### Crear Servicio Systemd

```bash
# Crear archivo de servicio
sudo nano /etc/systemd/system/robot.service
```

Contenido:
```ini
[Unit]
Description=Robot Control Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/robot_rpi
ExecStart=/usr/bin/python3 /home/pi/robot_rpi/robot_rpi.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# Habilitar servicio
sudo systemctl daemon-reload
sudo systemctl enable robot.service
sudo systemctl start robot.service

# Verificar estado
sudo systemctl status robot.service
```

Ahora el servidor se iniciará automáticamente al encender la Raspberry Pi.

---

## 🧪 Testing en RPi 2 W

### Test de Rendimiento

```bash
# Ejecutar test de hardware
sudo python3 test_hardware.py

# Monitorear CPU y memoria
htop
# (Instalar con: sudo apt install htop)
```

### Verificar Temperatura

```bash
# Ver temperatura CPU
vcgencmd measure_temp

# Si supera 70°C, considera añadir disipador
```

---

## 🐛 Troubleshooting RPi 2 W

### Servidor muy lento

**Solución**:
```bash
# Reducir calidad de logs
# En robot_rpi.py, línea de socketio.run:
log_output=False  # Ya está configurado
```

### Memoria insuficiente

**Solución**:
```bash
# Aumentar swap
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Cambiar CONF_SWAPSIZE=100 a CONF_SWAPSIZE=512
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

### WiFi inestable

**Solución**:
```bash
# Deshabilitar power management WiFi
sudo nano /etc/rc.local

# Añadir antes de "exit 0":
/sbin/iwconfig wlan0 power off

# Guardar y reiniciar
sudo reboot
```

---

## 📊 Comparación de Rendimiento

| Característica | RPi 3/4 | RPi 2 W (Optimizado) |
|----------------|---------|----------------------|
| PWM Frecuencia | 1000Hz | 500Hz |
| Loop Delay | 50ms | 100ms |
| Async Mode | Threading | Eventlet |
| Memoria Libre | ~300MB | ~150MB |
| CPU Uso (idle) | ~5% | ~15% |
| CPU Uso (activo) | ~20% | ~40% |

---

## 💡 Consejos para RPi 2 W

1. **Batería**: Usar regulador de 5V estable (mínimo 2A)
2. **Disipador**: Recomendado para uso prolongado
3. **SD Card**: Clase 10 o superior para mejor rendimiento
4. **Overclock**: Solo si es necesario, probar estabilidad
5. **Servicios**: Deshabilitar todo lo innecesario (Bluetooth, etc.)

---

## 🔌 Diagrama de Alimentación

```
Batería (7.4V - 12V)
    │
    ├─► L298N (Motores) ──► Motor Izq/Der
    │
    └─► Regulador 5V 2A ──► Raspberry Pi 2 W
                        └─► Sensores (5V)
```

> [!CAUTION]
> Nunca alimentar RPi directamente desde batería sin regulador. Puede dañar la placa.

---

## ✅ Checklist RPi 2 W

- [ ] Sistema operativo actualizado
- [ ] Dependencias Python instaladas
- [ ] GPIO habilitado en raspi-config
- [ ] WiFi configurado correctamente
- [ ] Servicio systemd configurado (opcional)
- [ ] Temperatura CPU < 70°C bajo carga
- [ ] Test de hardware completado exitosamente
- [ ] Interfaz web accesible desde móvil

---

**¡Tu Raspberry Pi 2 W está lista para la competición! 🏁**
