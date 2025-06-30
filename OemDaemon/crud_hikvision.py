#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRUD Hikvision DS-K1T344MBFWX-E1 - Separado del monitoreo original
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import json
from requests.auth import HTTPDigestAuth
import urllib3
import threading
from datetime import datetime, timedelta
import os
import base64
import time

# Intentar importar PIL, si falla usar alternativa básica
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("PIL no disponible. Preview de imagen deshabilitado.")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class HikvisionCRUD:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CRUD Usuario Hikvision DS-K1T344MBFWX-E1")
        self.root.geometry("900x800")
        self.root.resizable(True, True)
        self.session = None
        self.fdid = '1'  # ID biblioteca facial por defecto
        
        # Variables de operaciones para daemon
        self.operations_file = "user_operations.json"
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Frame de conexión
        conn_frame = ttk.LabelFrame(main_frame, text="Configuración de Conexión", padding="10")
        conn_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(conn_frame, text="IP del Dispositivo:").grid(row=0, column=0, sticky=tk.W)
        self.ip_var = tk.StringVar(value="10.0.10.34")
        ttk.Entry(conn_frame, textvariable=self.ip_var, width=20).grid(row=0, column=1, sticky=tk.W, padx=(5, 20))

        ttk.Label(conn_frame, text="Usuario:").grid(row=0, column=2, sticky=tk.W)
        self.user_var = tk.StringVar(value="admin")
        ttk.Entry(conn_frame, textvariable=self.user_var, width=15).grid(row=0, column=3, sticky=tk.W, padx=(5, 20))

        ttk.Label(conn_frame, text="Contraseña:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.pass_var = tk.StringVar(value="Oem2017*")
        ttk.Entry(conn_frame, textvariable=self.pass_var, show="*", width=20).grid(row=1, column=1, sticky=tk.W, padx=(5, 20), pady=(5, 0))

        ttk.Button(conn_frame, text="Probar Conexión", command=self.test_connection).grid(row=1, column=2, columnspan=2, pady=(5, 0))

        # Frame de usuario
        user_frame = ttk.LabelFrame(main_frame, text="Datos del Usuario", padding="10")
        user_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(user_frame, text="ID Empleado:").grid(row=0, column=0, sticky=tk.W)
        self.employee_var = tk.StringVar()
        ttk.Entry(user_frame, textvariable=self.employee_var, width=20).grid(row=0, column=1, sticky=tk.W, padx=(5, 20))

        ttk.Label(user_frame, text="Nombre Completo:").grid(row=0, column=2, sticky=tk.W)
        self.name_var = tk.StringVar()
        ttk.Entry(user_frame, textvariable=self.name_var, width=30).grid(row=0, column=3, sticky=tk.W, padx=(5, 0))

        # Frame de imagen con preview
        image_frame = ttk.LabelFrame(main_frame, text="Foto de Usuario", padding="10")
        image_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # Botones de imagen
        img_btn_frame = ttk.Frame(image_frame)
        img_btn_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(img_btn_frame, text="Imagen JPG:").pack(side=tk.LEFT)
        self.image_path_var = tk.StringVar()
        ttk.Entry(img_btn_frame, textvariable=self.image_path_var, width=40, state='readonly').pack(side=tk.LEFT, padx=(5, 5))
        ttk.Button(img_btn_frame, text="Seleccionar...", command=self.select_image).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(img_btn_frame, text="Limpiar", command=self.clear_image).pack(side=tk.LEFT)

        # Preview de imagen
        self.image_label = ttk.Label(image_frame, text="No hay imagen seleccionada", 
                                   relief="sunken", anchor="center")
        self.image_label.pack(expand=True, fill="both", pady=(5, 0))
        self.current_image = None

        # Frame de configuración de acceso
        access_frame = ttk.LabelFrame(main_frame, text="Configuración de Acceso", padding="10")
        access_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

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

        # Frame de botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(0, 10))

        ttk.Button(button_frame, text="Crear Usuario", command=self.create_user).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Leer Usuario", command=self.read_user).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Modificar Usuario", command=self.update_user).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Eliminar Usuario", command=self.delete_user).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Limpiar Campos", command=self.clear_fields).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Listar Usuarios", command=self.list_users).pack(side=tk.LEFT)

        # Frame de log
        log_frame = ttk.LabelFrame(main_frame, text="Log de Actividad", padding="10")
        log_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        self.log_text = tk.Text(log_frame, height=15, width=80)
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Configurar grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)

    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()

    def save_operation(self, operation_type, user_data):
        """Guarda la operación para que el daemon la detecte"""
        operation = {
            "type": operation_type,
            "timestamp": time.time(),
            "data": user_data
        }
        
        operations = []
        if os.path.exists(self.operations_file):
            try:
                with open(self.operations_file, 'r') as f:
                    operations = json.load(f)
            except:
                operations = []
        
        operations.append(operation)
        
        with open(self.operations_file, 'w') as f:
            json.dump(operations, f, indent=2)

    def select_image(self):
        path = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Imagen JPG", "*.jpg"), ("Todas las imágenes", "*.jpg *.jpeg *.png")]
        )
        if path:
            self.image_path_var.set(path)
            self.display_image(path)
            self.log_message(f"Imagen seleccionada: {os.path.basename(path)}")

    def clear_image(self):
        self.image_path_var.set("")
        self.current_image = None
        self.image_label.config(image="", text="No hay imagen seleccionada")
        self.log_message("Imagen eliminada")

    def display_image(self, image_path):
        """Muestra preview de la imagen seleccionada"""
        if not PIL_AVAILABLE:
            self.image_label.config(text=f"Imagen: {os.path.basename(image_path)}")
            return
            
        try:
            # Cargar y redimensionar imagen
            img = Image.open(image_path)
            img.thumbnail((300, 200), Image.Resampling.LANCZOS)
            
            # Convertir a PhotoImage
            self.current_image = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.current_image, text="")
            
        except Exception as e:
            self.log_message(f"Error al mostrar imagen: {e}")
            self.image_label.config(text=f"Imagen: {os.path.basename(image_path)}")

    def get_image_base64(self):
        """Convierte imagen a base64 para el daemon"""
        if not self.image_path_var.get():
            return None
            
        try:
            with open(self.image_path_var.get(), 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            self.log_message(f"Error al codificar imagen: {e}")
            return None

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
                    messagebox.showinfo("Conexión", "Conexión exitosa al dispositivo")
                else:
                    self.log_message(f"❌ Error de conexión: {response.status_code}")
                    messagebox.showerror("Error", f"Error de conexión: {response.status_code}")
            except Exception as e:
                self.log_message(f"❌ Error de conexión: {e}")
                messagebox.showerror("Error", f"Error de conexión: {e}")
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
                    
                    # Guardar operación para daemon
                    operation_data = {
                        "employeeNo": self.employee_var.get(),
                        "name": self.name_var.get(),
                        "faceData": self.get_image_base64() if image_path else None
                    }
                    self.save_operation("create", operation_data)
                    
                    self.clear_fields()
                else:
                    self.log_message(f"❌ Error {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_message(f"❌ Excepción: {e}")
                
        threading.Thread(target=create, daemon=True).start()

    def read_user(self):
        def read():
            if not self.employee_var.get():
                messagebox.showerror("Error", "ID de empleado es obligatorio")
                return
                
            if not self.session:
                self.session = self.create_session()
                if not self.session:
                    return
                    
            self.log_message(f"🔍 Leyendo usuario ID: {self.employee_var.get()}")
            
            # Usar método POST para búsqueda
            url = f"http://{self.ip_var.get()}/ISAPI/AccessControl/UserInfo/Search?format=json"
            search_data = {
                "UserInfoSearchCond": {
                    "searchID": "1",
                    "searchResultPosition": 0,
                    "maxResults": 1,
                    "EmployeeNoList": [{"employeeNo": self.employee_var.get()}]
                }
            }
            
            try:
                response = self.session.post(url, json=search_data, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'UserInfoSearch' in data and 'UserInfo' in data['UserInfoSearch']:
                        users = data['UserInfoSearch']['UserInfo']
                        if users:
                            user_info = users[0]
                            self.name_var.set(user_info.get('name', ''))
                            
                            # Cargar configuración adicional si existe
                            valid_info = user_info.get('Valid', {})
                            self.enabled_var.set(valid_info.get('enable', True))
                            
                            begin_time = valid_info.get('beginTime', '')
                            if begin_time:
                                self.start_date_var.set(begin_time.split('T')[0])
                                
                            end_time = valid_info.get('endTime', '')
                            if end_time:
                                self.end_date_var.set(end_time.split('T')[0])
                            
                            self.fingerprints_var.set(user_info.get('maxFingerPrintNum', 0))
                            self.faces_var.set(user_info.get('maxFaceNum', 5))
                            
                            self.log_message(f"✅ Usuario leído: {user_info.get('name', '')}")
                            messagebox.showinfo("Usuario encontrado", f"Nombre: {user_info.get('name', '')}")
                        else:
                            self.log_message(f"❌ Usuario {self.employee_var.get()} no encontrado")
                            messagebox.showwarning("No encontrado", "Usuario no encontrado")
                    else:
                        self.log_message(f"❌ Usuario {self.employee_var.get()} no encontrado")
                        messagebox.showwarning("No encontrado", "Usuario no encontrado")
                else:
                    self.log_message(f"❌ Error leyendo usuario: {response.status_code}")
                    
            except Exception as e:
                self.log_message(f"❌ Error: {e}")
                messagebox.showerror("Error", f"Error leyendo usuario: {e}")
                
        threading.Thread(target=read, daemon=True).start()

    def update_user(self):
        def update():
            if not self.employee_var.get() or not self.name_var.get():
                messagebox.showerror("Error", "ID Empleado y Nombre son obligatorios")
                return
                
            if not self.session:
                self.session = self.create_session()
                if not self.session:
                    return
                    
            self.log_message(f"✏️ Modificando usuario: {self.name_var.get()} (ID: {self.employee_var.get()})")
            
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
                
                if response.status_code == 200:
                    self.log_message("✅ Usuario modificado exitosamente")
                    
                    # Actualizar imagen si cambió
                    image_path = self.image_path_var.get()
                    if image_path:
                        self.upload_face_image(self.employee_var.get(), image_path)
                    
                    # Guardar operación para daemon
                    operation_data = {
                        "employeeNo": self.employee_var.get(),
                        "name": self.name_var.get(),
                        "faceData": self.get_image_base64() if image_path else None
                    }
                    self.save_operation("update", operation_data)
                    
                    messagebox.showinfo("Éxito", "Usuario modificado exitosamente")
                else:
                    self.log_message(f"❌ Error {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_message(f"❌ Excepción: {e}")
                
        threading.Thread(target=update, daemon=True).start()

    def delete_user(self):
        def delete():
            if not self.employee_var.get():
                messagebox.showerror("Error", "ID de empleado es obligatorio")
                return
                
            if not messagebox.askyesno("Confirmar", f"¿Eliminar usuario {self.employee_var.get()}?"):
                return
                
            if not self.session:
                self.session = self.create_session()
                if not self.session:
                    return
                    
            self.log_message(f"🗑️ Eliminando usuario ID: {self.employee_var.get()}")
            
            url = f"http://{self.ip_var.get()}/ISAPI/AccessControl/UserInfo/Delete?format=json"
            data = {"UserInfoDelCond": {"EmployeeNoList": [{"employeeNo": self.employee_var.get()}]}}
            
            try:
                response = self.session.put(url, json=data, timeout=30)
                
                if response.status_code == 200:
                    self.log_message("✅ Usuario eliminado exitosamente")
                    
                    # Guardar operación para daemon
                    operation_data = {"employeeNo": self.employee_var.get()}
                    self.save_operation("delete", operation_data)
                    
                    # Limpiar campos
                    self.clear_fields()
                    messagebox.showinfo("Éxito", "Usuario eliminado exitosamente")
                else:
                    self.log_message(f"❌ Error {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_message(f"❌ Excepción: {e}")
                
        threading.Thread(target=delete, daemon=True).start()

    def list_users(self):
        def list_all():
            if not self.session:
                self.session = self.create_session()
                if not self.session:
                    return
                    
            self.log_message("📋 Listando usuarios...")
            
            url = f"http://{self.ip_var.get()}/ISAPI/AccessControl/UserInfo/Search?format=json"
            data = {"UserInfoSearchCond": {"searchID": "1", "maxResults": 100}}
            
            try:
                response = self.session.post(url, json=data, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    users = data.get('UserInfoSearch', {}).get('UserInfo', [])
                    
                    # Crear ventana de lista
                    list_window = tk.Toplevel(self.root)
                    list_window.title("Lista de Usuarios")
                    list_window.geometry("800x500")
                    
                    # Treeview para mostrar usuarios
                    tree_frame = ttk.Frame(list_window)
                    tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
                    
                    tree = ttk.Treeview(tree_frame, columns=('ID', 'Nombre', 'Estado', 'Tipo'), show='headings')
                    tree.heading('ID', text='ID Empleado')
                    tree.heading('Nombre', text='Nombre')
                    tree.heading('Estado', text='Estado')
                    tree.heading('Tipo', text='Tipo')
                    
                    # Configurar anchos de columna
                    tree.column('ID', width=100)
                    tree.column('Nombre', width=250)
                    tree.column('Estado', width=100)
                    tree.column('Tipo', width=100)
                    
                    for user in users:
                        estado = "Activo" if user.get('Valid', {}).get('enable', True) else "Inactivo"
                        tree.insert('', 'end', values=(
                            user.get('employeeNo', ''),
                            user.get('name', ''),
                            estado,
                            user.get('userType', '')
                        ))
                    
                    # Scrollbar para treeview
                    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
                    tree.configure(yscrollcommand=scrollbar.set)
                    
                    tree.pack(side="left", fill="both", expand=True)
                    scrollbar.pack(side="right", fill="y")
                    
                    # Botón para cargar usuario seleccionado
                    def load_selected():
                        selection = tree.selection()
                        if selection:
                            item = tree.item(selection[0])
                            values = item['values']
                            if values:
                                self.employee_var.set(values[0])
                                self.read_user()
                                list_window.destroy()
                    
                    btn_frame = ttk.Frame(list_window)
                    btn_frame.pack(fill="x", padx=10, pady=(0, 10))
                    
                    ttk.Button(btn_frame, text="Cargar Seleccionado", command=load_selected).pack(side="left")
                    ttk.Button(btn_frame, text="Cerrar", command=list_window.destroy).pack(side="right")
                    
                    self.log_message(f"📋 {len(users)} usuarios listados")
                else:
                    self.log_message(f"❌ Error listando usuarios: {response.status_code}")
                    
            except Exception as e:
                self.log_message(f"❌ Error: {e}")
                messagebox.showerror("Error", f"Error listando usuarios: {e}")
                
        threading.Thread(target=list_all, daemon=True).start()

    def clear_fields(self):
        """Limpia todos los campos del formulario"""
        self.employee_var.set("")
        self.name_var.set("")
        self.clear_image()
        self.enabled_var.set(True)
        self.start_date_var.set(datetime.now().strftime("%Y-%m-%d"))
        end_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
        self.end_date_var.set(end_date)
        self.fingerprints_var.set(0)
        self.faces_var.set(5)
        self.log_message("🧹 Campos limpiados")

    def run(self):
        """Ejecuta la aplicación"""
        self.root.mainloop()

if __name__ == "__main__":
    app = HikvisionCRUD()
    app.run()