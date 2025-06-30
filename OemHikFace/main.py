#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lanzador principal para CRUD Multi-Dispositivo Hikvision
Sistema completo para gestión de usuarios en múltiples terminales DS-K1T344MBFWX-E1
"""

import sys
import os
import subprocess
import importlib.util

def check_dependencies():
    """Verifica dependencias requeridas"""
    required_packages = [
        'tkinter',
        'requests', 
        'sqlite3',
        'threading',
        'json',
        'datetime'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'tkinter':
                import tkinter
            elif package == 'requests':
                import requests
            elif package == 'sqlite3':
                import sqlite3
            elif package == 'threading':
                import threading
            elif package == 'json':
                import json
            elif package == 'datetime':
                import datetime
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Faltan dependencias:")
        for pkg in missing_packages:
            print(f"  • {pkg}")
        
        if 'requests' in missing_packages:
            print("\n📦 Para instalar requests:")
            print("pip install requests")
        
        if 'tkinter' in missing_packages:
            print("\n📦 Para instalar tkinter:")
            print("Ubuntu/Debian: sudo apt-get install python3-tk")
            print("Windows: Ya incluido con Python")
        
        return False
    
    return True

def show_main_menu():
    """Muestra menú principal"""
    print("""
🔧 CRUD Multi-Dispositivo Hikvision DS-K1T344MBFWX-E1
═══════════════════════════════════════════════════════

📋 OPCIONES DISPONIBLES:

1️⃣  Configuración Inicial (Primera vez)
    - Asistente paso a paso
    - Configurar dispositivos
    - Probar conexiones

2️⃣  Interfaz Gráfica (Recomendado)
    - Gestión visual completa
    - Monitoreo en tiempo real
    - Sincronización multi-dispositivo

3️⃣  Línea de Comandos (Avanzado)
    - Control total desde terminal
    - Automatización con scripts
    - Ideal para servidores

4️⃣  Verificar Sistema
    - Estado de dispositivos
    - Validar configuración
    - Diagnósticos

5️⃣  Ayuda y Documentación

0️⃣  Salir

═══════════════════════════════════════════════════════
    """)

def show_help():
    """Muestra ayuda y documentación"""
    print("""
📚 AYUDA - CRUD Multi-Dispositivo Hikvision
═══════════════════════════════════════════

🎯 OBJETIVO:
   Gestionar usuarios en múltiples terminales Hikvision
   con sincronización automática y monitoreo de eventos.

📡 DISPOSITIVOS SOPORTADOS:
   • DS-K1T344MBFWX-E1 (Principal)
   • Otras series DS-K1T con API similar

⚙️ FUNCIONALIDADES:
   ✅ Crear usuarios en todos los dispositivos
   ✅ Actualizar información sincronizada
   ✅ Eliminar usuarios de toda la red
   ✅ Subir fotos faciales automáticamente
   ✅ Monitoreo de eventos en tiempo real
   ✅ Backup automático de configuración

🔧 CONFIGURACIÓN INICIAL:
   1. Ejecuta "Configuración Inicial"
   2. Añade IPs de tus dispositivos
   3. Configura credenciales admin
   4. Prueba conectividad
   5. ¡Listo para usar!

🌐 REQUISITOS DE RED:
   • Dispositivos en la misma red
   • Puerto 8080 disponible (eventos)
   • Credenciales admin de cada terminal

💡 CONSEJOS:
   • Usa la interfaz gráfica para inicio
   • CLI es ideal para automatización
   • Siempre haz backup antes de cambios masivos

🆘 SOPORTE:
   • Revisa logs en caso de errores
   • Verifica conectividad de red
   • Consulta manual del dispositivo

═══════════════════════════════════════════
    """)

def run_setup():
    """Ejecuta configuración inicial"""
    try:
        from config_manager import MultiDeviceApp
        app = MultiDeviceApp()
        app.run_setup_wizard()
    except ImportError:
        print("❌ Error: No se puede cargar config_manager.py")
        print("Asegúrate de que todos los archivos estén en la misma carpeta")
    except Exception as e:
        print(f"❌ Error en configuración: {e}")

def run_gui():
    """Ejecuta interfaz gráfica"""
    try:
        from config_manager import MultiDeviceApp
        app = MultiDeviceApp()
        app.run_gui()
    except ImportError as e:
        print(f"❌ Error importando módulos: {e}")
        print("Archivos requeridos:")
        print("  • multi_device_crud.py")
        print("  • gui_multi_device.py") 
        print("  • config_manager.py")
    except Exception as e:
        print(f"❌ Error en interfaz gráfica: {e}")

def run_cli():
    """Ejecuta interfaz de línea de comandos"""
    try:
        from config_manager import MultiDeviceApp
        app = MultiDeviceApp()
        app.run_cli()
    except ImportError:
        print("❌ Error: No se pueden cargar los módulos")
    except Exception as e:
        print(f"❌ Error en CLI: {e}")

def verify_system():
    """Verifica estado del sistema"""
    print("\n🔍 VERIFICANDO SISTEMA...")
    print("=" * 40)
    
    # Verificar archivos
    required_files = [
        'multi_device_crud.py',
        'gui_multi_device.py',
        'config_manager.py'
    ]
    
    print("📁 Archivos requeridos:")
    all_files_ok = True
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - FALTA")
            all_files_ok = False
    
    # Verificar configuración
    print("\n⚙️ Configuración:")
    if os.path.exists('hikvision_config.json'):
        try:
            import json
            with open('hikvision_config.json', 'r') as f:
                config = json.load(f)
            
            device_count = len(config.get('devices', []))
            print(f"  ✅ Archivo de configuración existe")
            print(f"  📡 Dispositivos configurados: {device_count}")
            
            if device_count == 0:
                print("  ⚠️ No hay dispositivos configurados")
                print("  💡 Ejecuta 'Configuración Inicial'")
                
        except Exception as e:
            print(f"  ❌ Error leyendo configuración: {e}")
    else:
        print("  ⚠️ No existe archivo de configuración")
        print("  💡 Ejecuta 'Configuración Inicial'")
    
    # Verificar base de datos
    print("\n💾 Base de datos:")
    if os.path.exists('devices.db'):
        try:
            import sqlite3
            conn = sqlite3.connect('devices.db')
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM devices WHERE active = 1')
            device_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM users')
            user_count = cursor.fetchone()[0]
            
            conn.close()
            
            print(f"  ✅ Base de datos existe")
            print(f"  📡 Dispositivos activos: {device_count}")
            print(f"  👤 Usuarios registrados: {user_count}")
            
        except Exception as e:
            print(f"  ❌ Error accediendo a BD: {e}")
    else:
        print("  ℹ️ Base de datos se creará al primer uso")
    
    # Resultado final
    print("\n" + "=" * 40)
    if all_files_ok:
        print("✅ Sistema listo para usar")
        print("💡 Recomendación: Usa 'Interfaz Gráfica'")
    else:
        print("❌ Sistema incompleto")
        print("💡 Descarga todos los archivos del proyecto")

def main():
    """Función principal"""
    print("🚀 Iniciando CRUD Multi-Dispositivo Hikvision...")
    
    # Verificar dependencias
    if not check_dependencies():
        print("\n❌ No se pueden cargar las dependencias requeridas")
        print("🔧 Instala los paquetes faltantes y vuelve a intentar")
        return
    
    while True:
        show_main_menu()
        
        try:
            choice = input("👉 Selecciona una opción (0-5): ").strip()
            
            if choice == "0":
                print("\n👋 ¡Hasta luego!")
                break
                
            elif choice == "1":
                print("\n🔧 Iniciando configuración inicial...")
                run_setup()
                
            elif choice == "2":
                print("\n🖥️ Cargando interfaz gráfica...")
                run_gui()
                
            elif choice == "3":
                print("\n💻 Iniciando línea de comandos...")
                run_cli()
                
            elif choice == "4":
                verify_system()
                
            elif choice == "5":
                show_help()
                
            else:
                print("❌ Opción inválida. Selecciona 0-5.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Saliendo...")
            break
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            print("🔄 Reiniciando menú...")
        
        input("\n📎 Presiona Enter para continuar...")

if __name__ == "__main__":
    main()