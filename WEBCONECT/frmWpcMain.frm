VERSION 5.00
Object = "{248DD890-BB45-11CF-9ABC-0080C7E7B78D}#1.0#0"; "MSWINSCK.OCX"
Object = "{831FDD16-0C5C-11D2-A9FC-0000F8754DA1}#2.2#0"; "MSCOMCTL.OCX"
Begin VB.Form frmWpcMain 
   BackColor       =   &H00FFFFFF&
   BorderStyle     =   1  'Fixed Single
   ClientHeight    =   7590
   ClientLeft      =   2235
   ClientTop       =   2235
   ClientWidth     =   4665
   FontTransparent =   0   'False
   Icon            =   "frmWpcMain.frx":0000
   KeyPreview      =   -1  'True
   LinkTopic       =   "Form1"
   MaxButton       =   0   'False
   ScaleHeight     =   7590
   ScaleWidth      =   4665
   Begin MSWinsockLib.Winsock WinsockEjecutivo 
      Index           =   0
      Left            =   3840
      Top             =   480
      _ExtentX        =   741
      _ExtentY        =   741
      _Version        =   393216
   End
   Begin MSWinsockLib.Winsock WinsockSrvRecep 
      Left            =   480
      Top             =   480
      _ExtentX        =   741
      _ExtentY        =   741
      _Version        =   393216
   End
   Begin MSComctlLib.ProgressBar ProgressBarr 
      Height          =   255
      Left            =   2160
      TabIndex        =   19
      Top             =   2880
      Width           =   1335
      _ExtentX        =   2355
      _ExtentY        =   450
      _Version        =   393216
      Appearance      =   1
   End
   Begin VB.Frame FrameServidor 
      Caption         =   "Comunicacion con el Supervisor"
      Height          =   855
      Left            =   120
      TabIndex        =   16
      Top             =   5640
      Width           =   4455
      Begin VB.Label lbl_Supervisor 
         Height          =   375
         Left            =   120
         TabIndex        =   17
         Top             =   360
         Width           =   4095
      End
   End
   Begin VB.Timer Timer_Sincronismo 
      Interval        =   60000
      Left            =   1080
      Top             =   480
   End
   Begin VB.Frame Frame_SrvParkingYA 
      Caption         =   "Comunicacion con Servidor Parking YA"
      Height          =   855
      Left            =   120
      TabIndex        =   5
      Top             =   6600
      Width           =   4455
      Begin VB.Label lbl_ParkYA 
         Height          =   375
         Left            =   120
         TabIndex        =   9
         Top             =   360
         Width           =   4095
      End
   End
   Begin VB.Frame FrameCajero 
      Caption         =   "Comunicacion con Cajero"
      Height          =   855
      Left            =   120
      TabIndex        =   4
      Top             =   4680
      Width           =   4455
      Begin VB.Label lbl_Cajero 
         Height          =   375
         Left            =   120
         TabIndex        =   8
         Top             =   360
         Width           =   4095
      End
   End
   Begin VB.Frame FrameWPC 
      Caption         =   "Comunicacion con WPC"
      Height          =   855
      Left            =   120
      TabIndex        =   3
      Top             =   3720
      Width           =   4455
      Begin VB.Label lbl_WPC 
         Height          =   375
         Left            =   120
         TabIndex        =   7
         Top             =   360
         Width           =   4095
      End
   End
   Begin VB.CommandButton btnConfig 
      BackColor       =   &H0000FFFF&
      Caption         =   "Configuracion"
      Height          =   375
      Left            =   1560
      Style           =   1  'Graphical
      TabIndex        =   2
      Top             =   3240
      Width           =   1215
   End
   Begin VB.CommandButton btnServer 
      BackColor       =   &H0080C0FF&
      Caption         =   "Servidor"
      Height          =   375
      Left            =   240
      Style           =   1  'Graphical
      TabIndex        =   1
      Top             =   3240
      Width           =   975
   End
   Begin VB.CommandButton Btn_Cliente 
      BackColor       =   &H00FF8080&
      Caption         =   "Cliente"
      Height          =   375
      Left            =   3240
      MaskColor       =   &H00FF8080&
      Style           =   1  'Graphical
      TabIndex        =   0
      Top             =   3240
      Width           =   1095
   End
   Begin VB.Timer Timer 
      Enabled         =   0   'False
      Interval        =   1000
      Left            =   3120
      Top             =   480
   End
   Begin VB.Label lbl_Wires 
      Height          =   255
      Left            =   3600
      TabIndex        =   20
      Top             =   2880
      Width           =   855
   End
   Begin VB.Label Label6 
      Caption         =   "Conexiones Multiples :"
      Height          =   255
      Index           =   1
      Left            =   240
      TabIndex        =   18
      Top             =   2880
      Width           =   1695
   End
   Begin VB.Label lbl_Sincronismo 
      Height          =   255
      Left            =   2160
      TabIndex        =   15
      Top             =   2520
      Width           =   2175
   End
   Begin VB.Label Label6 
      Caption         =   "Ultimo Sincronismo :"
      Height          =   255
      Index           =   0
      Left            =   240
      TabIndex        =   14
      Top             =   2520
      Width           =   1695
   End
   Begin VB.Label lbl_IpLAN 
      Height          =   255
      Left            =   2160
      TabIndex        =   13
      Top             =   2160
      Width           =   2175
   End
   Begin VB.Label Label4 
      Caption         =   "Direccion Ip LAN  :"
      Height          =   255
      Left            =   240
      TabIndex        =   12
      Top             =   2160
      Width           =   1695
   End
   Begin VB.Label lbl_IpPublica 
      Height          =   255
      Left            =   2160
      TabIndex        =   11
      Top             =   1800
      Width           =   2175
   End
   Begin VB.Label Label3 
      Caption         =   "Direccion Ip Publica  :"
      Height          =   255
      Left            =   240
      TabIndex        =   10
      Top             =   1800
      Width           =   1695
   End
   Begin VB.Label Label2 
      Alignment       =   2  'Center
      Caption         =   "OEMSPOT WEBCONECT         03-10-2024"
      Height          =   255
      Left            =   480
      TabIndex        =   6
      Top             =   1440
      Width           =   3495
   End
   Begin VB.Image Image1 
      Height          =   1230
      Left            =   120
      Picture         =   "frmWpcMain.frx":030A
      Top             =   0
      Width           =   4440
   End
   Begin VB.Menu mnuDisplay 
      Caption         =   "&Comunicacíon"
      Visible         =   0   'False
   End
   Begin VB.Menu mnuNada0 
      Caption         =   "|"
      Enabled         =   0   'False
      Visible         =   0   'False
   End
   Begin VB.Menu mnuResetEnt 
      Caption         =   "Reset Poste de &Entrada"
      Visible         =   0   'False
   End
   Begin VB.Menu mnuNada1 
      Caption         =   "|"
      Enabled         =   0   'False
      Visible         =   0   'False
   End
   Begin VB.Menu mnuResetSal 
      Caption         =   "Reset Poste de &Salida"
      Visible         =   0   'False
   End
End
Attribute VB_Name = "frmWpcMain"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
' Implementaremos un servidor que pueda aceptar un número indefinido de conexiones entrantes.
' Creare un arreglo de controles winsock, en el Servidor mono-conexión,dejámos un socket
' a la escucha de conexiones entrantes, y al recibir una petición de conexión (evento "ConnectionRequest")
' le decíamos al Winsock que aceptara esa identidad y este a su vez establece una conexión con el cliente.
' Para el caso del servidor multi-conexión necesitamos dejar un socket escuchando permanentemente conexiones
' entrantes, este nunca se debe cerrar , por ende no podemos atender otra conexion , entonces lo que vamos
' a realizar es lo siguiente, un socket permanentemente se encontrara escuchando peticiones de conexion como
' si fuera un "RECEPCIONISTA" , mediante el arreglo de controles winsock iremos cargandolo dinamicamente
' a medida que aumenta la cantidad e conexiones simultaneas y cada uno de ellos aceptara la identidad de
' cada nueva conexion como si fueran "EJECUTIVOS"
' Para poder trabajar con varias conexiones a la vez necesitamos varios sockets disponibles, ya que cada uno solo
' puede trabajar con una sola conexión, y como en principio no conocemos la cantidad de Winsocks que necesitaremos
' crearemos un arreglo de controles Winsock y los cargaremos dinamicamente.
'Para crear el arrego, agrego un nuevo Winsock al formulario , luego copio el control y lo pego en el formulario,
'entonces cuando pregunte si deseo crear el arrego, le digo que "SI"...luego borramos el nuevo Winsock creado
'dado que que no lo usaremos dado que los crearemos dinamicamente y para ello solo necesito que exista el arreglo
'de controles winsock indice(n).


Private Const ASCII_STX = 2  ' Start of text
Private Const ASCII_ETX = 3  ' End of text
Private Const ASCII_EOF = 3  ' End of file

Private Declare Function SetSystemTime Lib "kernel32" (lpSystemTime As SYSTEMTIME) As Long

Private Type SYSTEMTIME
    wYear As Integer
    wMonth As Integer
    wDayOfWeek As Integer
    wDay As Integer
    wHour As Integer
    wMinute As Integer
    wSecond As Integer
    wMilliseconds As Integer
End Type

Option Explicit
Dim ArrayWinsockEjecutivo() As Winsock

Public informe As Integer


Private Sub Btn_Cliente_Click()
    'Dim ip As String
    'Dim num_Socket As Integer
    'Dim num_Elementos As Integer
    'Dim i As Integer
      
      'If formClientVisible Then
        ' Si el formulario está visible, lo ocultamos
      '  Form_Cliente.Hide
      '  formClientVisible = False
                                                                         ' Carga la cantidad de elementos del arreglo en este momento
 
      '  For i = 0 To Cantidad_Conexiones                                 ' Verificca si existe alguno existente en el arreglo que
      '    If ArrayWinsockEjecutivo(i).State <> sckClosed Then            ' este usado(Conectado..)
      '       num_Socket = i
      '       ip = ArrayWinsockEjecutivo(num_Socket).RemoteHostIP
      '       ArrayWinsockEjecutivo(num_Socket).Close                      ' cerramos la conexion de los sockets "Ejecutivos"
      '       Form_Servidor.TerminalServidor.SelStart = Len(Form_Servidor.TerminalServidor.Text)  ' Presenta el Texto de "Conexion cerrada" del cliente
      '       Form_Servidor.TerminalServidor.Text = Form_Servidor.TerminalServidor.Text & "Sock:" & num_Socket & "*** Conexion Cerrada IP: " & ip & vbCrLf
      '       Form_Servidor.TerminalServidor.SelStart = Len(Form_Servidor.TerminalServidor.Text)
      '    End If
      '  Next
 
      '  ip = WinsockSrvRecep.LocalIP
      '  WinsockSrvRecep.Close                                   ' Finalmente cerramos la conexion del socket "Recepcionista"
      '  Form_Servidor.TerminalServidor.SelStart = Len(Form_Servidor.TerminalServidor.Text)  ' Presenta el Texto de "Conexion cerrada"
      '  Form_Servidor.TerminalServidor.Text = Form_Servidor.TerminalServidor.Text & "Sock: Server Recepcionista *** Conexion Cerrada IP: " & ip & vbCrLf ' del cliente
      '  Form_Servidor.TerminalServidor.SelStart = Len(Form_Servidor.TerminalServidor.Text)
      '  Form_Servidor.TerminalServidor.Text = ""
    
    
   ' Else
        ' Si el formulario está oculto, lo mostramos
    '    Form_Cliente.Show
    '    formClientVisible = True
    'End If
 
End Sub

Private Sub btnConfig_Click()
  Form_Login.Show
End Sub

Private Sub btnServer_Click()
   
    If formServerVisible Then
        ' Si el formulario está visible, lo ocultamos
        Form_Servidor.Hide
        formServerVisible = False
        Form_Servidor.Btn_EscucharCliente_Click
       ' Form_Servidor.btn_CloseServer_Click     ' cierra todos los puertos que esten abiertos
    Else
        ' Si el formulario está oculto, lo mostramos
        Form_Servidor.lbl_SrvPort = Form_Config.Txt_Port_Http
        Form_Servidor.Show
        formServerVisible = True
    End If
 
End Sub

Private Sub mnuClose_Click()
  Unload Me
End Sub


'Private Sub Form_Load()
'    Dim numWinsocks As Integer
'    numWinsocks = 10 ' Cantidad deseada de objetos Winsock'
'
'    ReDim ArrayWinsockEjecutivo(0 To numWinsocks)
'
'   If Not IsArray(ArrayWinsockEjecutivo) Then
'        ' Error: El array de controles Winsock no está inicializado
'        MsgBox "Error: El array de controles Winsock no está inicializado 'FormLoad'.", vbCritical
'        Exit Sub
'    End If
'
'    Dim i As Integer
'    For i = 0 To numWinsocks
'        Set ArrayWinsockEjecutivo(i) = frmWpcMain.WinsockEjecutivo
'        ' Configura propiedades adicionales según sea necesario
'        ArrayWinsockEjecutivo(i).LocalPort = 0 ' Por ejemplo, establece el puerto local
'    Next i
'End Sub

Private Sub Form_Load()
    Dim numWinsocks As Integer
    numWinsocks = Cantidad_Conexiones                 ' Cantidad deseada de objetos Winsock

    ReDim ArrayWinsockEjecutivo(0 To numWinsocks - 1)

    If Not IsArray(ArrayWinsockEjecutivo) Then
        ' Error: El array de controles Winsock no está inicializado
        MsgBox "Error: El array de controles Winsock no está inicializado 'FormLoad'.", vbCritical
        Exit Sub
    End If

    Dim i As Integer
    For i = 0 To numWinsocks - 1
        If i = 0 Then
            ' El control Winsock(0) ya está en el formulario
            Set ArrayWinsockEjecutivo(i) = WinsockEjecutivo(i)
        Else
            ' Crea nuevos controles Winsock como parte del array
            Load WinsockEjecutivo(i)
            Set ArrayWinsockEjecutivo(i) = WinsockEjecutivo(i)
        End If
        ' Configura propiedades adicionales según sea necesario
        ArrayWinsockEjecutivo(i).LocalPort = 0 ' Por ejemplo, establece el puerto local a todos
    Next i                                     ' para que asuman un puerto automaticamente cada uno
End Sub

Private Sub Form_Unload(Cancel As Integer)
    Form_Servidor.btn_CloseServer_Click     ' cierra todos los puertos que esten abiertos
    Unload Form_Cliente
    Unload Form_Servidor
    DesconectarMySQL
    End                 ' FIN DEL PROGRAMA !!!!!!!!!!
End Sub

Private Sub Form_Terminate()
 If formClientVisible Then
    ' Si el formulario está visible, lo ocultamos
    Unload Form_Cliente
    Form_Servidor.btn_CloseServer_Click     ' cierra todos los puertos que esten abiertos
 End If

End Sub


Private Sub Timer_Sincronismo_Timer()
                                                 ' Aqui ingresa cada 1 minuto
tmr_5min = tmr_5min + 1
If tmr_5min = TIME_SINCRONISMO Then
  Timer_Sincronismo.Enabled = False
End If
End Sub

Private Sub Timer_Timer()                        ' Aqui ingresa cada 1 seg...
  
  Dim DirectorioActual As String
  
  Call CheckDB                                   ' Chequea la Base de Datos cada 1 seg...
  
  If Not ShowDisplayWpc = 99 Then
    If ShowDisplayWpc = 0 Then
      frmWpcMain.lbl_WPC.Caption = " "           ' Presenta Comunicacion con el WPC o Borra todo si no hay Informacion
      frmWpcMain.lbl_WPC.BackColor = &H8000000F  ' Cuando Borra reestablece el color transparente
    Else
      ShowDisplayWpc = ShowDisplayWpc - 1
    End If
  End If
  If Not ShowDisplayCajero = 99 Then
    If ShowDisplayCajero = 0 Then
      frmWpcMain.lbl_Cajero.Caption = " "           ' Presenta Comunicacion con el Cajero o Borra todo si no hay Informacion
      frmWpcMain.lbl_Cajero.BackColor = &H8000000F  ' Cuando Borra reestablece el color transparente
    Else
      ShowDisplayCajero = ShowDisplayCajero - 1
    End If
  End If
  If Not ShowDisplaySupervisor = 99 Then
    If ShowDisplaySupervisor = 0 Then
      frmWpcMain.lbl_Supervisor.Caption = " "           ' Presenta Comunicacion con el Supervisor o Borra todo si no hay Informacion
      frmWpcMain.lbl_Supervisor.BackColor = &H8000000F   ' Cuando Borra reestablece el color transparente
    Else
      ShowDisplaySupervisor = ShowDisplaySupervisor - 1
    End If
  End If
  If Not ShowDisplayParkYA = 99 Then
    If ShowDisplayParkYA = 0 Then
      frmWpcMain.lbl_ParkYA.Caption = " "           ' Presenta Comunicacion con el "Servidor Parking YA" o Borra todo si no hay Informacion
      frmWpcMain.lbl_ParkYA.BackColor = &H8000000F  ' Cuando Borra reestablece el color transparente
    Else
      ShowDisplayParkYA = ShowDisplayParkYA - 1
    End If
  End If
  
  IpPublica = GetPublicIP()                          ' carga cada 1 seg la Ip Publica

  frmWpcMain.lbl_IpPublica.Caption = IpPublica
  If IpPublica = " AUSENCIA DE INTERNET" Then
     frmWpcMain.lbl_IpPublica.BackColor = Rojo
  Else
     frmWpcMain.lbl_IpPublica.BackColor = &H8000000F
  End If
  If Not (IpPublica = IpPublica_Almacenada) Then     ' si cambia el valor lo informa
    IpPublica_Almacenada = IpPublica                 ' al servidor por un POST ALIVE
    Call Enviar_Post_Alive
    cont_Alive = TIME_ALIVE
  End If
  
  If cont_Alive = 0 Then                             ' cada 5 seg envia un POST ALIVE
    frmWpcMain.lbl_ParkYA.Caption = "ENVIO DE STATUS ALIVE AL SERVIDOR........"
    ShowDisplayParkYA = 1
    frmWpcMain.lbl_ParkYA.BackColor = Verde
    
    Call Enviar_Post_Alive                           ' para informar la IP PUBLICA al Servidor
    cont_Alive = TIME_ALIVE                          ' para poder recibir consultas u ordenes
  Else                                               ' del servidor....
    cont_Alive = cont_Alive - 1
  End If
  
  IpLAN = frmWpcMain.WinsockSrvRecep.LocalIP
  frmWpcMain.lbl_IpLAN.Caption = IpLAN
  
  
  If (tmr_OffLine > TIME_OFFLINE) Then
     DirectorioActual = App.Path & "\OffLine.jpg" ' No.... Entonces Carga el Directorio Actual
     frmWpcMain.Image1.Picture = LoadPicture(DirectorioActual)         ' Activa Imagen de Oemspot
  Else
     DirectorioActual = App.Path & "\logo HD webconect.jpg" ' No.... Entonces Carga el Directorio Actual
     frmWpcMain.Image1.Picture = LoadPicture(DirectorioActual)         ' Activa Imagen de Oemspot
     tmr_OffLine = tmr_OffLine + 1
  End If
  
  
End Sub





Public Function ExisteClaveJson(json As String, clave As String) As Boolean
    Dim inicio As Integer
    
    ' Buscar la clave en el JSON
    inicio = InStr(json, """" & clave & """") ' Busca la clave rodeada de comillas
    If inicio > 0 Then
        ' La clave está presente en el JSON
        ExisteClaveJson = True
    Else
        ' La clave no está presente en el JSON
        ExisteClaveJson = False
    End If
End Function

Private Function ExtraerJSON(solicitudCompleta As String) As String
    ' Aquí implementa la lógica para extraer el JSON del cuerpo de la solicitud
    ' Puedes utilizar técnicas de procesamiento de cadenas o bibliotecas JSON según sea necesario
    ' En este ejemplo sencillo, asumimos que el JSON comienza después de la primera línea en blanco
    Dim inicioJSON As Integer
    inicioJSON = InStr(solicitudCompleta, vbCrLf & vbCrLf)
    
    If inicioJSON > 0 Then
        ExtraerJSON = Mid$(solicitudCompleta, inicioJSON + 4) ' Saltamos las dos líneas en blanco
    Else
        ExtraerJSON = ""
    End If
End Function



Private Sub WinsockEjecutivo_Close(Index As Integer)

Dim ip As String

 ip = ArrayWinsockEjecutivo(Index).RemoteHostIP
 ArrayWinsockEjecutivo(Index).Close
 cantidad_Peticiones = cantidad_Peticiones - 1
 frmWpcMain.lbl_Wires.Caption = Str(cantidad_Peticiones)
 
 Form_Servidor.TerminalServidor.SelStart = Len(Form_Servidor.TerminalServidor.Text)                    ' Conexion cerrada por el Cliente...
 Form_Servidor.TerminalServidor.Text = Form_Servidor.TerminalServidor.Text & "Sock:" & Index & "*** Conexion Cerrada por el Cliente IP: " & ip & vbCrLf ' del cliente
 Form_Servidor.TerminalServidor.SelStart = Len(Form_Servidor.TerminalServidor.Text)
  

End Sub

Private Sub WinsockEjecutivo_DataArrival(Index As Integer, ByVal bytesTotal As Long)
Dim Buffer As String

On Error GoTo salir

 Dim responseData As String
 Dim cod_Ticket As String
 Dim comando As String
 Dim Importe As String
 Dim sql As String
 Dim Campo_id As Long
 Dim tiempoMaximoEspera As Integer
 Dim tiempoInicio As Single
 Dim esperaCompleta As Boolean
 Dim CampoRecepcion As String
 Dim inicioPausa As Single
 Dim Tolerancia As String
 Dim command As ADODB.command
 Dim codTicket As String
 Dim codStatus As String
 Dim fechaserver As String
 Dim DirectorioActual As String
            
 ArrayWinsockEjecutivo(Index).GetData Buffer                     ' Carga en "buffer" el texto ingresado
' TerminalServidor.SelStart = Len(TerminalServidor.Text)     ' Desplazamos el ScrollBarr al final del contenido
' TerminalServidor.Text = TerminalServidor.Text & "Sock:" & Index & " " & "Cliente: >" & Buffer & vbCrLf   ' Presentamos el Dato Recibido
 DatoRecibidoDelModulo = Buffer
'MsgBox (DatoRecibidoDelModulo)

 ' DatoRecibidoDelModulo = Mid$(Buffer, 2, 2) + Mid$(Buffer, 10, 12)    'Extraemos el "ADDR del dispositivo" y el codigo de 12 digitos recibido
 
 ' Aqui analizamos si recibimos un JSON del Server de PARKING YA o Si Recibimos un STRING por un mensaje WINSOCK
    
 If InStr(DatoRecibidoDelModulo, vbCrLf & vbCrLf) > 0 Then 'Esto generalmente se utiliza para identificar el final
 Dim jsonBody As String                                  'de una solicitud HTTP en el formato "cabeza de solicitud"
 jsonBody = ExtraerJSON(DatoRecibidoDelModulo)           'seguida por dos líneas en blanco antes del cuerpo de la solicitud.
 
 Dim inicioCodStatus As Integer                          ' Cargamos el contenido de la clave "codStatus"
 Dim finCodStatus As Integer
 inicioCodStatus = InStr(jsonBody, """codStatus"": """) + Len("""codStatus"": """)
 finCodStatus = InStr(inicioCodStatus, jsonBody, """")
 codStatus = Mid$(jsonBody, inicioCodStatus, finCodStatus - inicioCodStatus)   ' Aqui "codStatus" .....
 
 If (ExisteClaveJson(jsonBody, "cod_ticket")) Then
   Dim inicioCodTicket As Integer
   Dim finCodTicket As Integer
   inicioCodTicket = InStr(jsonBody, """cod_ticket"": """) + Len("""cod_ticket"": """)
   finCodTicket = InStr(inicioCodTicket, jsonBody, """")
   codTicket = Mid$(jsonBody, inicioCodTicket, finCodTicket - inicioCodTicket)   ' Aqui "codTicket".....
 End If
 
 If (ExisteClaveJson(jsonBody, "fecha_server")) Then
   Dim inicioCodfecha As Integer
   Dim finCodfecha As Integer
   inicioCodfecha = InStr(jsonBody, """fecha_server"": """) + Len("""fecha_server"": """)
   finCodfecha = InStr(inicioCodfecha, jsonBody, """")
   fechaserver = Mid$(jsonBody, inicioCodfecha, finCodfecha - inicioCodfecha)   ' Aqui "fechaserver".....
 End If
  
 
   
       Select Case codStatus                                  ' Aqui Analizamos el Comando Recibido....
         Case "W0"
           frmWpcMain.lbl_Cajero.Caption = "SOLICITUD DE LIQUIDACION  !!!..." ' Informa que recibe "Solicitud de Liquidacion"
           frmWpcMain.lbl_Cajero.BackColor = Verde                            ' Color Verde
           ShowDisplayCajero = 2
          
           If conexionActiva.State = adStateOpen Then                         ' Esta activa la conexion con la Base de datos ??
             Set command = New ADODB.command
                       
             command.ActiveConnection = conexionActiva
             sql = "INSERT INTO comunicacion (Transmision, Recepcion, id, FieldName) VALUES ('" & codTicket & codStatus & "','NULL' ,NULL , '0')"
             command.CommandText = sql
             command.Execute
                                                                                       'Aqui obtenmos el valor del campo id que es
             Campo_id = conexionActiva.Execute("SELECT @@IDENTITY").Fields(0).Value    ' el que se autoincrementa al insertar el registro
                   
             ' Ahora hemos insertado en la base la solicitud de Liquidacion y quedamos a la espera
             ' que el Cajero actualice el valor de la liquidacion en el campo "Recepcion"
             ' para poder responderle al Servidor de PARKING YA que sigue a la espera de respuesta
                   
             ' Esperar hasta que el campo "Recepcion" no sea NULL o tiempo de espera agotado
                      
             tiempoMaximoEspera = 10        ' Número x 250ms máximo que estamos dispuesto a esperar
             tiempoInicio = Timer           ' Guardar el tiempo de inicio
             esperaCompleta = False

      
             Do While Timer - tiempoInicio <= 10                   ' Esperar hasta que hayan pasado los segundos especificados
                CampoRecepcion = conexionActiva.Execute("SELECT Recepcion FROM comunicacion WHERE id = " & Campo_id).Fields(0).Value
                If CampoRecepcion <> "NULL" Then                  ' Verificar si el campo "Recepcion" ha sido modificado
                   esperaCompleta = True                          ' El campo "Recepcion" ha sido modificado, salir del bucle
                   Exit Do
                End If
                DoEvents ' Permitir que otros eventos se procesen durante la espera
             Loop
             
             
             command.ActiveConnection = conexionActiva           ' Borramos el registro en uso
             sql = "DELETE FROM comunicacion WHERE id = " & Campo_id
             command.CommandText = sql
             command.Execute
            
             cod_Ticket = Left(CampoRecepcion, 12)                      ' Extraigo los primeros 12 dígitos en cod_Ticket
             comando = Mid(CampoRecepcion, 13, 2)                       ' Extraigo los 2 siguientes dígitos en comando
             Importe = Mid(CampoRecepcion, 15)                          ' Extraigo todos los caracteres restantes en importe
             Importe = Format(Importe, "0.00")
             
             If esperaCompleta Then
               frmWpcMain.lbl_Cajero.Caption = "TCK :" & cod_Ticket & "      CMD:" & comando & "      $ :" & Importe
               frmWpcMain.lbl_Cajero.BackColor = Verde                  ' Informa que recibe "El importe solicitado"
               ShowDisplayCajero = 2                                    ' Color Verde
               
               If Importe = "Error:2 No Ingreso" Then
                 ' Respuesta al Servidor ParkingYA con el Importe informando que "No ingreso"
                  responseData = "HTTP/1.1 200 OK" & vbCrLf & _
                  "Content-Type: text/plain" & vbCrLf & _
                  vbCrLf & _
                  "{""error"": """ & Importe & """}"
                      
               Else
               ' Preparo el JSON de la respuesta al Servidor ParkingYA con el Importe
               responseData = "HTTP/1.1 200 OK" & vbCrLf & _
                  "Content-Type: text/plain" & vbCrLf & _
                  vbCrLf & _
                  "{""monto"": """ & Importe & """}"
               End If
               ArrayWinsockEjecutivo(Index).SendData responseData ' Enviamos la respuesta
             Else
               frmWpcMain.lbl_Cajero.Caption = "SUPERO EL TIEMPO MAXIMO DE ESPERA RESPUESTA DEL CAJERO !!!..."
               frmWpcMain.lbl_Cajero.BackColor = Rojo                                ' Informa que NO recibe "Respusta del Cajero"
               ShowDisplayCajero = 99
               Importe = "Error 3: Supero el tiempo de espera en la respuesta del cajero..."
               ' Preparo el JSON de la respuesta al Servidor ParkingYA con SIN RESPUESTA
               responseData = "HTTP/1.1 200 OK" & vbCrLf & _
                  "Content-Type: text/plain" & vbCrLf & _
                  vbCrLf & _
                  "{""error"": """ & Importe & """}"
               
               ArrayWinsockEjecutivo(Index).SendData responseData ' Enviamos la respuesta
             End If
             Set command = Nothing
           Else
            frmWpcMain.lbl_Cajero.Caption = "CONEXION A BASE DE DATOS INACTIVA !!!..."
            frmWpcMain.lbl_Cajero.BackColor = Rojo             ' Color Rojo
            ShowDisplayCajero = 99
           End If
        
        
        
         Case "W1"
           frmWpcMain.lbl_Cajero.Caption = "TICKET PAGO ELECTRONICAMENTE !!!..."    ' Informa que recibe "Informacion de Pago"
           frmWpcMain.lbl_Cajero.BackColor = Verde                            ' Color Verde
           ShowDisplayCajero = 2
                  
           If conexionActiva.State = adStateOpen Then               ' Esta activa la conexion con la Base de datos ??
             Set command = New ADODB.command
                       
             command.ActiveConnection = conexionActiva
             sql = "INSERT INTO comunicacion (Transmision, Recepcion, id, FieldName) VALUES ('" & codTicket & codStatus & "','NULL' ,NULL , '0')"
             command.CommandText = sql
             command.Execute
             
                                                           'Aqui obtenmos el valor del campo id que es
             Campo_id = conexionActiva.Execute("SELECT @@IDENTITY").Fields(0).Value    ' el que se autoincrementa al insertar el registro
                   
             ' Ahora hemos insertado en la base la "Informacion de Pago Electronico" y quedamos a la espera
             ' que el Cajero actualice  y retorne un "OK" en el campo "Recepcion"
             ' para poder responderle al Servidor de PARKING YA que sigue a la espera de respuesta
                   
             ' Esperar hasta que el campo "Recepcion" no sea NULL o tiempo de espera agotado
            
             tiempoMaximoEspera = 5         ' Número x 250ms máximo que estamos dispuesto a esperar
             tiempoInicio = Timer           ' Guardar el tiempo de inicio
             esperaCompleta = False

             Do While Timer - tiempoInicio <= 10                   ' Esperar hasta que hayan pasado los segundos especificados
                CampoRecepcion = conexionActiva.Execute("SELECT Recepcion FROM comunicacion WHERE id = " & Campo_id).Fields(0).Value
                If CampoRecepcion <> "NULL" Then                  ' Verificar si el campo "Recepcion" ha sido modificado
                   esperaCompleta = True                          ' El campo "Recepcion" ha sido modificado, salir del bucle
                   Exit Do
                End If
                DoEvents ' Permitir que otros eventos se procesen durante la espera
             Loop
             
             command.ActiveConnection = conexionActiva           ' Borramos el registro en uso
             sql = "DELETE FROM comunicacion WHERE id = " & Campo_id
             command.CommandText = sql
             command.Execute
            
             cod_Ticket = Left(CampoRecepcion, 12)                      ' Extraigo los primeros 12 dígitos en cod_Ticket
             comando = Mid(CampoRecepcion, 13, 2)                       ' Extraigo los 2 siguientes dígitos en comando
             Tolerancia = Mid(CampoRecepcion, 15)                       ' Extraigo todos los caracteres restantes en importe
             
             If esperaCompleta Then
               frmWpcMain.lbl_Cajero.Caption = "TCK :" & cod_Ticket & "      CMD:" & comando & " Tolerancia :" & Tolerancia
               frmWpcMain.lbl_Cajero.BackColor = Verde                  ' Informa que recibe "El importe solicitado"
               ShowDisplayCajero = 2                                    ' Color Verde
               
               ' Preparo el JSON de la respuesta al Servidor ParkingYA con el Importe
               responseData = "HTTP/1.1 200 OK" & vbCrLf & _
                  "Content-Type: text/plain" & vbCrLf & _
                  vbCrLf & _
                  "{""tolerancia"": """ & Tolerancia & """}"
               ArrayWinsockEjecutivo(Index).SendData responseData ' Enviamos la respuesta
             Else
               frmWpcMain.lbl_Cajero.Caption = "SUPERO EL TIEMPO MAXIMO DE ESPERA RESPUESTA DEL CAJERO !!!..."
               frmWpcMain.lbl_Cajero.BackColor = Rojo                                ' Informa que NO recibe "Respusta del Cajero"
               ShowDisplayCajero = 99
               Importe = " ERROR 1: SUPERO EL TIEMPO DE ESPERA DE RESPUESTA DEL CAJERO..."
               ' Preparo el JSON de la respuesta al Servidor ParkingYA con SIN RESPUESTA
               responseData = "HTTP/1.1 500 NO OK" & vbCrLf & _
                  "Content-Type: text/plain" & vbCrLf & _
                  vbCrLf & _
                  "{""tolerancia"": ""Error: 3 No responde el Cajero""}"
               ArrayWinsockEjecutivo(Index).SendData responseData ' Enviamos la respuesta
             End If
             Set command = Nothing
           Else
            frmWpcMain.lbl_Cajero.Caption = "CONEXION A BASE DE DATOS INACTIVA !!!..."
            frmWpcMain.lbl_Cajero.BackColor = Rojo             ' Color Rojo
            ShowDisplayCajero = 99
           End If
 
         
         Case "D0"
           frmWpcMain.lbl_ParkYA.Caption = "SINCRONIZACION DE FECHA HORA  !!!..."
           frmWpcMain.lbl_ParkYA.BackColor = Verde                         ' Informa que recibe "Solicitud de Liquidacion"
           ShowDisplayParkYA = 2                                           ' Color Verde
           frmWpcMain.lbl_Sincronismo.Caption = fechaserver
           
           responseData = "HTTP/1.1 200 OK" & vbCrLf & _
           "Content-Type: text/plain" & vbCrLf & _
           vbCrLf & _
           "{""Respuesta"": ""Fecha y Hora Sincronizada""}"                ' Preparo el JSON de la respuesta al Servidor ParkingYA
           ArrayWinsockEjecutivo(Index).SendData responseData                   ' Enviamos la respuesta
          
           Dim sysTime As SYSTEMTIME
           Dim FechaHoraServerDate As Date
           Dim fechaHoraSubstring As String
           fechaHoraSubstring = Mid$(fechaserver, 1, 19)                   ' Tomamos los primeros 19 caracteres
           FechaHoraServerDate = CDate(fechaHoraSubstring)                 ' Convertimos la cadena string a un objeto Date
           FechaHoraServerDate = DateAdd("h", 3, FechaHoraServerDate)      ' Ajusta la hora sumando 3 horas por el uso horario
           
           With sysTime
             .wYear = Year(FechaHoraServerDate)
             .wMonth = Month(FechaHoraServerDate)              ' Llena la estructura SYSTEMTIME con la fecha y hora actual
             .wDay = Day(FechaHoraServerDate)
             .wDayOfWeek = Weekday(FechaHoraServerDate) - 1
             .wHour = Hour(FechaHoraServerDate)
             .wMinute = Minute(FechaHoraServerDate)
             .wSecond = Second(FechaHoraServerDate)
             .wMilliseconds = 0
           End With
    
           ' Llama a la función SetSystemTime para fijar la fecha y hora del sistema
           If SetSystemTime(sysTime) <> 0 Then                        'llamamos SetSystemTime para fijar la fecha y hora del sistema
           '      MsgBox "¡La hora del sistema se ha actualizado correctamente!", vbInformation
           Else
           '    MsgBox "¡Error al intentar actualizar la hora del sistema!", vbExclamation
           End If

         Case "WA"
           tmr_OffLine = 0
           responseData = "HTTP/1.1 200 OK" & vbCrLf & _
           "Content-Type: text/plain" & vbCrLf & _
           vbCrLf & _
           "{""Respuesta"": ""Alive del Servidor Recibido""}"                ' Preparo el JSON de la respuesta al Servidor ParkingYA
           ArrayWinsockEjecutivo(Index).SendData responseData                   ' Enviamos la respuesta
         
         Case Else
       
       End Select

       
 
   End If
   Exit Sub
   
salir:
   frmWpcMain.lbl_ParkYA.Caption = "ERROR EL CLIENTE FINALIZO LA CONEXION....."
   ShowDisplayParkYA = 2
   frmWpcMain.lbl_ParkYA.BackColor = Amarillo
   'MsgBox "Error al ejecutar la consulta SQL: " & Err.Description, vbCritical
End Sub

Private Sub WinsockEjecutivo_Error(Index As Integer, ByVal Number As Integer, Description As String, ByVal Scode As Long, ByVal Source As String, ByVal HelpFile As String, ByVal HelpContext As Long, CancelDisplay As Boolean)
  
  'cerramos la conexion

  ArrayWinsockEjecutivo(Index).Close

  'mostramos informacion sobre el error

  frmWpcMain.lbl_ParkYA.Caption = "Error Socket Perdido..."
  ShowDisplayParkYA = 2
  frmWpcMain.lbl_ParkYA.BackColor = Rojo

  'MsgBox "Error numero " & Number & ": " & Description, vbCritical

End Sub

Private Sub WinsockEjecutivo_SendComplete(Index As Integer)
    If ArrayWinsockEjecutivo(Index).State <> sckClosed Then            ' este socket esta usado(Conectado..)
       ArrayWinsockEjecutivo(Index).Close                               ' cerramos la conexion que envio la respuesta solicitada
       frmWpcMain.ProgressBarr.Value = Index
       cantidad_Peticiones = cantidad_Peticiones - 1
       frmWpcMain.lbl_Wires.Caption = Str(cantidad_Peticiones)
 
     ' Btn_EscucharCliente_Click
    End If
End Sub

Private Sub WinsockSrvRecep_Close()
 
 WinsockSrvRecep.Close

End Sub

Private Sub WinsockSrvRecep_ConnectionRequest(ByVal requestID As Long)
    Dim ip As String
    Dim num_Socket As Integer
    Dim i As Integer

    On Error GoTo salir

    ' Obtener la IP del cliente que quiere acceder
    ip = WinsockSrvRecep.RemoteHostIP

    ' Asegurarse de que el array está inicializado
    If Not IsArray(ArrayWinsockEjecutivo) Then
        ' Error: El array de controles Winsock no está inicializado
        MsgBox "Error: El array de controles Winsock no está inicializado.", vbCritical
        Exit Sub
    End If

    ' Verificar si existe algún socket no usado en el array
    For i = 0 To UBound(ArrayWinsockEjecutivo)
        If ArrayWinsockEjecutivo(i).State = sckClosed Then
            num_Socket = i
            ArrayWinsockEjecutivo(num_Socket).Accept requestID ' El socket EJECUTIVO acepta la petición
            frmWpcMain.ProgressBarr.Value = num_Socket + 1
            cantidad_Peticiones = cantidad_Peticiones + 1
            frmWpcMain.lbl_Wires.Caption = Str(cantidad_Peticiones)
            Exit Sub
        End If
    Next

    ' Si no se encontró un socket libre en el array, mostrar un mensaje de error
    MsgBox "Error: No hay sockets disponibles para aceptar la conexión.", vbCritical
    Exit Sub

salir:
    If Err.Number <> 0 Then
        MsgBox "Error de Socket Servidor Numero " & Err.Number & ": " & Err.Description, vbCritical
        Err.Clear
    End If
End Sub



Private Sub WinsockSrvRecep_Error(ByVal Number As Integer, Description As String, ByVal Scode As Long, ByVal Source As String, ByVal HelpFile As String, ByVal HelpContext As Long, CancelDisplay As Boolean)
  WinsockSrvRecep.Close
  frmWpcMain.lbl_ParkYA.Caption = "Error Recepcion Socket Perdido..."
  ShowDisplayParkYA = 2
  frmWpcMain.lbl_ParkYA.BackColor = Rojo
  WinsockSrvRecep.LocalPort = Form_Servidor.lbl_SrvPort   'Asignamos el Puerto por donde escucha en Servidor
  WinsockSrvRecep.Listen
   ' MsgBox "Error de Conexion del Servidor Numero " & Number & ": " & Description, vbCritical
End Sub
