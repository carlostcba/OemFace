#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema CRUD Multi-Dispositivo para terminales Hikvision con sincronización automática
"""

import json
import os
import sqlite3
import threading
import time
from datetime import datetime
from typing import List, Dict, Any
import requests
from requests.auth import HTTPDigestAuth
import concurrent.futures

class MultiDeviceCRUD:
    def __init__(self, db_path="devices.db"):
        self.db_path = db_path
        self.devices = []
        self.sync_lock = threading.Lock()
        self.init_database()
        
    def init_database(self):
        """Inicializa la base de datos local"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de dispositivos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                ip TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                active BOOLEAN DEFAULT 1,
                last_sync TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de usuarios (cache local)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                employee_no TEXT NOT NULL,
                name TEXT NOT NULL,
                enabled BOOLEAN DEFAULT 1,
                image_path TEXT,
                sync_status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de sincronización
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_log (
                id INTEGER PRIMARY KEY,
                device_id INTEGER,
                user_id INTEGER,
                action TEXT,
                status TEXT,
                error_msg TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES devices (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_device(self, name: str, ip: str, username: str, password: str) -> bool:
        """Añade un dispositivo a la lista"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO devices (name, ip, username, password)
                VALUES (?, ?, ?, ?)
            ''', (name, ip, username, password))
            
            device_id = cursor.lastrowid
            conn.commit()
            
            # Probar conexión
            if self.test_device_connection(ip, username, password):
                self.log_message(f"✅ Dispositivo {name} ({ip}) añadido correctamente")
                return True
            else:
                self.log_message(f"⚠️ Dispositivo {name} añadido pero sin conexión")
                return False
                
        except Exception as e:
            self.log_message(f"❌ Error añadiendo dispositivo: {e}")
            return False
        finally:
            conn.close()
    
    def get_active_devices(self) -> List[Dict]:
        """Obtiene lista de dispositivos activos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM devices WHERE active = 1')
        devices = []
        
        for row in cursor.fetchall():
            devices.append({
                'id': row[0],
                'name': row[1],
                'ip': row[2],
                'username': row[3],
                'password': row[4],
                'last_sync': row[6]
            })
        
        conn.close()
        return devices
    
    def test_device_connection(self, ip: str, username: str, password: str) -> bool:
        """Prueba conexión con un dispositivo"""
        try:
            url = f"http://{ip}/ISAPI/System/deviceInfo"
            response = requests.get(
                url,
                auth=HTTPDigestAuth(username, password),
                timeout=5,
                verify=False
            )
            return response.status_code == 200
        except:
            return False
    
    def create_user_multi(self, employee_no: str, name: str, enabled: bool = True, 
                         image_path: str = None) -> Dict[str, Any]:
        """Crea usuario en todos los dispositivos activos"""
        
        # Guardar en BD local
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO users (employee_no, name, enabled, image_path)
            VALUES (?, ?, ?, ?)
        ''', (employee_no, name, enabled, image_path))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Sincronizar con dispositivos
        result = self.sync_user_to_devices(user_id, 'create')
        
        return {
            'user_id': user_id,
            'sync_results': result
        }
    
    def update_user_multi(self, user_id: int, employee_no: str = None, 
                         name: str = None, enabled: bool = None, 
                         image_path: str = None) -> Dict[str, Any]:
        """Actualiza usuario en todos los dispositivos"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Construir query dinámicamente
        updates = []
        params = []
        
        if employee_no is not None:
            updates.append("employee_no = ?")
            params.append(employee_no)
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if enabled is not None:
            updates.append("enabled = ?")
            params.append(enabled)
        if image_path is not None:
            updates.append("image_path = ?")
            params.append(image_path)
        
        if updates:
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(user_id)
            
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
        
        conn.close()
        
        # Sincronizar cambios
        result = self.sync_user_to_devices(user_id, 'update')
        
        return {
            'user_id': user_id,
            'sync_results': result
        }
    
    def delete_user_multi(self, user_id: int) -> Dict[str, Any]:
        """Elimina usuario de todos los dispositivos"""
        
        # Primero sincronizar eliminación
        result = self.sync_user_to_devices(user_id, 'delete')
        
        # Luego eliminar de BD local
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
        
        return {
            'user_id': user_id,
            'sync_results': result
        }
    
    def sync_user_to_devices(self, user_id: int, action: str) -> List[Dict]:
        """Sincroniza un usuario con todos los dispositivos activos"""
        
        # Obtener datos del usuario
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user_data = cursor.fetchone()
        conn.close()
        
        if not user_data and action != 'delete':
            return [{'error': 'Usuario no encontrado'}]
        
        devices = self.get_active_devices()
        results = []
        
        # Usar threading para sincronización paralela
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            
            for device in devices:
                future = executor.submit(
                    self.sync_single_device, 
                    device, user_data, action, user_id
                )
                futures.append((device, future))
            
            # Recopilar resultados
            for device, future in futures:
                try:
                    result = future.result(timeout=30)
                    results.append({
                        'device': device['name'],
                        'ip': device['ip'],
                        'status': result['status'],
                        'message': result.get('message', '')
                    })
                except Exception as e:
                    results.append({
                        'device': device['name'],
                        'ip': device['ip'],
                        'status': 'error',
                        'message': str(e)
                    })
                    
                    # Log del error
                    self.log_sync_error(device['id'], user_id, action, str(e))
        
        return results
    
    def sync_single_device(self, device: Dict, user_data: tuple, 
                          action: str, user_id: int) -> Dict:
        """Sincroniza con un dispositivo específico"""
        
        try:
            if action == 'create':
                return self.create_user_on_device(device, user_data)
            elif action == 'update':
                return self.update_user_on_device(device, user_data)
            elif action == 'delete':
                return self.delete_user_on_device(device, user_data[1] if user_data else str(user_id))
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def create_user_on_device(self, device: Dict, user_data: tuple) -> Dict:
        """Crea usuario en un dispositivo específico"""
        
        employee_no, name, enabled, image_path = user_data[1:5]
        
        # Datos del usuario para Hikvision
        user_info = {
            "UserInfo": {
                "employeeNo": str(employee_no),
                "name": name,
                "userType": "normal",
                "Valid": {
                    "enable": enabled,
                    "beginTime": "2024-01-01T00:00:00",
                    "endTime": "2025-12-31T23:59:59"
                },
                "doorRight": "1",
                "RightPlan": [{"doorNo": 1, "planTemplateNo": "1"}],
                "maxFingerPrintNum": 0,
                "maxFaceNum": 5 if image_path else 0
            }
        }
        
        # Crear usuario
        url = f"http://{device['ip']}/ISAPI/AccessControl/UserInfo/SetUp"
        
        response = requests.put(
            url,
            json=user_info,
            auth=HTTPDigestAuth(device['username'], device['password']),
            headers={'Content-Type': 'application/json'},
            timeout=10,
            verify=False
        )
        
        if response.status_code == 200:
            # Si hay imagen, subirla
            if image_path and os.path.exists(image_path):
                face_result = self.upload_face_to_device(device, employee_no, image_path)
                if face_result['status'] == 'success':
                    return {'status': 'success', 'message': 'Usuario y foto creados'}
                else:
                    return {'status': 'partial', 'message': 'Usuario creado, error en foto'}
            else:
                return {'status': 'success', 'message': 'Usuario creado'}
        else:
            return {'status': 'error', 'message': f'HTTP {response.status_code}'}
    
    def upload_face_to_device(self, device: Dict, employee_no: str, image_path: str) -> Dict:
        """Sube imagen facial a dispositivo"""
        
        try:
            url = f"http://{device['ip']}/ISAPI/Intelligent/FDLib/FaceDataRecord/capabilities"
            
            with open(image_path, 'rb') as img_file:
                files = {
                    'FaceDataRecord': (None, json.dumps({
                        "faceLibType": "blackFD",
                        "FDID": "1",
                        "FPID": employee_no
                    }), 'application/json'),
                    'FaceImage': (os.path.basename(image_path), img_file, 'image/jpeg')
                }
                
                response = requests.post(
                    url,
                    files=files,
                    auth=HTTPDigestAuth(device['username'], device['password']),
                    timeout=15,
                    verify=False
                )
                
                if response.status_code == 200:
                    return {'status': 'success'}
                else:
                    return {'status': 'error', 'message': f'HTTP {response.status_code}'}
                    
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def sync_all_users(self) -> Dict[str, Any]:
        """Sincroniza todos los usuarios locales con todos los dispositivos"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users')
        user_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        total_results = []
        
        for user_id in user_ids:
            result = self.sync_user_to_devices(user_id, 'update')
            total_results.extend(result)
        
        return {
            'total_users': len(user_ids),
            'total_syncs': len(total_results),
            'results': total_results
        }
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Obtiene estado de sincronización"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Contar dispositivos
        cursor.execute('SELECT COUNT(*) FROM devices WHERE active = 1')
        device_count = cursor.fetchone()[0]
        
        # Contar usuarios
        cursor.execute('SELECT COUNT(*) FROM users')
        user_count = cursor.fetchone()[0]
        
        # Últimos errores
        cursor.execute('''
            SELECT device_id, action, error_msg, timestamp 
            FROM sync_log 
            WHERE status = 'error' 
            ORDER BY timestamp DESC 
            LIMIT 5
        ''')
        
        recent_errors = cursor.fetchall()
        conn.close()
        
        return {
            'devices': device_count,
            'users': user_count,
            'recent_errors': recent_errors
        }
    
    def log_sync_error(self, device_id: int, user_id: int, action: str, error_msg: str):
        """Registra error de sincronización"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sync_log (device_id, user_id, action, status, error_msg)
            VALUES (?, ?, ?, 'error', ?)
        ''', (device_id, user_id, action, error_msg))
        
        conn.commit()
        conn.close()
    
    def log_message(self, message: str):
        """Log de mensajes (override en la interfaz gráfica)"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

# Ejemplo de uso
if __name__ == "__main__":
    # Inicializar sistema multi-dispositivo
    crud = MultiDeviceCRUD()
    
    # Añadir dispositivos
    crud.add_device("Terminal Principal", "192.168.1.100", "admin", "password123")
    crud.add_device("Terminal Entrada", "192.168.1.101", "admin", "password123")
    crud.add_device("Terminal Salida", "192.168.1.102", "admin", "password123")
    
    # Crear usuario en todos los dispositivos
    result = crud.create_user_multi("12345", "Juan Pérez", True, "/path/to/photo.jpg")
    print("Resultado creación:", result)
    
    # Actualizar usuario
    result = crud.update_user_multi(1, name="Juan Carlos Pérez")
    print("Resultado actualización:", result)
    
    # Estado de sincronización
    status = crud.get_sync_status()
    print("Estado:", status)