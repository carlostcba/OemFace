#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuración y Diagnóstico Hikvision DS-K1T344MBFWX-E1
Usando credenciales embebidas en URL (método confirmado funcionando)
"""

import requests
import pyodbc
import json
import configparser
import os
import sys
import urllib.parse
import urllib3

# Suprimir warnings SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class HikvisionSetup:
    def __init__(self):
        self.config_file = "hikvision_config.ini"
        self.working_method = None
        
    def crear_archivo_configuracion(self):
        """Crear archivo de configuración inicial"""
        config = configparser.ConfigParser()
        
        config['HIKVISION'] = {
            'ip': '192.168.0.222',
            'username': 'admin',
            'password': 'Oem2017*',
            'timeout': '15',
            'auth_method': 'url_embedded'  # Método confirmado funcionando
        }
        
        config['DATABASE'] = {
            'connection_string': 'Driver={ODBC Driver 17 for SQL Server};Server=localhost;Database=videoman;Trusted_Connection=yes;',
            'timeout': '10'
        }
        
        config['SYNC'] = {
            'max_usuarios_por_lote': '50',
            'pausa_entre_usuarios': '2',
            'reintentos_maximos': '3',
            'procesar_imagenes': 'true'
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            config.write(f)
        
        print(f"Archivo de configuración '{self.config_file}' creado")
        return config
    
    def cargar_configuracion(self):
        """Cargar configuración existente o crear nueva"""
        if not os.path.exists(self.config_file):
            print("Creando archivo de configuración...")
            return self.crear_archivo_configuracion()
        
        config = configparser.ConfigParser()
        config.read(self.config_file, encoding='utf-8')
        return config
    
    def crear_url_con_credenciales(self, ip, username, password, endpoint):
        """Crear URL con credenciales embebidas"""
        username_encoded = urllib.parse.quote(username, safe='')
        password_encoded = urllib.parse.quote(password, safe='*')  # Permitir asterisco
        return f"http://{username_encoded}:{password_encoded}@{ip}{endpoint}"
    
    def test_url_embedded_auth(self, ip, username, password):
        """Probar autenticación con credenciales embebidas en URL"""
        try:
            print("Probando credenciales embebidas en URL...")
            
            # Usar exactamente el mismo método que funciona en el navegador
            url = self.crear_url_con_credenciales(ip, username, password, "/ISAPI/System/deviceInfo")
            
            print(f"  URL de prueba: http://{username}:***@{ip}/ISAPI/System/deviceInfo")
            
            # Requests básico sin autenticación adicional
            response = requests.get(url, timeout=15, verify=False)
            
            if response.status_code == 200:
                print(f"  ✓ CREDENCIALES EMBEBIDAS - FUNCIONA")
                
                # Extraer información del dispositivo
                content = response.text
                if '<model>' in content:
                    model = content.split('<model>')[1].split('</model>')[0]
                    print(f"    Modelo: {model}")
                
                if '<serialNumber>' in content:
                    serial = content.split('<serialNumber>')[1].split('</serialNumber>')[0]
                    print(f"    Serie: {serial}")
                
                if '<firmwareVersion>' in content:
                    firmware = content.split('<firmwareVersion>')[1].split('</firmwareVersion>')[0]
                    print(f"    Firmware: {firmware}")
                
                if '<deviceName>' in content:
                    device_name = content.split('<deviceName>')[1].split('</deviceName>')[0]
                    print(f"    Nombre: {device_name}")
                
                self.working_method = "url_embedded"
                return True, "url_embedded"
            else:
                print(f"  ✗ Credenciales embebidas - Error {response.status_code}")
                print(f"    Respuesta: {response.text[:100]}")
                return False, None
                
        except Exception as e:
            print(f"  ✗ Credenciales embebidas - Error: {e}")
            return False, None
    
    def test_endpoints(self, ip, username, password):
        """Probar endpoints disponibles"""
        print("\n=== PROBANDO ENDPOINTS DISPONIBLES ===")
        
        endpoints = [
            ("/ISAPI/System/deviceInfo", "Información del dispositivo"),
            ("/ISAPI/System/status", "Estado del sistema"),
            ("/ISAPI/AccessControl/capabilities", "Capacidades de control"),
            ("/ISAPI/AccessControl/UserInfo/Count", "Contador de usuarios"),
            ("/ISAPI/AccessControl/UserInfo/capabilities", "Capacidades de usuario"),
            ("/ISAPI/Security/users", "Usuarios del sistema"),
            ("/ISAPI/System/Network/interfaces", "Interfaces de red")
        ]
        
        results = {}
        
        for endpoint, description in endpoints:
            try:
                url = self.crear_url_con_credenciales(ip, username, password, endpoint)
                response = requests.get(url, timeout=10, verify=False)
                
                if response.status_code == 200:
                    print(f"  ✓ {description}")
                    results[endpoint] = True
                else:
                    print(f"  ✗ {description} - Error {response.status_code}")
                    results[endpoint] = False
                    
            except Exception as e:
                print(f"  ✗ {description} - Error: {e}")
                results[endpoint] = False
        
        return results
    
    def test_user_operations(self, ip, username, password):
        """Probar operaciones de usuario"""
        print("\n=== PROBANDO OPERACIONES DE USUARIO ===")
        
        # Probar creación de usuario de prueba
        try:
            print("Probando creación de usuario...")
            
            url = self.crear_url_con_credenciales(ip, username, password, "/ISAPI/AccessControl/UserInfo/Record?format=json")
            
            test_user = {
                "UserInfo": {
                    "employeeNo": "99999",
                    "name": "Usuario Prueba",
                    "userType": "normal",
                    "Valid": {
                        "enable": False,  # Deshabilitado para prueba
                        "beginTime": "2024-01-01T00:00:00",
                        "endTime": "2025-12-31T23:59:59"
                    },
                    "doorRight": "1",
                    "maxFaceNum": 1
                }
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1)'
            }
            
            response = requests.post(url, json=test_user, headers=headers, timeout=15, verify=False)
            
            if response.status_code in [200, 201]:
                print("  ✓ Puede crear usuarios")
                
                # Intentar eliminar usuario de prueba
                delete_url = self.crear_url_con_credenciales(ip, username, password, "/ISAPI/AccessControl/UserInfo/Delete?format=json")
                delete_data = {
                    "UserInfoDelCond": {
                        "EmployeeNoList": [{"employeeNo": "99999"}]
                    }
                }
                
                delete_response = requests.put(delete_url, json=delete_data, headers=headers, timeout=15, verify=False)
                if delete_response.status_code in [200, 201]:
                    print("  ✓ Puede eliminar usuarios")
                else:
                    print("  ⚠ No se pudo eliminar usuario de prueba")
                
                return True
            elif response.status_code == 409:
                print("  ⚠ Usuario ya existe")
                return True
            else:
                print(f"  ✗ No puede crear usuarios - Error {response.status_code}")
                print(f"    Respuesta: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"  ✗ Error en operaciones de usuario: {e}")
            return False
    
    def test_database_connection(self):
        """Probar conexión a la base de datos"""
        print("\n=== PROBANDO CONEXIÓN A BASE DE DATOS ===")
        
        config = self.cargar_configuracion()
        connection_string = config.get('DATABASE', 'connection_string')
        
        # Lista de cadenas de conexión alternativas
        connection_strings = [
            connection_string,
            "Driver={ODBC Driver 17 for SQL Server};Server=localhost\\SQLEXPRESS;Database=videoman;Trusted_Connection=yes;",
            "Driver={SQL Server};Server=localhost;Database=videoman;Trusted_Connection=yes;",
            "Driver={ODBC Driver 17 for SQL Server};Server=.;Database=videoman;Trusted_Connection=yes;",
            "Driver={ODBC Driver 17 for SQL Server};Server=(local);Database=videoman;Trusted_Connection=yes;"
        ]
        
        for i, conn_str in enumerate(connection_strings):
            try:
                print(f"Probando conexión #{i+1}...")
                conn = pyodbc.connect(conn_str, timeout=10)
                
                # Probar consulta simple
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM per")
                count = cursor.fetchone()[0]
                
                print(f"  ✓ Conexión exitosa - {count} registros en tabla 'per'")
                conn.close()
                
                # Actualizar configuración con la cadena que funciona
                if i > 0:
                    config.set('DATABASE', 'connection_string', conn_str)
                    with open(self.config_file, 'w', encoding='utf-8') as f:
                        config.write(f)
                    print(f"  📝 Configuración actualizada")
                
                return True, conn_str
                
            except Exception as e:
                print(f"  ✗ Conexión #{i+1} falló: {str(e)[:100]}")
                continue
        
        print("  ✗ No se pudo conectar a la base de datos")
        return False, None
    
    def test_browser_url(self, ip, username, password):
        """Mostrar URL para probar en navegador"""
        print("\n=== PRUEBA EN NAVEGADOR ===")
        
        browser_url = f"http://{username}:{password}@{ip}/ISAPI/System/deviceInfo"
        print(f"URL para probar en navegador:")
        print(f"  {browser_url}")
        print(f"\nSi esta URL funciona en el navegador, el script también debería funcionar")
        
        return browser_url
    
    def run_complete_diagnosis(self):
        """Ejecutar diagnóstico completo"""
        print("="*60)
        print("DIAGNÓSTICO COMPLETO HIKVISION DS-K1T344MBFWX-E1")
        print("="*60)
        print("Método: Credenciales embebidas en URL (confirmado en navegador)")
        
        # Cargar configuración
        config = self.cargar_configuracion()
        ip = config.get('HIKVISION', 'ip')
        username = config.get('HIKVISION', 'username')
        password = config.get('HIKVISION', 'password')
        
        print(f"Dispositivo: {ip}")
        print(f"Usuario: {username}")
        
        results = {
            'auth_success': False,
            'endpoints_working': 0,
            'user_operations': False,
            'database_connection': False
        }
        
        # 1. Mostrar URL para navegador
        browser_url = self.test_browser_url(ip, username, password)
        
        # 2. Probar autenticación con credenciales embebidas
        print(f"\n=== PROBANDO AUTENTICACIÓN ===")
        auth_success, auth_method = self.test_url_embedded_auth(ip, username, password)
        results['auth_success'] = auth_success
        
        if auth_success:
            # Actualizar configuración con método que funciona
            config.set('HIKVISION', 'auth_method', 'url_embedded')
            
            # 3. Probar endpoints
            endpoint_results = self.test_endpoints(ip, username, password)
            results['endpoints_working'] = sum(endpoint_results.values())
            
            # 4. Probar operaciones de usuario
            results['user_operations'] = self.test_user_operations(ip, username, password)
        else:
            print(f"\n❌ AUTENTICACIÓN FALLÓ")
            print(f"Verifica que la URL funcione en el navegador:")
            print(f"  {browser_url}")
        
        # 5. Probar base de datos
        db_success, working_conn_str = self.test_database_connection()
        results['database_connection'] = db_success
        
        # Guardar configuración actualizada
        with open(self.config_file, 'w', encoding='utf-8') as f:
            config.write(f)
        
        # Mostrar resumen
        print("\n" + "="*60)
        print("RESUMEN DEL DIAGNÓSTICO")
        print("="*60)
        
        print(f"Autenticación: {'✓' if results['auth_success'] else '✗'}")
        print(f"Endpoints funcionando: {results['endpoints_working']}/7")
        print(f"Operaciones de usuario: {'✓' if results['user_operations'] else '✗'}")
        print(f"Conexión a base de datos: {'✓' if results['database_connection'] else '✗'}")
        
        # Evaluación final
        score = sum([
            results['auth_success'],
            results['endpoints_working'] >= 3,
            results['user_operations'],
            results['database_connection']
        ])
        
        print(f"\nPuntuación: {score}/4")
        
        if score >= 3:
            print("\n🎉 SISTEMA LISTO PARA PRODUCCIÓN")
            print("✓ Puede proceder con la sincronización masiva")
            print(f"\nEjecute: python hikvision_integration_fixed.py")
            return True
        elif score >= 2:
            print("\n⚠️ SISTEMA PARCIALMENTE FUNCIONAL")
            print("⚠️ Algunas funciones pueden estar limitadas")
            print(f"\nPuede intentar: python hikvision_integration_fixed.py")
            return True
        else:
            print("\n❌ REQUIERE CONFIGURACIÓN ADICIONAL")
            print("❌ Revisar configuración antes de continuar")
            if not results['auth_success']:
                print(f"\n🔧 ACCIONES REQUERIDAS:")
                print(f"1. Verificar que esta URL funcione en el navegador:")
                print(f"   {browser_url}")
                print(f"2. Verificar credenciales del dispositivo")
                print(f"3. Habilitar ISAPI en configuración web")
            return False
    
    def interactive_setup(self):
        """Configuración interactiva"""
        print("CONFIGURACIÓN INTERACTIVA")
        print("="*40)
        
        config = self.cargar_configuracion()
        
        # Solicitar datos del dispositivo
        current_ip = config.get('HIKVISION', 'ip')
        ip = input(f"IP del dispositivo [{current_ip}]: ").strip()
        if not ip:
            ip = current_ip
        
        current_user = config.get('HIKVISION', 'username')
        username = input(f"Usuario [{current_user}]: ").strip()
        if not username:
            username = current_user
        
        password = input("Contraseña: ").strip()
        if not password:
            password = config.get('HIKVISION', 'password')
        
        # Actualizar configuración
        config.set('HIKVISION', 'ip', ip)
        config.set('HIKVISION', 'username', username)
        config.set('HIKVISION', 'password', password)
        
        # Guardar configuración
        with open(self.config_file, 'w', encoding='utf-8') as f:
            config.write(f)
        
        print("\nConfiguración guardada")
        
        # Mostrar URL para probar en navegador
        print(f"\nPrimero prueba esta URL en tu navegador:")
        print(f"http://{username}:{password}@{ip}/ISAPI/System/deviceInfo")
        print(f"\nSi funciona en el navegador, presiona Enter para continuar...")
        input()
        
        # Ejecutar diagnóstico
        return self.run_complete_diagnosis()


def main():
    """Función principal"""
    setup = HikvisionSetup()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--interactive":
            setup.interactive_setup()
        elif sys.argv[1] == "--test":
            setup.run_complete_diagnosis()
        elif sys.argv[1] == "--create-config":
            setup.crear_archivo_configuracion()
            print("Archivo de configuración creado. Edite los valores y ejecute --test")
        else:
            print("Uso:")
            print("  --interactive    Configuración interactiva")
            print("  --test          Solo ejecutar diagnóstico")
            print("  --create-config Solo crear archivo de configuración")
    else:
        # Por defecto, ejecutar diagnóstico completo
        setup.run_complete_diagnosis()

if __name__ == "__main__":
    main()