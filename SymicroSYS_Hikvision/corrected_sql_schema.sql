-- =====================================
-- ESQUEMA CORREGIDO PARA MÚLTIPLES DISPOSITIVOS HIKVISION
-- Versión que maneja correctamente las claves primarias y foráneas
-- =====================================
USE [videoman];
GO

PRINT '=== INICIANDO CONFIGURACIÓN HIKVISION ===';
PRINT 'Verificando y corrigiendo estructura de base de datos...';
GO

-- =====================================
-- 1. VERIFICAR Y CORREGIR TABLA FACE
-- =====================================
PRINT '1. Verificando tabla FACE...';

-- Verificar si la tabla face tiene clave primaria
IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS 
    WHERE TABLE_NAME = 'face' AND CONSTRAINT_TYPE = 'PRIMARY KEY'
)
BEGIN
    PRINT '   ⚠️ Tabla face sin clave primaria. Agregando...';
    ALTER TABLE [dbo].[face] ADD CONSTRAINT [PK_face_FacialID] PRIMARY KEY ([FacialID]);
    PRINT '   ✅ Clave primaria agregada a tabla face';
END
ELSE
BEGIN
    PRINT '   ✅ Tabla face tiene clave primaria';
END
GO

-- Verificar si ya existen los campos adicionales
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('face') AND name = 'Sincronizado')
BEGIN
    PRINT '   📝 Agregando campos adicionales a tabla face...';
    
    ALTER TABLE [dbo].[face] ADD 
        -- Campos de sincronización
        [Sincronizado] TINYINT DEFAULT 0,                    -- 0=Pendiente, 1=Sincronizado, -1=Error
        [FechaSincronizacion] DATETIME NULL,                 -- Timestamp de última sincronización
        [UltimoIntento] DATETIME NULL,                       -- Último intento de sincronización
        [NumeroIntentos] INT DEFAULT 0,                      -- Contador de intentos fallidos
        
        -- Campos específicos Hikvision ISAPI
        [CalidadImagen] TINYINT DEFAULT 80,                  -- Calidad de la imagen (1-100)
        [TipoDeteccion] VARCHAR(20) DEFAULT 'face',          -- face, body, vehicle
        [UmbralCoincidencia] TINYINT DEFAULT 80,             -- Threshold de matching (1-100)
        [PermisoAcceso] TINYINT DEFAULT 1,                   -- 1=Permitir, 0=Denegar
        
        -- Metadatos de imagen
        [FormatoImagen] VARCHAR(10) DEFAULT 'JPEG',          -- JPEG, PNG, BMP
        [TamañoImagen] INT NULL,                             -- Tamaño en bytes
        [ResolucionX] INT NULL,                              -- Ancho en pixels
        [ResolucionY] INT NULL,                              -- Alto en pixels
        [HashImagen] VARCHAR(64) NULL,                       -- MD5/SHA256 para detectar duplicados
        
        -- Configuraciones avanzadas
        [DeteccionVital] TINYINT DEFAULT 1,                  -- 1=Activar liveness detection, 0=Desactivar
        [MascaraPermitida] TINYINT DEFAULT 0,                -- 1=Permitir con mascarilla, 0=No permitir
        [AnguloCara] DECIMAL(5,2) NULL,                      -- Ángulo de rotación de la cara
        [CalidadRostro] TINYINT NULL,                        -- Calidad calculada del rostro (1-100)
        
        -- Auditoría
        [CreadoPor] INT NULL,                                -- ID del usuario que creó el registro
        [FechaCreacion] DATETIME DEFAULT GETDATE(),          -- Fecha de creación
        [ModificadoPor] INT NULL,                            -- ID del usuario que modificó
        [FechaModificacion] DATETIME NULL,                   -- Fecha de última modificación
        
        -- Control de versiones
        [Version] INT DEFAULT 1,                             -- Versión del registro
        [Observaciones] NVARCHAR(500) NULL;                  -- Notas adicionales
    
    PRINT '   ✅ Campos adicionales agregados a tabla face';
END
ELSE
BEGIN
    PRINT '   ✅ Tabla face ya tiene los campos adicionales';
END
GO

-- =====================================
-- 2. CREAR TABLA HIKFACE (DISPOSITIVOS)
-- =====================================
PRINT '2. Creando tabla HIKFACE (dispositivos)...';

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'hikface')
BEGIN
    CREATE TABLE [dbo].[hikface](
        [DispositivoID] INT IDENTITY(1,1) PRIMARY KEY,
        [Nombre] NVARCHAR(100) NOT NULL,                     -- Nombre descriptivo del dispositivo
        [IPAddress] VARCHAR(15) NOT NULL,                    -- Dirección IP del dispositivo
        [Puerto] INT DEFAULT 80,                             -- Puerto HTTP (80) o HTTPS (443)
        [Usuario] NVARCHAR(50) DEFAULT 'admin',              -- Usuario para autenticación
        [Password] NVARCHAR(255) NOT NULL,                   -- Contraseña (se debe cifrar)
        [UsarHTTPS] TINYINT DEFAULT 0,                       -- 1=HTTPS, 0=HTTP
        [Activo] TINYINT DEFAULT 1,                          -- 1=Activo, 0=Inactivo
        [Ubicacion] NVARCHAR(200) NULL,                      -- Ubicación física del dispositivo
        [Zona] NVARCHAR(100) NULL,                           -- Zona o área de cobertura
        
        -- Configuración del dispositivo
        [ModeloDispositivo] NVARCHAR(50) NULL,               -- Ej: DS-K1T344MBFWX-E1
        [NumeroSerie] NVARCHAR(50) NULL,                     -- S/N del dispositivo
        [VersionFirmware] NVARCHAR(20) NULL,                 -- Versión del firmware
        [CapacidadMaxUsuarios] INT DEFAULT 3000,             -- Máximo usuarios soportados
        [CapacidadMaxCaras] INT DEFAULT 3000,                -- Máximo caras soportadas
        
        -- Estado operacional
        [EstadoConexion] TINYINT DEFAULT 0,                  -- 0=Desconocido, 1=Online, 2=Offline
        [UltimaConexion] DATETIME NULL,                      -- Última conexión exitosa
        [UltimoError] NVARCHAR(500) NULL,                    -- Último error registrado
        [TiempoRespuesta] INT NULL,                          -- Tiempo de respuesta en ms
        
        -- Configuración de sincronización
        [SincronizacionActiva] TINYINT DEFAULT 1,            -- 1=Sincronizar, 0=No sincronizar
        [IntervaloSincronizacion] INT DEFAULT 5,             -- Minutos entre sincronizaciones
        [HorarioSincronizacion] NVARCHAR(100) NULL,          -- Ej: "08:00-18:00" o "24x7"
        
        -- Auditoría
        [FechaCreacion] DATETIME DEFAULT GETDATE(),
        [CreadoPor] INT NULL,
        [FechaModificacion] DATETIME NULL,
        [ModificadoPor] INT NULL,
        
        -- Restricciones
        CONSTRAINT [UK_hikface_IPAddress] UNIQUE ([IPAddress]),
        CONSTRAINT [CK_hikface_Puerto] CHECK ([Puerto] BETWEEN 1 AND 65535),
        CONSTRAINT [CK_hikface_EstadoConexion] CHECK ([EstadoConexion] IN (0,1,2))
    );
    PRINT '   ✅ Tabla hikface creada exitosamente';
END
ELSE
BEGIN
    PRINT '   ✅ Tabla hikface ya existe';
END
GO

-- =====================================
-- 3. VERIFICAR TABLA PER TIENE CLAVE PRIMARIA
-- =====================================
PRINT '3. Verificando tabla PER...';

IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS 
    WHERE TABLE_NAME = 'per' AND CONSTRAINT_TYPE = 'PRIMARY KEY'
)
BEGIN
    PRINT '   ⚠️ Tabla per sin clave primaria. Agregando...';
    ALTER TABLE [dbo].[per] ADD CONSTRAINT [PK_per_PersonaID] PRIMARY KEY ([PersonaID]);
    PRINT '   ✅ Clave primaria agregada a tabla per';
END
ELSE
BEGIN
    PRINT '   ✅ Tabla per tiene clave primaria';
END
GO

-- =====================================
-- 4. CREAR TABLA COLA DE SINCRONIZACIÓN
-- =====================================
PRINT '4. Creando tabla COLA_SINCRONIZACION...';

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'cola_sincronizacion')
BEGIN
    CREATE TABLE [dbo].[cola_sincronizacion](
        [ColaID] INT IDENTITY(1,1) PRIMARY KEY,
        [FacialID] INT NOT NULL,                             -- FK a face
        [DispositivoID] INT NOT NULL,                        -- FK a hikface
        [PersonaID] INT NOT NULL,                            -- FK a per
        [TipoOperacion] VARCHAR(20) NOT NULL,                -- INSERT, UPDATE, DELETE
        [Prioridad] TINYINT DEFAULT 5,                       -- 1=Alta, 5=Normal, 9=Baja
        [Estado] TINYINT DEFAULT 0,                          -- 0=Pendiente, 1=Procesando, 2=Completado, 3=Error
        [NumeroIntentos] INT DEFAULT 0,                      -- Contador de intentos
        [MaximoIntentos] INT DEFAULT 3,                      -- Máximo número de intentos
        [FechaCreacion] DATETIME DEFAULT GETDATE(),
        [FechaProcesamiento] DATETIME NULL,
        [FechaCompletado] DATETIME NULL,
        [MensajeError] NVARCHAR(1000) NULL,
        [TiempoEjecucion] INT NULL,                          -- Tiempo en milisegundos
        
        -- Claves foráneas
        CONSTRAINT [FK_cola_sincronizacion_face] FOREIGN KEY ([FacialID]) REFERENCES [face]([FacialID]),
        CONSTRAINT [FK_cola_sincronizacion_hikface] FOREIGN KEY ([DispositivoID]) REFERENCES [hikface]([DispositivoID]),
        CONSTRAINT [FK_cola_sincronizacion_per] FOREIGN KEY ([PersonaID]) REFERENCES [per]([PersonaID]),
        
        -- Restricciones
        CONSTRAINT [CK_cola_TipoOperacion] CHECK ([TipoOperacion] IN ('INSERT', 'UPDATE', 'DELETE')),
        CONSTRAINT [CK_cola_Prioridad] CHECK ([Prioridad] BETWEEN 1 AND 9),
        CONSTRAINT [CK_cola_Estado] CHECK ([Estado] BETWEEN 0 AND 3)
    );
    PRINT '   ✅ Tabla cola_sincronizacion creada exitosamente';
END
ELSE
BEGIN
    PRINT '   ✅ Tabla cola_sincronizacion ya existe';
END
GO

-- =====================================
-- 5. CREAR TABLA LOG DE SINCRONIZACIÓN
-- =====================================
PRINT '5. Creando tabla LOG_SINCRONIZACION...';

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'log_sincronizacion')
BEGIN
    CREATE TABLE [dbo].[log_sincronizacion](
        [LogID] INT IDENTITY(1,1) PRIMARY KEY,
        [DispositivoID] INT NOT NULL,
        [FechaHora] DATETIME DEFAULT GETDATE(),
        [TipoEvento] VARCHAR(50) NOT NULL,                   -- CONEXION, SINCRONIZACION, ERROR, etc.
        [Nivel] VARCHAR(10) NOT NULL,                        -- INFO, WARNING, ERROR, DEBUG
        [Mensaje] NVARCHAR(1000) NOT NULL,
        [Detalle] NVARCHAR(MAX) NULL,                        -- JSON con detalles adicionales
        [FacialID] INT NULL,                                 -- FK opcional a face
        [PersonaID] INT NULL,                                -- FK opcional a per
        [TiempoEjecucion] INT NULL,                          -- Tiempo en milisegundos
        [IPOrigen] VARCHAR(15) NULL,                         -- IP desde donde se ejecutó
        [UsuarioSistema] NVARCHAR(100) NULL,                 -- Usuario del sistema operativo
        
        -- Claves foráneas
        CONSTRAINT [FK_log_sincronizacion_hikface] FOREIGN KEY ([DispositivoID]) REFERENCES [hikface]([DispositivoID]),
        
        -- Restricciones
        CONSTRAINT [CK_log_Nivel] CHECK ([Nivel] IN ('INFO', 'WARNING', 'ERROR', 'DEBUG'))
    );
    PRINT '   ✅ Tabla log_sincronizacion creada exitosamente';
END
ELSE
BEGIN
    PRINT '   ✅ Tabla log_sincronizacion ya existe';
END
GO

-- =====================================
-- 6. CREAR TABLA CONFIGURACIÓN
-- =====================================
PRINT '6. Creando tabla CONFIGURACION_HIKVISION...';

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'configuracion_hikvision')
BEGIN
    CREATE TABLE [dbo].[configuracion_hikvision](
        [ConfigID] INT IDENTITY(1,1) PRIMARY KEY,
        [Parametro] NVARCHAR(100) NOT NULL UNIQUE,
        [Valor] NVARCHAR(500) NOT NULL,
        [Descripcion] NVARCHAR(500) NULL,
        [TipoDato] VARCHAR(20) DEFAULT 'STRING',             -- STRING, INTEGER, BOOLEAN, JSON
        [Categoria] NVARCHAR(50) DEFAULT 'GENERAL',          -- GENERAL, SEGURIDAD, RENDIMIENTO
        [ModificablePorUsuario] TINYINT DEFAULT 1,           -- 1=Sí, 0=No (solo admin)
        [FechaModificacion] DATETIME DEFAULT GETDATE(),
        [ModificadoPor] INT NULL
    );
    PRINT '   ✅ Tabla configuracion_hikvision creada exitosamente';
END
ELSE
BEGIN
    PRINT '   ✅ Tabla configuracion_hikvision ya existe';
END
GO

-- =====================================
-- 7. CREAR TABLA ESTADÍSTICAS
-- =====================================
PRINT '7. Creando tabla ESTADISTICAS_DISPOSITIVOS...';

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'estadisticas_dispositivos')
BEGIN
    CREATE TABLE [dbo].[estadisticas_dispositivos](
        [EstadisticaID] INT IDENTITY(1,1) PRIMARY KEY,
        [DispositivoID] INT NOT NULL,
        [Fecha] DATE NOT NULL,
        [UsuariosEnrolados] INT DEFAULT 0,
        [CarasEnroladas] INT DEFAULT 0,
        [SincronizacionesExitosas] INT DEFAULT 0,
        [SincronizacionesFallidas] INT DEFAULT 0,
        [TiempoPromedioRespuesta] INT DEFAULT 0,             -- en milisegundos
        [UptimeDispositivo] DECIMAL(5,2) DEFAULT 0.00,       -- Porcentaje de disponibilidad
        [EspacioUtilizado] DECIMAL(5,2) DEFAULT 0.00,        -- Porcentaje de espacio usado
        [VersionFirmware] NVARCHAR(20) NULL,
        [UltimaActualizacion] DATETIME DEFAULT GETDATE(),
        
        -- Claves foráneas
        CONSTRAINT [FK_estadisticas_hikface] FOREIGN KEY ([DispositivoID]) REFERENCES [hikface]([DispositivoID]),
        
        -- Restricción de unicidad por dispositivo y fecha
        CONSTRAINT [UK_estadisticas_dispositivo_fecha] UNIQUE ([DispositivoID], [Fecha])
    );
    PRINT '   ✅ Tabla estadisticas_dispositivos creada exitosamente';
END
ELSE
BEGIN
    PRINT '   ✅ Tabla estadisticas_dispositivos ya existe';
END
GO

-- =====================================
-- 8. CREAR ÍNDICES OPTIMIZADOS
-- =====================================
PRINT '8. Creando índices optimizados...';

-- Índices en tabla face
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_face_sincronizado' AND object_id = OBJECT_ID('face'))
BEGIN
    CREATE INDEX [IX_face_sincronizado] ON [face]([Sincronizado]) INCLUDE ([FacialID], [Activo]);
    PRINT '   ✅ Índice IX_face_sincronizado creado';
END

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_face_fecha_sincronizacion' AND object_id = OBJECT_ID('face'))
BEGIN
    CREATE INDEX [IX_face_fecha_sincronizacion] ON [face]([FechaSincronizacion]) INCLUDE ([FacialID]);
    PRINT '   ✅ Índice IX_face_fecha_sincronizacion creado';
END

-- Índices en tabla hikface
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_hikface_activo' AND object_id = OBJECT_ID('hikface'))
BEGIN
    CREATE INDEX [IX_hikface_activo] ON [hikface]([Activo]) INCLUDE ([DispositivoID], [IPAddress]);
    PRINT '   ✅ Índice IX_hikface_activo creado';
END

-- Índices en cola_sincronizacion
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_cola_estado_prioridad' AND object_id = OBJECT_ID('cola_sincronizacion'))
BEGIN
    CREATE INDEX [IX_cola_estado_prioridad] ON [cola_sincronizacion]([Estado], [Prioridad]) INCLUDE ([ColaID], [FacialID], [DispositivoID]);
    PRINT '   ✅ Índice IX_cola_estado_prioridad creado';
END
GO

-- =====================================
-- 9. INSERTAR CONFIGURACIÓN INICIAL
-- =====================================
PRINT '9. Insertando configuración inicial...';

-- Verificar si ya existen configuraciones
IF NOT EXISTS (SELECT 1 FROM [configuracion_hikvision])
BEGIN
    INSERT INTO [configuracion_hikvision] ([Parametro], [Valor], [Descripcion], [TipoDato], [Categoria]) VALUES
    ('TIMEOUT_CONEXION', '30', 'Timeout en segundos para conexiones HTTP', 'INTEGER', 'RENDIMIENTO'),
    ('HILOS_SINCRONIZACION', '5', 'Número máximo de hilos de sincronización paralelos', 'INTEGER', 'RENDIMIENTO'),
    ('INTERVALO_VERIFICACION', '60', 'Intervalo en segundos para verificar estado de dispositivos', 'INTEGER', 'GENERAL'),
    ('CALIDAD_IMAGEN_MIN', '70', 'Calidad mínima de imagen requerida (1-100)', 'INTEGER', 'GENERAL'),
    ('UMBRAL_MATCHING_DEFAULT', '80', 'Umbral de matching por defecto (1-100)', 'INTEGER', 'GENERAL'),
    ('INTENTOS_MAXIMOS', '3', 'Número máximo de intentos de sincronización', 'INTEGER', 'GENERAL'),
    ('LIVENESS_DETECTION', 'true', 'Activar detección de vida por defecto', 'BOOLEAN', 'SEGURIDAD'),
    ('LOG_NIVEL', 'INFO', 'Nivel de logging (DEBUG, INFO, WARNING, ERROR)', 'STRING', 'GENERAL'),
    ('BACKUP_AUTOMATICO', 'true', 'Realizar backup automático de configuraciones', 'BOOLEAN', 'SEGURIDAD'),
    ('NOTIFICACIONES_EMAIL', 'false', 'Enviar notificaciones por email', 'BOOLEAN', 'GENERAL');
    
    PRINT '   ✅ Configuración inicial insertada';
END
ELSE
BEGIN
    PRINT '   ✅ Configuración inicial ya existe';
END
GO

-- =====================================
-- 10. CREAR TRIGGERS
-- =====================================
PRINT '10. Creando triggers...';

-- Trigger para fecha de modificación
IF NOT EXISTS (SELECT 1 FROM sys.triggers WHERE name = 'tr_face_update')
BEGIN
    EXEC('
    CREATE TRIGGER [tr_face_update]
    ON [face]
    AFTER UPDATE
    AS
    BEGIN
        SET NOCOUNT ON;
        UPDATE f
        SET FechaModificacion = GETDATE()
        FROM [face] f
        INNER JOIN inserted i ON f.FacialID = i.FacialID;
    END;
    ');
    PRINT '   ✅ Trigger tr_face_update creado';
END
ELSE
BEGIN
    PRINT '   ✅ Trigger tr_face_update ya existe';
END

-- Trigger para cola de sincronización
IF NOT EXISTS (SELECT 1 FROM sys.triggers WHERE name = 'tr_face_cola_sincronizacion')
BEGIN
    EXEC('
    CREATE TRIGGER [tr_face_cola_sincronizacion]
    ON [face]
    AFTER INSERT, UPDATE
    AS
    BEGIN
        SET NOCOUNT ON;
        
        -- Solo proceder si hay dispositivos activos
        IF NOT EXISTS (SELECT 1 FROM [hikface] WHERE Activo = 1 AND SincronizacionActiva = 1)
            RETURN;
        
        -- Insertar en cola para todos los dispositivos activos cuando es INSERT
        IF EXISTS(SELECT 1 FROM inserted) AND NOT EXISTS(SELECT 1 FROM deleted)
        BEGIN
            INSERT INTO [cola_sincronizacion] ([FacialID], [DispositivoID], [PersonaID], [TipoOperacion], [Prioridad])
            SELECT 
                i.FacialID,
                h.DispositivoID,
                pf.PersonaID,
                ''INSERT'',
                CASE WHEN i.Activo = 1 THEN 3 ELSE 5 END
            FROM inserted i
            INNER JOIN [perface] pf ON i.FacialID = pf.FacialID
            CROSS JOIN [hikface] h
            WHERE h.Activo = 1 AND h.SincronizacionActiva = 1
            AND i.Activo = 1;
        END
        
        -- Insertar en cola para todos los dispositivos activos cuando es UPDATE
        IF EXISTS(SELECT 1 FROM inserted) AND EXISTS(SELECT 1 FROM deleted)
        BEGIN
            INSERT INTO [cola_sincronizacion] ([FacialID], [DispositivoID], [PersonaID], [TipoOperacion], [Prioridad])
            SELECT 
                i.FacialID,
                h.DispositivoID,
                pf.PersonaID,
                ''UPDATE'',
                3
            FROM inserted i
            INNER JOIN [perface] pf ON i.FacialID = pf.FacialID
            CROSS JOIN [hikface] h
            WHERE h.Activo = 1 AND h.SincronizacionActiva = 1
            AND i.Activo = 1;
        END
    END;
    ');
    PRINT '   ✅ Trigger tr_face_cola_sincronizacion creado';
END
ELSE
BEGIN
    PRINT '   ✅ Trigger tr_face_cola_sincronizacion ya existe';
END
GO

-- =====================================
-- 11. CREAR VISTAS
-- =====================================
PRINT '11. Creando vistas...';

-- Vista: Resumen de dispositivos
IF NOT EXISTS (SELECT 1 FROM sys.views WHERE name = 'vw_resumen_dispositivos')
BEGIN
    EXEC('
    CREATE VIEW [vw_resumen_dispositivos] AS
    SELECT 
        h.DispositivoID,
        h.Nombre,
        h.IPAddress + '':'' + CAST(h.Puerto AS VARCHAR) AS Endpoint,
        h.Ubicacion,
        h.Zona,
        h.EstadoConexion,
        CASE h.EstadoConexion 
            WHEN 1 THEN ''Online''
            WHEN 2 THEN ''Offline''
            ELSE ''Desconocido''
        END AS EstadoTexto,
        h.UltimaConexion,
        h.CapacidadMaxUsuarios,
        ISNULL(e.UsuariosEnrolados, 0) AS UsuariosActuales,
        ISNULL(e.CarasEnroladas, 0) AS CarasActuales,
        CASE 
            WHEN h.CapacidadMaxUsuarios > 0 
            THEN CAST((ISNULL(e.UsuariosEnrolados, 0) * 100.0 / h.CapacidadMaxUsuarios) AS DECIMAL(5,2))
            ELSE 0 
        END AS PorcentajeUso,
        h.SincronizacionActiva,
        h.IntervaloSincronizacion
    FROM [hikface] h
    LEFT JOIN [estadisticas_dispositivos] e ON h.DispositivoID = e.DispositivoID 
        AND e.Fecha = CAST(GETDATE() AS DATE);
    ');
    PRINT '   ✅ Vista vw_resumen_dispositivos creada';
END
ELSE
BEGIN
    PRINT '   ✅ Vista vw_resumen_dispositivos ya existe';
END

-- Vista: Cola pendiente
IF NOT EXISTS (SELECT 1 FROM sys.views WHERE name = 'vw_cola_pendiente')
BEGIN
    EXEC('
    CREATE VIEW [vw_cola_pendiente] AS
    SELECT 
        h.Nombre AS Dispositivo,
        h.IPAddress,
        COUNT(*) AS RegistrosPendientes,
        MIN(c.FechaCreacion) AS PrimerPendiente,
        MAX(c.FechaCreacion) AS UltimoPendiente,
        SUM(CASE WHEN c.Prioridad <= 3 THEN 1 ELSE 0 END) AS PrioridadAlta,
        SUM(CASE WHEN c.NumeroIntentos > 0 THEN 1 ELSE 0 END) AS ConErrores
    FROM [cola_sincronizacion] c
    INNER JOIN [hikface] h ON c.DispositivoID = h.DispositivoID
    WHERE c.Estado IN (0, 1)
    GROUP BY h.DispositivoID, h.Nombre, h.IPAddress;
    ');
    PRINT '   ✅ Vista vw_cola_pendiente creada';
END
ELSE
BEGIN
    PRINT '   ✅ Vista vw_cola_pendiente ya existe';
END
GO

-- =====================================
-- 12. CREAR PROCEDIMIENTOS ALMACENADOS
-- =====================================
PRINT '12. Creando procedimientos almacenados...';

-- Procedimiento: Limpiar logs antiguos
IF NOT EXISTS (SELECT 1 FROM sys.procedures WHERE name = 'sp_limpiar_logs_antiguos')
BEGIN
    EXEC('
    CREATE PROCEDURE [sp_limpiar_logs_antiguos]
        @DiasAntiguedad INT = 30
    AS
    BEGIN
        SET NOCOUNT ON;
        
        DECLARE @FechaCorte DATETIME = DATEADD(DAY, -@DiasAntiguedad, GETDATE());
        DECLARE @Eliminados INT = 0;
        
        -- Limpiar logs de sincronización
        DELETE FROM [log_sincronizacion] 
        WHERE [FechaHora] < @FechaCorte 
        AND [Nivel] NOT IN (''ERROR'');
        
        SET @Eliminados = @@ROWCOUNT;
        
        -- Limpiar cola completada
        DELETE FROM [cola_sincronizacion] 
        WHERE [FechaCompletado] < @FechaCorte 
        AND [Estado] = 2;
        
        SET @Eliminados = @Eliminados + @@ROWCOUNT;
        
        SELECT 
            CONCAT(''Limpieza completada. '', @Eliminados, '' registros eliminados anteriores a: '', @FechaCorte) AS Resultado;
    END;
    ');
    PRINT '   ✅ Procedimiento sp_limpiar_logs_antiguos creado';
END
ELSE
BEGIN
    PRINT '   ✅ Procedimiento sp_limpiar_logs_antiguos ya existe';
END
GO

-- =====================================
-- 13. INSERTAR DISPOSITIVO DE EJEMPLO
-- =====================================
PRINT '13. Insertando dispositivo de ejemplo...';

-- Insertar tu dispositivo DS-K1T344MBFWX-E1 detectado
IF NOT EXISTS (SELECT 1 FROM [hikface] WHERE IPAddress = '192.168.1.222')
BEGIN
    INSERT INTO [hikface] (
        [Nombre], [IPAddress], [Puerto], [Usuario], [Password], 
        [Ubicacion], [Zona], [ModeloDispositivo], [NumeroSerie], 
        [VersionFirmware], [EstadoConexion], [UltimaConexion]
    ) VALUES (
        'Lector Principal DS-K1T344', 
        '192.168.1.222', 
        80, 
        'admin', 
        'CAMBIAR_PASSWORD', -- ⚠️ Cambiar por la contraseña real
        'Entrada Principal', 
        'Zona A', 
        'DS-K1T344MBFWX-E1', 
        'FN6462740', 
        'V4.13.0',
        1, -- Online
        GETDATE()
    );
    PRINT '   ✅ Dispositivo DS-K1T344MBFWX-E1 agregado (IP: 192.168.1.222)';
END
ELSE
BEGIN
    PRINT '   ✅ Dispositivo DS-K1T344MBFWX-E1 ya existe';
END
GO

-- =====================================
-- 14. VERIFICACIÓN FINAL
-- =====================================
PRINT '14. Verificación final del esquema...';

DECLARE @TablesCount INT;
DECLARE @ViewsCount INT;
DECLARE @TriggersCount INT;

SELECT @TablesCount = COUNT(*) FROM sys.tables 
WHERE name IN ('hikface', 'cola_sincronizacion', 'log_sincronizacion', 'configuracion_hikvision', 'estadisticas_dispositivos');

SELECT @ViewsCount = COUNT(*) FROM sys.views 
WHERE name IN ('vw_resumen_dispositivos', 'vw_cola_pendiente');

SELECT @TriggersCount = COUNT(*) FROM sys.triggers 
WHERE name IN ('tr_face_update', 'tr_face_cola_sincronizacion');

PRINT '=== RESULTADO FINAL ===';
PRINT CONCAT('✅ Tablas creadas: ', @TablesCount, '/5');
PRINT CONCAT('✅ Vistas creadas: ', @ViewsCount, '/2');
PRINT CONCAT('✅ Triggers creados: ', @TriggersCount, '/2');
PRINT '';
PRINT '🎯 TABLAS DISPONIBLES:';
PRINT '   • face (expandida con campos Hikvision)';
PRINT '   • hikface (dispositivos Hikvision)';
PRINT '   • cola_sincronizacion (trabajos pendientes)';
PRINT '   • log_sincronizacion (logs del sistema)';
PRINT '   • configuracion_hikvision (parámetros)';
PRINT '   • estadisticas_dispositivos (métricas)';
PRINT '';
PRINT '🎯 VISTAS DISPONIBLES:';
PRINT '   • vw_resumen_dispositivos';
PRINT '   • vw_cola_pendiente';
PRINT '';
PRINT '🚀 SISTEMA HIKVISION MULTI-DISPOSITIVOS LISTO!';
PRINT '📝 Próximo paso: Actualizar contraseña en tabla hikface';
PRINT '🔧 Luego ejecutar sincronización Python';
GO

-- =====================================
-- 15. CONSULTA DE VERIFICACIÓN
-- =====================================
PRINT '=== CONSULTA DE VERIFICACIÓN ===';

SELECT 
    'Dispositivos registrados' as Tabla,
    COUNT(*) as Registros
FROM hikface
UNION ALL
SELECT 
    'Configuraciones' as Tabla,
    COUNT(*) as Registros  
FROM configuracion_hikvision
UNION ALL
SELECT 
    'Registros faciales' as Tabla,
    COUNT(*) as Registros
FROM face
UNION ALL
SELECT 
    'Cola de sincronización' as Tabla,
    COUNT(*) as Registros
FROM cola_sincronizacion;

PRINT '';
PRINT '✅ Esquema Hikvision Multi-Dispositivos instalado correctamente';
PRINT '🎉 ¡Base de datos lista para sincronización masiva!';
GO