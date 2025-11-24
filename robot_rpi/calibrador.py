#!/usr/bin/env python3
"""
Sistema de Calibración Automática de Sensores
Para robot ASTI Challenge
"""

import RPi.GPIO as GPIO
import time
import json
from pathlib import Path


class CalibradorSensores:
    """Calibración automática de sensores IR y otros"""
    
    def __init__(self, sensor_izq, sensor_cen, sensor_der):
        self.sensor_izq = sensor_izq
        self.sensor_cen = sensor_cen
        self.sensor_der = sensor_der
        
        self.valores_ir = {'izq': [], 'cen': [], 'der': []}
        self.umbral_linea = None
        self.archivo_config = Path("calibracion.json")
    
    def calibrar_sensores_ir(self, duracion_lectura=3):
        """
        Calibración automática de sensores IR
        Proceso guiado para calibrar sobre superficie blanca y línea negra
        
        Args:
            duracion_lectura (int): Segundos de lectura por superficie
            
        Returns:
            dict: Umbrales calculados
        """
        print("\n" + "="*50)
        print("CALIBRACIÓN DE SENSORES IR")
        print("="*50)
        
        # Paso 1: Calibrar en superficie blanca
        print("\n[1/2] Coloca el robot sobre SUPERFICIE BLANCA")
        print("Esperando 5 segundos...")
        time.sleep(5)
        
        print(f"Leyendo sensores durante {duracion_lectura} segundos...")
        valores_blanco = self._leer_sensores_multiple(duracion_lectura * 100)
        print(f"Valores en blanco: {valores_blanco}")
        
        # Paso 2: Calibrar en línea negra
        print("\n[2/2] Coloca el robot sobre LÍNEA NEGRA")
        print("Esperando 5 segundos...")
        time.sleep(5)
        
        print(f"Leyendo sensores durante {duracion_lectura} segundos...")
        valores_negro = self._leer_sensores_multiple(duracion_lectura * 100)
        print(f"Valores en negro: {valores_negro}")
        
        # Calcular umbrales (punto medio)
        self.umbral_linea = {
            'izq': (valores_blanco['izq'] + valores_negro['izq']) / 2,
            'cen': (valores_blanco['cen'] + valores_negro['cen']) / 2,
            'der': (valores_blanco['der'] + valores_negro['der']) / 2,
            'blanco': valores_blanco,
            'negro': valores_negro
        }
        
        print("\n" + "="*50)
        print("CALIBRACIÓN COMPLETADA")
        print("="*50)
        print(f"Umbrales calculados:")
        print(f"  Izquierda: {self.umbral_linea['izq']:.2f}")
        print(f"  Centro:    {self.umbral_linea['cen']:.2f}")
        print(f"  Derecha:   {self.umbral_linea['der']:.2f}")
        
        # Guardar calibración
        self._guardar_calibracion()
        
        return self.umbral_linea
    
    def _leer_sensores_multiple(self, n_lecturas):
        """
        Lee los sensores múltiples veces y calcula el promedio
        
        Args:
            n_lecturas (int): Número de lecturas a realizar
            
        Returns:
            dict: Valores promedio de cada sensor
        """
        valores = {'izq': 0, 'cen': 0, 'der': 0}
        
        for i in range(n_lecturas):
            valores['izq'] += GPIO.input(self.sensor_izq)
            valores['cen'] += GPIO.input(self.sensor_cen)
            valores['der'] += GPIO.input(self.sensor_der)
            time.sleep(0.01)
            
            # Mostrar progreso cada 25%
            if (i + 1) % (n_lecturas // 4) == 0:
                progreso = ((i + 1) / n_lecturas) * 100
                print(f"  Progreso: {progreso:.0f}%")
        
        # Calcular promedios
        return {k: v / n_lecturas for k, v in valores.items()}
    
    def _guardar_calibracion(self):
        """Guarda la calibración en archivo JSON"""
        try:
            with open(self.archivo_config, 'w', encoding='utf-8') as f:
                json.dump(self.umbral_linea, f, indent=2, ensure_ascii=False)
            print(f"\n✓ Calibración guardada en: {self.archivo_config}")
            return True
        except Exception as e:
            print(f"\n✗ Error al guardar calibración: {e}")
            return False
    
    def cargar_calibracion(self):
        """
        Carga calibración desde archivo
        
        Returns:
            dict: Umbrales cargados o None si no existe
        """
        if not self.archivo_config.exists():
            print(f"[Calibración] No existe archivo: {self.archivo_config}")
            return None
        
        try:
            with open(self.archivo_config, 'r', encoding='utf-8') as f:
                self.umbral_linea = json.load(f)
            print(f"[Calibración] Cargada desde: {self.archivo_config}")
            return self.umbral_linea
        except Exception as e:
            print(f"[Calibración] Error al cargar: {e}")
            return None
    
    def verificar_calibracion(self, duracion=5):
        """
        Verifica la calibración actual leyendo sensores
        
        Args:
            duracion (int): Segundos de verificación
        """
        if self.umbral_linea is None:
            print("[Calibración] No hay calibración cargada")
            return
        
        print("\n" + "="*50)
        print("VERIFICACIÓN DE CALIBRACIÓN")
        print("="*50)
        print("Mueve el robot sobre línea negra y superficie blanca")
        print(f"Leyendo durante {duracion} segundos...\n")
        
        inicio = time.time()
        while time.time() - inicio < duracion:
            izq = GPIO.input(self.sensor_izq)
            cen = GPIO.input(self.sensor_cen)
            der = GPIO.input(self.sensor_der)
            
            # Determinar si está sobre línea (comparar con umbral)
            izq_linea = "LÍNEA" if izq < self.umbral_linea['izq'] else "BLANCO"
            cen_linea = "LÍNEA" if cen < self.umbral_linea['cen'] else "BLANCO"
            der_linea = "LÍNEA" if der < self.umbral_linea['der'] else "BLANCO"
            
            print(f"Izq: {izq:.2f} ({izq_linea}) | "
                  f"Cen: {cen:.2f} ({cen_linea}) | "
                  f"Der: {der:.2f} ({der_linea})")
            
            time.sleep(0.2)
        
        print("\n✓ Verificación completada")
    
    def leer_sensor_calibrado(self, sensor):
        """
        Lee un sensor y devuelve si detecta línea según calibración
        
        Args:
            sensor (str): 'izq', 'cen' o 'der'
            
        Returns:
            bool: True si detecta línea negra
        """
        if self.umbral_linea is None:
            print("[Calibración] Advertencia: No hay calibración cargada")
            return False
        
        pin_map = {
            'izq': self.sensor_izq,
            'cen': self.sensor_cen,
            'der': self.sensor_der
        }
        
        if sensor not in pin_map:
            return False
        
        valor = GPIO.input(pin_map[sensor])
        return valor < self.umbral_linea[sensor]


# Ejemplo de uso
if __name__ == "__main__":
    # Configurar GPIO (ejemplo con pines del robot)
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    SENSOR_IZQ = 5
    SENSOR_CEN = 6
    SENSOR_DER = 13
    
    GPIO.setup(SENSOR_IZQ, GPIO.IN)
    GPIO.setup(SENSOR_CEN, GPIO.IN)
    GPIO.setup(SENSOR_DER, GPIO.IN)
    
    # Crear calibrador
    calibrador = CalibradorSensores(SENSOR_IZQ, SENSOR_CEN, SENSOR_DER)
    
    # Intentar cargar calibración existente
    if calibrador.cargar_calibracion() is None:
        print("No hay calibración previa. Iniciando calibración...")
        calibrador.calibrar_sensores_ir()
    else:
        print("Calibración cargada correctamente")
        print("¿Deseas recalibrar? (s/n)")
        # En uso real, aquí iría input del usuario
    
    # Verificar calibración
    # calibrador.verificar_calibracion()
    
    GPIO.cleanup()
