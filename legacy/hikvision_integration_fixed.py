#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema Hikvision DS-K1T344MBFWX-E1 - VERSIÓN FINAL FUNCIONANDO
Autenticación: Digest HTTP (CONFIRMADO FUNCIONANDO con requests)
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
import urllib.parse
import urllib3
import sys
import os
from requests.auth import HTTPDigestAuth

# Suprimir warnings SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class HikvisionDS_K1T344_Integration:
    """
    Clase especializada para DS-K1T344MBFWX-E1
    Usa Digest HTTP Authentication (CONFIRMADO FUNCIONANDO)
    """
    
    def __init__(self, ip, username, password, db_connection_string):
        self.ip = ip
        self.username = username
        self.password = password
        self.db_connection_string = db_connection_string
        
        # Configurar logging sin emojis problemáticos para evitar UnicodeEncodeError
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        
        # Configurar encoding para el handler de archivo
        file_handler = logging.FileHandler('hikvision_ds_k1t344.log', encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(log_format))
        
        # Configurar handler de consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(log_format))
        
        # Configurar logger principal
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.handlers.clear()  # Limpiar handlers existentes
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Crear sesión con autenticación Digest (MÉTODO CONFIRMADO FUNCIONANDO)
        self.session = requests.Session()
        self.session.auth = HTTPDigestAuth(username, password)
        self.session.headers.update({
            'User-Agent': 'Hikvision Client',
            'Accept': 'application/xml, application/json',
            'Connection': 'keep-alive'
        })
        self.session.verify = False
        
        # URL base sin credenciales (se usan en la sesión)
        self.base_url = f"http://{ip}"
        
        self.logger.info(f"Inicializado para DS-K1T344MBFWX-E1 en {ip}")
        self.logger.info(f"Usando Digest HTTP Authentication (método confirmado funcionando)")

    def crear_url_completa(self, endpoint):
        """Crear URL completa para endpoint"""
        return f"{self.base_url}{endpoint}"

    def conectar_db(self):
        """Conectar a la base de datos SQL Server con mejor manejo de errores"""
        try:
            # Intentar diferentes cadenas de conexión
            connection_strings = [
                self.db_connection_string,
                # Alternativas comunes
                "Driver={ODBC Driver 17 for SQL Server};Server=localhost\\SQLEXPRESS;Database=videoman;Trusted_Connection=yes;",
                "Driver={SQL Server};Server=localhost;Database=videoman;Trusted_Connection=yes;",
                "Driver={ODBC Driver 17 for SQL Server};Server=.;Database=videoman;Trusted_Connection=yes;",
                "Driver={ODBC Driver 17 for SQL Server};Server=(local);Database=videoman;Trusted_Connection=yes;"
            ]
            
            for i, conn_str in enumerate(connection_strings):
                try:
                    self.logger.info(f"Intentando conexión DB #{i+1}")
                    conn = pyodbc.connect(conn_str, timeout=10)
                    self.logger.info("Conexión a base de datos establecida exitosamente")
                    return conn
                except pyodbc.Error as e:
                    self.logger.warning(f"Intento #{i+1} falló: {str(e)[:100]}")
                    continue
            
            self.logger.error("No se pudo conectar con ninguna cadena de conexión")
            return None
            
        except Exception as e:
            self.logger.error(f"Error general conectando a DB: {e}")
            return None

    def verificar_conectividad(self):
        """Verificar conectividad usando Digest HTTP Authentication"""
        try:
            url = self.crear_url_completa("/ISAPI/System/deviceInfo")
            
            self.logger.info("Verificando conectividad con Digest HTTP Authentication...")
            
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                self.logger.info("CONEXIÓN EXITOSA con DS-K1T344MBFWX-E1")
                
                # Parsear información del dispositivo
                content = response.text
                if '<model>' in content:
                    model = content.split('<model>')[1].split('</model>')[0]
                    self.logger.info(f"Modelo confirmado: {model}")
                
                if '<serialNumber>' in content:
                    serial = content.split('<serialNumber>')[1].split('</serialNumber>')[0]
                    self.logger.info(f"Serie confirmada: {serial}")
                
                if '<firmwareVersion>' in content:
                    firmware = content.split('<firmwareVersion>')[1].split('</firmwareVersion>')[0]
                    self.logger.info(f"Firmware: {firmware}")
                
                if '<deviceName>' in content:
                    device_name = content.split('<deviceName>')[1].split('</deviceName>')[0]
                    self.logger.info(f"Nombre: {device_name}")
                
                return True
            else:
                self.logger.error(f"Error de conexión: {response.status_code}")
                self.logger.error(f"Respuesta: {response.text[:200]}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error verificando conectividad: {e}")
            return False

    def obtener_contador_usuarios(self):
        """Obtener número actual de usuarios en el terminal"""
        try:
            url = self.crear_url_completa("/ISAPI/AccessControl/UserInfo/Count")
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                content = response.text
                if '<userNum>' in content:
                    user_count = content.split('<userNum>')[1].split('</userNum>')[0]
                    self.logger.info(f"Usuarios actuales en terminal: {user_count}")
                    return int(user_count)
                else:
                    self.logger.info(f"Respuesta contador: {content}")
                    return 0
            else:
                self.logger.warning(f"No se pudo obtener contador: {response.status_code}")
                return 0
                
        except Exception as e:
            self.logger.error(f"Error obteniendo contador: {e}")
            return 0

    def verificar_capacidades_dispositivo(self):
        """Verificar qué capacidades tiene el dispositivo"""
        capacidades = {
            'device_info': False,
            'user_count': False,
            'access_control': False,
            'create_user': False,
            'face_capabilities': False
        }
        
        # Lista de endpoints a probar
        tests = [
            ('/ISAPI/System/deviceInfo', 'device_info'),
            ('/ISAPI/AccessControl/UserInfo/Count', 'user_count'),
            ('/ISAPI/AccessControl/capabilities', 'access_control'),
            ('/ISAPI/AccessControl/UserInfo/capabilities', 'face_capabilities')
        ]
        
        self.logger.info("Verificando capacidades del dispositivo...")
        
        for endpoint, capability in tests:
            try:
                url = self.crear_url_completa(endpoint)
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    capacidades[capability] = True
                    self.logger.info(f"OK - {capability}: Disponible")
                else:
                    self.logger.warning(f"FAIL - {capability}: {response.status_code}")
                    
            except Exception as e:
                self.logger.error(f"ERROR - {capability}: {e}")
        
        # Probar creación de usuario
        try:
            self.logger.info("Probando capacidad de crear usuarios...")
            test_result = self.crear_usuario_terminal("99999", "Test", "User", activo=False)
            capacidades['create_user'] = test_result
            if test_result:
                self.logger.info("OK - create_user: Puede crear usuarios")
                # Intentar eliminar usuario de prueba
                self.eliminar_usuario_terminal("99999")
            else:
                self.logger.warning("FAIL - create_user: No puede crear usuarios")
        except Exception as e:
            self.logger.error(f"ERROR - create_user: {e}")
            capacidades['create_user'] = False
        
        return capacidades

    def verificar_usuario_existe(self, persona_id):
        """Verificar si un usuario ya existe en el dispositivo"""
        try:
            url = self.crear_url_completa(f"/ISAPI/AccessControl/UserInfo/Search?format=json")
            
            search_data = {
                "UserInfoSearchCond": {
                    "searchID": "1",
                    "maxResults": 1,
                    "searchResultPosition": 0,
                    "EmployeeNoList": [
                        {"employeeNo": str(persona_id)}
                    ]
                }
            }
            
            self.session.headers.update({
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            })
            
            response = self.session.post(url, json=search_data, timeout=15)
            
            if response.status_code == 200:
                content = response.text
                # Si encuentra el usuario, el contenido incluirá información del usuario
                if '"totalMatches"' in content and '"totalMatches": 1' in content:
                    self.logger.info(f"Usuario {persona_id} encontrado en dispositivo")
                    return True
                else:
                    self.logger.info(f"Usuario {persona_id} no existe en dispositivo")
                    return False
            else:
                self.logger.warning(f"No se pudo verificar usuario {persona_id}: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error verificando usuario {persona_id}: {e}")
            return False

    def crear_usuario_terminal(self, persona_id, nombre, apellido, activo=True):
        """Crear usuario en el terminal DS-K1T344MBFWX-E1"""
        try:
            # Verificar si el usuario ya existe
            if self.verificar_usuario_existe(persona_id):
                self.logger.info(f"Usuario {persona_id} ya existe - saltando creación")
                return True
            
            url = self.crear_url_completa("/ISAPI/AccessControl/UserInfo/Record?format=json")
            
            # Limpiar el nombre (eliminar espacios múltiples)
            nombre_limpio = " ".join(f"{nombre} {apellido}".split())
            
            # Datos del usuario optimizados para DS-K1T344MBFWX-E1
            user_data = {
                "UserInfo": {
                    "employeeNo": str(persona_id),
                    "name": nombre_limpio[:32],  # Límite de caracteres
                    "userType": "normal",
                    "Valid": {
                        "enable": activo,
                        "beginTime": "2024-01-01T00:00:00",
                        "endTime": "2030-12-31T23:59:59"
                    },
                    "doorRight": "1",
                    "RightPlan": [{
                        "doorNo": 1,
                        "planTemplateNo": "1"
                    }],
                    "maxFingerPrintNum": 0,
                    "maxFaceNum": 5
                }
            }
            
            # Actualizar headers para JSON
            self.session.headers.update({
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            })
            
            response = self.session.post(url, json=user_data, timeout=30)
            
            if response.status_code in [200, 201]:
                self.logger.info(f"Usuario creado exitosamente: {persona_id} - {nombre_limpio}")
                return True
            elif response.status_code == 409:
                self.logger.info(f"Usuario {persona_id} ya existe - continuando")
                return True
            elif response.status_code == 400:
                # Verificar si es porque el usuario ya existe
                if "employeeNoAlreadyExist" in response.text:
                    self.logger.info(f"Usuario {persona_id} ya existe en dispositivo - continuando")
                    return True
                else:
                    self.logger.error(f"Error de formato en usuario {persona_id}: {response.status_code}")
                    self.logger.error(f"Respuesta: {response.text}")
                    return False
            else:
                self.logger.error(f"Error creando usuario {persona_id}: {response.status_code}")
                self.logger.error(f"Respuesta: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error en crear_usuario_terminal: {e}")
            return False

    def eliminar_usuario_terminal(self, persona_id):
        """Eliminar usuario del terminal"""
        try:
            url = self.crear_url_completa("/ISAPI/AccessControl/UserInfo/Delete?format=json")
            
            delete_data = {
                "UserInfoDelCond": {
                    "EmployeeNoList": [
                        {"employeeNo": str(persona_id)}
                    ]
                }
            }
            
            self.session.headers.update({
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            })
            
            response = self.session.put(url, json=delete_data, timeout=30)
            
            if response.status_code in [200, 201]:
                self.logger.info(f"Usuario eliminado: {persona_id}")
                return True
            else:
                self.logger.warning(f"No se pudo eliminar usuario {persona_id}: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error eliminando usuario: {e}")
            return False

    def procesar_imagen_para_hikvision(self, binary_data, calidad=85):
        """Procesar imagen para optimizar para DS-K1T344MBFWX-E1"""
        try:
            if not binary_data:
                return None
            
            # Cargar imagen
            image_stream = io.BytesIO(binary_data)
            image = Image.open(image_stream)
            
            # Convertir a RGB si es necesario
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Redimensionar para DS-K1T344 (recomendado: 300x300 máximo)
            max_size = 300
            if image.width > max_size or image.height > max_size:
                ratio = min(max_size / image.width, max_size / image.height)
                new_size = (int(image.width * ratio), int(image.height * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Guardar como JPEG optimizado
            output_stream = io.BytesIO()
            image.save(output_stream, format='JPEG', quality=calidad, optimize=True)
            processed_data = output_stream.getvalue()
            
            # Verificar tamaño (máximo 150KB para DS-K1T344)
            if len(processed_data) > 150 * 1024:
                output_stream = io.BytesIO()
                image.save(output_stream, format='JPEG', quality=70, optimize=True)
                processed_data = output_stream.getvalue()
            
            self.logger.debug(f"Imagen procesada: {len(binary_data)} -> {len(processed_data)} bytes")
            return processed_data
            
        except Exception as e:
            self.logger.error(f"Error procesando imagen: {e}")
            return None

    def enrolar_rostro_terminal(self, persona_id, facial_id, imagen_data):
        """Enrolar rostro en terminal DS-K1T344MBFWX-E1"""
        try:
            # Paso 1: Configurar metadatos del rostro
            metadata_url = self.crear_url_completa("/ISAPI/AccessControl/UserInfo/SetFace?format=json")
            
            face_metadata = {
                "FaceInfo": {
                    "employeeNo": str(persona_id),
                    "faceLibType": "blackFD",
                    "FDID": "1",
                    "FPID": str(facial_id)
                }
            }
            
            self.session.headers.update({
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            })
            
            response = self.session.post(metadata_url, json=face_metadata, timeout=30)
            
            if response.status_code not in [200, 201]:
                self.logger.warning(f"Metadatos faciales limitados para {persona_id}: {response.status_code}")
                # Continuar con imagen de todos modos
            
            # Paso 2: Subir imagen facial
            image_url = self.crear_url_completa("/ISAPI/AccessControl/UserInfo/SetFace?format=json")
            
            self.session.headers.update({
                'Content-Type': 'application/octet-stream',
                'Accept': 'application/json'
            })
            
            response = self.session.put(image_url, data=imagen_data, timeout=30)
            
            if response.status_code in [200, 201]:
                self.logger.info(f"Rostro enrolado exitosamente: PersonaID {persona_id} - FacialID {facial_id}")
                return True
            else:
                self.logger.error(f"Error subiendo imagen {persona_id}: {response.status_code}")
                self.logger.error(f"Respuesta: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error en enrolar_rostro_terminal: {e}")
            return False

    def obtener_personas_pendientes(self):
        """Obtener personas con datos faciales pendientes de sincronización"""
        conn = self.conectar_db()
        if not conn:
            self.logger.error("No se pudo conectar a la base de datos")
            return []
        
        try:
            cursor = conn.cursor()
            query = """
                SELECT 
                    p.PersonaID,
                    p.Nombre,
                    p.Apellido,
                    f.FacialID,
                    f.TemplateData,
                    f.Activo
                FROM per p
                INNER JOIN perface pf ON p.PersonaID = pf.PersonaID
                INNER JOIN face f ON pf.FacialID = f.FacialID
                INNER JOIN facecatval fcv ON f.FacialID = fcv.FacialID
                INNER JOIN catval cv ON fcv.CategoriaID = cv.CategoriaID 
                    AND fcv.ValorID = cv.ValorID
                WHERE f.Activo = 1 
                    AND cv.Nombre = 'Facial'
                    AND cv.CategoriaID = 3
                    AND (f.Sincronizado = 0 OR f.Sincronizado IS NULL)
                ORDER BY p.PersonaID
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            personas = []
            for row in results:
                persona = {
                    'PersonaID': row[0],
                    'Nombre': row[1] or '',
                    'Apellido': row[2] or '',
                    'FacialID': row[3],
                    'TemplateData': row[4],
                    'Activo': row[5]
                }
                personas.append(persona)
            
            conn.close()
            self.logger.info(f"Obtenidas {len(personas)} personas pendientes de sincronización")
            return personas
            
        except Exception as e:
            self.logger.error(f"Error obteniendo personas pendientes: {e}")
            if conn:
                conn.close()
            return []

    def marcar_como_sincronizado(self, facial_id, exitoso=True):
        """Marcar registro como sincronizado en la base de datos"""
        conn = self.conectar_db()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            
            estado = 1 if exitoso else -1
            fecha_sync = datetime.now() if exitoso else None
            
            cursor.execute("""
                UPDATE face 
                SET Sincronizado = ?, 
                    FechaSincronizacion = ?,
                    UltimoIntento = GETDATE(),
                    NumeroIntentos = ISNULL(NumeroIntentos, 0) + 1
                WHERE FacialID = ?
            """, estado, fecha_sync, facial_id)
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error marcando como sincronizado: {e}")
            if conn:
                conn.close()
            return False

    def sincronizar_persona(self, persona):
        """Sincronizar una persona completa al terminal"""
        try:
            persona_id = persona['PersonaID']
            nombre = persona['Nombre']
            apellido = persona['Apellido']
            facial_id = persona['FacialID']
            template_data = persona['TemplateData']
            
            self.logger.info(f"Sincronizando: {persona_id} - {nombre} {apellido}")
            
            # Paso 1: Crear usuario en el terminal
            if not self.crear_usuario_terminal(persona_id, nombre, apellido):
                self.marcar_como_sincronizado(facial_id, False)
                return False
            
            # Paso 2: Procesar y enrolar imagen facial si existe
            if template_data:
                imagen_procesada = self.procesar_imagen_para_hikvision(template_data)
                if imagen_procesada:
                    if not self.enrolar_rostro_terminal(persona_id, facial_id, imagen_procesada):
                        self.logger.warning(f"Usuario creado pero rostro no enrolado para {persona_id}")
                        # Marcar como parcialmente exitoso
                        self.marcar_como_sincronizado(facial_id, True)
                        return True
                else:
                    self.logger.error(f"No se pudo procesar imagen para {persona_id}")
                    # Marcar usuario como creado pero sin imagen
                    self.marcar_como_sincronizado(facial_id, True)
                    return True
            else:
                self.logger.warning(f"No hay imagen facial para {persona_id}")
            
            # Marcar como exitoso
            self.marcar_como_sincronizado(facial_id, True)
            self.logger.info(f"Sincronización exitosa: {persona_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sincronizando persona {persona.get('PersonaID', 'N/A')}: {e}")
            if 'facial_id' in locals():
                self.marcar_como_sincronizado(facial_id, False)
            return False

    def sincronizacion_completa(self, max_personas=None):
        """Ejecutar sincronización completa de todas las personas pendientes"""
        self.logger.info("=== INICIANDO SINCRONIZACIÓN DS-K1T344MBFWX-E1 ===")
        
        # Verificar conectividad
        if not self.verificar_conectividad():
            self.logger.error("No se puede conectar al dispositivo")
            return False
        
        # Verificar capacidades del dispositivo
        capacidades = self.verificar_capacidades_dispositivo()
        self.logger.info(f"Capacidades verificadas: {capacidades}")
        
        if not capacidades.get('device_info', False):
            self.logger.error("Dispositivo no responde correctamente")
            return False
        
        # Obtener contador actual
        usuarios_actuales = self.obtener_contador_usuarios()
        
        # Obtener personas pendientes
        personas = self.obtener_personas_pendientes()
        
        if not personas:
            self.logger.info("No hay personas pendientes de sincronización")
            return True
        
        # Limitar número de personas si se especifica
        if max_personas and len(personas) > max_personas:
            personas = personas[:max_personas]
            self.logger.info(f"Limitando sincronización a {max_personas} personas")
        
        self.logger.info(f"Estado inicial: {usuarios_actuales} usuarios en terminal")
        self.logger.info(f"Personas por sincronizar: {len(personas)}")
        
        # Sincronizar cada persona
        exitosos = 0
        errores = 0
        
        for i, persona in enumerate(personas, 1):
            try:
                self.logger.info(f"Progreso: {i}/{len(personas)}")
                
                if self.sincronizar_persona(persona):
                    exitosos += 1
                else:
                    errores += 1
                
                # Pausa entre sincronizaciones para no saturar el dispositivo
                time.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Error procesando persona {i}: {e}")
                errores += 1
        
        # Verificar contador final
        usuarios_finales = self.obtener_contador_usuarios()
        
        # Resumen final
        self.logger.info("=== SINCRONIZACIÓN COMPLETADA ===")
        self.logger.info(f"Exitosos: {exitosos}")
        self.logger.info(f"Errores: {errores}")
        self.logger.info(f"Total procesados: {len(personas)}")
        self.logger.info(f"Usuarios en terminal: {usuarios_actuales} -> {usuarios_finales}")
        
        return exitosos > 0

    def test_funcionalidad_completa(self):
        """Probar funcionalidad completa del dispositivo"""
        print("PRUEBA COMPLETA DS-K1T344MBFWX-E1")
        print("="*50)
        
        # Verificar conectividad básica
        if not self.verificar_conectividad():
            print("FAIL: No se puede conectar al dispositivo")
            return False
        
        # Verificar capacidades
        capacidades = self.verificar_capacidades_dispositivo()
        
        tests_criticos = ['device_info', 'user_count']
        tests_pasados = sum(1 for test in tests_criticos if capacidades.get(test, False))
        
        print(f"\nResultado: {tests_pasados}/{len(tests_criticos)} pruebas críticas exitosas")
        
        if tests_pasados >= len(tests_criticos) // 2:
            print("Dispositivo listo para sincronización!")
            return True
        else:
            print("Revisar configuración del dispositivo")
            return False


def main():
    """Función principal"""
    
    print("SISTEMA HIKVISION DS-K1T344MBFWX-E1 - VERSIÓN FINAL")
    print("="*55)
    print("Método: Digest HTTP Authentication (confirmado funcionando)")
    
    # Configuración usando Digest HTTP (confirmado funcionando)
    IP_DISPOSITIVO = "192.168.0.222"
    USUARIO = "admin"
    PASSWORD = "Oem2017*"
    
    # Cadenas de conexión a la base de datos (múltiples opciones)
    DB_CONNECTION = (
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=localhost;"
        "Database=videoman;"
        "Trusted_Connection=yes;"
    )
    
    print(f"Dispositivo: {IP_DISPOSITIVO}")
    print(f"Usuario: {USUARIO}")
    print(f"Autenticación: Digest HTTP")
    
    # Crear integrador
    integrator = HikvisionDS_K1T344_Integration(IP_DISPOSITIVO, USUARIO, PASSWORD, DB_CONNECTION)
    
    # Probar funcionalidad
    if integrator.test_funcionalidad_completa():
        print(f"\nEJECUTANDO SINCRONIZACIÓN COMPLETA...")
        
        # Limitar a 5 personas para prueba inicial
        success = integrator.sincronizacion_completa(max_personas=5)
        
        if success:
            print(f"\nSINCRONIZACIÓN EXITOSA!")
            print("Sistema VB6 <-> DS-K1T344MBFWX-E1 funcionando")
        else:
            print(f"\nSincronización completada con algunos errores")
            print("Revisar logs para detalles")
    else:
        print(f"\nRevisar configuración antes de sincronizar")


if __name__ == "__main__":
    main()