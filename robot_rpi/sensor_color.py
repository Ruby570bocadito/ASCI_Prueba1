#!/usr/bin/env python3
"""
Control de Sensor de Color TCS3200
Para clasificación de objetos - Automatización Industrial
Robot ASTI Challenge
"""

import RPi.GPIO as GPIO
import time


class SensorColor:
    """Control de sensor de color TCS3200 para clasificación de objetos"""
    
    def __init__(self, s0, s1, s2, s3, out):
        """
        Inicializa el sensor de color
        
        Args:
            s0, s1: Pines de selección de frecuencia
            s2, s3: Pines de selección de filtro de color
            out: Pin de salida de frecuencia
        """
        self.s0 = s0
        self.s1 = s1
        self.s2 = s2
        self.s3 = s3
        self.out = out
        
        self.colores_calibrados = {}
        self._setup()
    
    def _setup(self):
        """Configura los pines GPIO"""
        GPIO.setup(self.s0, GPIO.OUT)
        GPIO.setup(self.s1, GPIO.OUT)
        GPIO.setup(self.s2, GPIO.OUT)
        GPIO.setup(self.s3, GPIO.OUT)
        GPIO.setup(self.out, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Configurar frecuencia de salida al 20% (s0=HIGH, s1=LOW)
        GPIO.output(self.s0, GPIO.HIGH)
        GPIO.output(self.s1, GPIO.LOW)
    
    def _leer_frecuencia(self, filtro):
        """
        Lee la frecuencia para un filtro de color específico
        
        Args:
            filtro (str): 'R', 'G', 'B' o 'C' (clear)
            
        Returns:
            int: Frecuencia leída
        """
        # Configurar filtro
        filtros = {
            'R': (GPIO.LOW, GPIO.LOW),   # Rojo
            'G': (GPIO.HIGH, GPIO.HIGH), # Verde
            'B': (GPIO.LOW, GPIO.HIGH),  # Azul
            'C': (GPIO.HIGH, GPIO.LOW)   # Clear (sin filtro)
        }
        
        if filtro not in filtros:
            return 0
        
        s2_val, s3_val = filtros[filtro]
        GPIO.output(self.s2, s2_val)
        GPIO.output(self.s3, s3_val)
        
        time.sleep(0.01)  # Pequeña pausa para estabilizar
        
        # Contar pulsos durante un tiempo fijo
        pulsos = 0
        timeout = time.time() + 0.1  # 100ms
        
        while time.time() < timeout:
            if GPIO.input(self.out) == GPIO.LOW:
                pulsos += 1
                while GPIO.input(self.out) == GPIO.LOW:
                    pass
        
        return pulsos
    
    def leer_rgb(self):
        """
        Lee los valores RGB del sensor
        
        Returns:
            tuple: (r, g, b) valores de frecuencia
        """
        r = self._leer_frecuencia('R')
        g = self._leer_frecuencia('G')
        b = self._leer_frecuencia('B')
        
        return (r, g, b)
    
    def leer_color(self):
        """
        Lee y clasifica el color detectado
        
        Returns:
            str: Nombre del color detectado
        """
        r, g, b = self.leer_rgb()
        return self._clasificar_color(r, g, b)
    
    def _clasificar_color(self, r, g, b):
        """
        Clasifica el color basándose en valores RGB
        
        Args:
            r, g, b: Valores de frecuencia RGB
            
        Returns:
            str: Nombre del color
        """
        # Si hay colores calibrados, usar esos
        if self.colores_calibrados:
            return self._clasificar_con_calibracion(r, g, b)
        
        # Clasificación básica sin calibración
        total = r + g + b
        if total == 0:
            return "NEGRO"
        
        # Normalizar valores
        r_norm = r / total
        g_norm = g / total
        b_norm = b / total
        
        # Determinar color dominante
        max_val = max(r_norm, g_norm, b_norm)
        
        if max_val == r_norm:
            if r_norm > 0.5:
                return "ROJO"
        elif max_val == g_norm:
            if g_norm > 0.5:
                return "VERDE"
        elif max_val == b_norm:
            if b_norm > 0.5:
                return "AZUL"
        
        # Verificar si es blanco (todos los valores altos)
        if r_norm > 0.3 and g_norm > 0.3 and b_norm > 0.3:
            return "BLANCO"
        
        return "DESCONOCIDO"
    
    def calibrar_color(self, nombre_color, n_muestras=10):
        """
        Calibra un color específico tomando múltiples muestras
        
        Args:
            nombre_color (str): Nombre del color a calibrar
            n_muestras (int): Número de muestras a tomar
        """
        print(f"\nCalibrando color: {nombre_color}")
        print(f"Coloca objeto {nombre_color} frente al sensor")
        print("Esperando 3 segundos...")
        time.sleep(3)
        
        print(f"Tomando {n_muestras} muestras...")
        muestras_r = []
        muestras_g = []
        muestras_b = []
        
        for i in range(n_muestras):
            r, g, b = self.leer_rgb()
            muestras_r.append(r)
            muestras_g.append(g)
            muestras_b.append(b)
            print(f"  Muestra {i+1}/{n_muestras}: R={r}, G={g}, B={b}")
            time.sleep(0.2)
        
        # Calcular promedios
        r_prom = sum(muestras_r) / n_muestras
        g_prom = sum(muestras_g) / n_muestras
        b_prom = sum(muestras_b) / n_muestras
        
        self.colores_calibrados[nombre_color] = {
            'r': r_prom,
            'g': g_prom,
            'b': b_prom
        }
        
        print(f"✓ Color {nombre_color} calibrado: R={r_prom:.1f}, G={g_prom:.1f}, B={b_prom:.1f}")
    
    def _clasificar_con_calibracion(self, r, g, b):
        """
        Clasifica color usando valores calibrados
        
        Args:
            r, g, b: Valores RGB leídos
            
        Returns:
            str: Nombre del color más cercano
        """
        if not self.colores_calibrados:
            return "SIN_CALIBRACION"
        
        # Calcular distancia euclidiana a cada color calibrado
        distancias = {}
        for nombre, valores in self.colores_calibrados.items():
            dist = ((r - valores['r'])**2 + 
                   (g - valores['g'])**2 + 
                   (b - valores['b'])**2) ** 0.5
            distancias[nombre] = dist
        
        # Retornar el color con menor distancia
        color_cercano = min(distancias, key=distancias.get)
        
        # Si la distancia es muy grande, es desconocido
        if distancias[color_cercano] > 100:  # Umbral ajustable
            return "DESCONOCIDO"
        
        return color_cercano
    
    def calibrar_colores_basicos(self):
        """Calibra los colores básicos: ROJO, VERDE, AZUL"""
        colores = ["ROJO", "VERDE", "AZUL"]
        
        print("\n" + "="*50)
        print("CALIBRACIÓN DE COLORES BÁSICOS")
        print("="*50)
        
        for color in colores:
            self.calibrar_color(color)
            time.sleep(1)
        
        print("\n✓ Calibración de colores básicos completada")
        print(f"Colores calibrados: {list(self.colores_calibrados.keys())}")


# Ejemplo de uso
if __name__ == "__main__":
    # Configurar GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # Pines del sensor de color (ajustar según tu conexión)
    S0 = 17
    S1 = 27
    S2 = 22
    S3 = 23
    OUT = 24
    
    # Crear sensor
    sensor = SensorColor(S0, S1, S2, S3, OUT)
    
    # Opción 1: Calibrar colores
    # sensor.calibrar_colores_basicos()
    
    # Opción 2: Leer color continuamente
    print("Leyendo colores (Ctrl+C para salir)...")
    try:
        while True:
            r, g, b = sensor.leer_rgb()
            color = sensor.leer_color()
            print(f"R={r:4d} G={g:4d} B={b:4d} -> {color}")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nDetenido por usuario")
    
    GPIO.cleanup()
