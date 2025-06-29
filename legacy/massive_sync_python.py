#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sincronización Masiva Multi-Dispositivos Hikvision
Integración con Sistema VB6 - Carga Paralela a Múltiples Lectores Faciales
"""

import requests
import pyodbc
import base64
import json
import logging
import hashlib
from PIL import Image
import io
from datetime import datetime, timedelta
import time
import threading
import queue
import concurrent.futures
from typing import List, Dict, Any, Optional, Tuple
import configparser
import ssl
import urllib3
from dataclasses import dataclass
import schedule

# Suprimir warnings SSL no verificados
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

@dataclass
class DispositivoHikvision:
    """Clase para representar un dispositivo Hikvision"""
    dispositivo_id: int
    nombre: str
    ip_address: str
    puerto: int
    usuario: str
    password: str
    usar_https: bool
    activo: bool
    ubicacion: str
    zona: str
    capacidad_max_usuarios: int
    estado_conexion: int
    sincronizacion_activa: bool

@dataclass
class RegistroFacial:
    """Clase para representar un registro facial"""
    facial_id: int
    persona_id: int
    nombre: str
    apellido: str
    template_data: bytes
    activo: bool
    calidad_imagen: int
    umbral_coincidencia: int
    deteccion_vital: bool
    hash_imagen: str

class HikvisionMassiveSync:
    """Clase principal para sincronización masiva con múltiples dispositivos Hikvision"""
    
    def __init__(self, config_file: str = "hikvision_config.ini"):
        """Inicializar el sincronizador masivo"""
        
        # Cargar configuración
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        
        # Configuración de base de datos
        self.db_connection_string = self.config.get('DATABASE', 'connection_string')
        
        # Configuración de logging
        self._setup_logging()
        
        # Cola de trabajo para hilos
        self.work_queue = queue.Queue()
        self.result_queue = queue.Queue()
        
        # Control de hilos
        self.max_workers = int(self.config.get('SYNC', 'max_workers', fallback='5'))
        self.timeout_connection = int(self.config.get('SYNC', 'timeout_connection', fallback='30'))
        
        # Estadísticas
        self.stats = {
            'dispositivos_procesados': 0,
            'usuarios_sincronizados': 0,
            'errores_conexion': 0,
            'tiempo_inicio': None
        }
        
        self.logger.info(f"Inicializado sincronizador masivo con {self.max_workers} workers")

    def _setup_logging(self):
        """Configurar sistema de logging"""
        log_level = self.config.get('LOGGING', 'level', fallback='INFO')
        log_file = self.config.get('LOGGING', 'file', fallback='hikvision_massive.log')
        
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - [%(threadName)s] - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def conectar_db(self) -> Optional[pyodbc.Connection]:
        """Establecer conexión con la base de datos"""
        try:
            conn = pyodbc.connect(self.db_connection_string)
            conn.autocommit = False
            return conn
        except Exception as e:
            self.logger.error(f"Error conectando a DB: {e}")
            return None

    def obtener_dispositivos_activos(self) -> List[DispositivoHikvision]:
        """Obtener lista de dispositivos Hikvision activos"""
        conn = self.conectar_db()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            query = """
                SELECT 
                    DispositivoID, Nombre, IPAddress, Puerto, Usuario, Password,
                    UsarHTTPS, Activo, Ubicacion, Zona, CapacidadMaxUsuarios,
                    EstadoConexion, SincronizacionActiva
                FROM hikface 
                WHERE Activo = 1 AND SincronizacionActiva = 1
                ORDER BY Nombre
            """
            
            cursor.execute(query)
            dispositivos = []
            
            for row in cursor.fetchall():
                dispositivo = DispositivoHikvision(
                    dispositivo_id=row[0],
                    nombre=row[1],
                    ip_address=row[2],
                    puerto=row[3],
                    usuario=row[4],
                    password=row[5],  # En producción, descifrar aquí
                    usar_https=bool(row[6]),
                    activo=bool(row[7]),
                    ubicacion=row[8] or "",
                    zona=row[9] or "",
                    capacidad_max_usuarios=row[10],
                    estado_conexion=row[11],
                    sincronizacion_activa=bool(row[12])
                )
                dispositivos.append(dispositivo)
            
            conn.close()
            self.logger.info(f"Obtenidos {len(dispositivos)} dispositivos activos")
            return dispositivos
            
        except Exception as e:
            self.logger.error(f"Error obteniendo dispositivos: {e}")
            return []

    def obtener_cola_sincronizacion(self, dispositivo_id: int = None) -> List[Dict]:
        """Obtener registros pendientes de la cola de sincronización"""
        conn = self.conectar_db()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            
            where_clause = "WHERE cs.Estado = 0"  # Solo pendientes
            params = []
            
            if dispositivo_id:
                where_clause += " AND cs.DispositivoID = ?"
                params.append(dispositivo_id)
            
            query = f"""
                SELECT 
                    cs.ColaID,
                    cs.FacialID,
                    cs.DispositivoID,
                    cs.PersonaID,
                    cs.TipoOperacion,
                    cs.Prioridad,
                    p.Nombre,
                    p.Apellido,
                    f.TemplateData,
                    f.Activo,
                    f.CalidadImagen,
                    f.UmbralCoincidencia,
                    f.DeteccionVital,
                    f.HashImagen
                FROM cola_sincronizacion cs
                INNER JOIN face f ON cs.FacialID = f.FacialID
                INNER JOIN per p ON cs.PersonaID = p.PersonaID
                {where_clause}
                ORDER BY cs.Prioridad ASC, cs.FechaCreacion ASC
            """
            
            cursor.execute(query, params)
            registros = []
            
            for row in cursor.fetchall():
                registro = {
                    'cola_id': row[0],
                    'facial_id': row[1],
                    'dispositivo_id': row[2],
                    'persona_id': row[3],
                    'tipo_operacion': row[4],
                    'prioridad': row[5],
                    'nombre': row[6],
                    'apellido': row[7],
                    'template_data': row[8],
                    'activo': row[9],
                    'calidad_imagen': row[10] or 80,
                    'umbral_coincidencia': row[11] or 80,
                    'deteccion_vital': bool(row[12]) if row[12] is not None else True,
                    'hash_imagen': row[13]
                }
                registros.append(registro)
            
            conn.close()
            return registros
            
        except Exception as e:
            self.logger.error(f"Error obteniendo cola de sincronización: {e}")
            return []

    def procesar_imagen_facial(self, binary_data: bytes, calidad_objetivo: int = 85) -> Optional[bytes]:
        """Procesar imagen facial para optimizar para Hikvision"""
        try:
            # Verificar si los datos están vacíos
            if not binary_data:
                self.logger.error("Datos de imagen vacíos")
                return None
            
            # Crear stream de imagen
            image_stream = io.BytesIO(binary_data)
            image = Image.open(image_stream)
            
            # Convertir a RGB si es necesario
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Redimensionar si es muy grande (Hikvision recomienda max 400x400)
            max_size = 400
            if image.width > max_size or image.height > max_size:
                # Mantener proporción
                ratio = min(max_size / image.width, max_size / image.height)
                new_size = (int(image.width * ratio), int(image.height * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
                self.logger.debug(f"Imagen redimensionada a {new_size}")
            
            # Guardar como JPEG optimizado
            output_stream = io.BytesIO()
            image.save(output_stream, format='JPEG', quality=calidad_objetivo, optimize=True)
            processed_data = output_stream.getvalue()
            
            # Verificar tamaño final (max 200KB recomendado)
            if len(processed_data) > 200 * 1024:
                # Re-comprimir con calidad menor
                output_stream = io.BytesIO()
                image.save(output_stream, format='JPEG', quality=70, optimize=True)
                processed_data = output_stream.getvalue()
            
            self.logger.debug(f"Imagen procesada: {len(binary_data)} -> {len(processed_data)} bytes")
            return processed_data
            
        except Exception as e:
            self.logger.error(f"Error procesando imagen: {e}")
            return None

    def calcular_hash_imagen(self, binary_data: bytes) -> str:
        """Calcular hash SHA256 de la imagen"""
        try:
            return hashlib.sha256(binary_data).hexdigest()
        except Exception as e:
            self.logger.error(f"Error calculando hash: {e}")
            return ""

    def crear_sesion_hikvision(self, dispositivo: DispositivoHikvision) -> Optional[requests.Session]:
        """Crear sesión HTTP para dispositivo Hikvision"""
        try:
            session = requests.Session()
            
            # Configurar autenticación básica
            credentials = f"{dispositivo.usuario}:{dispositivo.password}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            session.headers.update({
                'Authorization': f'Basic {encoded_credentials}',
                'Content-Type': 'application/json',
                'User-Agent': 'VB6-HikvisionSync/1.0'
            })
            
            # Configurar timeouts y SSL
            session.timeout = self.timeout_connection
            if dispositivo.usar_https:
                session.verify = False  # Para certificados autofirmados
            
            return session
            
        except Exception as e:
            self.logger.error(f"Error creando sesión para {dispositivo.nombre}: {e}")
            return None

    def verificar_conectividad_dispositivo(self, dispositivo: DispositivoHikvision) -> bool:
        """Verificar si el dispositivo está disponible"""
        try:
            session = self.crear_sesion_hikvision(dispositivo)
            if not session:
                return False
            
            protocol = "https" if dispositivo.usar_https else "http"
            url = f"{protocol}://{dispositivo.ip_address}:{dispositivo.puerto}/ISAPI/System/deviceInfo"
            
            response = session.get(url, timeout=10)
            
            if response.status_code == 200:
                self._actualizar_estado_dispositivo(dispositivo.dispositivo_id, 1)  # Online
                return True
            else:
                self._actualizar_estado_dispositivo(dispositivo.dispositivo_id, 2)  # Offline
                return False
                
        except Exception as e:
            self.logger.error(f"Error verificando conectividad {dispositivo.nombre}: {e}")
            self._actualizar_estado_dispositivo(dispositivo.dispositivo_id, 2)  # Offline
            return False

    def _actualizar_estado_dispositivo(self, dispositivo_id: int, estado: int):
        """Actualizar estado de conexión del dispositivo en BD"""
        conn = self.conectar_db()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE hikface 
                SET EstadoConexion = ?, UltimaConexion = GETDATE()
                WHERE DispositivoID = ?
            """, estado, dispositivo_id)
            conn.commit()
            conn.close()
        except Exception as e:
            self.logger.error(f"Error actualizando estado dispositivo {dispositivo_id}: {e}")

    def sincronizar_usuario_dispositivo(self, dispositivo: DispositivoHikvision, registro: Dict) -> bool:
        """Sincronizar un usuario específico con un dispositivo"""
        try:
            session = self.crear_sesion_hikvision(dispositivo)
            if not session:
                return False
            
            protocol = "https" if dispositivo.usar_https else "http"
            base_url = f"{protocol}://{dispositivo.ip_address}:{dispositivo.puerto}"
            
            # Procesar imagen
            if registro['template_data']:
                imagen_procesada = self.procesar_imagen_facial(registro['template_data'])
                if not imagen_procesada:
                    self.logger.error(f"No se pudo procesar imagen para persona {registro['persona_id']}")
                    return False
            else:
                self.logger.error(f"No hay datos de imagen para persona {registro['persona_id']}")
                return False
            
            # 1. Crear/Actualizar usuario
            if registro['tipo_operacion'] in ['INSERT', 'UPDATE']:
                success = self._crear_usuario_hikvision(session, base_url, registro)
                if not success:
                    return False
                
                # 2. Enrolar rostro
                success = self._enrolar_rostro_hikvision(session, base_url, registro, imagen_procesada)
                if not success:
                    return False
            
            elif registro['tipo_operacion'] == 'DELETE':
                success = self._eliminar_usuario_hikvision(session, base_url, registro)
                if not success:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error sincronizando usuario {registro['persona_id']} en {dispositivo.nombre}: {e}")
            return False

    def _crear_usuario_hikvision(self, session: requests.Session, base_url: str, registro: Dict) -> bool:
        """Crear usuario en dispositivo Hikvision"""
        try:
            url = f"{base_url}/ISAPI/AccessControl/UserInfo/Record?format=json"
            
            user_data = {
                "UserInfo": {
                    "employeeNo": str(registro['persona_id']),
                    "name": f"{registro['nombre']} {registro['apellido']}".strip(),
                    "userType": "normal",
                    "Valid": {
                        "enable": bool(registro['activo']),
                        "beginTime": "2024-01-01T00:00:00",
                        "endTime": "2030-12-31T23:59:59"
                    },
                    "RightPlan": [{
                        "doorNo": 1,
                        "planTemplateNo": "1"
                    }],
                    "maxFingerPrintNum": 10,
                    "maxFaceNum": 5
                }
            }
            
            response = session.post(url, json=user_data, timeout=30)
            
            if response.status_code in [200, 201]:
                self.logger.info(f"Usuario creado/actualizado: {registro['persona_id']} - {registro['nombre']}")
                return True
            elif response.status_code == 409:  # Usuario ya existe
                self.logger.info(f"Usuario ya existe: {registro['persona_id']} - actualizando...")
                return True
            else:
                self.logger.error(f"Error creando usuario {registro['persona_id']}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error en _crear_usuario_hikvision: {e}")
            return False

    def _enrolar_rostro_hikvision(self, session: requests.Session, base_url: str, registro: Dict, imagen_data: bytes) -> bool:
        """Enrolar rostro en dispositivo Hikvision"""
        try:
            # URL para enrolamiento facial
            url = f"{base_url}/ISAPI/AccessControl/UserInfo/SetFace?format=json"
            
            # Configurar metadatos del rostro
            face_data = {
                "FaceInfo": {
                    "employeeNo": str(registro['persona_id']),
                    "faceLibType": "blackFD",
                    "FDID": "1",
                    "FPID": str(registro['facial_id'])
                }
            }
            
            # Enviar metadatos
            response = session.post(url, json=face_data, timeout=30)
            
            if response.status_code not in [200, 201]:
                self.logger.error(f"Error en metadatos de rostro {registro['persona_id']}: {response.text}")
                return False
            
            # Subir imagen facial
            headers = session.headers.copy()
            headers['Content-Type'] = 'application/octet-stream'
            
            response = session.put(url, data=imagen_data, headers=headers, timeout=30)
            
            if response.status_code in [200, 201]:
                self.logger.info(f"Rostro enrolado: {registro['persona_id']} - FacialID: {registro['facial_id']}")
                return True
            else:
                self.logger.error(f"Error subiendo imagen {registro['persona_id']}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error en _enrolar_rostro_hikvision: {e}")
            return False

    def _eliminar_usuario_hikvision(self, session: requests.Session, base_url: str, registro: Dict) -> bool:
        """Eliminar usuario de dispositivo Hikvision"""
        try:
            url = f"{base_url}/ISAPI/AccessControl/UserInfo/Delete?format=json"
            
            delete_data = {
                "UserInfoDelCond": {
                    "EmployeeNoList": [
                        {"employeeNo": str(registro['persona_id'])}
                    ]
                }
            }
            
            response = session.put(url, json=delete_data, timeout=30)
            
            if response.status_code in [200, 201]:
                self.logger.info(f"Usuario eliminado: {registro['persona_id']}")
                return True
            else:
                self.logger.error(f"Error eliminando usuario {registro['persona_id']}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error en _eliminar_usuario_hikvision: {e}")
            return False

    def actualizar_estado_cola(self, cola_id: int, estado: int, mensaje_error: str = None, tiempo_ejecucion: int = None):
        """Actualizar estado de registro en cola de sincronización"""
        conn = self.conectar_db()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            
            if estado == 2:  # Completado
                cursor.execute("""
                    UPDATE cola_sincronizacion 
                    SET Estado = ?, FechaCompletado = GETDATE(), TiempoEjecucion = ?
                    WHERE ColaID = ?
                """, estado, tiempo_ejecucion, cola_id)
            elif estado == 3:  # Error
                cursor.execute("""
                    UPDATE cola_sincronizacion 
                    SET Estado = ?, MensajeError = ?, NumeroIntentos = NumeroIntentos + 1
                    WHERE ColaID = ?
                """, estado, mensaje_error, cola_id)
            else:  # Procesando
                cursor.execute("""
                    UPDATE cola_sincronizacion 
                    SET Estado = ?, FechaProcesamiento = GETDATE()
                    WHERE ColaID = ?
                """, estado, cola_id)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error actualizando estado cola {cola_id}: {e}")

    def registrar_log(self, dispositivo_id: int, tipo_evento: str, nivel: str, mensaje: str, 
                     detalle: str = None, facial_id: int = None, persona_id: int = None):
        """Registrar evento en log de sincronización"""
        conn = self.conectar_db()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO log_sincronizacion 
                (DispositivoID, TipoEvento, Nivel, Mensaje, Detalle, FacialID, PersonaID)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, dispositivo_id, tipo_evento, nivel, mensaje, detalle, facial_id, persona_id)
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error registrando log: {e}")

    def worker_sincronizacion(self, thread_id: int):
        """Worker thread para procesamiento paralelo"""
        self.logger.info(f"Worker {thread_id} iniciado")
        
        while True:
            try:
                # Obtener trabajo de la cola
                work_item = self.work_queue.get(timeout=5)
                if work_item is None:  # Señal de parada
                    break
                
                dispositivo, registro = work_item
                start_time = time.time()
                
                self.logger.info(f"Worker {thread_id}: Procesando PersonaID {registro['persona_id']} en {dispositivo.nombre}")
                
                # Marcar como procesando
                self.actualizar_estado_cola(registro['cola_id'], 1)  # Procesando
                
                # Intentar sincronización
                success = self.sincronizar_usuario_dispositivo(dispositivo, registro)
                
                # Calcular tiempo de ejecución
                tiempo_ejecucion = int((time.time() - start_time) * 1000)  # milisegundos
                
                if success:
                    # Marcar como completado
                    self.actualizar_estado_cola(registro['cola_id'], 2, tiempo_ejecucion=tiempo_ejecucion)
                    self.registrar_log(
                        dispositivo.dispositivo_id, 
                        'SINCRONIZACION', 
                        'INFO', 
                        f"Usuario {registro['persona_id']} sincronizado exitosamente",
                        facial_id=registro['facial_id'],
                        persona_id=registro['persona_id']
                    )
                    self.stats['usuarios_sincronizados'] += 1
                else:
                    # Marcar como error
                    self.actualizar_estado_cola(registro['cola_id'], 3, "Error en sincronización")
                    self.registrar_log(
                        dispositivo.dispositivo_id, 
                        'ERROR', 
                        'ERROR', 
                        f"Error sincronizando usuario {registro['persona_id']}",
                        facial_id=registro['facial_id'],
                        persona_id=registro['persona_id']
                    )
                
                # Reportar resultado
                self.result_queue.put((success, dispositivo.nombre, registro['persona_id']))
                
                # Marcar tarea como completada
                self.work_queue.task_done()
                
                # Pequeña pausa para no sobrecargar el dispositivo
                time.sleep(0.5)
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error en worker {thread_id}: {e}")
                if 'registro' in locals():
                    self.actualizar_estado_cola(registro['cola_id'], 3, str(e))
                self.work_queue.task_done()
        
        self.logger.info(f"Worker {thread_id} terminado")

    def sincronizacion_masiva(self, dispositivos: List[DispositivoHikvision] = None):
        """Ejecutar sincronización masiva con todos los dispositivos"""
        
        self.logger.info("=== INICIANDO SINCRONIZACIÓN MASIVA ===")
        self.stats['tiempo_inicio'] = time.time()
        
        # Obtener dispositivos si no se proporcionaron
        if not dispositivos:
            dispositivos = self.obtener_dispositivos_activos()
        
        if not dispositivos:
            self.logger.warning("No hay dispositivos activos para sincronizar")
            return
        
        # Verificar conectividad de dispositivos
        dispositivos_online = []
        for dispositivo in dispositivos:
            if self.verificar_conectividad_dispositivo(dispositivo):
                dispositivos_online.append(dispositivo)
                self.logger.info(f"✅ Dispositivo online: {dispositivo.nombre} ({dispositivo.ip_address})")
            else:
                self.logger.error(f"❌ Dispositivo offline: {dispositivo.nombre} ({dispositivo.ip_address})")
                self.stats['errores_conexion'] += 1
        
        if not dispositivos_online:
            self.logger.error("No hay dispositivos online disponibles")
            return
        
        # Obtener trabajos pendientes
        total_trabajos = 0
        for dispositivo in dispositivos_online:
            registros_pendientes = self.obtener_cola_sincronizacion(dispositivo.dispositivo_id)
            for registro in registros_pendientes:
                self.work_queue.put((dispositivo, registro))
                total_trabajos += 1
        
        self.logger.info(f"Total de trabajos en cola: {total_trabajos}")
        
        if total_trabajos == 0:
            self.logger.info("No hay trabajos pendientes de sincronización")
            return
        
        # Iniciar workers
        workers = []
        for i in range(min(self.max_workers, total_trabajos)):
            worker = threading.Thread(target=self.worker_sincronizacion, args=(i,), name=f"Worker-{i}")
            worker.start()
            workers.append(worker)
        
        self.logger.info(f"Iniciados {len(workers)} workers para procesar {total_trabajos} trabajos")
        
        # Monitorear progreso
        trabajos_completados = 0
        trabajos_exitosos = 0
        
        while trabajos_completados < total_trabajos:
            try:
                result = self.result_queue.get(timeout=1)
                success, dispositivo_nombre, persona_id = result
                trabajos_completados += 1
                
                if success:
                    trabajos_exitosos += 1
                
                # Mostrar progreso cada 10 trabajos o al final
                if trabajos_completados % 10 == 0 or trabajos_completados == total_trabajos:
                    porcentaje = (trabajos_completados / total_trabajos) * 100
                    self.logger.info(f"Progreso: {trabajos_completados}/{total_trabajos} ({porcentaje:.1f}%) - Exitosos: {trabajos_exitosos}")
                
            except queue.Empty:
                continue
        
        # Esperar que terminen todos los workers
        self.work_queue.join()
        
        # Detener workers
        for _ in workers:
            self.work_queue.put(None)
        
        for worker in workers:
            worker.join()
        
        # Estadísticas finales
        tiempo_total = time.time() - self.stats['tiempo_inicio']
        self.stats['dispositivos_procesados'] = len(dispositivos_online)
        
        self.logger.info("=== SINCRONIZACIÓN MASIVA COMPLETADA ===")
        self.logger.info(f"⏱️  Tiempo total: {tiempo_total:.2f} segundos")
        self.logger.info(f"🖥️  Dispositivos procesados: {self.stats['dispositivos_procesados']}")
        self.logger.info(f"👥 Usuarios sincronizados: {trabajos_exitosos}/{total_trabajos}")
        self.logger.info(f"✅ Tasa de éxito: {(trabajos_exitosos/total_trabajos)*100:.1f}%")
        self.logger.info(f"❌ Errores de conexión: {self.stats['errores_conexion']}")
        
        # Actualizar estadísticas en BD
        self._actualizar_estadisticas_dispositivos(dispositivos_online)

    def _actualizar_estadisticas_dispositivos(self, dispositivos: List[DispositivoHikvision]):
        """Actualizar estadísticas diarias de dispositivos"""
        conn = self.conectar_db()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            fecha_hoy = datetime.now().date()
            
            for dispositivo in dispositivos:
                # Obtener estadísticas del día
                cursor.execute("""
                    SELECT COUNT(*) as exitosas
                    FROM cola_sincronizacion
                    WHERE DispositivoID = ? 
                    AND Estado = 2 
                    AND CAST(FechaCompletado AS DATE) = ?
                """, dispositivo.dispositivo_id, fecha_hoy)
                
                exitosas = cursor.fetchone()[0]
                
                cursor.execute("""
                    SELECT COUNT(*) as fallidas
                    FROM cola_sincronizacion
                    WHERE DispositivoID = ? 
                    AND Estado = 3 
                    AND CAST(FechaCreacion AS DATE) = ?
                """, dispositivo.dispositivo_id, fecha_hoy)
                
                fallidas = cursor.fetchone()[0]
                
                # Insertar o actualizar estadísticas
                cursor.execute("""
                    MERGE estadisticas_dispositivos AS target
                    USING (SELECT ? AS DispositivoID, ? AS Fecha) AS source
                    ON target.DispositivoID = source.DispositivoID AND target.Fecha = source.Fecha
                    WHEN MATCHED THEN
                        UPDATE SET 
                            SincronizacionesExitosas = ?,
                            SincronizacionesFallidas = ?,
                            UltimaActualizacion = GETDATE()
                    WHEN NOT MATCHED THEN
                        INSERT (DispositivoID, Fecha, SincronizacionesExitosas, SincronizacionesFallidas)
                        VALUES (?, ?, ?, ?);
                """, dispositivo.dispositivo_id, fecha_hoy, exitosas, fallidas,
                    dispositivo.dispositivo_id, fecha_hoy, exitosas, fallidas)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error actualizando estadísticas: {e}")

    def limpiar_trabajos_antiguos(self, dias: int = 7):
        """Limpiar trabajos completados antiguos"""
        conn = self.conectar_db()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            fecha_limite = datetime.now() - timedelta(days=dias)
            
            cursor.execute("""
                DELETE FROM cola_sincronizacion
                WHERE Estado = 2 
                AND FechaCompletado < ?
            """, fecha_limite)
            
            eliminados = cursor.rowcount
            conn.commit()
            conn.close()
            
            self.logger.info(f"Limpieza completada: {eliminados} registros eliminados")
            
        except Exception as e:
            self.logger.error(f"Error en limpieza: {e}")

    def generar_reporte_estado(self):
        """Generar reporte del estado actual del sistema"""
        conn = self.conectar_db()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            
            print("\n" + "="*60)
            print("REPORTE DE ESTADO - SISTEMA HIKVISION")
            print("="*60)
            
            # Estado de dispositivos
            cursor.execute("""
                SELECT 
                    Nombre,
                    IPAddress,
                    CASE EstadoConexion 
                        WHEN 1 THEN 'Online'
                        WHEN 2 THEN 'Offline'
                        ELSE 'Desconocido'
                    END as Estado,
                    UltimaConexion,
                    SincronizacionActiva
                FROM hikface 
                WHERE Activo = 1
                ORDER BY Nombre
            """)
            
            print("\n📱 DISPOSITIVOS:")
            print("-" * 50)
            for row in cursor.fetchall():
                estado_sync = "✅" if row[4] else "⏸️"
                print(f"{estado_sync} {row[0]} ({row[1]}) - {row[2]}")
            
            # Cola pendiente
            cursor.execute("""
                SELECT 
                    h.Nombre,
                    COUNT(*) as Pendientes,
                    MIN(cs.FechaCreacion) as MasAntiguo
                FROM cola_sincronizacion cs
                INNER JOIN hikface h ON cs.DispositivoID = h.DispositivoID
                WHERE cs.Estado = 0
                GROUP BY h.DispositivoID, h.Nombre
                ORDER BY COUNT(*) DESC
            """)
            
            print("\n⏳ COLA PENDIENTE:")
            print("-" * 50)
            total_pendientes = 0
            for row in cursor.fetchall():
                total_pendientes += row[1]
                print(f"📤 {row[0]}: {row[1]} registros (desde {row[2]})")
            
            if total_pendientes == 0:
                print("✅ No hay trabajos pendientes")
            
            # Estadísticas del día
            cursor.execute("""
                SELECT 
                    SUM(SincronizacionesExitosas) as Exitosas,
                    SUM(SincronizacionesFallidas) as Fallidas
                FROM estadisticas_dispositivos
                WHERE Fecha = CAST(GETDATE() AS DATE)
            """)
            
            row = cursor.fetchone()
            exitosas = row[0] or 0
            fallidas = row[1] or 0
            total_hoy = exitosas + fallidas
            
            print(f"\n📊 ESTADÍSTICAS HOY:")
            print("-" * 50)
            print(f"✅ Exitosas: {exitosas}")
            print(f"❌ Fallidas: {fallidas}")
            if total_hoy > 0:
                print(f"📈 Tasa éxito: {(exitosas/total_hoy)*100:.1f}%")
            
            print("\n" + "="*60)
            
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error generando reporte: {e}")


def crear_configuracion_ejemplo():
    """Crear archivo de configuración de ejemplo"""
    config = configparser.ConfigParser()
    
    config['DATABASE'] = {
        'connection_string': 'Driver={ODBC Driver 17 for SQL Server};Server=localhost;Database=videoman;Trusted_Connection=yes;'
    }
    
    config['SYNC'] = {
        'max_workers': '5',
        'timeout_connection': '30',
        'retry_attempts': '3'
    }
    
    config['LOGGING'] = {
        'level': 'INFO',
        'file': 'hikvision_massive.log'
    }
    
    with open('hikvision_config.ini', 'w') as configfile:
        config.write(configfile)
    
    print("✅ Archivo de configuración 'hikvision_config.ini' creado")


def main():
    """Función principal"""
    
    # Crear configuración si no existe
    import os
    if not os.path.exists('hikvision_config.ini'):
        crear_configuracion_ejemplo()
        print("⚠️  Configurar hikvision_config.ini antes de continuar")
        return
    
    # Crear instancia del sincronizador
    sync = HikvisionMassiveSync()
    
    # Generar reporte de estado
    sync.generar_reporte_estado()
    
    # Ejecutar sincronización masiva
    sync.sincronizacion_masiva()
    
    # Limpiar trabajos antiguos
    sync.limpiar_trabajos_antiguos()


def programar_sincronizacion_automatica():
    """Programar sincronización automática cada 30 minutos"""
    sync = HikvisionMassiveSync()
    
    schedule.every(30).minutes.do(sync.sincronizacion_masiva)
    schedule.every().day.at("02:00").do(sync.limpiar_trabajos_antiguos)
    schedule.every(5).minutes.do(sync.generar_reporte_estado)
    
    print("🔄 Sincronización automática programada (cada 30 min)")
    print("🧹 Limpieza automática programada (diaria a las 02:00)")
    print("📊 Reporte de estado programado (cada 5 min)")
    
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--auto":
            programar_sincronizacion_automatica()
        elif sys.argv[1] == "--report":
            sync = HikvisionMassiveSync()
            sync.generar_reporte_estado()
        else:
            print("Uso: python massive_sync.py [--auto|--report]")
    else:
        main()
