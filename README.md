# CRUD Hikvision Terminal

Sistema CRUD con interfaz gráfica para gestionar usuarios en terminales Hikvision DS-K1T344MBFWX-E1 con soporte para reconocimiento facial y monitoreo en tiempo real.

## Características Principales

### Gestión de Usuarios
- **Crear usuarios** con datos completos (ID empleado, nombre, foto facial)
- **Modificar** usuarios existentes
- **Eliminar** usuarios del sistema
- **Listar** todos los usuarios registrados

### Reconocimiento Facial
- Carga de fotos en formato JPG
- Configuración de máximo número de caras por usuario
- Soporte para huellas dactilares (opcional)

### Monitoreo en Tiempo Real
- Servidor HTTP integrado para recibir eventos
- Procesamiento de eventos de acceso (códigos 5-75, 5-76)
- Log de actividad detallado
- Configuración automática de notificaciones

## Estructura del Código

### Clase Principal: `HikvisionCRUD`

#### Configuración de Conexión
```python
# Variables de conexión predeterminadas
self.ip_var = "192.168.0.222"        # IP del dispositivo
self.user_var = "admin"              # Usuario admin
self.pass_var = "Oem2017*"           # Contraseña
```

#### Métodos de Usuario
- `create_user()`: Crea nuevo usuario con datos completos
- `update_user()`: Modifica usuario existente
- `delete_user()`: Elimina usuario por ID
- `list_users()`: Lista todos los usuarios

#### Gestión de Imágenes
- `upload_face_data()`: Sube foto facial al dispositivo
- `select_image()`: Selector de archivos JPG

### Monitoreo de Eventos

#### Clase `EventHandler`
Servidor HTTP que recibe notificaciones del dispositivo:

```python
class EventHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Procesa eventos POST del dispositivo
        # Maneja formato JSON y multipart
```

#### Procesamiento de Eventos
- `process_access_event()`: Eventos de acceso facial
- `process_multipart_event()`: Eventos con imágenes
- `extract_json_from_binary()`: Extrae JSON de datos binarios

## Configuración de Dispositivo

### Parámetros de Usuario
```python
user_data = {
    "UserInfo": {
        "employeeNo": str(employee_id),
        "name": user_name,
        "userType": "normal",
        "Valid": {
            "enable": True/False,
            "beginTime": "YYYY-MM-DDTHH:MM:SS",
            "endTime": "YYYY-MM-DDTHH:MM:SS"
        },
        "doorRight": "1",
        "RightPlan": [{"doorNo": 1, "planTemplateNo": "1"}],
        "maxFingerPrintNum": 0-10,
        "maxFaceNum": 0-10
    }
}
```

### Configuración de Eventos
- Puerto del servidor: Configurable (default: 8080)
- Tipos de evento monitoreados:
  - `majorEventType: 5` (Control de Acceso)
  - `subEventType: 75/76` (Eventos específicos)

## Funcionalidades de la Interfaz

### Panel de Conexión
- IP del dispositivo
- Credenciales de autenticación
- Prueba de conectividad

### Panel de Usuario
- ID empleado (obligatorio)
- Nombre completo (obligatorio)
- Selector de imagen JPG

### Panel de Acceso
- Estado habilitado/deshabilitado
- Fechas de validez (inicio/fin)
- Límites de huellas y caras

### Monitoreo
- Área de eventos en tiempo real
- Log de actividad detallado
- Control de servidor de eventos

## APIs Utilizadas

### Endpoints Hikvision
```
POST /ISAPI/AccessControl/UserInfo/Record
PUT /ISAPI/AccessControl/UserInfo/Modify
DELETE /ISAPI/AccessControl/UserInfo/Delete
GET /ISAPI/AccessControl/UserInfo/Search
POST /ISAPI/Intelligent/FDLib/FaceDataRecord
```

### Autenticación
- HTTP Digest Authentication
- Sesiones persistentes con `requests.Session()`

## Manejo de Errores

### Conexión
- Verificación de conectividad
- Manejo de timeouts
- Reintento automático de sesiones

### Procesamiento de Datos
- Validación de campos obligatorios
- Verificación de formatos de imagen
- Parseo seguro de JSON

### Logging
- Timestamps en todos los mensajes
- Categorización de eventos (✅ éxito, ❌ error, 🚪 acceso)
- Log hexadecimal para debug

## Dependencias

```
tkinter          # Interfaz gráfica
requests         # HTTP client
urllib3          # Supresión de warnings SSL
threading        # Servidor de eventos
datetime         # Manejo de fechas
json             # Procesamiento JSON
```

## Uso del Sistema

1. **Configurar conexión** con IP y credenciales
2. **Probar conectividad** antes de operar
3. **Crear usuarios** con foto facial
4. **Iniciar servidor** de eventos para monitoreo
5. **Configurar notificaciones** automáticamente

## Notas Técnicas

- Desactiva warnings SSL con `urllib3.disable_warnings()`
- Usa threading para servidor no bloqueante
- Procesa eventos multipart con imágenes
- Mantiene log persistente de actividad
- Interfaz responsive con scroll automático
