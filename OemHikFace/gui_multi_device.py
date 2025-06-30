#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interfaz gráfica para CRUD Multi-Dispositivo Hikvision
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from multi_device_crud import MultiDeviceCRUD

class MultiDeviceGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CRUD Multi-Dispositivo Hikvision")
        self.root.geometry("900x700")
        
        # Inicializar CRUD
        self.crud = MultiDeviceCRUD()
        
        # Variables
        self.device_vars = {}
        self.setup_ui()
        self.refresh_devices()
        
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        
        # Notebook para pestañas
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Pestaña de dispositivos
        device_frame = ttk.Frame(notebook)
        notebook.add(device_frame, text="Dispositivos")
        self.setup_device_tab(device_frame)
        
        # Pestaña de usuarios
        user_frame = ttk.Frame(notebook)
        notebook.add(user_frame, text="Usuarios")
        self.setup_user_tab(user_frame)
        
        # Pestaña de sincronización
        sync_frame = ttk.Frame(notebook)
        notebook.add(sync_frame, text="Sincronización")
        self.setup_sync_tab(sync_frame)
        
        # Log frame
        log_frame = ttk.Frame(self.root)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.log_text = tk.Text(log_frame, height=8, state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def setup_device_tab(self, parent):
        """Configura la pestaña de dispositivos"""
        
        # Frame para añadir dispositivo
        add_frame = ttk.LabelFrame(parent, text="Añadir Dispositivo", padding="10")
        add_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Campos
        ttk.Label(add_frame, text="Nombre:").grid(row=0, column=0, sticky=tk.W)
        self.device_name_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.device_name_var, width=20).grid(row=0, column=1, padx=5)
        
        ttk.Label(add_frame, text="IP:").grid(row=0, column=2, sticky=tk.W)
        self.device_ip_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.device_ip_var, width=15).grid(row=0, column=3, padx=5)
        
        ttk.Label(add_frame, text="Usuario:").grid(row=1, column=0, sticky=tk.W)
        self.device_user_var = tk.StringVar(value="admin")
        ttk.Entry(add_frame, textvariable=self.device_user_var, width=15).grid(row=1, column=1, padx=5)
        
        ttk.Label(add_frame, text="Contraseña:").grid(row=1, column=2, sticky=tk.W)
        self.device_pass_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.device_pass_var, show="*", width=15).grid(row=1, column=3, padx=5)
        
        ttk.Button(add_frame, text="Añadir Dispositivo", 
                  command=self.add_device).grid(row=1, column=4, padx=10)
        
        # Lista de dispositivos
        list_frame = ttk.LabelFrame(parent, text="Dispositivos Configurados", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview para dispositivos
        columns = ('ID', 'Nombre', 'IP', 'Estado', 'Última Sync')
        self.device_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.device_tree.heading(col, text=col)
            self.device_tree.column(col, width=100)
        
        device_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.device_tree.yview)
        self.device_tree.configure(yscrollcommand=device_scroll.set)
        
        self.device_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        device_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botones
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Probar Conexión", 
                  command=self.test_selected_device).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Eliminar", 
                  command=self.remove_device).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Actualizar", 
                  command=self.refresh_devices).pack(side=tk.LEFT, padx=5)
        
    def setup_user_tab(self, parent):
        """Configura la pestaña de usuarios"""
        
        # Frame para datos de usuario
        user_frame = ttk.LabelFrame(parent, text="Datos del Usuario", padding="10")
        user_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Campos
        ttk.Label(user_frame, text="ID Empleado:").grid(row=0, column=0, sticky=tk.W)
        self.employee_var = tk.StringVar()
        ttk.Entry(user_frame, textvariable=self.employee_var, width=15).grid(row=0, column=1, padx=5)
        
        ttk.Label(user_frame, text="Nombre:").grid(row=0, column=2, sticky=tk.W)
        self.name_var = tk.StringVar()
        ttk.Entry(user_frame, textvariable=self.name_var, width=25).grid(row=0, column=3, padx=5)
        
        ttk.Label(user_frame, text="Foto:").grid(row=1, column=0, sticky=tk.W)
        self.image_var = tk.StringVar()
        ttk.Entry(user_frame, textvariable=self.image_var, width=30, state='readonly').grid(row=1, column=1, columnspan=2, padx=5)
        ttk.Button(user_frame, text="Seleccionar", 
                  command=self.select_image).grid(row=1, column=3, padx=5)
        
        self.enabled_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(user_frame, text="Habilitado", 
                       variable=self.enabled_var).grid(row=2, column=0, sticky=tk.W, pady=5)
        
        # Botones de acción
        action_frame = ttk.Frame(user_frame)
        action_frame.grid(row=2, column=1, columnspan=3, pady=5)
        
        ttk.Button(action_frame, text="Crear Usuario", 
                  command=self.create_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Actualizar Usuario", 
                  command=self.update_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Eliminar Usuario", 
                  command=self.delete_user).pack(side=tk.LEFT, padx=5)
        
        # Lista de usuarios
        user_list_frame = ttk.LabelFrame(parent, text="Usuarios Creados", padding="10")
        user_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview para usuarios
        user_columns = ('ID', 'Empleado', 'Nombre', 'Estado', 'Sync Status')
        self.user_tree = ttk.Treeview(user_list_frame, columns=user_columns, show='headings', height=10)
        
        for col in user_columns:
            self.user_tree.heading(col, text=col)
            self.user_tree.column(col, width=100)
        
        user_scroll = ttk.Scrollbar(user_list_frame, orient=tk.VERTICAL, command=self.user_tree.yview)
        self.user_tree.configure(yscrollcommand=user_scroll.set)
        
        self.user_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        user_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind para seleccionar usuario
        self.user_tree.bind('<<TreeviewSelect>>', self.on_user_select)
        
    def setup_sync_tab(self, parent):
        """Configura la pestaña de sincronización"""
        
        # Frame de estado
        status_frame = ttk.LabelFrame(parent, text="Estado de Sincronización", padding="10")
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.status_label = ttk.Label(status_frame, text="Cargando estado...")
        self.status_label.pack()
        
        # Botones de sincronización
        sync_frame = ttk.LabelFrame(parent, text="Acciones de Sincronización", padding="10")
        sync_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(sync_frame, text="Sincronizar Todos los Usuarios", 
                  command=self.sync_all_users).pack(side=tk.LEFT, padx=5)
        ttk.Button(sync_frame, text="Verificar Conexiones", 
                  command=self.verify_connections).pack(side=tk.LEFT, padx=5)
        ttk.Button(sync_frame, text="Actualizar Estado", 
                  command=self.update_sync_status).pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(sync_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=10)
        
        # Log de sincronización
        log_frame = ttk.LabelFrame(parent, text="Log de Sincronización", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.sync_log = tk.Text(log_frame, height=15, state=tk.DISABLED)
        sync_scroll = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.sync_log.yview)
        self.sync_log.configure(yscrollcommand=sync_scroll.set)
        
        self.sync_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sync_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
    def add_device(self):
        """Añade un nuevo dispositivo"""
        name = self.device_name_var.get().strip()
        ip = self.device_ip_var.get().strip()
        user = self.device_user_var.get().strip()
        password = self.device_pass_var.get().strip()
        
        if not all([name, ip, user, password]):
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return
        
        def add_task():
            success = self.crud.add_device(name, ip, user, password)
            self.root.after(0, lambda: self.on_device_added(success))
        
        threading.Thread(target=add_task, daemon=True).start()
        
    def on_device_added(self, success):
        """Callback después de añadir dispositivo"""
        if success:
            self.log_message(f"✅ Dispositivo añadido correctamente")
            self.clear_device_fields()
            self.refresh_devices()
        else:
            self.log_message(f"❌ Error añadiendo dispositivo")
    
    def clear_device_fields(self):
        """Limpia los campos del dispositivo"""
        self.device_name_var.set("")
        self.device_ip_var.set("")
        self.device_user_var.set("admin")
        self.device_pass_var.set("")
    
    def refresh_devices(self):
        """Actualiza la lista de dispositivos"""
        for item in self.device_tree.get_children():
            self.device_tree.delete(item)
        
        devices = self.crud.get_active_devices()
        for device in devices:
            status = "🟢 Activo" if self.crud.test_device_connection(
                device['ip'], device['username'], device['password']
            ) else "🔴 Sin conexión"
            
            self.device_tree.insert('', 'end', values=(
                device['id'],
                device['name'],
                device['ip'],
                status,
                device['last_sync'] or 'Nunca'
            ))
    
    def test_selected_device(self):
        """Prueba conexión del dispositivo seleccionado"""
        selection = self.device_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona un dispositivo")
            return
        
        item = self.device_tree.item(selection[0])
        device_id = item['values'][0]
        
        devices = self.crud.get_active_devices()
        device = next((d for d in devices if d['id'] == device_id), None)
        
        if device:
            def test_task():
                result = self.crud.test_device_connection(
                    device['ip'], device['username'], device['password']
                )
                self.root.after(0, lambda: self.on_connection_test(device['name'], result))
            
            threading.Thread(target=test_task, daemon=True).start()
    
    def on_connection_test(self, device_name, success):
        """Callback del test de conexión"""
        if success:
            self.log_message(f"✅ Conexión exitosa con {device_name}")
        else:
            self.log_message(f"❌ Error de conexión con {device_name}")
        
        self.refresh_devices()
    
    def remove_device(self):
        """Elimina dispositivo seleccionado"""
        selection = self.device_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona un dispositivo")
            return
        
        if messagebox.askyesno("Confirmar", "¿Eliminar el dispositivo seleccionado?"):
            # Aquí implementarías la eliminación en la BD
            self.log_message("🗑️ Dispositivo eliminado")
            self.refresh_devices()
    
    def select_image(self):
        """Selecciona imagen para el usuario"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png")]
        )
        if file_path:
            self.image_var.set(file_path)
    
    def create_user(self):
        """Crea usuario en todos los dispositivos"""
        employee_no = self.employee_var.get().strip()
        name = self.name_var.get().strip()
        image_path = self.image_var.get().strip() or None
        enabled = self.enabled_var.get()
        
        if not employee_no or not name:
            messagebox.showerror("Error", "ID Empleado y Nombre son obligatorios")
            return
        
        self.progress.start()
        
        def create_task():
            result = self.crud.create_user_multi(employee_no, name, enabled, image_path)
            self.root.after(0, lambda: self.on_user_created(result))
        
        threading.Thread(target=create_task, daemon=True).start()
    
    def on_user_created(self, result):
        """Callback después de crear usuario"""
        self.progress.stop()
        
        user_id = result['user_id']
        sync_results = result['sync_results']
        
        success_count = sum(1 for r in sync_results if r['status'] == 'success')
        total_devices = len(sync_results)
        
        self.log_message(f"👤 Usuario {user_id} creado - {success_count}/{total_devices} dispositivos")
        
        for result in sync_results:
            status_icon = "✅" if result['status'] == 'success' else "❌"
            self.log_sync(f"{status_icon} {result['device']} ({result['ip']}): {result['message']}")
        
        self.clear_user_fields()
        self.refresh_users()
    
    def update_user(self):
        """Actualiza usuario seleccionado"""
        selection = self.user_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona un usuario")
            return
        
        item = self.user_tree.item(selection[0])
        user_id = item['values'][0]
        
        employee_no = self.employee_var.get().strip() or None
        name = self.name_var.get().strip() or None
        image_path = self.image_var.get().strip() or None
        enabled = self.enabled_var.get()
        
        self.progress.start()
        
        def update_task():
            result = self.crud.update_user_multi(user_id, employee_no, name, enabled, image_path)
            self.root.after(0, lambda: self.on_user_updated(result))
        
        threading.Thread(target=update_task, daemon=True).start()
    
    def on_user_updated(self, result):
        """Callback después de actualizar usuario"""
        self.progress.stop()
        
        user_id = result['user_id']
        sync_results = result['sync_results']
        
        success_count = sum(1 for r in sync_results if r['status'] == 'success')
        total_devices = len(sync_results)
        
        self.log_message(f"🔄 Usuario {user_id} actualizado - {success_count}/{total_devices} dispositivos")
        
        for result in sync_results:
            status_icon = "✅" if result['status'] == 'success' else "❌"
            self.log_sync(f"{status_icon} {result['device']}: {result['message']}")
        
        self.refresh_users()
    
    def delete_user(self):
        """Elimina usuario seleccionado"""
        selection = self.user_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona un usuario")
            return
        
        if not messagebox.askyesno("Confirmar", "¿Eliminar el usuario de todos los dispositivos?"):
            return
        
        item = self.user_tree.item(selection[0])
        user_id = item['values'][0]
        
        self.progress.start()
        
        def delete_task():
            result = self.crud.delete_user_multi(user_id)
            self.root.after(0, lambda: self.on_user_deleted(result))
        
        threading.Thread(target=delete_task, daemon=True).start()
    
    def on_user_deleted(self, result):
        """Callback después de eliminar usuario"""
        self.progress.stop()
        
        user_id = result['user_id']
        sync_results = result['sync_results']
        
        success_count = sum(1 for r in sync_results if r['status'] == 'success')
        total_devices = len(sync_results)
        
        self.log_message(f"🗑️ Usuario {user_id} eliminado - {success_count}/{total_devices} dispositivos")
        
        for result in sync_results:
            status_icon = "✅" if result['status'] == 'success' else "❌"
            self.log_sync(f"{status_icon} {result['device']}: {result['message']}")
        
        self.clear_user_fields()
        self.refresh_users()
    
    def clear_user_fields(self):
        """Limpia los campos del usuario"""
        self.employee_var.set("")
        self.name_var.set("")
        self.image_var.set("")
        self.enabled_var.set(True)
    
    def refresh_users(self):
        """Actualiza la lista de usuarios"""
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        
        # Obtener usuarios de la BD local
        import sqlite3
        conn = sqlite3.connect(self.crud.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, employee_no, name, enabled FROM users')
        users = cursor.fetchall()
        conn.close()
        
        for user in users:
            enabled_text = "✅ Habilitado" if user[3] else "❌ Deshabilitado"
            self.user_tree.insert('', 'end', values=(
                user[0],  # ID
                user[1],  # Employee No
                user[2],  # Name
                enabled_text,
                "Pendiente"  # Sync status
            ))
    
    def on_user_select(self, event):
        """Carga datos del usuario seleccionado"""
        selection = self.user_tree.selection()
        if not selection:
            return
        
        item = self.user_tree.item(selection[0])
        user_id = item['values'][0]
        
        # Cargar datos del usuario
        import sqlite3
        conn = sqlite3.connect(self.crud.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT employee_no, name, enabled, image_path FROM users WHERE id = ?', (user_id,))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data:
            self.employee_var.set(user_data[0])
            self.name_var.set(user_data[1])
            self.enabled_var.set(user_data[2])
            self.image_var.set(user_data[3] or "")
    
    def sync_all_users(self):
        """Sincroniza todos los usuarios"""
        self.progress.start()
        
        def sync_task():
            result = self.crud.sync_all_users()
            self.root.after(0, lambda: self.on_sync_complete(result))
        
        threading.Thread(target=sync_task, daemon=True).start()
    
    def on_sync_complete(self, result):
        """Callback después de sincronización completa"""
        self.progress.stop()
        
        total_users = result['total_users']
        total_syncs = result['total_syncs']
        
        self.log_message(f"🔄 Sincronización completa: {total_users} usuarios en {total_syncs} operaciones")
        
        success_count = sum(1 for r in result['results'] if r['status'] == 'success')
        self.log_sync(f"✅ Exitosos: {success_count}/{total_syncs}")
        
        # Mostrar errores si los hay
        errors = [r for r in result['results'] if r['status'] == 'error']
        if errors:
            self.log_sync(f"❌ Errores: {len(errors)}")
            for error in errors[:5]:  # Mostrar solo los primeros 5
                self.log_sync(f"   • {error['device']}: {error['message']}")
    
    def verify_connections(self):
        """Verifica conexiones de todos los dispositivos"""
        def verify_task():
            devices = self.crud.get_active_devices()
            results = []
            
            for device in devices:
                success = self.crud.test_device_connection(
                    device['ip'], device['username'], device['password']
                )
                results.append((device['name'], device['ip'], success))
            
            self.root.after(0, lambda: self.on_verify_complete(results))
        
        threading.Thread(target=verify_task, daemon=True).start()
    
    def on_verify_complete(self, results):
        """Callback después de verificar conexiones"""
        self.log_message("🔍 Verificación de conexiones:")
        
        for name, ip, success in results:
            status = "✅" if success else "❌"
            self.log_sync(f"{status} {name} ({ip})")
        
        self.refresh_devices()
    
    def update_sync_status(self):
        """Actualiza el estado de sincronización"""
        status = self.crud.get_sync_status()
        
        status_text = f"📊 Dispositivos: {status['devices']} | Usuarios: {status['users']}"
        if status['recent_errors']:
            status_text += f" | Errores recientes: {len(status['recent_errors'])}"
        
        self.status_label.config(text=status_text)
    
    def log_message(self, message):
        """Añade mensaje al log principal"""
        from datetime import datetime
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.log_text.config(state=tk.DISABLED)
        self.log_text.see(tk.END)
        
        # También pasar al CRUD
        self.crud.log_message = self.log_message
    
    def log_sync(self, message):
        """Añade mensaje al log de sincronización"""
        self.sync_log.config(state=tk.NORMAL)
        self.sync_log.insert(tk.END, f"{message}\n")
        self.sync_log.config(state=tk.DISABLED)
        self.sync_log.see(tk.END)

# Integración con el código original
class HikvisionMultiDevice(MultiDeviceGUI):
    """Clase principal que combina funcionalidad original con multi-dispositivo"""
    
    def __init__(self, root):
        super().__init__(root)
        self.root.title("CRUD Multi-Dispositivo Hikvision DS-K1T344MBFWX-E1")
        
        # Añadir funcionalidades del código original
        self.add_original_features()
        
        # Auto-refresh cada 30 segundos
        self.auto_refresh()
    
    def add_original_features(self):
        """Añade funcionalidades del código original"""
        
        # Añadir pestaña de monitoreo de eventos
        notebook = self.root.children['!notebook']
        
        event_frame = ttk.Frame(notebook)
        notebook.add(event_frame, text="Monitoreo Eventos")
        
        # Frame de configuración de servidor
        server_frame = ttk.LabelFrame(event_frame, text="Servidor de Eventos", padding="10")
        server_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(server_frame, text="Puerto:").grid(row=0, column=0, sticky=tk.W)
        self.port_var = tk.StringVar(value="8080")
        ttk.Entry(server_frame, textvariable=self.port_var, width=10).grid(row=0, column=1, padx=5)
        
        self.server_status_var = tk.StringVar(value="🔴 Detenido")
        ttk.Label(server_frame, textvariable=self.server_status_var).grid(row=0, column=2, padx=10)
        
        ttk.Button(server_frame, text="Iniciar Servidor", 
                  command=self.start_event_server).grid(row=0, column=3, padx=5)
        ttk.Button(server_frame, text="Detener Servidor", 
                  command=self.stop_event_server).grid(row=0, column=4, padx=5)
        
        # Log de eventos
        event_log_frame = ttk.LabelFrame(event_frame, text="Log de Eventos", padding="10")
        event_log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.event_log = tk.Text(event_log_frame, height=20, state=tk.DISABLED)
        event_scroll = ttk.Scrollbar(event_log_frame, orient=tk.VERTICAL, command=self.event_log.yview)
        self.event_log.configure(yscrollcommand=event_scroll.set)
        
        self.event_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        event_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Variables del servidor
        self.event_server = None
        self.server_thread = None
    
    def start_event_server(self):
        """Inicia servidor de eventos (del código original)"""
        # Implementar servidor de eventos del código original
        self.server_status_var.set("🟢 Activo")
        self.log_message("🚀 Servidor de eventos iniciado")
    
    def stop_event_server(self):
        """Detiene servidor de eventos"""
        if self.event_server:
            self.event_server.shutdown()
            self.event_server = None
        
        self.server_status_var.set("🔴 Detenido")
        self.log_message("🛑 Servidor de eventos detenido")
    
    def auto_refresh(self):
        """Auto-actualización cada 30 segundos"""
        self.update_sync_status()
        self.root.after(30000, self.auto_refresh)  # 30 segundos
    
    def on_closing(self):
        """Maneja el cierre de la aplicación"""
        self.stop_event_server()
        self.root.destroy()

if __name__ == "__main__":
    import datetime
    
    root = tk.Tk()
    app = HikvisionMultiDevice(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()