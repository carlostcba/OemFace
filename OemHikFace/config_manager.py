#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestor de configuración para CRUD Multi-Dispositivo Hikvision
"""

import json
import os
from typing import Dict, List, Any
import configparser

class ConfigManager:
    def __init__(self, config_file="hikvision_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Carga configuración desde archivo"""
        default_config = {
            "devices": [],
            "settings": {
                "event_server_port": 8080,
                "sync_interval": 30,
                "max_retries": 3,
                "timeout": 10,
                "auto_sync": True,
                "backup_enabled": True,
                "backup_interval": 3600
            },
            "user_defaults": {
                "max_fingerprints": 0,
                "max_faces": 5,
                "default_validity_days": 365,
                "door_right": "1",
                "plan_template": "1"
            },
            "logging": {
                "level": "INFO",
                "max_log_size": 10485760,  # 10MB
                "backup_count": 5
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge con configuración por defecto
                    return self.merge_configs(default_config, loaded_config)
            except Exception as e:
                print(f"Error cargando configuración: {e}")
                return default_config
        else:
            # Crear archivo de configuración inicial
            self.save_config(default_config)
            return default_config
    
    def merge_configs(self, default: Dict, loaded: Dict) -> Dict:
        """Mezcla configuración por defecto con la cargada"""
        result = default.copy()
        
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def save_config(self, config: Dict = None):
        """Guarda configuración a archivo"""
        if config is None:
            config = self.config
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error guardando configuración: {e}")
            return False
    
    def add_device_to_config(self, name: str, ip: str, username: str, password: str) -> bool:
        """Añade dispositivo a la configuración"""
        device = {
            "name": name,
            "ip": ip,
            "username": username,
            "password": password,
            "enabled": True,
            "added_date": str(datetime.now())
        }
        
        # Verificar si ya existe
        for existing_device in self.config["devices"]:
            if existing_device["ip"] == ip:
                existing_device.update(device)
                return self.save_config()
        
        self.config["devices"].append(device)
        return self.save_config()
    
    def remove_device_from_config(self, ip: str) -> bool:
        """Elimina dispositivo de la configuración"""
        self.config["devices"] = [
            d for d in self.config["devices"] if d["ip"] != ip
        ]
        return self.save_config()
    
    def get_devices(self) -> List[Dict]:
        """Obtiene lista de dispositivos configurados"""
        return [d for d in self.config["devices"] if d.get("enabled", True)]
    
    def get_setting(self, key: str, default=None):
        """Obtiene un valor de configuración"""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set_setting(self, key: str, value: Any) -> bool:
        """Establece un valor de configuración"""
        keys = key.split('.')
        config = self.config
        
        try:
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            config[keys[-1]] = value
            return self.save_config()
        except Exception:
            return False
    
    def export_config(self, export_path: str) -> bool:
        """Exporta configuración a otro archivo"""
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False
    
    def import_config(self, import_path: str) -> bool:
        """Importa configuración desde archivo"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            self.config = self.merge_configs(self.config, imported_config)
            return self.save_config()
        except Exception:
            return False
    
    def create_device_template(self) -> Dict:
        """Crea plantilla para nuevo dispositivo"""
        return {
            "name": "",
            "ip": "",
            "username": "admin",
            "password": "",
            "enabled": True,
            "model": "DS-K1T344MBFWX-E1",
            "location": "",
            "notes": ""
        }
    
    def validate_config(self) -> List[str]:
        """Valida la configuración y retorna lista de errores"""
        errors = []
        
        # Validar dispositivos
        if not self.config.get("devices"):
            errors.append("No hay dispositivos configurados")
        
        for i, device in enumerate(self.config.get("devices", [])):
            if not device.get("name"):
                errors.append(f"Dispositivo {i+1}: Falta nombre")
            if not device.get("ip"):
                errors.append(f"Dispositivo {i+1}: Falta IP")
            if not device.get("username"):
                errors.append(f"Dispositivo {i+1}: Falta usuario")
            if not device.get("password"):
                errors.append(f"Dispositivo {i+1}: Falta contraseña")
        
        # Validar configuraciones
        settings = self.config.get("settings", {})
        
        port = settings.get("event_server_port", 8080)
        if not isinstance(port, int) or port < 1 or port > 65535:
            errors.append("Puerto del servidor de eventos inválido")
        
        timeout = settings.get("timeout", 10)
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            errors.append("Timeout inválido")
        
        return errors
    
    def get_backup_settings(self) -> Dict:
        """Obtiene configuración de backup"""
        return {
            "enabled": self.get_setting("settings.backup_enabled", True),
            "interval": self.get_setting("settings.backup_interval", 3600),
            "max_backups": self.get_setting("settings.max_backups", 10),
            "backup_path": self.get_setting("settings.backup_path", "./backups")
        }
    
    def create_quick_setup(self) -> Dict:
        """Crea configuración rápida para setup inicial"""
        return {
            "step1_network": {
                "description": "Configurar red de dispositivos",
                "required_info": [
                    "IPs de terminales Hikvision",
                    "Usuario admin (default: admin)", 
                    "Contraseñas de cada terminal"
                ]
            },
            "step2_server": {
                "description": "Configurar servidor de eventos",
                "default_port": 8080,
                "firewall_note": "Abrir puerto en firewall si es necesario"
            },
            "step3_sync": {
                "description": "Configurar sincronización",
                "auto_sync": True,
                "sync_interval": 30,
                "retry_attempts": 3
            },
            "step4_users": {
                "description": "Configurar parámetros de usuarios",
                "max_faces_per_user": 5,
                "max_fingerprints_per_user": 0,
                "default_validity_days": 365
            }
        }

class SetupWizard:
    """Asistente de configuración inicial"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.setup_data = {}
    
    def run_console_wizard(self):
        """Ejecuta asistente en consola"""
        print("🔧 Asistente de Configuración Hikvision Multi-Dispositivo")
        print("=" * 60)
        
        # Paso 1: Dispositivos
        self.setup_devices()
        
        # Paso 2: Configuración del servidor
        self.setup_server()
        
        # Paso 3: Configuración de usuarios
        self.setup_user_defaults()
        
        # Paso 4: Guardar configuración
        self.save_setup()
        
        print("\n✅ Configuración completada!")
        print("📁 Configuración guardada en:", self.config.config_file)
    
    def setup_devices(self):
        """Configurar dispositivos"""
        print("\n📡 PASO 1: Configuración de Dispositivos")
        print("-" * 40)
        
        devices = []
        
        while True:
            print(f"\n🔌 Dispositivo #{len(devices) + 1}")
            
            name = input("Nombre del dispositivo: ").strip()
            if not name:
                break
            
            ip = input("IP del dispositivo: ").strip()
            username = input("Usuario (default: admin): ").strip() or "admin"
            password = input("Contraseña: ").strip()
            
            if ip and password:
                devices.append({
                    "name": name,
                    "ip": ip,
                    "username": username,
                    "password": password,
                    "enabled": True
                })
                print(f"✅ {name} añadido")
            
            if input("\n¿Añadir otro dispositivo? (s/N): ").lower() != 's':
                break
        
        self.config.config["devices"] = devices
        print(f"\n📊 Total dispositivos configurados: {len(devices)}")
    
    def setup_server(self):
        """Configurar servidor de eventos"""
        print("\n🌐 PASO 2: Configuración del Servidor")
        print("-" * 40)
        
        port = input("Puerto del servidor de eventos (default: 8080): ").strip()
        if port.isdigit():
            self.config.set_setting("settings.event_server_port", int(port))
        
        auto_sync = input("¿Habilitar sincronización automática? (S/n): ").lower() != 'n'
        self.config.set_setting("settings.auto_sync", auto_sync)
        
        if auto_sync:
            interval = input("Intervalo de sincronización en segundos (default: 30): ").strip()
            if interval.isdigit():
                self.config.set_setting("settings.sync_interval", int(interval))
        
        print("✅ Configuración del servidor guardada")
    
    def setup_user_defaults(self):
        """Configurar parámetros por defecto de usuarios"""
        print("\n👤 PASO 3: Configuración de Usuarios")
        print("-" * 40)
        
        max_faces = input("Máximo de caras por usuario (default: 5): ").strip()
        if max_faces.isdigit():
            self.config.set_setting("user_defaults.max_faces", int(max_faces))
        
        max_fingerprints = input("Máximo de huellas por usuario (default: 0): ").strip()
        if max_fingerprints.isdigit():
            self.config.set_setting("user_defaults.max_fingerprints", int(max_fingerprints))
        
        validity_days = input("Días de validez por defecto (default: 365): ").strip()
        if validity_days.isdigit():
            self.config.set_setting("user_defaults.default_validity_days", int(validity_days))
        
        print("✅ Configuración de usuarios guardada")
    
    def save_setup(self):
        """Guardar configuración final"""
        print("\n💾 PASO 4: Guardando Configuración")
        print("-" * 40)
        
        if self.config.save_config():
            print("✅ Configuración guardada correctamente")
            
            # Validar configuración
            errors = self.config.validate_config()
            if errors:
                print("\n⚠️ Advertencias en la configuración:")
                for error in errors:
                    print(f"  • {error}")
            else:
                print("✅ Configuración válida")
        else:
            print("❌ Error guardando configuración")

# Archivo de arranque principal
class MultiDeviceApp:
    """Aplicación principal que integra todo"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.crud = None
        self.gui = None
    
    def run_setup_wizard(self):
        """Ejecuta el asistente de configuración"""
        wizard = SetupWizard(self.config)
        wizard.run_console_wizard()
    
    def run_gui(self):
        """Ejecuta la interfaz gráfica"""
        import tkinter as tk
        from gui_multi_device import HikvisionMultiDevice
        
        root = tk.Tk()
        self.gui = HikvisionMultiDevice(root)
        
        # Cargar dispositivos desde configuración
        self.load_devices_from_config()
        
        root.mainloop()
    
    def load_devices_from_config(self):
        """Carga dispositivos desde la configuración"""
        devices = self.config.get_devices()
        
        for device in devices:
            success = self.gui.crud.add_device(
                device["name"],
                device["ip"], 
                device["username"],
                device["password"]
            )
            
            if success:
                print(f"✅ Dispositivo {device['name']} cargado")
            else:
                print(f"❌ Error cargando {device['name']}")
    
    def run_cli(self):
        """Ejecuta interfaz de línea de comandos"""
        from multi_device_crud import MultiDeviceCRUD
        
        self.crud = MultiDeviceCRUD()
        
        print("🖥️ Modo CLI - CRUD Multi-Dispositivo Hikvision")
        print("Comandos disponibles:")
        print("  devices    - Gestionar dispositivos")
        print("  users      - Gestionar usuarios") 
        print("  sync       - Sincronización")
        print("  status     - Estado del sistema")
        print("  exit       - Salir")
        
        while True:
            try:
                command = input("\n> ").strip().lower()
                
                if command == "exit":
                    break
                elif command == "devices":
                    self.cli_devices()
                elif command == "users":
                    self.cli_users()
                elif command == "sync":
                    self.cli_sync()
                elif command == "status":
                    self.cli_status()
                elif command == "help":
                    self.show_help()
                else:
                    print("❌ Comando no reconocido. Usa 'help' para ver comandos.")
                    
            except KeyboardInterrupt:
                print("\n👋 Saliendo...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def cli_devices(self):
        """CLI para gestión de dispositivos"""
        print("\n📡 GESTIÓN DE DISPOSITIVOS")
        print("1. Listar dispositivos")
        print("2. Añadir dispositivo")
        print("3. Probar conexiones")
        print("4. Volver")
        
        choice = input("Selecciona opción: ").strip()
        
        if choice == "1":
            devices = self.crud.get_active_devices()
            if devices:
                print(f"\n📋 Dispositivos configurados ({len(devices)}):")
                for device in devices:
                    status = "🟢" if self.crud.test_device_connection(
                        device['ip'], device['username'], device['password']
                    ) else "🔴"
                    print(f"  {status} {device['name']} ({device['ip']})")
            else:
                print("📭 No hay dispositivos configurados")
                
        elif choice == "2":
            name = input("Nombre: ")
            ip = input("IP: ")
            user = input("Usuario (admin): ") or "admin"
            password = input("Contraseña: ")
            
            if self.crud.add_device(name, ip, user, password):
                print("✅ Dispositivo añadido")
                # También guardar en configuración
                self.config.add_device_to_config(name, ip, user, password)
            else:
                print("❌ Error añadiendo dispositivo")
                
        elif choice == "3":
            devices = self.crud.get_active_devices()
            print("\n🔍 Probando conexiones...")
            
            for device in devices:
                success = self.crud.test_device_connection(
                    device['ip'], device['username'], device['password']
                )
                status = "✅" if success else "❌"
                print(f"  {status} {device['name']} ({device['ip']})")
    
    def cli_users(self):
        """CLI para gestión de usuarios"""
        print("\n👤 GESTIÓN DE USUARIOS")
        print("1. Crear usuario")
        print("2. Listar usuarios")
        print("3. Actualizar usuario")
        print("4. Eliminar usuario")
        print("5. Volver")
        
        choice = input("Selecciona opción: ").strip()
        
        if choice == "1":
            emp_id = input("ID Empleado: ")
            name = input("Nombre: ")
            enabled = input("Habilitado (S/n): ").lower() != 'n'
            image = input("Ruta imagen (opcional): ").strip() or None
            
            result = self.crud.create_user_multi(emp_id, name, enabled, image)
            
            success_count = sum(1 for r in result['sync_results'] if r['status'] == 'success')
            total = len(result['sync_results'])
            
            print(f"📊 Usuario creado en {success_count}/{total} dispositivos")
            
        elif choice == "2":
            import sqlite3
            conn = sqlite3.connect(self.crud.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT employee_no, name, enabled FROM users')
            users = cursor.fetchall()
            conn.close()
            
            if users:
                print(f"\n📋 Usuarios registrados ({len(users)}):")
                for user in users:
                    status = "✅" if user[2] else "❌"
                    print(f"  {status} {user[1]} (ID: {user[0]})")
            else:
                print("📭 No hay usuarios registrados")
                
        elif choice == "3":
            user_id = input("ID del usuario a actualizar: ")
            if user_id.isdigit():
                name = input("Nuevo nombre (Enter para mantener): ").strip() or None
                enabled_input = input("Habilitado S/n/Enter: ").strip().lower()
                enabled = None if not enabled_input else enabled_input != 'n'
                
                result = self.crud.update_user_multi(int(user_id), name=name, enabled=enabled)
                success_count = sum(1 for r in result['sync_results'] if r['status'] == 'success')
                total = len(result['sync_results'])
                
                print(f"📊 Usuario actualizado en {success_count}/{total} dispositivos")
            else:
                print("❌ ID inválido")
                
        elif choice == "4":
            user_id = input("ID del usuario a eliminar: ")
            if user_id.isdigit():
                confirm = input("¿Confirmar eliminación? (s/N): ").lower() == 's'
                if confirm:
                    result = self.crud.delete_user_multi(int(user_id))
                    success_count = sum(1 for r in result['sync_results'] if r['status'] == 'success')
                    total = len(result['sync_results'])
                    
                    print(f"📊 Usuario eliminado de {success_count}/{total} dispositivos")
                else:
                    print("❌ Operación cancelada")
            else:
                print("❌ ID inválido")
    
    def cli_sync(self):
        """CLI para sincronización"""
        print("\n🔄 SINCRONIZACIÓN")
        print("1. Sincronizar todos los usuarios")
        print("2. Estado de sincronización")
        print("3. Log de errores")
        print("4. Volver")
        
        choice = input("Selecciona opción: ").strip()
        
        if choice == "1":
            print("🔄 Iniciando sincronización completa...")
            result = self.crud.sync_all_users()
            
            total_users = result['total_users']
            total_syncs = result['total_syncs']
            success_count = sum(1 for r in result['results'] if r['status'] == 'success')
            
            print(f"📊 Sincronización completa:")
            print(f"  👤 Usuarios: {total_users}")
            print(f"  🔄 Operaciones: {total_syncs}")
            print(f"  ✅ Exitosas: {success_count}")
            print(f"  ❌ Errores: {total_syncs - success_count}")
            
        elif choice == "2":
            status = self.crud.get_sync_status()
            
            print(f"📊 ESTADO DEL SISTEMA:")
            print(f"  📡 Dispositivos activos: {status['devices']}")
            print(f"  👤 Usuarios registrados: {status['users']}")
            print(f"  ❌ Errores recientes: {len(status['recent_errors'])}")
            
        elif choice == "3":
            status = self.crud.get_sync_status()
            recent_errors = status['recent_errors']
            
            if recent_errors:
                print(f"❌ ERRORES RECIENTES ({len(recent_errors)}):")
                for error in recent_errors:
                    print(f"  • Dispositivo {error[0]} - {error[1]}: {error[2]}")
                    print(f"    {error[3]}")
            else:
                print("✅ No hay errores recientes")
    
    def cli_status(self):
        """Muestra estado general del sistema"""
        print("\n📊 ESTADO GENERAL DEL SISTEMA")
        print("=" * 40)
        
        # Dispositivos
        devices = self.crud.get_active_devices()
        print(f"📡 Dispositivos configurados: {len(devices)}")
        
        online_count = 0
        for device in devices:
            if self.crud.test_device_connection(device['ip'], device['username'], device['password']):
                online_count += 1
        
        print(f"🟢 Dispositivos en línea: {online_count}/{len(devices)}")
        
        # Usuarios
        import sqlite3
        conn = sqlite3.connect(self.crud.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        user_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM users WHERE enabled = 1')
        enabled_count = cursor.fetchone()[0]
        conn.close()
        
        print(f"👤 Total usuarios: {user_count}")
        print(f"✅ Usuarios habilitados: {enabled_count}")
        
        # Configuración
        errors = self.config.validate_config()
        if errors:
            print(f"⚠️ Errores de configuración: {len(errors)}")
        else:
            print("✅ Configuración válida")
    
    def show_help(self):
        """Muestra ayuda de comandos"""
        print("\n📚 AYUDA - COMANDOS DISPONIBLES")
        print("=" * 40)
        print("devices    - Gestionar dispositivos Hikvision")
        print("users      - Crear, modificar y eliminar usuarios")
        print("sync       - Sincronización entre dispositivos") 
        print("status     - Estado general del sistema")
        print("help       - Mostrar esta ayuda")
        print("exit       - Salir de la aplicación")

if __name__ == "__main__":
    import sys
    from datetime import datetime
    
    app = MultiDeviceApp()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "setup":
            app.run_setup_wizard()
        elif command == "cli":
            app.run_cli()
        elif command == "gui":
            app.run_gui()
        else:
            print("❌ Comando no reconocido")
            print("Uso: python config_manager.py [setup|cli|gui]")
    else:
        # Sin argumentos, mostrar menú
        print("🔧 CRUD Multi-Dispositivo Hikvision")
        print("=" * 40)
        print("1. Configuración inicial (setup)")
        print("2. Interfaz gráfica (GUI)")
        print("3. Línea de comandos (CLI)")
        print("4. Salir")
        
        choice = input("\nSelecciona una opción: ").strip()
        
        if choice == "1":
            app.run_setup_wizard()
        elif choice == "2":
            app.run_gui()
        elif choice == "3":
            app.run_cli()
        else:
            print("👋 Saliendo...")