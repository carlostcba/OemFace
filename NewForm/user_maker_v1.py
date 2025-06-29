#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interfaz gráfica para crear usuarios en terminal Hikvision DS-K1T344MBFWX-E1
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import json
from requests.auth import HTTPDigestAuth
import urllib3
import threading
from datetime import datetime, timedelta

# Suprimir warnings SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class HikvisionUserCreator:
    def __init__(self, root):
        self.root = root
        self.root.title("Creador de Usuarios Hikvision DS-K1T344MBFWX-E1")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Variables
        self.session = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuración de conexión
        conn_frame = ttk.LabelFrame(main_frame, text="Configuración de Conexión", padding="10")
        conn_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(conn_frame, text="IP del Dispositivo:").grid(row=0, column=0, sticky=tk.W)
        self.ip_var = tk.StringVar(value="192.168.0.222")
        ttk.Entry(conn_frame, textvariable=self.ip_var, width=20).grid(row=0, column=1, sticky=tk.W, padx=(5, 20))
        
        ttk.Label(conn_frame, text="Usuario:").grid(row=0, column=2, sticky=tk.W)
        self.user_var = tk.StringVar(value="admin")
        ttk.Entry(conn_frame, textvariable=self.user_var, width=15).grid(row=0, column=3, sticky=tk.W, padx=(5, 20))
        
        ttk.Label(conn_frame, text="Contraseña:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.pass_var = tk.StringVar(value="Oem2017*")
        ttk.Entry(conn_frame, textvariable=self.pass_var, show="*", width=20).grid(row=1, column=1, sticky=tk.W, padx=(5, 20), pady=(5, 0))
        
        ttk.Button(conn_frame, text="Probar Conexión", command=self.test_connection).grid(row=1, column=2, columnspan=2, pady=(5, 0))
        
        # Datos del usuario
        user_frame = ttk.LabelFrame(main_frame, text="Datos del Usuario", padding="10")
        user_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(user_frame, text="ID Empleado:").grid(row=0, column=0, sticky=tk.W)
        self.employee_var = tk.StringVar()
        ttk.Entry(user_frame, textvariable=self.employee_var, width=20).grid(row=0, column=1, sticky=tk.W, padx=(5, 20))
        
        ttk.Label(user_frame, text="Nombre Completo:").grid(row=0, column=2, sticky=tk.W)
        self.name_var = tk.StringVar()
        ttk.Entry(user_frame, textvariable=self.name_var, width=30).grid(row=0, column=3, sticky=tk.W, padx=(5, 0))
        
        # Configuración de acceso
        access_frame = ttk.LabelFrame(main_frame, text="Configuración de Acceso", padding="10")
        access_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(access_frame, text="Estado:").grid(row=0, column=0, sticky=tk.W)
        self.enabled_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(access_frame, text="Habilitado", variable=self.enabled_var).grid(row=0, column=1, sticky=tk.W, padx=(5, 20))
        
        ttk.Label(access_frame, text="Fecha Inicio:").grid(row=0, column=2, sticky=tk.W)
        self.start_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(access_frame, textvariable=self.start_date_var, width=12).grid(row=0, column=3, sticky=tk.W, padx=(5, 0))
        
        ttk.Label(access_frame, text="Fecha Fin:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        end_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
        self.end_date_var = tk.StringVar(value=end_date)
        ttk.Entry(access_frame, textvariable=self.end_date_var, width=12).grid(row=1, column=1, sticky=tk.W, padx=(5, 20), pady=(5, 0))
        
        ttk.Label(access_frame, text="Max. Huellas:").grid(row=1, column=2, sticky=tk.W, pady=(5, 0))
        self.fingerprints_var = tk.IntVar(value=0)
        ttk.Spinbox(access_frame, from_=0, to=10, textvariable=self.fingerprints_var, width=5).grid(row=1, column=3, sticky=tk.W, padx=(5, 0), pady=(5, 0))
        
        ttk.Label(access_frame, text="Max. Caras:").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        self.faces_var = tk.IntVar(value=5)
        ttk.Spinbox(access_frame, from_=0, to=10, textvariable=self.faces_var, width=5).grid(row=2, column=1, sticky=tk.W, padx=(5, 0), pady=(5, 0))
        
        # Botones de acción
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(0, 10))
        
        ttk.Button(button_frame, text="Crear Usuario", command=self.create_user, style="Accent.TButton").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Limpiar Campos", command=self.clear_fields).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Listar Usuarios", command=self.list_users).pack(side=tk.LEFT)
        
        # Log de actividad
        log_frame = ttk.LabelFrame(main_frame, text="Log de Actividad", padding="10")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configurar expansión
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
    def log_message(self, message):
        """Agregar mensaje al log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def create_session(self):
        """Crear sesión con autenticación"""
        try:
            session = requests.Session()
            session.auth = HTTPDigestAuth(self.user_var.get(), self.pass_var.get())
            session.headers.update({
                'User-Agent': 'Hikvision Client',
                'Accept': 'application/xml, application/json',
                'Connection': 'keep-alive',
                'Content-Type': 'application/json'
            })
            session.verify = False
            return session
        except Exception as e:
            self.log_message(f"❌ Error creando sesión: {e}")
            return None
            
    def test_connection(self):
        """Probar conexión al dispositivo"""
        def test():
            self.log_message("🔍 Probando conexión...")
            session = self.create_session()
            if not session:
                return
                
            try:
                url = f"http://{self.ip_var.get()}/ISAPI/System/deviceInfo"
                response = session.get(url, timeout=10)
                
                if response.status_code == 200:
                    self.log_message("✅ Conexión exitosa")
                    self.session = session
                    # Extraer información del dispositivo
                    if 'xml' in response.headers.get('content-type', ''):
                        self.log_message(f"📱 Dispositivo conectado")
                    else:
                        self.log_message(f"📱 Respuesta: {response.status_code}")
                else:
                    self.log_message(f"❌ Error de conexión: {response.status_code}")
                    
            except Exception as e:
                self.log_message(f"❌ Error de conexión: {e}")
                
        threading.Thread(target=test, daemon=True).start()
        
    def create_user(self):
        """Crear usuario en el dispositivo"""
        def create():
            # Validaciones
            if not self.employee_var.get() or not self.name_var.get():
                messagebox.showerror("Error", "ID Empleado y Nombre son obligatorios")
                return
                
            if not self.session:
                self.log_message("⚠️ Conectándose al dispositivo...")
                self.session = self.create_session()
                if not self.session:
                    return
                    
            self.log_message(f"👤 Creando usuario: {self.name_var.get()} (ID: {self.employee_var.get()})")
            
            # Preparar datos del usuario
            user_data = {
                "UserInfo": {
                    "employeeNo": str(self.employee_var.get()),
                    "name": self.name_var.get(),
                    "userType": "normal",
                    "Valid": {
                        "enable": self.enabled_var.get(),
                        "beginTime": f"{self.start_date_var.get()}T00:00:00",
                        "endTime": f"{self.end_date_var.get()}T23:59:59"
                    },
                    "doorRight": "1",
                    "RightPlan": [{
                        "doorNo": 1,
                        "planTemplateNo": "1"
                    }],
                    "maxFingerPrintNum": self.fingerprints_var.get(),
                    "maxFaceNum": self.faces_var.get()
                }
            }
            
            url = f"http://{self.ip_var.get()}/ISAPI/AccessControl/UserInfo/Record?format=json"
            
            try:
                response = self.session.post(url, json=user_data, timeout=30)
                
                if response.status_code in [200, 201]:
                    self.log_message("✅ Usuario creado exitosamente")
                    messagebox.showinfo("Éxito", f"Usuario '{self.name_var.get()}' creado correctamente")
                    self.clear_fields()
                elif response.status_code == 409:
                    self.log_message("⚠️ El usuario ya existe")
                    messagebox.showwarning("Advertencia", "El usuario ya existe en el sistema")
                else:
                    self.log_message(f"❌ Error {response.status_code}: {response.text}")
                    messagebox.showerror("Error", f"Error al crear usuario: {response.status_code}")
                    
            except Exception as e:
                self.log_message(f"❌ Excepción: {e}")
                messagebox.showerror("Error", f"Error de conexión: {e}")
                
        threading.Thread(target=create, daemon=True).start()
        
    def list_users(self):
        """Listar usuarios existentes"""
        def list_all():
            if not self.session:
                self.session = self.create_session()
                if not self.session:
                    return
                    
            self.log_message("📋 Obteniendo lista de usuarios...")
            
            url = f"http://{self.ip_var.get()}/ISAPI/AccessControl/UserInfo/Search?format=json"
            
            search_data = {
                "UserInfoSearchCond": {
                    "searchID": "1",
                    "maxResults": 100,
                    "searchResultPosition": 0
                }
            }
            
            try:
                response = self.session.post(url, json=search_data, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    users = data.get('UserInfoSearch', {}).get('UserInfo', [])
                    
                    if users:
                        self.log_message(f"📋 Encontrados {len(users)} usuarios:")
                        for user in users[:10]:  # Mostrar solo los primeros 10
                            name = user.get('name', 'Sin nombre')
                            emp_no = user.get('employeeNo', 'Sin ID')
                            enabled = user.get('Valid', {}).get('enable', False)
                            status = "✅" if enabled else "❌"
                            self.log_message(f"  {status} {name} (ID: {emp_no})")
                        
                        if len(users) > 10:
                            self.log_message(f"  ... y {len(users) - 10} usuarios más")
                    else:
                        self.log_message("📋 No se encontraron usuarios")
                else:
                    self.log_message(f"❌ Error al listar usuarios: {response.status_code}")
                    
            except Exception as e:
                self.log_message(f"❌ Error al listar usuarios: {e}")
                
        threading.Thread(target=list_all, daemon=True).start()
        
    def clear_fields(self):
        """Limpiar campos del formulario"""
        self.employee_var.set("")
        self.name_var.set("")
        self.enabled_var.set(True)
        self.start_date_var.set(datetime.now().strftime("%Y-%m-%d"))
        end_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
        self.end_date_var.set(end_date)
        self.fingerprints_var.set(0)
        self.faces_var.set(5)

def main():
    root = tk.Tk()
    app = HikvisionUserCreator(root)
    root.mainloop()

if __name__ == "__main__":
    main()