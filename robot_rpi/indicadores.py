#!/usr/bin/env python3
"""
Sistema de Indicadores LED RGB
Para comunicación de estado del robot
Robot ASTI Challenge
"""

import RPi.GPIO as GPIO
import time
import threading


class SistemaIndicadores:
    """Control de LEDs RGB para indicar estado del robot"""
    
    def __init__(self, pin_rojo, pin_verde, pin_azul):
        """
        Inicializa el sistema de indicadores
        
        Args:
            pin_rojo (int): Pin GPIO para LED rojo
            pin_verde (int): Pin GPIO para LED verde
            pin_azul (int): Pin GPIO para LED azul
        """
        self.pin_rojo = pin_rojo
        self.pin_verde = pin_verde
        self.pin_azul = pin_azul
        
        self.estado_actual = None
        self.efecto_activo = False
        self.thread_efecto = None
        
        self._setup()
    
    def _setup(self):
        """Configura los pines GPIO"""
        GPIO.setup(self.pin_rojo, GPIO.OUT)
        GPIO.setup(self.pin_verde, GPIO.OUT)
        GPIO.setup(self.pin_azul, GPIO.OUT)
        
        # Inicializar apagados
        self.apagar()
    
    def _set_color(self, rojo, verde, azul):
        """
        Establece el color RGB
        
        Args:
            rojo, verde, azul (bool): Estado de cada LED
        """
        GPIO.output(self.pin_rojo, GPIO.HIGH if rojo else GPIO.LOW)
        GPIO.output(self.pin_verde, GPIO.HIGH if verde else GPIO.LOW)
        GPIO.output(self.pin_azul, GPIO.HIGH if azul else GPIO.LOW)
    
    def indicar_estado(self, estado):
        """
        Indica un estado específico con color
        
        Args:
            estado (str): Estado a indicar
        """
        # Detener cualquier efecto activo
        self._detener_efecto()
        
        estados = {
            'IDLE': (0, 0, 1),           # Azul
            'MANUAL': (1, 1, 1),         # Blanco
            'LINEA': (0, 1, 0),          # Verde
            'SUMO': (1, 0, 0),           # Rojo
            'LOGISTICA': (1, 1, 0),      # Amarillo
            'BUSCANDO': (1, 0, 1),       # Magenta
            'TRANSPORTANDO': (0, 1, 0),  # Verde
            'CLASIFICANDO': (0, 1, 1),   # Cian
            'ERROR': (1, 0, 0),          # Rojo
            'CALIBRANDO': (1, 1, 0),     # Amarillo
            'EXITO': (0, 1, 0),          # Verde
        }
        
        if estado in estados:
            r, g, b = estados[estado]
            self._set_color(r, g, b)
            self.estado_actual = estado
            print(f"[LED] Estado: {estado}")
        else:
            print(f"[LED] Estado desconocido: {estado}")
            self.apagar()
    
    def apagar(self):
        """Apaga todos los LEDs"""
        self._detener_efecto()
        self._set_color(0, 0, 0)
        self.estado_actual = None
    
    def parpadear(self, estado, veces=3, intervalo=0.3):
        """
        Hace parpadear el LED en un color específico
        
        Args:
            estado (str): Estado/color a parpadear
            veces (int): Número de parpadeos
            intervalo (float): Tiempo entre parpadeos
        """
        for _ in range(veces):
            self.indicar_estado(estado)
            time.sleep(intervalo)
            self.apagar()
            time.sleep(intervalo)
    
    def _efecto_parpadeo_continuo(self, estado, intervalo):
        """Efecto de parpadeo continuo (thread)"""
        while self.efecto_activo:
            self.indicar_estado(estado)
            time.sleep(intervalo)
            self.apagar()
            time.sleep(intervalo)
    
    def parpadear_continuo(self, estado, intervalo=0.5):
        """
        Inicia parpadeo continuo en background
        
        Args:
            estado (str): Estado/color a parpadear
            intervalo (float): Tiempo entre parpadeos
        """
        self._detener_efecto()
        
        self.efecto_activo = True
        self.thread_efecto = threading.Thread(
            target=self._efecto_parpadeo_continuo,
            args=(estado, intervalo),
            daemon=True
        )
        self.thread_efecto.start()
        print(f"[LED] Parpadeo continuo: {estado}")
    
    def _efecto_fade(self):
        """Efecto de fade (requiere PWM, simplificado aquí)"""
        # Nota: Para fade real se necesitaría PWM
        # Esta es una versión simplificada
        while self.efecto_activo:
            self._set_color(1, 1, 1)
            time.sleep(0.5)
            self._set_color(0, 0, 0)
            time.sleep(0.5)
    
    def _detener_efecto(self):
        """Detiene cualquier efecto activo"""
        if self.efecto_activo:
            self.efecto_activo = False
            if self.thread_efecto:
                self.thread_efecto.join(timeout=1)
            self.thread_efecto = None
    
    def secuencia_inicio(self):
        """Secuencia de LEDs al iniciar el robot"""
        print("[LED] Secuencia de inicio...")
        
        # Rojo
        self._set_color(1, 0, 0)
        time.sleep(0.3)
        
        # Verde
        self._set_color(0, 1, 0)
        time.sleep(0.3)
        
        # Azul
        self._set_color(0, 0, 1)
        time.sleep(0.3)
        
        # Blanco
        self._set_color(1, 1, 1)
        time.sleep(0.3)
        
        # Apagar
        self.apagar()
        print("[LED] ✓ Secuencia completada")
    
    def secuencia_exito(self):
        """Secuencia de LEDs para indicar éxito"""
        print("[LED] ¡Éxito!")
        self.parpadear('EXITO', veces=5, intervalo=0.2)
    
    def secuencia_error(self):
        """Secuencia de LEDs para indicar error"""
        print("[LED] Error detectado")
        self.parpadear('ERROR', veces=3, intervalo=0.5)
    
    def test_completo(self):
        """Prueba todos los estados y efectos"""
        print("\n" + "="*50)
        print("TEST DE SISTEMA DE INDICADORES LED")
        print("="*50)
        
        # Probar todos los estados
        estados = ['IDLE', 'MANUAL', 'LINEA', 'SUMO', 'LOGISTICA', 
                   'BUSCANDO', 'TRANSPORTANDO', 'ERROR']
        
        print("\n1. Probando estados...")
        for estado in estados:
            print(f"   - {estado}")
            self.indicar_estado(estado)
            time.sleep(1)
        
        self.apagar()
        time.sleep(0.5)
        
        print("\n2. Probando parpadeo...")
        self.parpadear('EXITO', veces=3)
        time.sleep(0.5)
        
        print("\n3. Probando secuencias...")
        self.secuencia_inicio()
        time.sleep(0.5)
        self.secuencia_exito()
        
        print("\n✓ Test completado")
    
    def __del__(self):
        """Limpieza al destruir el objeto"""
        self._detener_efecto()
        self.apagar()


# Ejemplo de uso
if __name__ == "__main__":
    # Configurar GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # Pines de LEDs (ajustar según tu conexión)
    LED_ROJO = 26
    LED_VERDE = 19
    LED_AZUL = 13
    
    # Crear sistema de indicadores
    leds = SistemaIndicadores(LED_ROJO, LED_VERDE, LED_AZUL)
    
    try:
        # Ejecutar test completo
        leds.test_completo()
        
        # O usar manualmente
        # leds.secuencia_inicio()
        # leds.indicar_estado('LINEA')
        # time.sleep(5)
        # leds.secuencia_exito()
        
    except KeyboardInterrupt:
        print("\nDetenido por usuario")
    finally:
        leds.apagar()
        GPIO.cleanup()
