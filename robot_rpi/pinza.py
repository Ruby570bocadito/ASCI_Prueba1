#!/usr/bin/env python3
"""
Control de Pinza/Brazo con Servo
Para manipulación de objetos - Automatización Industrial
Robot ASTI Challenge
"""

import RPi.GPIO as GPIO
import time


class ControlPinza:
    """Control de pinza/brazo usando servo"""
    
    def __init__(self, pin_servo, angulo_abierto=90, angulo_cerrado=0):
        """
        Inicializa el control de la pinza
        
        Args:
            pin_servo (int): Pin GPIO para el servo
            angulo_abierto (int): Ángulo cuando la pinza está abierta (0-180)
            angulo_cerrado (int): Ángulo cuando la pinza está cerrada (0-180)
        """
        self.pin_servo = pin_servo
        self.angulo_abierto = angulo_abierto
        self.angulo_cerrado = angulo_cerrado
        self.angulo_actual = angulo_abierto
        
        self._setup()
    
    def _setup(self):
        """Configura el pin GPIO y el PWM para el servo"""
        GPIO.setup(self.pin_servo, GPIO.OUT)
        
        # Crear PWM a 50Hz (estándar para servos)
        self.pwm = GPIO.PWM(self.pin_servo, 50)
        self.pwm.start(0)
        
        # Inicializar en posición abierta
        self.abrir()
    
    def _angulo_a_duty_cycle(self, angulo):
        """
        Convierte ángulo (0-180) a duty cycle para PWM
        
        Args:
            angulo (int): Ángulo deseado (0-180)
            
        Returns:
            float: Duty cycle (2-12%)
        """
        # Servo típico: 2% = 0°, 12% = 180°
        return 2 + (angulo / 180) * 10
    
    def mover_a_angulo(self, angulo, velocidad=0.5):
        """
        Mueve el servo a un ángulo específico
        
        Args:
            angulo (int): Ángulo objetivo (0-180)
            velocidad (float): Velocidad de movimiento (segundos de pausa)
        """
        # Limitar ángulo
        angulo = max(0, min(180, angulo))
        
        duty_cycle = self._angulo_a_duty_cycle(angulo)
        self.pwm.ChangeDutyCycle(duty_cycle)
        time.sleep(velocidad)
        
        # Detener señal PWM para evitar jitter
        self.pwm.ChangeDutyCycle(0)
        
        self.angulo_actual = angulo
    
    def abrir(self, velocidad=0.5):
        """
        Abre la pinza completamente
        
        Args:
            velocidad (float): Velocidad de apertura
        """
        print("[Pinza] Abriendo...")
        self.mover_a_angulo(self.angulo_abierto, velocidad)
    
    def cerrar(self, velocidad=0.5):
        """
        Cierra la pinza completamente
        
        Args:
            velocidad (float): Velocidad de cierre
        """
        print("[Pinza] Cerrando...")
        self.mover_a_angulo(self.angulo_cerrado, velocidad)
    
    def agarrar_objeto(self, pausa_antes=0.5, pausa_despues=0.5):
        """
        Secuencia completa para agarrar un objeto
        
        Args:
            pausa_antes (float): Pausa antes de cerrar
            pausa_despues (float): Pausa después de cerrar
        """
        print("[Pinza] Iniciando secuencia de agarre...")
        
        # 1. Asegurar que está abierta
        self.abrir()
        time.sleep(pausa_antes)
        
        # 2. Cerrar para agarrar
        self.cerrar()
        time.sleep(pausa_despues)
        
        print("[Pinza] ✓ Objeto agarrado")
    
    def soltar_objeto(self, pausa_antes=0.5, pausa_despues=0.5):
        """
        Secuencia completa para soltar un objeto
        
        Args:
            pausa_antes (float): Pausa antes de abrir
            pausa_despues (float): Pausa después de abrir
        """
        print("[Pinza] Iniciando secuencia de liberación...")
        
        time.sleep(pausa_antes)
        
        # Abrir para soltar
        self.abrir()
        time.sleep(pausa_despues)
        
        print("[Pinza] ✓ Objeto liberado")
    
    def ajustar_apertura(self, porcentaje):
        """
        Ajusta la apertura de la pinza a un porcentaje
        
        Args:
            porcentaje (int): Porcentaje de apertura (0-100)
        """
        # Calcular ángulo proporcional
        rango = self.angulo_abierto - self.angulo_cerrado
        angulo = self.angulo_cerrado + (rango * porcentaje / 100)
        
        self.mover_a_angulo(int(angulo))
    
    def test_movimiento(self):
        """Prueba de movimiento completo de la pinza"""
        print("\n" + "="*50)
        print("TEST DE MOVIMIENTO DE PINZA")
        print("="*50)
        
        print("\n1. Abriendo completamente...")
        self.abrir()
        time.sleep(1)
        
        print("\n2. Cerrando completamente...")
        self.cerrar()
        time.sleep(1)
        
        print("\n3. Abriendo a 50%...")
        self.ajustar_apertura(50)
        time.sleep(1)
        
        print("\n4. Abriendo a 75%...")
        self.ajustar_apertura(75)
        time.sleep(1)
        
        print("\n5. Secuencia de agarre...")
        self.agarrar_objeto()
        time.sleep(1)
        
        print("\n6. Secuencia de liberación...")
        self.soltar_objeto()
        
        print("\n✓ Test completado")
    
    def detener(self):
        """Detiene el PWM y limpia"""
        self.pwm.stop()
    
    def __del__(self):
        """Limpieza al destruir el objeto"""
        try:
            self.pwm.stop()
        except:
            pass


# Ejemplo de uso
if __name__ == "__main__":
    # Configurar GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # Pin del servo (ajustar según tu conexión)
    SERVO_PIN = 18
    
    # Crear control de pinza
    # Ajustar ángulos según tu servo y pinza específicos
    pinza = ControlPinza(
        pin_servo=SERVO_PIN,
        angulo_abierto=90,   # Ajustar según tu pinza
        angulo_cerrado=0     # Ajustar según tu pinza
    )
    
    try:
        # Ejecutar test de movimiento
        pinza.test_movimiento()
        
        # O usar manualmente
        # pinza.agarrar_objeto()
        # time.sleep(2)
        # pinza.soltar_objeto()
        
    except KeyboardInterrupt:
        print("\nDetenido por usuario")
    finally:
        pinza.detener()
        GPIO.cleanup()
