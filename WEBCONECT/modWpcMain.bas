Attribute VB_Name = "modWpcMain"
 Option Explicit '


' 25-01-24   Se incorpora el comando W5 informando la Tolerancia de Salida e Importe
'            Se incorpora el comando W1 informando la Tolerancia de Salida

' 27-01-24   Se incorpora la configuracion del "Identificador de Playa" con 6 digitos numerico
'

' 28-01-24   Se incorpora el comando W2ERROR informando que supero la tolerancia
'

' 30-01-24   Se incorpora en el archivo init.ini los datos de conexion a la base de datos
'

' 31-01-24   Se incorpora el envio de la fecha y hora en los comandos W2OK y W2ERROR
'            Se incorpora el comando "" para sincronizar la fecha y hora con el servidor
'

' 01-02-24   Se corrije error en la respuesta del "W0"
'

' 05-02-24   Se incorpora el comando "W7" para informar que el servidor de Parking
'            en la playa borro una o todas las transacciones pendientes que aun
'            no se han retirado del predio.. "XXXXXXXXXXXXW7" significa que borra
'            un ticket en particular.."000000000000W7" indica que borra todas las
'            transacciones pendientes. Se incorpora EndPoint para recepcion del Comando
'            Se incorpora en el envio del "Alive" la "Capacidad de la Playa" y el
'            estado de actual de "Vehiculos en Playa"

' 06-02-24   Se incorpora el comando "W8" para informar al servidor de "Parking YA"
'            que se ha realizado un Cierre de Caja y se envian todos los resultados
'            del cierre, incluyendo el "Puesto de Venta"....
'            Si en la respuesta del "Alive" el servidor de "Parking Ya" no envia
'            la fecha y hora , NO realiza la accion de sincronizar la fecha y hora
'            del servidor Local

' 09-02-24   Se incorpora el parametro "Operador" en el comando "W8" Cierre de Caja
'            Se resuelve lel error en las mutiples peticiones. Se presenta mediante
'            e objeto "progress barr" la cantidad de peticiones simultaneas que
'            procesa el "WebConect"

' 12-02-24   Incorpora,os control de error en el "Alive" cuando se direcciona erroneamente
'            el servidor...."ERROR DE DIRECCIONAMIENTO CON EL SERVIDOR"
'            Se reposiciono el Label "lbl_ParkYA" que informa comunicacion con el
'            servidor "Parking YA"

' 19-02-24   Se corrijio error en el W7 por mal direccionamiento de la URL

' 09-04-24   Se aumento el tiempo de espera de la respuesta del servidor a 3000ms dado que al utilizar la VPN
'            se hacen mas lentos los tiempos de comunicacion..

' 20-05-24   Se reemplazo el motor de base de datos "MYSQL 4.15 ", por el "MYSQL 8.4 " y se modifico
'            la cadena de conexion

' 24-05-24   Se reemplazo el arrays dinamico por el Array Fijo en 100 conexiones
'

' 11-06-24   Se incorpora deteccion de "Falla de Internet" y reconexion automatica
'            Se reincorpora el "Alive" para mantener sincronizado al Servidor de Parking con el
'            servidor de Parking YA

' 09-07-24   Se elimina la base de datos Access y todo queda trabajando en Mysql 8.4
'            Se incorporan clases para manejo del numero de dipositivo y agregado de
'            Log de eventos en el Cajero

' 10-07-24   Se corrijio error en el "Alive" por recibir la fecha del server en la nube en formato "DD-MM-YYYY HH:MM:SS y
'            se convierte a "YYYY-MM-DD  HH:MM:SS" para actualizar la hora del servidor en el piso dado que la
'            Configuracion Regional debe estar en el formato que acepta Mysql 8.4

' 14-07-24   Se mejoro el Copywrite....
'

' 15-08-24   Se corrijieron errores en la recepcion del Cajero  y envio al Servidor Parking Ya
'            del Cierre de Caja . Se incorporo indicacion de "OFF LINE" cuando no se recibe el
'            Comando "WA" desde el servidor de "PARKING YA" durante mas de 30 segundos.
'            Esto significa que cayo Internet o la VPN . Se fijo en 18 seg el tiempo maximo
'            de espera del comando "WA" que representa que hay comunicacion con el server en la nube

' 29-08-24   Se inserta en el campo "estado" de la tabla "Cierre de Caja" el resultado de la confirmacion
'            si el cierre fue recibido o no por el servidor de "Parking Ya" . Si lo recibio inseta "Enviado",
'            En caso contrario inserta "No Enviado" de forma que pueda enviarse manualmente por el medio
'            del Supervisor en la solapa "Consultas" --> "Reenvio de Cierres de Caja"

' 03-10-24   Se modifica de integer a long la variable "campoid" que representa el campo autoincremental de
'            la tabla "comunicacion" , dado que estaba "desbordado" .
'            Se borran los registros que contengan por error el comando W0 y W1 con los campos Transmision y Recepcion
'            ambos con valores distintos de "NULL" ( Condicion erronea) dado que de lo contrario permanecen etenamente
'            en la tabla. Se modifica Campoid a long en Data Arrival y CheckDB


Public MainEntorno As Entorno
Public DatoRecibidoDelModulo As String
Public formServerVisible As Boolean
Public formClientVisible As Boolean
Public ShowDisplayWpc As Integer
Public ShowDisplayCajero As Integer
Public ShowDisplaySupervisor As Integer
Public ShowDisplayParkYA As Integer
Public cont_Alive As Integer
Public IpPublica As String
Public IpPublica_Almacenada As String
Public IpLAN As String
Public Const Verde = &HC0C000
Public Const Rojo = &HFF&
Public Const Amarillo = &HFFFF&
Public tmr_5min As Integer
Public cantidad_Peticiones As Integer
Public Const Cantidad_Conexiones = 100
Public tmr_OffLine As Integer

Public Const TIME_ALIVE = 10  ' Constante de tiempo de POST ALIVE en segundos
Public Const TIME_SINCRONISMO = 5  ' Constante de Sincronizacion de fecha y hora expresada en segundos
Private Const ASCII_STX = 2   ' Start of text
Private Const ASCII_ETX = 3   ' End of text
Private Const ASCII_EOF = 3   ' End of file
Public Const TIME_OFFLINE = 18      'Maximo tiempo en (seg)hasta entrar en modo offline

Public Declare Sub Sleep Lib "kernel32" (ByVal dwMilliseconds As Long)
Public Declare Function SetSystemTime Lib "kernel32" (lpSystemTime As SYSTEMTIME) As Long
Private Declare Sub GetSystemTime Lib "kernel32" (lpSystemTime As SYSTEMTIME)

Public Type SYSTEMTIME
    wYear As Integer
    wMonth As Integer
    wDayOfWeek As Integer
    wDay As Integer
    wHour As Integer
    wMinute As Integer
    wSecond As Integer
    wMilliseconds As Integer
End Type


Public conexionActiva As ADODB.Connection        ' Declaro variables para el control ADODB para conectarme a la base de datos

' Declaraciones e funciones necesarias para Obtener la IP Publica para informarla al Servidor de Parking YA
Private Declare Function URLDownloadToFile Lib "urlmon" Alias _
    "URLDownloadToFileA" (ByVal pCaller As Long, _
    ByVal szURL As String, ByVal szFileName As String, _
    ByVal dwReserved As Long, ByVal lpfnCB As Long) As Long

Private Declare Function DeleteUrlCacheEntry Lib "Wininet.dll" Alias _
    "DeleteUrlCacheEntryA" (ByVal lpszUrlName As String) As Long

Public ArrayWinsockEjecutivo() As Winsock



' Rutina de Inicializacion
Public Sub Main()

   ShowDisplayWpc = 0
   ShowDisplayCajero = 0
   ShowDisplaySupervisor = 0
   ShowDisplayParkYA = 0
   cont_Alive = TIME_ALIVE                                    ' Inicializamos envio de "Status Alive" cada 10 seg..
   tmr_5min = 4                                               ' Inicializamos el Timer de Sincronismo...en 1 min
   frmWpcMain.ProgressBarr.Max = 100                          ' pero las proximas sincronizaciones de fecha y hora
   frmWpcMain.ProgressBarr.Min = 0                            ' dependeran de la constante "TIME_SINCRONISMO"
   cantidad_Peticiones = 0
   tmr_OffLine = 0                                            ' inicializo el timer OffLine con 0 seg.
   
    Set MainEntorno = New Entorno
  
   If (MainEntorno.LeerValoresINI) Then
    
     Call ConectarMySQL
     Call CheckConfigTable                                       ' Verifica consistencia de la tabla Config_Webconect
    
    Form_Servidor.lbl_SrvPort = Form_Config.Txt_Port_Http
   
     frmWpcMain.WinsockSrvRecep.Close                         'Cerramos cualquier posible conexion anterior
     frmWpcMain.WinsockSrvRecep.LocalPort = Form_Servidor.lbl_SrvPort   'Asignamos el Puerto por donde escucha en Servidor
     frmWpcMain.WinsockSrvRecep.Listen                        'Activamos el Servidor en modo escucha
     Form_Servidor.TerminalServidor.Text = ""
     Form_Servidor.TerminalServidor.Text = Form_Servidor.TerminalServidor.Text & "***Escuhando Conexiones de Clientes.. !!! ***" & vbCrLf
     Form_Servidor.TerminalServidor.SelStart = Len(Form_Servidor.TerminalServidor.Text) ' Desplazamos el ScrollBarr (Barra de desplazamiento) para el nuevo texto
     
     Call Inicializar_Timer
     frmWpcMain.Show
  Else
     MsgBox " No se encontraron los Archivos del sistema .INI ....La aplicacion NO puede ejecutarse !!!", vbCritical, "ERROR"
     End
  End If
  
End Sub


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
'                            RUTINAS DEL MANEJO DE TIMER
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Sub Inicializar_Timer()
  
  frmWpcMain.Timer.Interval = 1000
  frmWpcMain.Timer.Enabled = True
 

End Sub

Sub CheckConfigTable()          ' Verificamos si existe la tabla "Config_WebConect" y todos los campos que la componen
  On Error GoTo salir
  
  Dim sql As String
  Dim command As ADODB.command
  
  Dim rs0 As ADODB.Recordset

  If conexionActiva.State = adStateOpen Then              ' Esta activa la conexion con la Base de datos ??
    Set rs0 = New ADODB.Recordset                         ' Ejecuta la consulta para verificar la existencia de la tabla
    rs0.Open "SHOW TABLES LIKE 'Config_WebConect'", conexionActiva, adOpenStatic, adLockReadOnly
    If rs0.EOF Then                 ' Si no se cumple EOF significa que hay registros por ende la tabla existe
      sql = "CREATE TABLE Config_WebConect (" & _
          "dispositivo INT AUTO_INCREMENT , " & _
          "User CHAR(20) DEFAULT'Oemspot', " & _
          "Password CHAR(20) DEFAULT'Oem2017*', " & _
          "Server_Port_Http INT DEFAULT'9000', " & _
          "Server_Port_Winsock INT DEFAULT'9001', " & _
          "IdPlaya INT DEFAULT'000001', " & _
          "EndPointHTTP_Alive CHAR(100) DEFAULT'https://desarrolloypruebas.com.ar:4006/api/parking/alive', " & _
          "EndPointHTTP_Input CHAR(100) DEFAULT'https://desarrolloypruebas.com.ar:4006/api/parking/ingreso', " & _
          "EndPointHTTP_Output CHAR(100) DEFAULT'https://desarrolloypruebas.com.ar:4006/api/parking/salida', " & _
          "EndPointHTTP_CashPay CHAR(100) DEFAULT'https://desarrolloypruebas.com.ar:4006/api/parking/pagoEfectivo', " & _
          "EndPointHTTP_ClearTicket CHAR(100) DEFAULT'https://desarrolloypruebas.com.ar:4006/api/parking/borradoTicket', " & _
          "EndPointHTTP_CloseBox CHAR(100) DEFAULT'https://desarrolloypruebas.com.ar:4006/api/parking/cierreCaja', " & _
          "PRIMARY KEY (dispositivo))"
           
      Set command = New ADODB.command              ' Aqui se crea la tabla "Config_Webconect"
      command.ActiveConnection = conexionActiva
      command.CommandText = sql
      command.Execute
       
      sql = "INSERT INTO Config_WebConect () VALUES ()" ' Como la cree con valores Default, para que se
      command.CommandText = sql                         ' asignen debemos insertar un registro que tomara
      command.Execute                                   ' los valores Default
      
    End If
    If rs0.State = 1 Then rs0.Close                      ' Liberamos el Recordset"0"
    Set rs0 = Nothing
    Exit Sub
    
  End If
  MsgBox "Error al Conectarse con la Base de Datos..!!!", vbCritical
  DesconectarMySQL
  End
  Exit Sub
  
salir:
  MsgBox "Error al Verificar la Tabla de Configuracion Web_Conect", vbCritical
  DesconectarMySQL
  End
End Sub

Sub ConectarMySQL()
   
    Set conexionActiva = New ADODB.Connection                                   ' Creamos una instancia de la conexión
    conexionActiva.Open MainEntorno.DSN_MySQL                                   ' Abrimos la conexión
    
    If Not conexionActiva.State = adStateOpen Then                              ' Se establecio la conexion correctamente ??
       MsgBox "Error al conectar a la base de datos.", vbCritical
       End
    End If
    AgregarLog 170, "Webconect Inicio", MainEntorno
End Sub



Sub DesconectarMySQL()
    ' Cierra la conexión
    If Not conexionActiva Is Nothing Then
        If conexionActiva.State = adStateOpen Then
             AgregarLog 171, "Webconect Desconexion", MainEntorno
            conexionActiva.Close
            Set conexionActiva = Nothing
        End If
    End If
End Sub


Public Sub CheckDB()                             ' Chequear Base de Datos
On Error GoTo MISTAKE:

Dim CampoRecepcion, CampoTransmision, sql As String
Dim CelCommand As String                         'Almacena el comando de la comunicacion Celular
Dim Campoid As Long                              ' si =0 ,indica que no hay comandos celulares
Dim CampocreatedAt As Date
Dim tolerancia_salida As String
Dim importe_pagado As String

Dim dbCommand As ADODB.command                   ' Definimos las variables que contendran las propiedades de los objetos ADODB
Dim dbcommand2 As ADODB.command
Dim dbRecordset As ADODB.Recordset


If conexionActiva.State = adStateOpen Then              ' Esta activa la conexion con la Base de datos ??
    
    Set dbCommand = New ADODB.command
    dbCommand.ActiveConnection = conexionActiva
    
    Set dbRecordset = New ADODB.Recordset
    dbRecordset.Open "SELECT * FROM  comunicacion ", conexionActiva, adOpenForwardOnly, adLockReadOnly

    CelCommand = 0                                           ' Indica que no hay comandos Celulares

    If dbRecordset.EOF Then                                  ' Hay algun registro a procesar ??
    ' DirectorioActual = App.Path & "\logo HD webconect.jpg" ' No.... Entonces Carga el Directorio Actual
    ' frmWpcMain.Image1.Picture = LoadPicture(DirectorioActual)         ' Activa Imagen de Oemspot
      If dbRecordset.State = 1 Then dbRecordset.Close        ' Cerramos el Recordset
      Set dbCommand = Nothing                                ' Vaciamos los objetos liberando memoria
      Set dbRecordset = Nothing
      Exit Sub
    End If

    ' La tabla "comunicacion" tiene 2 campos "Transmision" y "Recepcion".
    ' El WPC informa los ingresos y egresos en el campo "Recepcion"
    
    ' El Cajero escucha las ordenes del Server Parking YA a traves del Webconect por el campo
    ' "Transmision" y responde por el campo "Recepcion"
    
    ' El WebConect informa las ordenes del Server Parking YA en el campo "Transmision"
    ' y escucha por el campo "Recepcion" las ordenes del WPC y Respuestas del Cajero

    While Not dbRecordset.EOF                                'Carga el primer registro de la tabla
      CampoTransmision = dbRecordset!transmision
      CampoRecepcion = dbRecordset!recepcion
      
      Campoid = dbRecordset!id
      CampocreatedAt = dbRecordset!createdAt
      
      If CampoRecepcion = "NULL" Then
         CelCommand = "NULL"
      Else
         CelCommand = Mid$(CampoRecepcion, 13, 2)
      End If
     
            
      Select Case CelCommand
      
         Case "W0"                                                   ' Hay solicitud de Liquidacion?
            If (CampoRecepcion <> "NULL") And (CampoTransmision <> "NULL") Then
             sql = "DELETE FROM comunicacion WHERE id = " & Campoid                 ' Si por casualidad el Data Arrival no pudo borrar el registro
             dbCommand.CommandText = sql                                            ' en curso, nos queda en la tabla el registro con el campo recepcion
             dbCommand.Execute                                                      ' y Transmision con valores , lo cuales inconsistente .
            End If                                                                  ' Een este unico caso borramos el registro
            
            
         Case "W1"
          If (CampoRecepcion <> "NULL") And (CampoTransmision <> "NULL") Then       ' Idem para el W1
             sql = "DELETE FROM comunicacion WHERE id = " & Campoid
             dbCommand.CommandText = sql
             dbCommand.Execute
            End If
           
           
           
         Case "W2"
              
              If (Len(CampoRecepcion) > 16) Then
                CelCommand = Mid$(CampoRecepcion, 1, 12)                  ' Captura los 12 digitos'
                If Not ShowDisplayWpc Then                                ' Muestra en el Display de la aplicacion
                  frmWpcMain.lbl_WPC.Caption = "SUPERO LA TOLERANCIA: " + CelCommand + "  Habilitado.."
                  ShowDisplayWpc = 2                                      ' Informa al Servidor de "Parking Ya" que sale
                End If                                                    ' Un vehiculo ..
                Call Enviar_Post_SuperoTolerancia(CelCommand, CampocreatedAt)
              Else
                CelCommand = Mid$(CampoRecepcion, 1, 12)                  ' Captura los 12 digitos'
                If Not ShowDisplayWpc Then                                ' Muestra en el Display de la aplicacion
                  frmWpcMain.lbl_WPC.Caption = "EGRESO VEHICULAR: " + CelCommand + "  Habilitado.."
                  ShowDisplayWpc = 2                                      ' Informa al Servidor de "Parking Ya" que sale
                End If
                Call Enviar_Post_Salida(CelCommand, CampocreatedAt)       ' Un vehiculo ..
              End If
              If conexionActiva.State = adStateOpen Then                ' Como ya enviamos al servidor de "Parking YA"
                Set dbcommand2 = New ADODB.command                      ' el JSON borramos el registro de la
                dbcommand2.ActiveConnection = conexionActiva            ' Tabla comunicacion y nos vamos.....
                sql = "DELETE FROM comunicacion WHERE id=" & Campoid
                dbcommand2.CommandText = sql
                dbcommand2.Execute
              End If
              
         
         Case "W4"
              CelCommand = Mid$(CampoRecepcion, 1, 12)                  ' Captura los 12 digitos'
              If Not ShowDisplayWpc Then                                ' Muestra en el Display de la aplicacion
                frmWpcMain.lbl_WPC.Caption = "INGRESO VEHICULAR: " + CelCommand + "  Habilitado.."
                ShowDisplayWpc = 2                                      ' Informa al Servidor de "Parking Ya" que ingreso
              End If
              Call Enviar_Post_Entrada(CelCommand, CampocreatedAt)      ' Un vehiculo ..
              If conexionActiva.State = adStateOpen Then                ' Como ya enviamos al servidor de "Parking YA"
                Set dbcommand2 = New ADODB.command                      ' el JSON borramos el registro de la
                dbcommand2.ActiveConnection = conexionActiva            ' Tabla comunicacion y nos vamos.....
                sql = "DELETE FROM comunicacion WHERE id=" & Campoid
                dbcommand2.CommandText = sql
                dbcommand2.Execute
              End If
              
                            
         Case "W5"
              CelCommand = Mid$(CampoRecepcion, 1, 12)                  ' Captura los 12 digitos del Identificador o Ticket
              tolerancia_salida = Mid$(CampoRecepcion, 15, 8)             ' Captura la Tolerancia de salida
              importe_pagado = Mid$(CampoRecepcion, 23)
              If Not ShowDisplayCajero Then                                ' Muestra en el Display de la aplicacion
                frmWpcMain.lbl_Cajero.Caption = "PAGO EN EFECTIVO: " + CelCommand + "  Habilitado.."
                ShowDisplayCajero = 2                                      ' Informa al Servidor de "Parking Ya" que "Pago en Efvo"
              End If
              Call Enviar_Post_PayCash(CelCommand, CampocreatedAt, importe_pagado, tolerancia_salida)
              If conexionActiva.State = adStateOpen Then                ' Como ya enviamos al servidor de "Parking YA"
                Set dbcommand2 = New ADODB.command                      ' el JSON borramos el registro de la
                dbcommand2.ActiveConnection = conexionActiva            ' Tabla comunicacion y nos vamos.....
                sql = "DELETE FROM comunicacion WHERE id=" & Campoid
                dbcommand2.CommandText = sql
                dbcommand2.Execute
              End If
              
                            
         Case "W7"
              CelCommand = Mid$(CampoRecepcion, 1, 12)                  ' Captura los 12 digitos'
              If Not ShowDisplaySupervisor Then                         ' Muestra en el Display de la aplicacion
                If CelCommand = "000000000000" Then
                  frmWpcMain.lbl_Supervisor.Caption = "BORRADO DE TODOS LOS VEHICULOS EN PLAYA"
                Else
                  frmWpcMain.lbl_Supervisor.Caption = "BORRADO DEL TICKET NRO: " & CelCommand
                End If
                ShowDisplaySupervisor = 2                                      ' Informa al Servidor de "Parking Ya" que
              End If                                                           ' se borra 1 o todos los tickets pendientes
              Call Enviar_Post_BorradoTicket(CelCommand, CampocreatedAt)       ' de salir por orden del "Supervisor" ..
              If conexionActiva.State = adStateOpen Then                       ' Como ya enviamos al servidor de "Parking YA"
                Set dbcommand2 = New ADODB.command                             ' el JSON borramos el registro de la
                dbcommand2.ActiveConnection = conexionActiva                   ' Tabla comunicacion y nos vamos.....
                sql = "DELETE FROM comunicacion WHERE id=" & Campoid
                dbcommand2.CommandText = sql
                dbcommand2.Execute
              End If
              
              
         Case "W8"
              CelCommand = CampoRecepcion
              If Not ShowDisplayCajero Then                                    ' Muestra en el Display de la aplicacion
                frmWpcMain.lbl_Cajero.Caption = "ENVIANDO DATOS DE CIERRE DE CAJA "
                ShowDisplayCajero = 2                                          ' Informa al Servidor de "Parking Ya" que
              End If                                                           ' el "Cierre de Caja" por orden del "Cajero"
              Call Enviar_Cierre_Caja(CelCommand, CampocreatedAt)
              If conexionActiva.State = adStateOpen Then                       ' Como ya enviamos al servidor de "Parking YA"
                Set dbcommand2 = New ADODB.command                             ' el JSON borramos el registro de la
                dbcommand2.ActiveConnection = conexionActiva                   ' Tabla comunicacion y nos vamos.....
                sql = "DELETE FROM comunicacion WHERE id=" & Campoid
                dbcommand2.CommandText = sql
                dbcommand2.Execute
              End If
              
                            
         Case "NULL"
         
         Case Else
            If conexionActiva.State = adStateOpen Then
              Set dbcommand2 = New ADODB.command
              dbcommand2.ActiveConnection = conexionActiva
              sql = "UPDATE comunicacion SET recepcion = 'NO ACKNOWLES'"
              dbCommand.CommandText = sql
              dbCommand.Execute
            End If
      
      End Select
            
      dbRecordset.MoveNext
    Wend
    
  End If
  
  If dbRecordset.State = 1 Then dbRecordset.Close  ' Cerramos el Recordset
  Set dbCommand = Nothing                          ' Vaciamos los objetos liberando memoria
  Set dbRecordset = Nothing
  Exit Sub

MISTAKE:
  If dbRecordset.State = 1 Then dbRecordset.Close  ' Cerramos el Recordset
  Set dbCommand = Nothing                          ' Vaciamos los objetos liberando memoria
  Set dbRecordset = Nothing
  frmWpcMain.lbl_WPC = Err.Description             ' Muestra el Error en el Display de la aplicacion
  ShowDisplayWpc = 2
  frmWpcMain.lbl_WPC.BackColor = Rojo             ' Coloca el Label de Informacion del WPC en Rojo lo que significa
  'MsgBox "Error: " & Err.Description, vbExclamation, "Error al conectar a la base de datos."
End Sub

Private Sub Enviar_Post_Entrada(uuid As String, createdAt As Date)

Dim httpReq As Object
Dim response As String
Dim fechaHoraString As String
Dim Id_Playa As String

Id_Playa = Form_Config.Txt_IdPlaya
Id_Playa = Format(Id_Playa, "000000")

Set httpReq = CreateObject("WinHttp.WinHttpRequest.5.1")

Dim url As String
Dim jsonData As String

url = Form_Config.Txt_Entrada
    
jsonData = "{" & vbCrLf & _
        """cod_ticket"": """ & uuid & """," & vbCrLf & _
        """id_parking"": """ & Id_Playa & """," & vbCrLf & _
        """fecha"": """ & createdAt & """," & vbCrLf & _
        """codStatus"": ""W4""" & vbCrLf & _
    "}"
    
  
httpReq.Open "POST", url, False
httpReq.SetRequestHeader "Content-Type", "application/json"   ' Indicamos que el JSON va en el body NO en el encabezado
httpReq.SetTimeouts 30000, 30000, 30000, 30000                    ' Fijamos tiempo espera maxima para resolver,conectar,enviar,recibir en ms.

httpReq.Send jsonData ' Enviamos el JSON
'MsgBox jsonData

If httpReq.Status = 200 Then                                   ' La solicitud fue exitosa, procesa la respuesta
    ' MsgBox "Respuesta del servidor: " & httpReq.ResponseText
    frmWpcMain.lbl_WPC.BackColor = Verde                     ' Coloca el Label de Informacion del WPC en Verde lo que significa
Else                                                         ' que el Sevidor de Parking YA recibio el mensaje..!!!
    ' MsgBox "Error: " & httpReq.Status & " - " & httpReq.StatusText  ' La solicitud falló, muestra el código de estado y la descripción
    frmWpcMain.lbl_WPC.BackColor = Rojo                      ' Coloca el Label de Informacion del WPC en Rojo lo que significa
    AgregarLog 3101, "INGRESO:" & uuid, MainEntorno
End If                                                       ' que el servidor no recibio el mensaje
Set httpReq = Nothing
End Sub
Public Sub Enviar_Post_Alive()

    Dim httpReq As Object                                    ' Aqui enviamos cada "TIME_ALIVE" segundos un post al servidor
    Dim response As String                                   ' de "Parking YA" informando que estamos vivo y refrescamos
    Dim server_port As String                                ' la informacion de la IP y Puerto donde trabaja el
    Dim url As String                                        ' Servidor del Parking en la playa de estacionamiento
    Dim jsonData As String
    Dim Id_Playa As String
    Dim fechaserver As String
    Dim totalVehiculos As Integer
    Dim sql As String
    Dim Vehiculos_Playa As String
    Dim MaxVehiculos As String
    
    On Error GoTo salir
    
    
    Id_Playa = Form_Config.Txt_IdPlaya                      ' Aqui levantamos el id_Playa
    Id_Playa = Format(Id_Playa, "000000")

    server_port = Form_Config.Txt_Port_Http                 ' Aqui levantamos el Port Http
    server_port = Format(server_port, "0000")

    totalVehiculos = 0                                      ' Aqui levantamos la cantidad actual de vehiculos en Playa
    If conexionActiva.State = adStateOpen Then              ' Verificamos si la conexión está activa
      Dim dbCommand As New ADODB.command                    ' Creamos un objeto de comando
      Set dbCommand.ActiveConnection = conexionActiva
      Dim dbRecordset As New ADODB.Recordset                ' Crear un objeto de recordset
      sql = "SELECT SUM(vehiculos_en_playa) AS total_vehiculos FROM estado_de_la_playa"
      dbRecordset.Open sql, conexionActiva, adOpenForwardOnly, adLockReadOnly     ' hacemos la consulta recordset
      If Not dbRecordset.EOF Then                           ' se encontraron registros ???
        totalVehiculos = dbRecordset.Fields("total_vehiculos").Value ' Definimos la variable que tendra la suma de todos
      Else
        MsgBox "No se encontraron registros en la tabla estado_de_la_playa."
      End If
      dbRecordset.Close                                     ' cerramos el recordset
      Set dbRecordset = Nothing                             ' Limpiamos objetos para liberar memoria
      Set dbCommand = Nothing
    End If
    Vehiculos_Playa = CStr(totalVehiculos)                  ' Convertimos a String para armar el JSON
    
  
    MaxVehiculos = 0                                        ' Aqui levantamos la Capacidad de vehiculos en Playa
    If conexionActiva.State = adStateOpen Then        ' Verificamos si la conexión está activa
      Dim command As New ADODB.command                      ' Creamos un objeto de comando
      Set command.ActiveConnection = conexionActiva
      Dim Recordset As New ADODB.Recordset                  ' Crear un objeto de recordset
      sql = "SELECT Capacidad_Playa FROM Playa"
      Recordset.Open sql, conexionActiva, adOpenForwardOnly, adLockReadOnly     ' hacemos la consulta recordset
      If Not Recordset.EOF Then                             ' se encontraron registros ???
        MaxVehiculos = Recordset!Capacidad_Playa         ' Definimos la variable que tendra la suma de todos los vehiculos
      Else
        MsgBox "No se encontraron registros en la Base Access tabla Playa."
      End If
      Recordset.Close                                       ' cerramos el recordset
      Set Recordset = Nothing                               ' Limpiamos objetos para liberar memoria
      Set command = Nothing
    End If
   
    Set httpReq = CreateObject("WinHttp.WinHttpRequest.5.1")

    url = Form_Config.Txt_Estado

    jsonData = "{" & vbCrLf & _
        """id_parking"": """ & Id_Playa & """," & vbCrLf & _
        """capacidad_vehiculos"": """ & MaxVehiculos & """," & vbCrLf & _
        """cant_vehiculos"": """ & Vehiculos_Playa & """," & vbCrLf & _
        """ip"": """ & IpPublica & """," & vbCrLf & _
        """puerto"": """ & server_port & """" & vbCrLf & _
    "}"
    
   ' MsgBox jsonData
   
    httpReq.Open "POST", url, False
    httpReq.SetRequestHeader "Content-Type", "application/json"
    httpReq.SetTimeouts 30000, 30000, 30000, 30000

    httpReq.Send jsonData
    
    If httpReq.Status = 200 Then                                  ' Si la solicitud fue exitosa, procesa la respuesta
        response = httpReq.ResponseText                           ' Obtenemos la respuesta del servidor en "response"
        frmWpcMain.lbl_ParkYA.Caption = "ENVIO DE STATUS ALIVE AL SERVIDOR..."
        ShowDisplayParkYA = 2
        frmWpcMain.lbl_ParkYA.BackColor = Verde                   ' Como respuesta al "Alive" el servidor de "Parking YA"
       
        If (frmWpcMain.ExisteClaveJson(response, "fecha_server")) Then  ' Existe el comando
          Dim inicioCodfecha As Integer
          Dim finCodfecha As Integer
          inicioCodfecha = InStr(response, """fecha_server"": """) + Len("""fecha_server"": """)
          finCodfecha = InStr(inicioCodfecha, response, """")
          fechaserver = Mid$(response, 18, 19)                    ' Aqui "fechaserver".....
     
          Dim sysTime As SYSTEMTIME
          Dim FechaHoraServerDate As Date
          Dim fechaHoraSubstring As String
          fechaHoraSubstring = Mid$(fechaserver, 1, 19)             ' Tomamos los primeros 19 caracteres
          FechaHoraServerDate = CDate(fechaHoraSubstring)           ' Convertimos la cadena string a un objeto Date
          FechaHoraServerDate = ConvertirFechaHora(fechaHoraSubstring)
         
       
       
           FechaHoraServerDate = DateAdd("h", 3, FechaHoraServerDate)   ' Ajusta la hora sumando 3 horas por el uso horario
        
          If frmWpcMain.Timer_Sincronismo.Enabled = False Then        ' Si el Timer esta inactivo , significa que debemos
                                                                       ' enviara la fecha y hora del servidor , la cual
            frmWpcMain.lbl_ParkYA.Caption = "SINCRONIZACION DE FECHA HORA  !!!..."
            frmWpcMain.lbl_ParkYA.BackColor = Verde                   ' Informa que recibe "Solicitud de Sincronismo"
            ShowDisplayParkYA = 2                                     ' Color Verde
            frmWpcMain.lbl_Sincronismo.Caption = fechaserver
          
            frmWpcMain.Timer_Sincronismo = True                       ' actualizar la fecha y hora del sistema con la
            tmr_5min = 0                                              ' informacion de sincronismo que llega del servidor "Parking Ya"
            With sysTime
              .wYear = Year(FechaHoraServerDate)
              .wMonth = Month(FechaHoraServerDate)                    ' Llena la estructura SYSTEMTIME con la fecha y hora actual
              .wDay = Day(FechaHoraServerDate)
              .wDayOfWeek = Weekday(FechaHoraServerDate) - 1
              .wHour = Hour(FechaHoraServerDate)
              .wMinute = Minute(FechaHoraServerDate)
              .wSecond = Second(FechaHoraServerDate)
              .wMilliseconds = 0
            End With
                                     
            If SetSystemTime(sysTime) <> 0 Then                       'llamamos SetSystemTime para fijar la fecha y hora del sistema
              frmWpcMain.lbl_Sincronismo.BackColor = &H8000000F       'Backcolor Gris...Ok"
            Else
              frmWpcMain.lbl_Sincronismo.BackColor = Rojo
              'MsgBox "¡Error al intentar actualizar la hora del sistema!", vbExclamation
            End If
          End If
        End If
    Else
        frmWpcMain.lbl_ParkYA.BackColor = Rojo
        ShowDisplayParkYA = 2
        frmWpcMain.lbl_ParkYA.Caption = "ERROR ENVIO DE STATUS ALIVE AL SERVIDOR..."
        AgregarLog 3106, "ALIVE SIN RESPUESTA", MainEntorno
    End If
    Set httpReq = Nothing
    Exit Sub

salir:
     frmWpcMain.lbl_ParkYA.BackColor = Rojo
     ShowDisplayParkYA = 2
     frmWpcMain.lbl_ParkYA.Caption = "ERROR DE DIRECCIONAMIENTO DE SERVIDOR..."
     AgregarLog 3106, "ALIVE SIN RESPUESTA", MainEntorno
     Set httpReq = Nothing
End Sub

Function ConvertirFechaHora(fechaHoraString As String) As Date
    Dim dia As String
    Dim mes As String
    Dim anio As String                                                  ' fechaHoraString = "10-07-2024 15:24:55"
    Dim hora As String
    Dim minutos As String
    Dim segundos As String
    Dim FechaHoraCorrectaString As String
    Dim FechaHoraServerDate As Date

    ' Separar la fecha y la hora
    dia = Mid(fechaHoraString, 1, 2)
    mes = Mid(fechaHoraString, 4, 2)
    anio = Mid(fechaHoraString, 7, 4)
    hora = Mid(fechaHoraString, 12, 2)
    minutos = Mid(fechaHoraString, 15, 2)
    segundos = Mid(fechaHoraString, 18, 2)

    ' Reorganizar la fecha y hora al formato YYYY-MM-DD hh:mm:ss
    FechaHoraCorrectaString = anio & "-" & mes & "-" & dia & " " & hora & ":" & minutos & ":" & segundos

    ' Convertir la cadena corregida a un objeto Date
    FechaHoraServerDate = CDate(FechaHoraCorrectaString)

    ' Devolver el objeto Date
    ConvertirFechaHora = FechaHoraServerDate
End Function


Private Sub Enviar_Post_Salida(uuid As String, createdAt As Date)

Dim httpReq As Object
Dim response As String
Dim Id_Playa As String

Id_Playa = Form_Config.Txt_IdPlaya
Id_Playa = Format(Id_Playa, "000000")

Set httpReq = CreateObject("WinHttp.WinHttpRequest.5.1")

Dim url As String
Dim jsonData As String

url = Form_Config.Txt_Salida                                ' Cargamos la URL del formulario "Config"

jsonData = "{" & vbCrLf & _
        """cod_ticket"": """ & uuid & """," & vbCrLf & _
        """id_parking"": """ & Id_Playa & """," & vbCrLf & _
        """fecha_salida"": """ & createdAt & """," & vbCrLf & _
        """codStatus"": ""W2OK""" & vbCrLf & _
    "}"

httpReq.Open "POST", url, False
httpReq.SetRequestHeader "Content-Type", "application/json"   ' Indicamos que el JSON va en el body NO en el encabezado
httpReq.SetTimeouts 30000, 30000, 30000, 30000                    ' Fijamos tiempo espera maxima para resolver,conectar,enviar,recibir en ms.

httpReq.Send jsonData                                         ' Enviamos el JSON
'MsgBox jsonData

If httpReq.Status = 200 Then                                   ' La solicitud fue exitosa, procesa la respuesta
    ' MsgBox "Respuesta del servidor: " & httpReq.ResponseText
    frmWpcMain.lbl_WPC.BackColor = Verde                   ' Coloca el Label de Informacion del WPC en Verde lo que significa
Else                                                          ' que el Sevidor de Parking YA recibio el mensaje..!!!
    ' MsgBox "Error: " & httpReq.Status & " - " & httpReq.StatusText  ' La solicitud falló, muestra el código de estado y la descripción
    frmWpcMain.lbl_WPC.BackColor = Rojo                      ' Coloca el Label de Informacion del WPC en Rojo lo que significa
    AgregarLog 3102, "EGRESO: " & uuid, MainEntorno
End If                                                        ' que el servidor no recibio el mensaje
Set httpReq = Nothing
End Sub
Private Sub Enviar_Post_PayCash(uuid As String, createdAt As Date, importe_pagado As String, tolerancia_salida As String)

Dim httpReq As Object
Dim response As String

Set httpReq = CreateObject("WinHttp.WinHttpRequest.5.1")

Dim url As String
Dim jsonData As String

Dim Id_Playa As String

Id_Playa = Form_Config.Txt_IdPlaya
Id_Playa = Format(Id_Playa, "000000")

url = Form_Config.Txt_CashPay                                 ' Cargamos la URL del formulario "Config"

jsonData = "{" & vbCrLf & _
    """cod_ticket"": """ & uuid & """," & vbCrLf & _
    """codStatus"": ""W5""," & vbCrLf & _
    """id_parking"": """ & Id_Playa & """," & vbCrLf & _
    """importe"": """ & importe_pagado & """," & vbCrLf & _
    """tolerancia"": """ & tolerancia_salida & """," & vbCrLf & _
    """fecha_pago"": """ & createdAt & """" & vbCrLf & _
"}"

httpReq.Open "POST", url, False
httpReq.SetRequestHeader "Content-Type", "application/json"   ' Indicamos que el JSON va en el body NO en el encabezado
httpReq.SetTimeouts 30000, 30000, 30000, 30000                    ' Fijamos tiempo espera maxima para resolver,conectar,enviar,recibir en ms.

httpReq.Send jsonData                                         ' Enviamos el JSON

If httpReq.Status = 200 Then                                  ' La solicitud fue exitosa, procesa la respuesta
    ' MsgBox "Respuesta del servidor: " & httpReq.ResponseText
    frmWpcMain.lbl_Cajero.BackColor = Verde                   ' Coloca el Label de Informacion del WPC en Verde lo que significa
Else                                                          ' que el Sevidor de Parking YA recibio el mensaje..!!!
    ' MsgBox "Error: " & httpReq.Status & " - " & httpReq.StatusText  ' La solicitud falló, muestra el código de estado y la descripción
    frmWpcMain.lbl_Cajero.BackColor = Rojo                    ' Coloca el Label de Informacion del WPC en Rojo lo que significa
    AgregarLog 3103, "PAGO CAJA:" & uuid, MainEntorno
End If                                                        ' que el servidor no recibio el mensaje
Set httpReq = Nothing
End Sub

Private Sub Enviar_Post_SuperoTolerancia(uuid As String, createdAt As Date)

Dim httpReq As Object
Dim response As String
Dim Id_Playa As String

Id_Playa = Form_Config.Txt_IdPlaya
Id_Playa = Format(Id_Playa, "000000")

Set httpReq = CreateObject("WinHttp.WinHttpRequest.5.1")

Dim url As String
Dim jsonData As String

url = Form_Config.Txt_Salida                                ' Cargamos la URL del formulario "Config"

jsonData = "{" & vbCrLf & _
        """cod_ticket"": """ & uuid & """," & vbCrLf & _
        """id_parking"": """ & Id_Playa & """," & vbCrLf & _
        """fecha_salida"": """ & createdAt & """," & vbCrLf & _
        """codStatus"": ""W2ERROR""" & vbCrLf & _
    "}"

'MsgBox jsonData

httpReq.Open "POST", url, False
httpReq.SetRequestHeader "Content-Type", "application/json"   ' Indicamos que el JSON va en el body NO en el encabezado
httpReq.SetTimeouts 30000, 30000, 30000, 30000                    ' Fijamos tiempo espera maxima para resolver,conectar,enviar,recibir en ms.

httpReq.Send jsonData                                         ' Enviamos el JSON

If httpReq.Status = 200 Then                                   ' La solicitud fue exitosa, procesa la respuesta
    ' MsgBox "Respuesta del servidor: " & httpReq.ResponseText
    frmWpcMain.lbl_WPC.BackColor = Verde                     ' Coloca el Label de Informacion del WPC en Verde lo que significa
Else                                                         ' que el Sevidor de Parking YA recibio el mensaje..!!!
    ' MsgBox "Error: " & httpReq.Status & " - " & httpReq.StatusText  ' La solicitud falló, muestra el código de estado y la descripción
    frmWpcMain.lbl_WPC.BackColor = Rojo                      ' Coloca el Label de Informacion del WPC en Rojo lo que significa
    AgregarLog 3104, "TOLER.EXCED :" & uuid, MainEntorno
End If                                                       ' que el servidor no recibio el mensaje
Set httpReq = Nothing
End Sub
Private Sub Enviar_Post_BorradoTicket(uuid As String, createdAt As Date)

Dim httpReq As Object
Dim response As String
Dim fechaHoraString As String
Dim Id_Playa As String

Id_Playa = Form_Config.Txt_IdPlaya
Id_Playa = Format(Id_Playa, "000000")

Set httpReq = CreateObject("WinHttp.WinHttpRequest.5.1")

Dim url As String
Dim jsonData As String

url = Form_Config.Txt_Borrado_Ticket
    
jsonData = "{" & vbCrLf & _
        """cod_ticket"": """ & uuid & """," & vbCrLf & _
        """id_parking"": """ & Id_Playa & """," & vbCrLf & _
        """fecha"": """ & createdAt & """," & vbCrLf & _
        """codStatus"": ""W7""" & vbCrLf & _
    "}"
    

httpReq.Open "POST", url, False
httpReq.SetRequestHeader "Content-Type", "application/json"   ' Indicamos que el JSON va en el body NO en el encabezado
httpReq.SetTimeouts 30000, 30000, 30000, 30000                    ' Fijamos tiempo espera maxima para resolver,conectar,enviar,recibir en ms.

httpReq.Send jsonData ' Enviamos el JSON

'MsgBox jsonData

If httpReq.Status = 200 Then                                  ' La solicitud fue exitosa, procesa la respuesta
    ' MsgBox "Respuesta del servidor: " & httpReq.ResponseText
    frmWpcMain.lbl_Supervisor.BackColor = Verde               ' Coloca el Label de Informacion del WPC en Verde lo que significa
Else                                                          ' que el Sevidor de Parking YA recibio el mensaje..!!!
    ' MsgBox "Error: " & httpReq.Status & " - " & httpReq.StatusText  ' La solicitud falló, muestra el código de estado y la descripción
    frmWpcMain.lbl_Supervisor.BackColor = Rojo                ' Coloca el Label de Informacion del WPC en Rojo lo que significa
    AgregarLog 3105, "BORRADO:" & uuid, MainEntorno
End If                                                        ' que el servidor no recibio el mensaje
Set httpReq = Nothing
End Sub

Private Sub Enviar_Cierre_Caja(cadena As String, createdAt As Date)

Dim sql As String
Dim command As ADODB.command
Dim httpReq As Object
Dim response As String
Dim fechaHoraString As String
Dim Id_Playa As String

Id_Playa = Form_Config.Txt_IdPlaya
Id_Playa = Format(Id_Playa, "000000")

Set httpReq = CreateObject("WinHttp.WinHttpRequest.5.1")

Dim url As String
Dim jsonData As String
Dim partes() As String

' Usamos la función Split para dividir la cadena en partes usando "-" como delimitador
partes = Split(cadena, "=")

' Ahora cada elemento del array partes contiene un valor separado de la cadena original
Dim codigo As String
Dim nroCaja As String
Dim NombreUsuario As String
Dim ApellidoUsuario As String
Dim fechaApertura As String
Dim fechaCierre As String
Dim tot As String
Dim arq As String
Dim dif As String
Dim sumaMontoOemspot As String
Dim sumaMontoCliente As String
Dim sumaMontoEfectivo As String
Dim contMontoOemspot As String
Dim contMontoEfectivo As String
Dim puntoVenta As String
Dim operador As String

' Asignamos los valores a las variables individuales
nroCaja = Mid$(partes(0), 1, 12)
codigo = Mid$(partes(0), 13, 14)
NombreUsuario = partes(1)
ApellidoUsuario = partes(2)
fechaApertura = partes(3)
fechaCierre = partes(4)
tot = partes(5)
arq = partes(6)
dif = partes(7)
sumaMontoOemspot = partes(8)
sumaMontoCliente = partes(9)
sumaMontoEfectivo = partes(10)
contMontoOemspot = partes(11)
contMontoEfectivo = partes(12)
puntoVenta = partes(13)


url = Form_Config.Txt_Cierre_Caja
    
jsonData = "{" & vbCrLf & _
    """id_parking"": """ & Id_Playa & """," & vbCrLf & _
    """fecha"": """ & createdAt & """," & vbCrLf & _
    """codStatus"": ""W8""," & vbCrLf & _
    """cajaNumero"": """ & nroCaja & """," & vbCrLf & _
    """nombre"": """ & NombreUsuario & """," & vbCrLf & _
    """apellido"": """ & ApellidoUsuario & """," & vbCrLf & _
    """fechaApertura"": """ & fechaApertura & """," & vbCrLf & _
    """fechaCierre"": """ & fechaCierre & """," & vbCrLf & _
    """totalRecaudado"": """ & tot & """," & vbCrLf & _
    """arqueoCaja"": """ & arq & """," & vbCrLf & _
    """diferencia"": """ & dif & """," & vbCrLf & _
    """montoParkingYA"": """ & sumaMontoOemspot & """," & vbCrLf & _
    """montoCliente"": """ & sumaMontoCliente & """," & vbCrLf & _
    """montoefectivo"": """ & sumaMontoEfectivo & """," & vbCrLf & _
    """contMontoElectronico"": """ & contMontoOemspot & """," & vbCrLf & _
    """contMontoEfectivo"": """ & contMontoEfectivo & """," & vbCrLf & _
    """puntoVenta"": """ & puntoVenta & """" & vbCrLf & _
"}"
  
' MsgBox jsonData
  
httpReq.Open "POST", url, False
httpReq.SetRequestHeader "Content-Type", "application/json"   ' Indicamos que el JSON va en el body NO en el encabezado
httpReq.SetTimeouts 30000, 30000, 30000, 30000                    ' Fijamos tiempo espera maxima para resolver,conectar,enviar,recibir en ms.

httpReq.Send jsonData ' Enviamos el JSON

If httpReq.Status = 200 Then                                  ' La solicitud fue exitosa, procesa la respuesta
    ' MsgBox "Respuesta del servidor: " & httpReq.ResponseText
    frmWpcMain.lbl_Cajero.BackColor = Verde                   ' Coloca el Label de Informacion del WPC en Verde lo que significa
 
    If conexionActiva.State = adStateOpen Then
      sql = "UPDATE cierrecaja SET estado = 'Enviado' WHERE id_cierre = " & nroCaja
      Set command = New ADODB.command
      command.ActiveConnection = conexionActiva
      command.CommandText = sql
      command.Execute
    End If
Else                                                          ' que el Sevidor de Parking YA recibio el mensaje..!!!
    ' MsgBox "Error: " & httpReq.Status & " - " & httpReq.StatusText  ' La solicitud falló, muestra el código de estado y la descripción
    frmWpcMain.lbl_Cajero.BackColor = Rojo                    ' Coloca el Label de Informacion del WPC en Rojo lo que significa
    AgregarLog 3100, "CIERRE CAJA : " & nroCaja, MainEntorno
End If                                                        ' que el servidor no recibio el mensaje
Set httpReq = Nothing
End Sub

Public Function GetPublicIP() As String
    Dim url As String
    Dim response As String

    url = "https://httpbin.org/ip"  ' URL del servicio que devuelve la IP pública
    
    On Error GoTo ErrorHandler

    ' Realizar la solicitud HTTP y obtener la respuesta
    With CreateObject("MSXML2.ServerXMLHTTP")
        .Open "GET", url, False
        .Send
        
        ' Verificar si la solicitud fue exitosa y la respuesta no está vacía
        If .Status = 200 And .ResponseText <> "" Then
            response = .ResponseText
            ' Extraer la IP pública del JSON de respuesta
            GetPublicIP = ExtraerDireccionIP(response)
        Else
            ' Si la solicitud no fue exitosa o la respuesta está vacía, lanzar un error
            Err.Raise vbObjectError + 1, "GetPublicIP", "Fallo en la solicitud HTTP"
        End If
    End With
    Exit Function

ErrorHandler:    ' En caso de error, asignar un mensaje indicando que falló la conexión a Internet
    GetPublicIP = " AUSENCIA DE INTERNET"
    frmWpcMain.lbl_IpPublica.BackColor = Rojo
    Resume Next
End Function

Private Function ExtraerDireccionIP(ByVal response As String) As String
    Dim startPos As Integer
    Dim endPos As Integer
    Dim ip As String

    ' Buscar la posición del valor de "origin" en la cadena JSON
    startPos = InStr(response, """origin"": """) + Len("""origin"": """)
    endPos = InStr(startPos, response, """")

    ' Extraer la IP de la respuesta
    If startPos > 0 And endPos > 0 Then
        ip = Mid(response, startPos, endPos - startPos)
    Else
        ip = " AUSENCIA DE INTERNET"
        frmWpcMain.lbl_IpPublica.BackColor = Rojo
    End If

    ExtraerDireccionIP = ip
End Function
Public Function IsArrayInitialized(arr() As Variant) As Boolean
    On Error Resume Next
    IsArrayInitialized = IsArray(arr) And Not IsError(LBound(arr))
    On Error GoTo 0
End Function

Public Sub AgregarLog(ByVal Id_Error_ As Long, _
                      ByVal Texto_ As String, _
                      ByVal dEntorno As Entorno)

    Dim ADOCommand As ADODB.command
    Dim nId_Log As Long
    Dim Fecha_Actual As String ' Usaremos una cadena para formatear la fecha correctamente
    Dim NError As Integer
    Dim Intentos As Integer

Grabar:
    On Error GoTo ERRORES
    
    If conexionActiva.State = adStateOpen Then              ' Esta activa la conexion con la Base de datos ??
       
    
    Set ADOCommand = New ADODB.command
    ADOCommand.ActiveConnection = conexionActiva
    
    nId_Log = NewId_Evento()
    Fecha_Actual = Format(Now, "yyyy-MM-dd HH:mm:ss") ' Formato de fecha para MySQL

 '   NError = Cls_Error.NivelError(Id_Error_) ' Obtener el nivel de error buscando el Id_Error
    NError = 4
    ' Construir la consulta SQL para MySQL
    ADOCommand.CommandText = "INSERT INTO Sistema (Id_Evento, Id_Error, Fecha, Id_Empleado, Texto, Id_Nivel_Error, Id_Playa, Id_Isleta, Id_Dispositivo) " & _
                             "VALUES (" & nId_Log & ", " & Id_Error_ & ", '" & Fecha_Actual & "', " & dEntorno.UsuarioDefault & ", '" & Mid(Texto_, 1, 30) & "', " & _
                             NError & ", " & dEntorno.Id_Playa & ", " & dEntorno.Id_Isleta & ", " & dEntorno.Id_Dispositivo & ")"

    ADOCommand.Execute

    ' Liberar recursos
    Set ADOCommand = Nothing

End If
    Exit Sub

ERRORES:
    Intentos = Intentos + 1
    If Intentos < 11 Then
        Sleep 10 ' Función Sleep en VB6
        Resume Grabar
    Else
        MsgBox "Error al intentar agregar el registro al log."
    End If

End Sub


Public Function NewId_Evento() As Long
    Dim myTime As SYSTEMTIME
    Dim fecha As Date
    
    ' Obtener la fecha y la hora del sistema
    GetSystemTime myTime
    fecha = Date
    
    ' Calcular el nuevo ID de evento
    NewId_Evento = CLng(DateDiff("d", "01/01/" & Year(fecha), fecha)) * 1000000 + _
                   CLng(myTime.wHour) * 10000 + _
                   CLng(myTime.wMinute) * 100 + _
                   CLng(myTime.wSecond) + _
                   Int(myTime.wMilliseconds / 10)
End Function

