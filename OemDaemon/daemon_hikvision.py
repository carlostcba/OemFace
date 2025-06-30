import os
import sys
import json
import time
import threading
import requests
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import pystray
from PIL import Image, ImageDraw
import queue

class EventHandler(BaseHTTPRequestHandler):
    def __init__(self, daemon_instance, *args, **kwargs):
        self.daemon = daemon_instance
        super().__init__(*args, **kwargs)
        
    def do_POST(self):
        """Maneja eventos POST del dispositivo Hikvision - adaptado del original"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            content_type = self.headers.get('Content-Type', '')
            
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                
                # Verificar si es multipart como en original
                if 'multipart' in content_type.lower():
                    self.process_multipart_event(post_data, content_type)
                else:
                    # Intentar procesar como JSON puro
                    try:
                        event_data = json.loads(post_data.decode('utf-8'))
                        self.process_json_event(event_data)
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        # Si falla, tratar como multipart sin header
                        self.process_multipart_event(post_data, content_type)
            
            # Responder OK al dispositivo como en original
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "OK"}')
            
        except Exception as e:
            self.daemon.log_event(f"❌ Error en servidor HTTP: {e}")
            self.send_response(500)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suprimir logs del servidor HTTP como en original"""
        pass
        
    def process_json_event(self, event_data):
        """Procesa evento en formato JSON - adaptado del original"""
        try:
            # Verificar si es evento directo o dentro de Events
            if 'AccessControllerEvent' in event_data:
                # Evento directo
                self.process_access_event(event_data)
            elif 'Events' in event_data:
                # Evento dentro de estructura Events
                self.process_access_event(event_data)
            else:
                # Buscar cualquier estructura de evento
                events = event_data.get('Events', {}).get('Event', [])
                if not isinstance(events, list):
                    events = [events] if events else []
                    
                for event in events:
                    if 'AccessControllerEvent' in event:
                        # Procesar evento individual
                        temp_data = {'Events': {'Event': event}, 'dateTime': event_data.get('dateTime', '')}
                        self.process_access_event(temp_data)
                        
        except Exception as e:
            self.daemon.log_event(f"❌ Error procesando evento JSON: {e}")

    def process_access_event(self, event_data):
        """Procesa eventos de acceso - EXACTO del código original"""
        try:
            # Verificar si es evento directo
            if 'AccessControllerEvent' in event_data:
                acc_event = event_data['AccessControllerEvent']
                major_type = acc_event.get('majorEventType', 0)
                minor_type = acc_event.get('subEventType', 0)

                # Filtrar solo eventos 5-75 y 5-76 como en original
                if major_type != 5 or minor_type not in [75, 76]:
                    return

                date_time = event_data.get('dateTime', datetime.now().isoformat())
                employee_no = acc_event.get('employeeNoString', '')
                name = acc_event.get('name', '')
                verify_mode = acc_event.get('currentVerifyMode', 'N/A')

                # Log del evento EXACTO como en original
                if minor_type == 75:
                    main_line = f"🚪 EVENTO 5-75"
                    if employee_no:
                        main_line += f" | Usuario: {employee_no}"
                    if name:
                        main_line += f" | Nombre: {name}"
                    event_type = "access_granted"
                else:
                    main_line = "🚪 EVENTO 5-76"
                    event_type = "access_denied"

                self.daemon.log_event(main_line)
                self.daemon.log_event(f"   🔐 Método: {verify_mode}")
                self.daemon.log_event(f"   📅 Tiempo: {date_time}")
                self.daemon.log_event(f"   🔢 Códigos: Major=5, Minor={minor_type}")

                # Crear comando F en formato OemProxy
                if minor_type == 75:
                    # F3: Evento acceso concedido (5-75)
                    command_data = self.daemon.create_f_command_oemproxy("3", {
                        "employeeNo": employee_no,
                        "name": name,
                        "verifyMode": verify_mode,
                        "dateTime": date_time,
                        "eventType": "ACCESS_OK"
                    })
                else:
                    # F4: Evento acceso denegado (5-76)
                    command_data = self.daemon.create_f_command_oemproxy("4", {
                        "employeeNo": employee_no,
                        "name": name,
                        "verifyMode": verify_mode,
                        "dateTime": date_time,
                        "eventType": "ACCESS_DENIED"
                    })
                
                # Enviar comando
                if self.daemon.send_oemproxy_command(command_data):
                    self.daemon.log_event(f"📡 Comando F{3 if minor_type == 75 else 4} enviado - Usuario: {employee_no}")
                else:
                    self.daemon.log_event(f"❌ Error enviando comando F{3 if minor_type == 75 else 4}")
                    
                return

            # Verificar estructura de eventos como en original
            events = event_data.get('Events', {}).get('Event', [])
            if not isinstance(events, list):
                events = [events]
                
            for event in events:
                acc_event = event.get('AccessControllerEvent', {})
                major_type = acc_event.get('majorEventType', 0)
                minor_type = acc_event.get('subEventType', 0)

                # Filtrar solo eventos 5-75 y 5-76 como en original
                if major_type != 5 or minor_type not in [75, 76]:
                    continue

                date_time = event_data.get('dateTime', datetime.now().isoformat())
                employee_no = acc_event.get('employeeNoString', '')
                name = acc_event.get('name', '')
                verify_mode = acc_event.get('currentVerifyMode', 'N/A')

                # Log del evento como en original
                if minor_type == 75:
                    main_line = f"🚪 EVENTO 5-75"
                    if employee_no:
                        main_line += f" | Usuario: {employee_no}"
                    if name:
                        main_line += f" | Nombre: {name}"
                    event_type = "access_granted"
                else:
                    main_line = "🚪 EVENTO 5-76"
                    event_type = "access_denied"

                self.daemon.log_event(main_line)
                self.daemon.log_event(f"   🔐 Método: {verify_mode}")
                self.daemon.log_event(f"   📅 Tiempo: {date_time}")
                self.daemon.log_event(f"   🔢 Códigos: Major=5, Minor={minor_type}")

                # Crear comando F en formato OemProxy
                if minor_type == 75:
                    # F3: Evento acceso concedido (5-75)
                    command_data = self.daemon.create_f_command_oemproxy("3", {
                        "employeeNo": employee_no,
                        "name": name,
                        "verifyMode": verify_mode,
                        "dateTime": date_time,
                        "eventType": "ACCESS_OK"
                    })
                else:
                    # F4: Evento acceso denegado (5-76)
                    command_data = self.daemon.create_f_command_oemproxy("4", {
                        "employeeNo": employee_no,
                        "name": name,
                        "verifyMode": verify_mode,
                        "dateTime": date_time,
                        "eventType": "ACCESS_DENIED"
                    })
                
                # Enviar comando
                if self.daemon.send_oemproxy_command(command_data):
                    self.daemon.log_event(f"📡 Comando F{3 if minor_type == 75 else 4} enviado - Usuario: {employee_no}")
                else:
                    self.daemon.log_event(f"❌ Error enviando comando F{3 if minor_type == 75 else 4}")
                    
        except Exception as e:
            self.daemon.log_event(f"❌ Error procesando evento de acceso: {e}")

    def process_multipart_event(self, data, content_type):
        """Procesa eventos multipart - EXACTO del código original"""
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
                                    self.process_json_event(event_data)
                                    return
                        except (json.JSONDecodeError, UnicodeDecodeError) as e:
                            continue
            
            # Fallback: buscar JSON en todo el contenido
            self.extract_json_from_binary(data)
                
        except Exception as e:
            self.daemon.log_event(f"❌ Error procesando multipart: {e}")
            # Log hexadecimal para debug
            if len(data) > 0:
                hex_sample = data[:100].hex() if len(data) >= 100 else data.hex()
                self.daemon.log_event(f"🔍 Muestra hex: {hex_sample[:50]}...")

    def extract_json_from_binary(self, data):
        """Extrae JSON de datos binarios - EXACTO del código original"""
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
                self.daemon.log_event("📨 Evento recibido (sin JSON detectable)")
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
                    self.process_json_event(event_data)
                except json.JSONDecodeError as e:
                    self.daemon.log_event(f"❌ JSON inválido: {e}")
                    self.daemon.log_event(f"🔍 JSON extraído: {json_str[:200]}...")
            else:
                self.daemon.log_event("📨 Evento recibido (JSON incompleto)")
                
        except Exception as e:
            self.daemon.log_event(f"❌ Error extrayendo JSON: {e}")

def create_event_handler(daemon_instance):
    """Factory function para crear handler con referencia al daemon"""
    def handler(*args, **kwargs):
        return EventHandler(daemon_instance, *args, **kwargs)
    return handler

class HikvisionDaemon:
    def __init__(self):
        self.running = True
        self.operations_file = "user_operations.json"
        self.processed_operations = set()
        self.event_queue = queue.Queue()
        
        # Configuración
        self.server_port = 8080
        self.post_url = "http://192.168.0.100:8081/api/events"  # URL destino
        self.device_id = "01"
        
        # Configuración para formato OemProxy
        self.STX = '\x02'
        self.ETX = '\x03'
        self.ACK = '\x06'
        self.NAK = '\x15'
        self.SIB = '\x0F'
        
        # Cargar operaciones ya procesadas
        self.load_processed_operations()
        
        # Iniciar servidor HTTP para eventos
        self.start_event_server()
        
        # Iniciar monitoreo de operaciones CRUD
        self.start_operation_monitor()
        
        # Crear icono de bandeja
        self.create_tray_icon()
        
    def load_processed_operations(self):
        """Carga el archivo de operaciones procesadas"""
        processed_file = "processed_operations.json"
        if os.path.exists(processed_file):
            try:
                with open(processed_file, 'r') as f:
                    data = json.load(f)
                    self.processed_operations = set(data.get('processed', []))
            except:
                self.processed_operations = set()
                
    def save_processed_operations(self):
        """Guarda las operaciones procesadas"""
        processed_file = "processed_operations.json"
        with open(processed_file, 'w') as f:
            json.dump({"processed": list(self.processed_operations)}, f)
            
    def log_event(self, message):
        """Registra eventos en archivo de log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        with open("daemon_log.txt", "a", encoding="utf-8") as f:
            f.write(log_message)
            
        print(log_message.strip())
        
    def create_f_command_oemproxy(self, command_type, data):
        """Crea comando F en formato OemProxy (texto plano)"""
        
        # Construir datos según tipo de comando
        if command_type == "0":  # Crear usuario
            command_data = f"{data.get('employeeNo', '')}|{data.get('name', '')}|NORMAL"
        elif command_type == "1":  # Modificar usuario
            command_data = f"{data.get('employeeNo', '')}|{data.get('name', '')}|MODIFIED"
        elif command_type == "2":  # Eliminar usuario
            command_data = f"{data.get('employeeNo', '')}"
        elif command_type == "3":  # Evento acceso OK
            timestamp = data.get('dateTime', '').replace('-', '').replace(':', '').replace('T', '')[:14]
            command_data = f"{data.get('employeeNo', '')}|{data.get('name', '')}|{data.get('verifyMode', '')}|{timestamp}"
        elif command_type == "4":  # Evento acceso denegado
            timestamp = data.get('dateTime', '').replace('-', '').replace(':', '').replace('T', '')[:14]
            command_data = f"{data.get('employeeNo', '')}|DENIED|{data.get('verifyMode', '')}|{timestamp}"
        else:
            command_data = ""
        
        # Construir comando completo: STX + ID + F + TIPO + DATOS + ETX
        command = f"{self.STX}{self.device_id}F{command_type}{command_data}{self.ETX}"
        
        return command
        
    def send_oemproxy_command(self, command_string):
        """Envía comando en formato OemProxy via POST"""
        try:
            # Convertir string a representación legible para debug
            readable_cmd = command_string.replace(self.STX, '\\x02').replace(self.ETX, '\\x03')
            self.log_event(f"📤 Enviando: {readable_cmd}")
            
            # Enviar como texto plano
            response = requests.post(
                self.post_url,
                data=command_string,
                headers={'Content-Type': 'text/plain'},
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_event(f"✅ Comando enviado correctamente")
                return True
            else:
                self.log_event(f"❌ Error enviando comando: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_event(f"❌ Error en POST: {e}")
            return False
            
    def process_crud_operation(self, operation):
        """Procesa operación CRUD y genera comando F en formato OemProxy"""
        op_type = operation.get('type')
        op_data = operation.get('data', {})
        
        if op_type == 'create':
            # F0: Crear usuario
            command_string = self.create_f_command_oemproxy("0", {
                "employeeNo": op_data.get('employeeNo'),
                "name": op_data.get('name')
            })
            
        elif op_type == 'update':
            # F1: Modificar usuario  
            command_string = self.create_f_command_oemproxy("1", {
                "employeeNo": op_data.get('employeeNo'),
                "name": op_data.get('name')
            })
            
        elif op_type == 'delete':
            # F2: Eliminar usuario
            command_string = self.create_f_command_oemproxy("2", {
                "employeeNo": op_data.get('employeeNo')
            })
            
        else:
            self.log_event(f"⚠️ Tipo de operación desconocido: {op_type}")
            return
            
        # Enviar comando
        if self.send_oemproxy_command(command_string):
            self.log_event(f"🔄 Operación {op_type} procesada para usuario {op_data.get('employeeNo')}")
        else:
            self.log_event(f"❌ Error procesando operación {op_type}")
            
    def monitor_operations(self):
        """Monitorea archivo de operaciones CRUD"""
        while self.running:
            try:
                if os.path.exists(self.operations_file):
                    with open(self.operations_file, 'r') as f:
                        operations = json.load(f)
                    
                    for operation in operations:
                        op_id = f"{operation['timestamp']}_{operation['type']}"
                        
                        if op_id not in self.processed_operations:
                            self.process_crud_operation(operation)
                            self.processed_operations.add(op_id)
                            self.save_processed_operations()
                            
            except Exception as e:
                self.log_event(f"❌ Error monitoreando operaciones: {e}")
                
            time.sleep(2)  # Verificar cada 2 segundos
            
    def start_operation_monitor(self):
        """Inicia hilo de monitoreo de operaciones"""
        thread = threading.Thread(target=self.monitor_operations, daemon=True)
        thread.start()
        self.log_event("🔍 Monitor de operaciones CRUD iniciado")

    def start_event_server(self):
        """Inicia servidor HTTP para recibir eventos"""
        try:
            handler = create_event_handler(self)
            self.server = HTTPServer(('0.0.0.0', self.server_port), handler)
            
            server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            server_thread.start()
            
            self.log_event(f"🌐 Servidor de eventos iniciado en puerto {self.server_port}")
        except Exception as e:
            self.log_event(f"❌ Error iniciando servidor: {e}")
            
    def create_tray_icon(self):
        """Crea icono en bandeja del sistema"""
        try:
            # Crear imagen simple para el icono
            image = Image.new('RGB', (64, 64), color='blue')
            draw = ImageDraw.Draw(image)
            draw.ellipse([16, 16, 48, 48], fill='white')
            
            # Menú del icono
            menu = pystray.Menu(
                pystray.MenuItem("Estado", self.show_status),
                pystray.MenuItem("Ver Log", self.show_log),
                pystray.MenuItem("Configuración", self.show_config),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Salir", self.quit_daemon)
            )
            
            # Crear icono
            self.icon = pystray.Icon("HikvisionDaemon", image, "Hikvision Daemon", menu)
            
            # Ejecutar en hilo separado
            icon_thread = threading.Thread(target=self.icon.run, daemon=True)
            icon_thread.start()
            
            self.log_event("🔧 Icono de bandeja creado")
            
        except Exception as e:
            self.log_event(f"❌ Error creando icono: {e}")
            
    def show_status(self, icon, item):
        """Muestra estado del daemon"""
        status = f"""Hikvision Daemon - Estado:
        
Servidor: Puerto {self.server_port} {'✅ Activo' if self.running else '❌ Inactivo'}
Monitor CRUD: {'✅ Activo' if self.running else '❌ Inactivo'}
URL Destino: {self.post_url}
Device ID: {self.device_id}
Formato: OemProxy (texto plano)

Operaciones procesadas: {len(self.processed_operations)}
        """
        
        print(status)
        self.log_event("ℹ️ Estado consultado")
        
    def show_log(self, icon, item):
        """Abre archivo de log"""
        try:
            if os.path.exists("daemon_log.txt"):
                os.startfile("daemon_log.txt")  # Windows
            else:
                self.log_event("📄 Archivo de log no encontrado")
        except:
            self.log_event("❌ Error abriendo log")
            
    def show_config(self, icon, item):
        """Muestra configuración"""
        config = f"""Configuración actual:
        
Puerto servidor: {self.server_port}
URL destino: {self.post_url}  
Device ID: {self.device_id}
Archivo operaciones: {self.operations_file}
Formato comandos: OemProxy (STX+ID+F+TIPO+DATOS+ETX)
        """
        print(config)
        self.log_event("⚙️ Configuración consultada")
        
    def quit_daemon(self, icon, item):
        """Termina el daemon"""
        self.running = False
        if hasattr(self, 'server'):
            self.server.shutdown()
        if hasattr(self, 'icon'):
            self.icon.stop()
        self.log_event("🛑 Daemon terminado")
        sys.exit(0)
        
    def run_daemon(self):
        """Ejecuta el daemon principal"""
        self.log_event("🚀 Hikvision Daemon iniciado (Formato OemProxy)")
        self.log_event(f"🔗 Escuchando eventos en puerto {self.server_port}")
        self.log_event(f"📡 Enviando comandos F a: {self.post_url}")
        self.log_event(f"📋 Formato: STX+{self.device_id}+F+TIPO+DATOS+ETX")
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.log_event("⏹️ Daemon interrumpido por usuario")
        finally:
            self.quit_daemon(None, None)

if __name__ == "__main__":
    # Configurar para ejecutar como servicio de Windows si es necesario
    if len(sys.argv) > 1 and sys.argv[1] == '--service':
        # Ejecutar como servicio sin interfaz
        daemon = HikvisionDaemon()
        daemon.run_daemon()
    else:
        # Ejecutar con icono de bandeja
        daemon = HikvisionDaemon()
        
        # Mantener programa activo
        try:
            while daemon.running:
                time.sleep(1)
        except KeyboardInterrupt:
            daemon.quit_daemon(None, None)