#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interfaz gráfica CRUD para crear, leer, actualizar y eliminar usuarios en terminal Hikvision DS-K1T344MBFWX-E1 con carga de foto facial y monitoreo de eventos en tiempo real
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import requests
import json
from requests.auth import HTTPDigestAuth
import urllib3
import threading
from datetime import datetime, timedelta
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import socket

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class EventHandler(BaseHTTPRequestHandler):
    """Manejador de eventos HTTP para recibir notificaciones de Hikvision"""
    
    def __init__(self, app_instance, *args, **kwargs):
        self.app = app_instance
        super().__init__(*args, **kwargs)
    
    def do_POST(self):
        """Maneja eventos POST enviados por el dispositivo Hikvision"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            content_type = self.headers.get('Content-Type', '')
            
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                
                # Verificar si es multipart
                if 'multipart' in content_type.lower():
                    self.app.process_multipart_event(post_data, content_type)
                else:
                    # Intentar procesar como JSON puro
                    try:
                        event_data = json.loads(post_data.decode('utf-8'))
                        self.app.process_access_event(event_data)
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        # Si falla, tratar como multipart sin header
                        self.app.process_multipart_event(post_data, content_type)
            
            # Responder OK al dispositivo
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "OK"}')
            
        except Exception as e:
            self.app.log_event(f"❌ Error en servidor HTTP: {e}")
            self.send_response(500)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suprimir logs del servidor HTTP"""
        pass

class HikvisionUserCreator:
    def __init__(self, root):
        self.root = root
        self.root.title("Creador de Usuarios Hikvision DS-K1T344MBFWX-E1")
        self.root.geometry("1000x800")
        self.root.resizable(True, True)
        self.session = None
        self.event_server = None
        self.event_server_thread = None
        self.server_port = 8080
        self.setup_ui()
        
        # Cerrar servidor al cerrar aplicación
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

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

        user_frame = ttk.LabelFrame(main_frame, text="Datos del Usuario", padding="10")
        user_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(user_frame, text="ID Empleado:").grid(row=0, column=0, sticky=tk.W)
        self.employee_var = tk.StringVar()
        ttk.Entry(user_frame, textvariable=self.employee_var, width=20).grid(row=0, column=1, sticky=tk.W, padx=(5, 20))

        ttk.Label(user_frame, text="Nombre Completo:").grid(row=0, column=2, sticky=tk.W)
        self.name_var = tk.StringVar()
        ttk.Entry(user_frame, textvariable=self.name_var, width=30).grid(row=0, column=3, sticky=tk.W, padx=(5, 0))

        ttk.Label(user_frame, text="Imagen JPG:").grid(row=1, column=0, sticky=tk.W)
        self.image_path_var = tk.StringVar()
        ttk.Entry(user_frame, textvariable=self.image_path_var, width=40, state='readonly').grid(row=1, column=1, columnspan=2, sticky=tk.W)
        ttk.Button(user_frame, text="Seleccionar...", command=self.select_image).grid(row=1, column=3, sticky=tk.W)

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

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(0, 10))

        ttk.Button(button_frame, text="Crear Usuario", command=self.create_user).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Modificar Usuario", command=self.update_user).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Eliminar Usuario", command=self.delete_user).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Limpiar Campos", command=self.clear_fields).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Listar Usuarios", command=self.list_users).pack(side=tk.LEFT)

        # Frame para monitoreo de eventos
        event_frame = ttk.LabelFrame(main_frame, text="Monitoreo de Eventos en Tiempo Real", padding="10")
        event_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        event_control_frame = ttk.Frame(event_frame)
        event_control_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(event_control_frame, text="Puerto Servidor:").pack(side=tk.LEFT)
        self.port_var = tk.StringVar(value="8080")
        ttk.Entry(event_control_frame, textvariable=self.port_var, width=8).pack(side=tk.LEFT, padx=(5, 10))

        self.start_server_btn = ttk.Button(event_control_frame, text="Iniciar Servidor", command=self.start_event_server)
        self.start_server_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.stop_server_btn = ttk.Button(event_control_frame, text="Detener Servidor", command=self.stop_event_server, state=tk.DISABLED)
        self.stop_server_btn.pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(event_control_frame, text="Configurar Eventos", command=self.configure_event_notification).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(event_control_frame, text="Config. Manual", command=self.show_manual_config).pack(side=tk.LEFT, padx=(5, 0))

        self.server_status_label = ttk.Label(event_control_frame, text="● Servidor: Detenido", foreground="red")
        self.server_status_label.pack(side=tk.RIGHT)

        # Área de eventos
        self.event_text = scrolledtext.ScrolledText(event_frame, height=8, width=100)
        self.event_text.pack(fill=tk.BOTH, expand=True)

        log_frame = ttk.LabelFrame(main_frame, text="Log de Actividad", padding="10")
        log_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)

    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()

    def log_event(self, message):
        """Log específico para eventos de acceso"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.event_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.event_text.see(tk.END)
        self.root.update()

    def select_image(self):
        path = filedialog.askopenfilename(filetypes=[("Imagen JPG", "*.jpg"), ("Todas las imágenes", "*.jpg *.jpeg *.png")])
        if path:
            self.image_path_var.set(path)

    def create_session(self):
        try:
            session = requests.Session()
            session.auth = HTTPDigestAuth(self.user_var.get(), self.pass_var.get())
            session.headers.update({
                'User-Agent': 'Hikvision Client',
                'Accept': 'application/xml, application/json',
                'Connection': 'keep-alive'
            })
            session.verify = False
            return session
        except Exception as e:
            self.log_message(f"❌ Error creando sesión: {e}")
            return None

    def test_connection(self):
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
                    # Verificar biblioteca facial al conectar
                    self.ensure_face_library_exists()
                else:
                    self.log_message(f"❌ Error de conexión: {response.status_code}")
            except Exception as e:
                self.log_message(f"❌ Error de conexión: {e}")
        threading.Thread(target=test, daemon=True).start()

    def ensure_face_library_exists(self):
        """Verifica y crea biblioteca facial por defecto si no existe"""
        self.log_message("🔍 Verificando biblioteca facial...")
        
        # Primero verificar si existe biblioteca por defecto
        url = f"http://{self.ip_var.get()}/ISAPI/Intelligent/FDLib?format=json"
        try:
            response = self.session.get(url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                libraries = data.get('FPLibListInfo', {}).get('FPLib', [])
                
                # Buscar biblioteca blackFD
                for lib in libraries:
                    if lib.get('faceLibType') == 'blackFD':
                        self.fdid = lib.get('FDID', '1')
                        self.log_message(f"✅ Biblioteca facial encontrada: {self.fdid}")
                        return True
            
            # Si no existe, crear biblioteca por defecto
            self.log_message("📁 Creando biblioteca facial por defecto...")
            create_data = {
                "FPLibInfo": {
                    "faceLibType": "blackFD",
                    "name": "Default Face Library",
                    "customInfo": "Biblioteca creada por aplicación",
                    "libArmingType": "armingLib",
                    "libAttribute": "blackList"
                }
            }
            
            response = self.session.post(url, json=create_data, timeout=15)
            if response.status_code in [200, 201]:
                result = response.json()
                self.fdid = result.get('FPLibInfo', {}).get('FDID', '1')
                self.log_message(f"✅ Biblioteca facial creada: {self.fdid}")
                return True
            else:
                # Usar ID por defecto si falla
                self.fdid = '1'
                self.log_message("⚠️ Usando biblioteca por defecto ID=1")
                return True
                
        except Exception as e:
            self.log_message(f"⚠️ Error biblioteca facial: {e}")
            self.fdid = '1'  # Usar ID por defecto
            return True

    def upload_face_image(self, employee_id, image_path):
        """Sube imagen facial usando formato multipart manual según documentación ISAPI"""
        self.log_message(f"📸 Subiendo imagen facial para ID {employee_id}...")
        
        if not os.path.exists(image_path):
            self.log_message("❌ Ruta de imagen inválida")
            return False
            
        file_size = os.path.getsize(image_path)
        if file_size > 200 * 1024:
            self.log_message(f"⚠️ Imagen muy grande ({file_size/1024:.1f}KB). Máximo recomendado: 200KB")
        
        # Verificar biblioteca facial
        if not hasattr(self, 'fdid'):
            if not self.ensure_face_library_exists():
                return False
        
        url = f"http://{self.ip_var.get()}/ISAPI/Intelligent/FDLib/FaceDataRecord?format=json"
        
        try:
            # Preparar metadata JSON con FDID
            face_data = {
                "faceLibType": "blackFD",
                "FDID": self.fdid,
                "FPID": str(employee_id),
                "name": self.name_var.get() if self.name_var.get() else f"User_{employee_id}"
            }
            
            # Leer imagen
            with open(image_path, 'rb') as img_file:
                image_data = img_file.read()
            
            # Crear boundary personalizado
            boundary = '---------------------------7e13971310878'
            
            # Construir multipart manualmente según documentación
            body = f'--{boundary}\r\n'
            body += 'Content-Disposition: form-data; name="FaceDataRecord"\r\n'
            body += 'Content-Type: application/json\r\n'
            body += f'Content-Length: {len(json.dumps(face_data))}\r\n'
            body += '\r\n'
            body += json.dumps(face_data)
            body += f'\r\n--{boundary}\r\n'
            body += 'Content-Disposition: form-data; name="FaceImage"\r\n'
            body += 'Content-Type: image/jpeg\r\n'
            body += f'Content-Length: {len(image_data)}\r\n'
            body += '\r\n'
            
            # Convertir a bytes y agregar imagen
            body_bytes = body.encode('utf-8') + image_data + f'\r\n--{boundary}--\r\n'.encode('utf-8')
            
            headers = {
                'Content-Type': f'multipart/form-data; boundary={boundary}',
                'Content-Length': str(len(body_bytes))
            }
            
            response = self.session.post(url, data=body_bytes, headers=headers, timeout=30)
            
            if response.status_code in [200, 201]:
                self.log_message("✅ Imagen facial cargada correctamente")
                return True
            else:
                self.log_message(f"❌ Error al subir imagen: {response.status_code}")
                try:
                    error_data = response.json()
                    if 'statusString' in error_data:
                        self.log_message(f"   Detalle: {error_data['statusString']}")
                except:
                    self.log_message(f"   Respuesta: {response.text[:200]}")
                return False
                
        except Exception as e:
            self.log_message(f"❌ Error cargando imagen: {e}")
            return False

    def create_user(self):
        def create():
            if not self.employee_var.get() or not self.name_var.get():
                messagebox.showerror("Error", "ID Empleado y Nombre son obligatorios")
                return
                
            if not self.session:
                self.session = self.create_session()
                if not self.session:
                    return
                    
            self.log_message(f"👤 Creando usuario: {self.name_var.get()} (ID: {self.employee_var.get()})")
            
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
                    "RightPlan": [{"doorNo": 1, "planTemplateNo": "1"}],
                    "maxFingerPrintNum": self.fingerprints_var.get(),
                    "maxFaceNum": self.faces_var.get()
                }
            }
            
            url = f"http://{self.ip_var.get()}/ISAPI/AccessControl/UserInfo/Record?format=json"
            
            try:
                response = self.session.post(url, json=user_data, timeout=30)
                
                if response.status_code in [200, 201]:
                    self.log_message("✅ Usuario creado exitosamente")
                    
                    # Subir imagen si está seleccionada
                    image_path = self.image_path_var.get()
                    if image_path:
                        if self.upload_face_image(self.employee_var.get(), image_path):
                            messagebox.showinfo("Éxito", f"Usuario '{self.name_var.get()}' creado con imagen facial")
                        else:
                            messagebox.showwarning("Parcial", f"Usuario creado pero falló la carga de imagen")
                    else:
                        messagebox.showinfo("Éxito", f"Usuario '{self.name_var.get()}' creado correctamente")
                    
                    self.clear_fields()
                else:
                    self.log_message(f"❌ Error {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_message(f"❌ Excepción: {e}")
                
        threading.Thread(target=create, daemon=True).start()

    def update_user(self):
        def update():
            if not self.employee_var.get():
                messagebox.showerror("Error", "Debe ingresar el ID del empleado a modificar")
                return
                
            if not self.session:
                self.session = self.create_session()
                if not self.session:
                    return
                    
            self.log_message(f"✏️ Modificando usuario ID {self.employee_var.get()}...")
            
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
                    "RightPlan": [{"doorNo": 1, "planTemplateNo": "1"}],
                    "maxFingerPrintNum": self.fingerprints_var.get(),
                    "maxFaceNum": self.faces_var.get()
                }
            }
            
            url = f"http://{self.ip_var.get()}/ISAPI/AccessControl/UserInfo/Modify?format=json"
            
            try:
                response = self.session.put(url, json=user_data, timeout=30)
                
                if response.status_code in [200, 201]:
                    self.log_message("✅ Usuario modificado correctamente")
                    
                    # Actualizar imagen si está seleccionada
                    image_path = self.image_path_var.get()
                    if image_path:
                        if self.upload_face_image(self.employee_var.get(), image_path):
                            messagebox.showinfo("Éxito", "Usuario e imagen actualizados")
                        else:
                            messagebox.showwarning("Parcial", "Usuario actualizado pero falló la carga de imagen")
                    else:
                        messagebox.showinfo("Éxito", "Usuario modificado")
                else:
                    self.log_message(f"❌ Error {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_message(f"❌ Error al modificar usuario: {e}")
                
        threading.Thread(target=update, daemon=True).start()

    def delete_user(self):
        def delete():
            if not self.employee_var.get():
                messagebox.showerror("Error", "Debe ingresar el ID del empleado a eliminar")
                return
                
            if not self.session:
                self.session = self.create_session()
                if not self.session:
                    return
                    
            confirm = messagebox.askyesno("Confirmar", f"¿Está seguro que desea eliminar al usuario ID {self.employee_var.get()}?")
            if not confirm:
                return
                
            self.log_message(f"🗑️ Eliminando usuario ID {self.employee_var.get()}...")
            
            url = f"http://{self.ip_var.get()}/ISAPI/AccessControl/UserInfo/Delete?format=json"
            
            # Estructura correcta según documentación JSON_UserInfoDelCond
            data = {
                "UserInfoDelCond": {
                    "EmployeeNoList": [{
                        "employeeNo": str(self.employee_var.get())
                    }]
                }
            }
            
            try:
                response = self.session.put(url, json=data, timeout=30)
                
                if response.status_code in [200, 201]:
                    self.log_message("✅ Usuario eliminado correctamente")
                    messagebox.showinfo("Éxito", "Usuario eliminado")
                    self.clear_fields()
                else:
                    self.log_message(f"❌ Error al eliminar: {response.status_code} - {response.text}")
                    
            except Exception as e:
                self.log_message(f"❌ Error al eliminar usuario: {e}")
                
        threading.Thread(target=delete, daemon=True).start()

    def list_users(self):
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
                        for user in users[:10]:
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
        self.employee_var.set("")
        self.name_var.set("")
        self.enabled_var.set(True)
        self.start_date_var.set(datetime.now().strftime("%Y-%m-%d"))
        end_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
        self.end_date_var.set(end_date)
        self.fingerprints_var.set(0)
        self.faces_var.set(5)
        self.image_path_var.set("")

    def get_local_ip(self):
        """Obtiene la IP local de la máquina"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def start_event_server(self):
        """Inicia el servidor HTTP para recibir eventos"""
        try:
            self.server_port = int(self.port_var.get())
            
            # Crear manejador con referencia a esta instancia
            def handler(*args, **kwargs):
                EventHandler(self, *args, **kwargs)
            
            self.event_server = HTTPServer(('', self.server_port), handler)
            
            def run_server():
                self.log_message(f"🚀 Servidor de eventos iniciado en puerto {self.server_port}")
                self.event_server.serve_forever()
            
            self.event_server_thread = threading.Thread(target=run_server, daemon=True)
            self.event_server_thread.start()
            
            # Actualizar UI
            self.start_server_btn.config(state=tk.DISABLED)
            self.stop_server_btn.config(state=tk.NORMAL)
            self.server_status_label.config(text="● Servidor: Activo", foreground="green")
            
            local_ip = self.get_local_ip()
            self.log_event(f"🌐 Servidor escuchando en http://{local_ip}:{self.server_port}")
            self.log_event("📡 Configure el dispositivo para enviar eventos a esta URL")
            
        except Exception as e:
            self.log_message(f"❌ Error iniciando servidor: {e}")

    def stop_event_server(self):
        """Detiene el servidor de eventos"""
        if self.event_server:
            self.event_server.shutdown()
            self.event_server = None
            
        # Actualizar UI
        self.start_server_btn.config(state=tk.NORMAL)
        self.stop_server_btn.config(state=tk.DISABLED)
        self.server_status_label.config(text="● Servidor: Detenido", foreground="red")
        
        self.log_message("🛑 Servidor de eventos detenido")

    def configure_event_notification(self):
        """Configura el dispositivo para enviar eventos a nuestro servidor"""
        def configure():
            if not self.session:
                self.session = self.create_session()
                if not self.session:
                    return
            
            local_ip = self.get_local_ip()
            notification_url = f"http://{local_ip}:{self.server_port}/events"
            
            self.log_message("⚙️ Configurando notificación de eventos...")
            
            # Configurar notificación HTTP
            url = f"http://{self.ip_var.get()}/ISAPI/Event/notification/httpHosts"
            
            config_data = {
                "HttpHostNotificationList": {
                    "HttpHostNotification": [{
                        "id": "1",
                        "url": notification_url,
                        "protocolType": "HTTP",
                        "parameterFormatType": "JSON",
                        "addressingFormatType": "ipaddress",
                        "ipAddress": local_ip,
                        "portNo": self.server_port,
                        "userName": "",
                        "httpAuthenticationMethod": "none"
                    }]
                }
            }
            
            try:
                response = self.session.put(url, json=config_data, timeout=15)
                if response.status_code in [200, 201]:
                    self.log_message("✅ Notificación HTTP configurada")
                    
                    # Activar eventos de control de acceso
                    self.configure_access_events()
                else:
                    self.log_message(f"⚠️ Error configuración HTTP: {response.status_code}")
                    
            except Exception as e:
                self.log_message(f"❌ Error configurando eventos: {e}")
        
        threading.Thread(target=configure, daemon=True).start()

    def configure_access_events(self):
        """Configura eventos de control de acceso"""
        try:
            # Configurar eventos de control de acceso
            url = f"http://{self.ip_var.get()}/ISAPI/Event/triggers/AccessControllerEvent"
            
            event_config = {
                "AccessControllerEventTrigger": {
                    "enabled": True,
                    "eventType": "AccessControllerEvent",
                    "AccessControllerEventTriggerList": [{
                        "eventType": "AccessControllerEvent"
                    }]
                }
            }
            
            response = self.session.put(url, json=event_config, timeout=15)
            if response.status_code in [200, 201]:
                self.log_message("✅ Eventos de acceso activados")
                self.log_event("🎯 Monitoreo de eventos activo - Esperando intentos de acceso...")
            else:
                self.log_message(f"⚠️ Error activando eventos: {response.status_code}")
                
        except Exception as e:
            self.log_message(f"❌ Error configurando eventos de acceso: {e}")

    def process_access_event(self, event_data):
        """Procesa eventos de acceso recibidos del dispositivo"""
        try:
            # Log del evento crudo para debug
            self.log_event(f"🔍 Evento recibido: {json.dumps(event_data, indent=2)[:300]}...")
            
            # Extraer información del evento
            event_type = event_data.get('eventType', 'Desconocido')
            date_time = event_data.get('dateTime', datetime.now().isoformat())
            
            if 'AccessControllerEvent' in event_data:
                acc_event = event_data['AccessControllerEvent']
                
                # Información básica del evento
                card_no = acc_event.get('cardNo', 'N/A')
                employee_no = acc_event.get('employeeNoString', 'N/A')
                door_no = acc_event.get('doorNo', 'N/A')
                verify_mode = acc_event.get('currentVerifyMode', 'N/A')
                name = acc_event.get('name', 'N/A')
                
                # Determinar tipo de acceso
                major_type = acc_event.get('majorEventType', 0)
                minor_type = acc_event.get('subEventType', 0)
                
                # Interpretar códigos de evento
                access_result = self.interpret_event_codes(major_type, minor_type)
                
                # Log del evento principal
                event_msg = f"🚪 {access_result}"
                if employee_no != 'N/A':
                    event_msg += f" | Usuario: {employee_no}"
                if name != 'N/A':
                    event_msg += f" | Nombre: {name}"
                if card_no != 'N/A':
                    event_msg += f" | Tarjeta: {card_no}"
                if door_no != 'N/A':
                    event_msg += f" | Puerta: {door_no}"
                
                self.log_event(event_msg)
                
                # Información adicional
                if verify_mode != 'N/A':
                    self.log_event(f"   🔐 Método: {verify_mode}")
                self.log_event(f"   📅 Tiempo: {date_time}")
                self.log_event(f"   🔢 Códigos: Major={major_type}, Minor={minor_type}")
                
            elif 'eventType' in event_data:
                # Otros tipos de eventos
                self.log_event(f"📨 Evento: {event_type}")
                self.log_event(f"   📅 Tiempo: {date_time}")
                
                # Buscar información adicional
                for key, value in event_data.items():
                    if key not in ['eventType', 'dateTime'] and isinstance(value, (str, int, float)):
                        self.log_event(f"   {key}: {value}")
            else:
                # Evento desconocido
                self.log_event(f"❓ Evento desconocido recibido")
                self.log_event(f"   📅 Tiempo: {date_time}")
                
        except Exception as e:
            self.log_event(f"❌ Error procesando evento: {e}")
            # Log del contenido para debug
            try:
                content_preview = str(event_data)[:200] if event_data else "Vacío"
                self.log_event(f"🔍 Contenido: {content_preview}...")
            except:
                self.log_event("🔍 Contenido no mostrable")

    def process_multipart_event(self, data, content_type=""):
        """Procesa eventos con imágenes en formato multipart"""
        try:
            # Buscar boundary en content-type
            boundary = None
            if 'boundary=' in content_type:
                boundary = content_type.split('boundary=')[1].split(';')[0]
            
            # Si no hay boundary, buscar patrones comunes
            if not boundary:
                # Buscar boundary en los datos
                data_start = data[:500]  # Primeros 500 bytes
                for line in data_start.split(b'\r\n'):
                    if line.startswith(b'--') and len(line) > 10:
                        boundary = line[2:].decode('ascii', errors='ignore')
                        break
            
            if boundary:
                # Dividir por boundary
                parts = data.split(f'--{boundary}'.encode())
                
                for part in parts:
                    if b'application/json' in part:
                        # Buscar el JSON en esta parte
                        try:
                            # Separar headers del content
                            if b'\r\n\r\n' in part:
                                headers, content = part.split(b'\r\n\r\n', 1)
                                
                                # Limpiar content y buscar JSON
                                content_str = content.decode('utf-8', errors='ignore')
                                json_start = content_str.find('{')
                                json_end = content_str.rfind('}') + 1
                                
                                if json_start != -1 and json_end > json_start:
                                    json_str = content_str[json_start:json_end]
                                    event_data = json.loads(json_str)
                                    self.process_access_event(event_data)
                                    return
                        except (json.JSONDecodeError, UnicodeDecodeError) as e:
                            continue
            
            # Fallback: buscar JSON en todo el contenido
            self.extract_json_from_binary(data)
                
        except Exception as e:
            self.log_event(f"❌ Error procesando multipart: {e}")
            # Log hexadecimal para debug
            hex_sample = data[:100].hex() if len(data) >= 100 else data.hex()
            self.log_event(f"🔍 Muestra hex: {hex_sample[:50]}...")

    def extract_json_from_binary(self, data):
        """Extrae JSON de datos binarios"""
        try:
            # Buscar el inicio de JSON
            json_patterns = [b'{"', b'{\r\n', b'{\n', b'{ "']
            
            start_pos = -1
            for pattern in json_patterns:
                pos = data.find(pattern)
                if pos != -1:
                    start_pos = pos
                    break
            
            if start_pos == -1:
                self.log_event("📨 Evento recibido (sin JSON detectable)")
                return
            
            # Extraer desde el inicio del JSON
            json_data = data[start_pos:]
            
            # Buscar el final del JSON (contando llaves)
            brace_count = 0
            end_pos = -1
            in_string = False
            escape_next = False
            
            for i, byte in enumerate(json_data):
                char = chr(byte) if byte < 128 else '?'
                
                if escape_next:
                    escape_next = False
                    continue
                    
                if char == '\\':
                    escape_next = True
                    continue
                    
                if char == '"':
                    in_string = not in_string
                    continue
                    
                if not in_string:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end_pos = i + 1
                            break
            
            if end_pos > 0:
                json_bytes = json_data[:end_pos]
                json_str = json_bytes.decode('utf-8', errors='replace')
                
                try:
                    event_data = json.loads(json_str)
                    self.process_access_event(event_data)
                except json.JSONDecodeError as e:
                    self.log_event(f"❌ JSON inválido: {e}")
                    self.log_event(f"🔍 JSON extraído: {json_str[:200]}...")
            else:
                self.log_event("📨 Evento recibido (JSON incompleto)")
                
        except Exception as e:
            self.log_event(f"❌ Error extrayendo JSON: {e}")

    def interpret_event_codes(self, major, minor):
        """Interpreta códigos de evento de Hikvision"""
        # Códigos comunes de eventos de acceso
        event_codes = {
            (1, 1): "✅ ACCESO AUTORIZADO",
            (1, 2): "❌ ACCESO DENEGADO - Tarjeta inválida",
            (1, 3): "❌ ACCESO DENEGADO - Sin permisos",
            (1, 4): "❌ ACCESO DENEGADO - Fuera de horario",
            (1, 5): "❌ ACCESO DENEGADO - Anti-passback",
            (1, 6): "⏰ ACCESO DENEGADO - Expirado",
            (1, 15): "👤 RECONOCIMIENTO FACIAL EXITOSO",
            (1, 16): "❌ RECONOCIMIENTO FACIAL FALLIDO",
            (1, 17): "🔐 AUTENTICACIÓN POR CONTRASEÑA",
            (5, 1): "🚪 PUERTA ABIERTA",
            (5, 2): "🚪 PUERTA CERRADA",
            (5, 3): "⚠️ PUERTA FORZADA",
        }
        
        return event_codes.get((major, minor), f"EVENTO {major}-{minor}")

    def show_manual_config(self):
        """Muestra instrucciones de configuración manual"""
        local_ip = self.get_local_ip()
        port = self.port_var.get()
        
        instructions = f"""
📋 CONFIGURACIÓN MANUAL PARA DS-K1T344MBFWX-E1:

🌐 1. Abrir navegador: http://{self.ip_var.get()}
👤 2. Usuario: {self.user_var.get()} / Contraseña: [tu contraseña]

⚙️ 3. BUSCAR EN ESTAS RUTAS (varía según firmware):

📍 OPCIÓN A - Network:
   Network → Advanced → Event Server
   O Network → Event Server
   O Network → Notification → HTTP

📍 OPCIÓN B - Event:
   Event → Event Server
   O Event → Notification
   O Event → HTTP Notification

📍 OPCIÓN C - System:
   System → Event → HTTP Notification
   O System → Network → Event Server

📍 OPCIÓN D - Access Control:
   Access Control → Event
   O Access Control → Linkage → Event

📡 4. CONFIGURAR CUANDO ENCUENTRES:
   • Enable/Habilitado: ✅ ON
   • Server Address/IP: {local_ip}
   • Port/Puerto: {port}
   • URL Path: /events (o dejar vacío)
   • Method/Método: POST
   • Authentication: None/Ninguna

✅ 5. TIPOS DE EVENTOS A ACTIVAR:
   • Door Events / Eventos de Puerta
   • Card Events / Eventos de Tarjeta  
   • Face Recognition / Reconocimiento Facial
   • Access Control / Control de Acceso
   • All Events / Todos los Eventos

💾 6. APLICAR/SAVE configuración

🔧 Si no encuentras la interfaz, usa:
   • "Test Endpoints" abajo para verificar APIs
   • Revisa Manual → Help en la interfaz web
        """
        
        # Ventana con instrucciones
        config_window = tk.Toplevel(self.root)
        config_window.title("Configuración Manual - DS-K1T344MBFWX-E1")
        config_window.geometry("700x600")
        
        text_widget = scrolledtext.ScrolledText(config_window, wrap=tk.WORD, font=("Courier", 9))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, instructions)
        text_widget.config(state=tk.DISABLED)
        
        # Botones
        btn_frame = ttk.Frame(config_window)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Copiar IP", 
                  command=lambda: self.copy_to_clipboard(local_ip)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Abrir Web", 
                  command=lambda: self.open_device_web()).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Test Endpoints", 
                  command=self.test_event_endpoints).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Cerrar", 
                  command=config_window.destroy).pack(side=tk.RIGHT)

    def test_event_endpoints(self):
        """Prueba diferentes endpoints para encontrar el correcto"""
        def test():
            if not self.session:
                self.session = self.create_session()
                if not self.session:
                    return
                    
            self.log_message("🔍 Probando endpoints de eventos...")
            
            # Lista de endpoints comunes para configuración de eventos
            endpoints = [
                "/ISAPI/Event/notification/httpHosts",
                "/ISAPI/Event/triggers/AccessControllerEvent", 
                "/ISAPI/System/Event/notification",
                "/ISAPI/AccessControl/Event/notification",
                "/ISAPI/Event/notification/httpHosts/capabilities",
                "/ISAPI/Event/notification",
                "/ISAPI/System/notification/httpHosts",
                "/ISAPI/ContentMgmt/Event/notification"
            ]
            
            working_endpoints = []
            
            for endpoint in endpoints:
                try:
                    url = f"http://{self.ip_var.get()}{endpoint}"
                    response = self.session.get(url, timeout=5)
                    
                    if response.status_code == 200:
                        self.log_message(f"✅ FUNCIONA: {endpoint}")
                        working_endpoints.append(endpoint)
                    elif response.status_code == 404:
                        self.log_message(f"❌ No existe: {endpoint}")
                    else:
                        self.log_message(f"⚠️  Código {response.status_code}: {endpoint}")
                        
                except Exception as e:
                    self.log_message(f"❌ Error en {endpoint}: {e}")
            
            if working_endpoints:
                self.log_message(f"🎯 Endpoints disponibles: {len(working_endpoints)}")
                self.log_message("💡 Usa 'Configurar Eventos' para configuración automática")
            else:
                self.log_message("❌ No se encontraron endpoints de eventos")
                self.log_message("💡 Configura manualmente en la interfaz web")
        
        threading.Thread(target=test, daemon=True).start()

    def copy_to_clipboard(self, text):
        """Copia texto al portapapeles"""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.log_message(f"📋 Copiado: {text}")

    def open_device_web(self):
        """Abre la interfaz web del dispositivo"""
        import webbrowser
        url = f"http://{self.ip_var.get()}"
        try:
            webbrowser.open(url)
            self.log_message(f"🌐 Abriendo: {url}")
        except Exception as e:
            self.log_message(f"❌ Error abriendo navegador: {e}")

    def on_closing(self):
        """Maneja el cierre de la aplicación"""
        if self.event_server:
            self.stop_event_server()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = HikvisionUserCreator(root)
    root.mainloop()
