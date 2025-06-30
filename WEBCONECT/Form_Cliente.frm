VERSION 5.00
Object = "{248DD890-BB45-11CF-9ABC-0080C7E7B78D}#1.0#0"; "MSWINSCK.OCX"
Begin VB.Form Form_Cliente 
   BackColor       =   &H00FF8080&
   Caption         =   "Cliente"
   ClientHeight    =   5850
   ClientLeft      =   60
   ClientTop       =   405
   ClientWidth     =   6660
   FillColor       =   &H80000007&
   LinkTopic       =   "Form1"
   ScaleHeight     =   5850
   ScaleWidth      =   6660
   StartUpPosition =   3  'Windows Default
   Begin VB.Frame Frame2 
      Caption         =   "Url del Server"
      Height          =   1215
      Left            =   120
      TabIndex        =   10
      Top             =   4440
      Width           =   6375
      Begin VB.CommandButton Command1 
         Caption         =   "IP Publica"
         Height          =   435
         Left            =   2160
         TabIndex        =   14
         Top             =   600
         Width           =   1935
      End
      Begin VB.CommandButton btn_EnvioGet 
         Caption         =   "Envio Get"
         Height          =   255
         Left            =   4080
         TabIndex        =   13
         Top             =   840
         Width           =   1815
      End
      Begin VB.CommandButton btn_Envio_Post 
         Caption         =   "Envio Post"
         Height          =   255
         Left            =   480
         TabIndex        =   12
         Top             =   840
         Width           =   1455
      End
      Begin VB.Label lbl_UrlServer 
         BeginProperty Font 
            Name            =   "MS Sans Serif"
            Size            =   9.75
            Charset         =   0
            Weight          =   400
            Underline       =   0   'False
            Italic          =   0   'False
            Strikethrough   =   0   'False
         EndProperty
         Height          =   375
         Left            =   120
         TabIndex        =   11
         Top             =   360
         Width           =   6135
      End
   End
   Begin VB.Frame Frame1 
      Caption         =   "Conexion"
      Height          =   1095
      Left            =   120
      TabIndex        =   3
      Top             =   3120
      Width           =   6375
      Begin VB.TextBox RemotePort 
         Height          =   285
         Left            =   1080
         TabIndex        =   7
         Top             =   720
         Width           =   975
      End
      Begin VB.CommandButton btn_CloseServer 
         Caption         =   "Desconectar"
         Height          =   255
         Left            =   4560
         TabIndex        =   6
         Top             =   720
         Width           =   1215
      End
      Begin VB.CommandButton Btn_ConectToServer 
         Caption         =   "Conectar"
         Height          =   255
         Left            =   2760
         TabIndex        =   5
         Top             =   720
         Width           =   1335
      End
      Begin VB.TextBox RemoteHost 
         Height          =   285
         Left            =   1200
         TabIndex        =   4
         Top             =   240
         Width           =   4575
      End
      Begin VB.Label Label2 
         Caption         =   "Puerto Servidor:"
         Height          =   375
         Left            =   120
         TabIndex        =   9
         Top             =   600
         Width           =   855
      End
      Begin VB.Label Label1 
         Caption         =   "IP Servidor:"
         Height          =   255
         Left            =   120
         TabIndex        =   8
         Top             =   240
         Width           =   855
      End
   End
   Begin VB.CommandButton btn_SendServer 
      Caption         =   "Enviar"
      Height          =   315
      Left            =   4920
      TabIndex        =   2
      Top             =   2640
      Width           =   1455
   End
   Begin VB.TextBox DatoaEnviar 
      Height          =   285
      Left            =   120
      TabIndex        =   1
      Top             =   2640
      Width           =   4575
   End
   Begin MSWinsockLib.Winsock WinsockClient 
      Left            =   3480
      Top             =   480
      _ExtentX        =   741
      _ExtentY        =   741
      _Version        =   393216
   End
   Begin VB.TextBox TerminalCliente 
      Height          =   2445
      Left            =   120
      MultiLine       =   -1  'True
      ScrollBars      =   2  'Vertical
      TabIndex        =   0
      Top             =   120
      Width           =   6375
   End
End
Attribute VB_Name = "Form_Cliente"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False

Private Sub btn_CloseServer_Click()
 TerminalCliente.Text = TerminalCliente.Text & "***Conexion Cerrada por Usuario !!! ***" & vbCrLf  ' que el servidor cerro la conexion
 TerminalCliente.SelStart = Len(TerminalCliente.Text) ' Desplazamos el ScrollBarr (Barra de desplazamiento) para el nuevo texto
 WinsockClient.Close
 TerminalCliente.Text = ""
End Sub

Private Sub Btn_ConectToServer_Click()

  If RemoteHost.Text <> "" Then
    If RemotePort.Text <> "" Then
      If WinsockClient.State = 0 Then
        WinsockClient.RemoteHost = RemoteHost.Text            ' Iniciamos conexion con el Servidor
        WinsockClient.RemotePort = RemotePort.Text
        WinsockClient.Close
        WinsockClient.Connect
        TerminalCliente.Text = TerminalCliente.Text & "***Intento de Conexion iniciado por Usuario !!! ***" & vbCrLf  ' que el servidor cerro la conexion
        TerminalCliente.SelStart = Len(TerminalCliente.Text) ' Desplazamos el ScrollBarr (Barra de desplazamiento) para el nuevo texto
      End If
    End If
  End If
End Sub


Private Sub btn_Envio_Post_Click()

Dim httpReq As Object
Dim response As String


Set httpReq = CreateObject("WinHttp.WinHttpRequest.5.1")

Dim url As String

url = Form_Config.Txt_Entrada

Dim jsonData As String


jsonData = "{" & vbCrLf & _
    """uuid"": ""dff9bc60-a264-4b6e-960c-192bbe5c9e68""," & vbCrLf & _
    """id_parking"": ""2""," & vbCrLf & _
    """fecha"": ""11-01-2024 11:39:00""," & vbCrLf & _
    """codStatus"": ""W5""" & vbCrLf & _
"}"

httpReq.Open "POST", url, False
httpReq.SetRequestHeader "Content-Type", "application/json" ' Ajusta el tipo de contenido según lo que necesites
'httpReq.SetRequestHeader "Content-Type", "application/x-www-form-urlencoded"

httpReq.Send jsonData

If httpReq.Status = 200 Then
    ' La solicitud fue exitosa, procesa la respuesta
    MsgBox "Respuesta del servidor: " & httpReq.ResponseText
Else
    ' La solicitud falló, muestra el código de estado y la descripción
    MsgBox "Error: " & httpReq.Status & " - " & httpReq.StatusText
End If
Set httpReq = Nothing

End Sub

Public Sub btn_EnvioGet_Click()

Dim httpReq As Object
Dim response As String
Dim command As String
Dim Address As String

Set httpReq = CreateObject("WinHttp.WinHttpRequest.5.1")

Dim url As String
'url = "http://181.87.136.54:9000/ejemplo/18138402" ' Reemplaza con la URL de tu servidor y recurso
url = wpcini.ServerIP + "/" + DatoRecibidoDelModulo

If (Len(DatoRecibidoDelModulo) < 10) Then
  Exit Sub
End If

httpReq.Open "GET", url, False
httpReq.SetRequestHeader "Content-Type", "application/json" ' Ajusta el tipo de contenido según lo que necesites
'httpReq.SetRequestHeader "Content-Type", "application/x-www-form-urlencoded"
httpReq.Send

response = httpReq.ResponseText

'MsgBox response ' Muestra la respuesta del servidor

command = (Mid$(response, 3, 3))
Address = (Mid$(response, 1, 2))

Select Case command

Case "ACK"
   Form_Servidor.DatoaEnviar.Text = "K5"
    frmWpcMain.lbl_Cajero.Caption = "Dispositivo: " + Address + "  Habilitado.."
    ShowDisplayCajero = 2
   
Case "NAK"
   Form_Servidor.DatoaEnviar.Text = "K2"
   frmWpcMain.lbl_Cajero.Caption = "Dispositivo: " + Address + "  Denegado !!"
   ShowDisplayCajero = 2

End Select
Form_Servidor.nroDevice.Text = Mid$(response, 1, 2)
Form_Servidor.btn_ServerEnvia_Click



End Sub

Private Sub btn_EnvioPost_Click()

Dim httpReq As Object
Dim response As String


Set httpReq = CreateObject("WinHttp.WinHttpRequest.5.1")

Dim url As String

url = "https://181.87.142.194:9101/ingreso" ' Reemplaza con la URL de tu servidor y recurso
'url = wpcini.ServerIP
Dim jsonData As String

jsonData = "{Datorecibidodelmodulo: ""valor1"", ""campo2"": ""valor2""}" ' Ajusta los datos JSON según tus necesidades
'postdata = "parametro1=valor1&parametro2=valor2" ' Puedes agregar más parámetros si es necesario

httpReq.Open "POST", url, False
httpReq.SetRequestHeader "Content-Type", "application/json" ' Ajusta el tipo de contenido según lo que necesites
'httpReq.SetRequestHeader "Content-Type", "application/x-www-form-urlencoded"


httpReq.Send jsonData
'httpReq.Send postdata


response = httpReq.ResponseText

MsgBox response ' Muestra la respuesta del servidor
 

End Sub



Private Sub btn_SendServer_Click()
  WinsockClient.SendData DatoaEnviar.Text & vbCrLf      ' Enviamos el dato al socket Servidor
  TerminalCliente.SelStart = Len(TerminalCliente.Text)  ' Desplazamos el ScrollBarr
  TerminalCliente.Text = TerminalCliente.Text & "Cliente: >" & DatoaEnviar.Text & vbCrLf ' Presentamos el Dato Enviado
  TerminalCliente.SelStart = Len(TerminalCliente.Text) ' Desplazamos el ScrollBarr al final del contenido
  DatoaEnviar.Text = ""
End Sub

Private Sub Command1_Click()
 Dim IpPublica As String
 IpPublica = GetPublicIP()
 Command1.Caption = IpPublica
End Sub


Private Sub Form_QueryUnload(Cancel As Integer, UnloadMode As Integer)
  If UnloadMode = vbFormControlMenu Then
  ' El formulario está siendo cerrado desde el menú de control (botón X)
    MsgBox "No se permite cerrar el formulario de esta manera. Cerrar mediante el boton 'Cliente'"
    Cancel = 1 ' Cancelar el cierre del formulario
  End If
End Sub

Private Sub WinsockClient_Close()                     ' Si se disparo este evento significa que la conexion fallo o
 TerminalCliente.Text = TerminalCliente.Text & "***Conexion Cerrada por el Servidor o por Error de Conexion !!! ***" & vbCrLf  ' que el servidor cerro la conexion
 TerminalCliente.SelStart = Len(TerminalCliente.Text) ' Desplazamos el ScrollBarr al final del contenido
 WinsockClient.Close
End Sub

Private Sub WinsockClient_Connect()                   ' Como se establecio la comunicacion presentamos le mensaje
 TerminalCliente.Text = TerminalCliente.Text & "***Conexion establecida !!! ***" & vbCrLf
 TerminalCliente.SelStart = Len(TerminalCliente.Text) ' Desplazamos el ScrollBarr (Barra de desplazamiento) para el nuevo texto
End Sub

Private Sub WinsockClient_DataArrival(ByVal bytesTotal As Long)
   Dim BufferRecepcion As String                                          ' Dispara este evento cuando recibe un dato
   Dim aux As String
   Dim i As Integer
   
   aux = (Chr$(2) + "01K51D" + Chr$(3))
   'aux = Chr$(2)
   WinsockClient.GetData BufferRecepcion
   If BufferRecepcion = aux Then
      i = i + 1
   End If
   TerminalCliente.SelStart = Len(TerminalCliente.Text)                   ' Desplazamos el ScrollBarr al final del contenido
   TerminalCliente.Text = TerminalCliente.Text & "Servidor: >" & BufferRecepcion & vbCrLf ' Presentamos el Dato Recibido
   TerminalCliente.SelStart = Len(TerminalCliente.Text)
End Sub

Private Sub WinsockClient_Error(ByVal Number As Integer, Description As String, ByVal Scode As Long, ByVal Source As String, ByVal HelpFile As String, ByVal HelpContext As Long, CancelDisplay As Boolean)
  WinsockClient.Close
  MsgBox "Error de conexion del Cliente Numero " & Number & ": " & Description, vbCritical
End Sub


