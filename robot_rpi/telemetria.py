#!/usr/bin/env python3
"""
Sistema de Telemetría para Robot ASTI Challenge
Registra eventos, genera estadísticas y crea evidencias para documentación
"""

import json
import datetime
import os
import csv
from pathlib import Path


class SistemaTelemetria:
    """Sistema completo de telemetría y logging"""
    
    def __init__(self, archivo_log="telemetria.json", directorio_logs="logs"):
        self.directorio = Path(directorio_logs)
        self.directorio.mkdir(exist_ok=True)
        
        # Crear nombre de archivo con timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.archivo = self.directorio / f"{timestamp}_{archivo_log}"
        
        self.datos = []
        self.inicio_sesion = datetime.datetime.now()
        self.eventos_desde_guardado = 0
        
        print(f"[Telemetría] Iniciada - Archivo: {self.archivo}")
    
    def registrar_evento(self, tipo, datos):
        """
        Registra un evento con timestamp
        
        Args:
            tipo (str): Tipo de evento (ej: 'MOVIMIENTO', 'SENSOR', 'MODO')
            datos (dict): Datos del evento
        """
        evento = {
            'timestamp': datetime.datetime.now().isoformat(),
            'tiempo_transcurrido': (datetime.datetime.now() - self.inicio_sesion).total_seconds(),
            'tipo': tipo,
            'datos': datos
        }
        self.datos.append(evento)
        self.eventos_desde_guardado += 1
        
        # Guardar cada 10 eventos (optimizado para RPi 2 W)
        if self.eventos_desde_guardado >= 10:
            self.guardar()
            self.eventos_desde_guardado = 0
    
    def guardar(self):
        """Guarda los datos en archivo JSON"""
        try:
            with open(self.archivo, 'w', encoding='utf-8') as f:
                json.dump(self.datos, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[Telemetría] Error al guardar: {e}")
            return False
    
    def obtener_estadisticas(self):
        """
        Genera estadísticas de la sesión
        
        Returns:
            dict: Estadísticas completas
        """
        return {
            'total_eventos': len(self.datos),
            'tiempo_total': (datetime.datetime.now() - self.inicio_sesion).total_seconds(),
            'eventos_por_tipo': self._contar_por_tipo(),
            'inicio_sesion': self.inicio_sesion.isoformat(),
            'archivo': str(self.archivo)
        }
    
    def _contar_por_tipo(self):
        """Cuenta eventos por tipo"""
        conteo = {}
        for evento in self.datos:
            tipo = evento['tipo']
            conteo[tipo] = conteo.get(tipo, 0) + 1
        return conteo
    
    def exportar_csv(self, archivo_csv=None):
        """
        Exporta datos a CSV para análisis
        
        Args:
            archivo_csv (str): Nombre del archivo CSV (opcional)
        """
        if archivo_csv is None:
            archivo_csv = self.archivo.with_suffix('.csv')
        
        try:
            with open(archivo_csv, 'w', newline='', encoding='utf-8') as f:
                if not self.datos:
                    return False
                
                # Obtener todas las claves posibles
                claves = set()
                for evento in self.datos:
                    claves.update(evento.keys())
                    if 'datos' in evento:
                        claves.update([f"datos_{k}" for k in evento['datos'].keys()])
                
                writer = csv.DictWriter(f, fieldnames=sorted(claves))
                writer.writeheader()
                
                for evento in self.datos:
                    fila = evento.copy()
                    if 'datos' in fila:
                        datos = fila.pop('datos')
                        for k, v in datos.items():
                            fila[f'datos_{k}'] = v
                    writer.writerow(fila)
            
            print(f"[Telemetría] Exportado a CSV: {archivo_csv}")
            return True
        except Exception as e:
            print(f"[Telemetría] Error al exportar CSV: {e}")
            return False
    
    def obtener_eventos_por_tipo(self, tipo):
        """
        Filtra eventos por tipo
        
        Args:
            tipo (str): Tipo de evento a filtrar
            
        Returns:
            list: Lista de eventos del tipo especificado
        """
        return [e for e in self.datos if e['tipo'] == tipo]
    
    def obtener_ultimos_eventos(self, n=10):
        """
        Obtiene los últimos N eventos
        
        Args:
            n (int): Número de eventos a obtener
            
        Returns:
            list: Últimos N eventos
        """
        return self.datos[-n:] if len(self.datos) >= n else self.datos
    
    def limpiar(self):
        """Limpia los datos de la sesión actual"""
        self.datos = []
        self.inicio_sesion = datetime.datetime.now()
        self.eventos_desde_guardado = 0
        print("[Telemetría] Datos limpiados")
    
    def generar_reporte(self):
        """
        Genera un reporte legible de la sesión
        
        Returns:
            str: Reporte formateado
        """
        stats = self.obtener_estadisticas()
        
        reporte = []
        reporte.append("=" * 50)
        reporte.append("REPORTE DE TELEMETRÍA")
        reporte.append("=" * 50)
        reporte.append(f"Inicio de sesión: {stats['inicio_sesion']}")
        reporte.append(f"Tiempo total: {stats['tiempo_total']:.2f} segundos")
        reporte.append(f"Total de eventos: {stats['total_eventos']}")
        reporte.append("")
        reporte.append("Eventos por tipo:")
        for tipo, cantidad in sorted(stats['eventos_por_tipo'].items()):
            reporte.append(f"  - {tipo}: {cantidad}")
        reporte.append("=" * 50)
        
        return "\n".join(reporte)
    
    def __del__(self):
        """Guardar datos al destruir el objeto"""
        if self.eventos_desde_guardado > 0:
            self.guardar()


# Ejemplo de uso
if __name__ == "__main__":
    # Crear sistema de telemetría
    telemetria = SistemaTelemetria()
    
    # Registrar algunos eventos de ejemplo
    telemetria.registrar_evento('INICIO', {'modo': 'test'})
    telemetria.registrar_evento('MOVIMIENTO', {'accion': 'avanzar', 'velocidad': 80})
    telemetria.registrar_evento('SENSORES_IR', {'izq': 0, 'cen': 1, 'der': 0})
    telemetria.registrar_evento('MOVIMIENTO', {'accion': 'girar_izquierda', 'velocidad': 70})
    telemetria.registrar_evento('SENSORES_IR', {'izq': 1, 'cen': 0, 'der': 0})
    
    # Obtener estadísticas
    print(telemetria.generar_reporte())
    
    # Exportar a CSV
    telemetria.exportar_csv()
    
    # Guardar JSON
    telemetria.guardar()
    
    print(f"\nArchivos generados en: {telemetria.directorio}")
