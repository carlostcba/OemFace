VERSION 5.00
Begin VB.Form Form_Servidor 
   BackColor       =   &H0080FFFF&
   Caption         =   "Servidor"
   ClientHeight    =   6660
   ClientLeft      =   60
   ClientTop       =   405
   ClientWidth     =   6315
   FillColor       =   &H80000007&
   LinkTopic       =   "Form1"
   ScaleHeight     =   6660
   ScaleWidth      =   6315
   StartUpPosition =   3  'Windows Default
   Begin VB.CommandButton btn_ClearTerminal 
      Caption         =   "Limpiar Terminal"
      Height          =   375
      Left            =   2280
      TabIndex        =   13
      Top             =   3600
      Width           =   1695
   End
   Begin VB.Frame Frame2 
      Caption         =   "Envio de Datos"
      Height          =   1215
      Left            =   120
      TabIndex        =   5
      Top             =   4080
      Width           =   6015
      Begin VB.CommandButton btn_ServerEnvia 
         Caption         =   "Enviar al Cliente"
         Height          =   375
         Left            =   4560
         TabIndex        =   8
         Top             =   360
         Width           =   1335
      End
      Begin VB.TextBox DatoaEnviar 
         Height          =   375
         Left            =   1560
         TabIndex        =   7
         Top             =   360
         Width           =   2535
      End
      Begin VB.TextBox nroDevice 
         Height          =   375
         Left            =   240
         TabIndex        =   6
         Top             =   360
         Width           =   975
      End
      Begin VB.Label Label3 
         Caption         =   "Comando :"
         Height          =   255
         Left            =   2400
         TabIndex        =   10
         Top             =   840
         Width           =   855
      End
      Begin VB.Label Label1 
         Caption         =   "Address :"
         Height          =   255
         Left            =   480
         TabIndex        =   9
         Top             =   840
         Width           =   735
      End
   End
   Begin VB.Frame Frame1 
      Caption         =   "Conexion"
      Height          =   1095
      Left            =   120
      TabIndex        =   1
      Top             =   5400
      Width           =   6015
      Begin VB.CommandButton btn_CloseServer 
         Caption         =   "Desconectar"
         Height          =   375
         Left            =   4680
         TabIndex        =   3
         Top             =   600
         Width           =   1215
      End
      Begin VB.CommandButton Btn_EscucharCliente 
         Caption         =   "Escuchar"
         Height          =   375
         Left            =   360
         TabIndex        =   2
         Top             =   600
         Width           =   1095
      End
      Begin VB.Label lbl_SrvPort 
         Caption         =   "Local Port"
         Height          =   255
         Left            =   3240
         TabIndex        =   14
         Top             =   240
         Width           =   855
      End
      Begin VB.Label Label5 
         Caption         =   "Label5"
         Height          =   255
         Left            =   3000
         TabIndex        =   12
         Top             =   720
         Width           =   1455
      End
      Begin VB.Label Label4 
         Caption         =   "Label4"
         Height          =   255
         Left            =   2160
         TabIndex        =   11
         Top             =   720
         Width           =   855
      End
      Begin VB.Label Label2 
         Caption         =   "Puerto Local donde escucha el Server :"
         Height          =   375
         Left            =   360
         TabIndex        =   4
         Top             =   240
         Width           =   2895
      End
   End
   Begin VB.TextBox TerminalServidor 
      Height          =   3405
      Left            =   120
      MultiLine       =   -1  'True
      ScrollBars      =   2  'Vertical
      TabIndex        =   0
      Top             =   120
      Width           =   6015
   End
End
Attribute VB_Name = "Form_Servidor"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False



Private Sub btn_ClearTerminal_Click()
  TerminalServidor.Text = ""
End Sub

Public Sub btn_CloseServer_Click()
 
Dim ip As String
Dim num_Socket As Integer
Dim num_Elementos As Integer
Dim i As Integer







                                                                  ' Carga la cantidad de elementos del arreglo en este momento
' For i = 0 To Cantidad_Conexiones                                 ' Verificca si existe alguno existente en el arreglo que
'   If ArrayWinsockEjecutivo(i).State <> sckClosed Then            ' este usado(Conectado..)
'     num_Socket = i
'     ip = ArrayWinsockEjecutivo(num_Socket).RemoteHostIP
'     ArrayWinsockEjecutivo(num_Socket).Close                      ' cerramos la conexion de los sockets "Ejecutivos"
'     TerminalServidor.SelStart = Len(TerminalServidor.Text)  ' Presenta el Texto de "Conexion cerrada" del cliente
'     TerminalServidor.Text = TerminalServidor.Text & "Sock:" & num_Socket & "*** Conexion Cerrada IP: " & ip & vbCrLf
'     TerminalServidor.SelStart = Len(TerminalServidor.Text)
'   End If
' Next
 
 ip = frmWpcMain.WinsockSrvRecep.LocalIP
 frmWpcMain.WinsockSrvRecep.Close                            ' Finalmente cerramos la conexion del socket "Recepcionista"
 TerminalServidor.SelStart = Len(TerminalServidor.Text)  ' Presenta el Texto de "Conexion cerrada"
 TerminalServidor.Text = TerminalServidor.Text & "Sock: Server Recepcionista *** Conexion Cerrada IP: " & ip & vbCrLf ' del cliente
 TerminalServidor.SelStart = Len(TerminalServidor.Text)
 TerminalServidor.Text = ""
 
 'frmWpcMain.lbl_ParkYA.Caption = "SERVIDOR DE PARKING INACTIVO !!!..."
 'frmWpcMain.lbl_ParkYA.BackColor = Rojo                 ' Color Rojo
 'ShowDisplayParkYA = 2
  
End Sub

Public Sub Btn_EscucharCliente_Click()
  If Form_Servidor.lbl_SrvPort <> "" Then
    frmWpcMain.WinsockSrvRecep.Close                         'Cerramos cualquier posible conexion anterior
    frmWpcMain.WinsockSrvRecep.LocalPort = Form_Servidor.lbl_SrvPort  'Asignamos el Puerto por donde escucha en Servidor
    frmWpcMain.WinsockSrvRecep.Listen                        'Activamos el Servidor en modo escucha
    TerminalServidor.Text = ""
    TerminalServidor.Text = TerminalServidor.Text & "***Escuhando Conexiones de Clientes.. !!! ***" & vbCrLf
    TerminalServidor.SelStart = Len(TerminalServidor.Text) ' Desplazamos el ScrollBarr (Barra de desplazamiento) para el nuevo texto
    'frmWpcMain.lbl_ParkYA.Caption = "SERVIDOR DE PARKING ACTIVO !!!..."
    'frmWpcMain.lbl_ParkYA.BackColor = Verde
    'ShowDisplayParkYA = 2
    
  End If
End Sub

Private Sub btn_OemPass_Click()

Dim numElementos As Integer                               ' Indica la cantidad de sockets en el arreglo de winsocks
Dim i As Integer
Dim Address As Integer
Dim cmd As String
Dim Socketsend As String


  cmd = "O3"
  Address = 1
  
  Socketsend = Chr$(ASCII_STX) + Format(Address, "#00") + cmd
  ' Calculo CheckSum y pongo fin del texto y CR
  Socketsend = Socketsend + CalculoCS(Socketsend) + Chr$(ASCII_EOF)
  
  
  numElementos = WinsockSrvEjecut.UBound
  For i = 0 To numElementos
    If WinsockSrvEjecut(i).State = sckConnected Then
      WinsockSrvEjecut(i).SendData Socketsend
    End If
  Next
  
  TerminalServidor.SelStart = Len(TerminalServidor.Text)  ' Desplazamos el ScrollBarr
  TerminalServidor.Text = TerminalServidor.Text & "Server: >" & Socketsend & vbCrLf ' Presentamos el Dato Enviado
  TerminalServidor.SelStart = Len(TerminalServidor.Text) ' Desplazamos el ScrollBarr al final del contenido
  
End Sub

Public Function CalculoCS(ByVal comando As String) As Variant
  Dim IFor As Integer
  Dim XFor As Integer
  Dim Checksum As Integer
  
  'Calculo del checksum
  Checksum = 0
  XFor = Len(comando)
  For IFor = 1 To XFor
    Checksum = (Asc(Mid$(comando, IFor, 1)) + Checksum) And &HFF
  Next IFor
  
  'Calculo el 2's
  Checksum = ((&HFF - Checksum) + 1) And &HFF
  
  ' Retorno el valor calculado
  If Len(Hex(Checksum)) < 2 Then
    CalculoCS = "0" + Hex(Checksum)
  Else
    CalculoCS = Hex(Checksum)
  End If
End Function


Private Sub btn_SendServer_Click()
  
  
  
Dim numElementos As Integer                               ' Indica la cantidad de sockets en el arreglo de winsocks
Dim i As Integer
Dim Address As Integer
Dim cmd As String
Dim Socketsend As String


  cmd = Mid$(DatoaEnviar.Text, 3, 2)
  Address = Mid$(DatoaEnviar.Text, 1, 2)
  
  Socketsend = Chr$(ASCII_STX) + Format(Address, "#00") + cmd
  ' Calculo CheckSum y pongo fin del texto y CR
  Socketsend = Socketsend + CalculoCS(Socketsend) + Chr$(ASCII_EOF)
  
  
  numElementos = WinsockSrvEjecut.UBound
  For i = 0 To numElementos
    If WinsockSrvEjecut(i).State = sckConnected Then
      WinsockSrvEjecut(i).SendData Socketsend
    End If
  Next
  
  TerminalServidor.SelStart = Len(TerminalServidor.Text)  ' Desplazamos el ScrollBarr
  TerminalServidor.Text = TerminalServidor.Text & "Server: >" & Socketsend & vbCrLf ' Presentamos el Dato Enviado
  TerminalServidor.SelStart = Len(TerminalServidor.Text) ' Desplazamos el ScrollBarr al final del contenido

End Sub

Public Sub btn_ServerEnvia_Click()
  
On Error GoTo ErrorExit

Dim numElementos As Integer                               ' Indica la cantidad de sockets en el arreglo de winsocks
Dim i As Integer
Dim Address As Integer
Dim cmd As String
Dim Socketsend As String

  If DatoaEnviar.Text = "" Then
    Exit Sub
  End If
  
  cmd = DatoaEnviar.Text
  Address = Mid$(nroDevice.Text, 1, 2)
  
  Socketsend = Chr$(ASCII_STX) + Format(Address, "#00") + cmd
  ' Calculo CheckSum y pongo fin del texto y CR
  Socketsend = Socketsend + CalculoCS(Socketsend) + Chr$(ASCII_EOF)
  
  numElementos = WinsockSrvEjecut.UBound
  For i = 0 To numElementos
    If WinsockSrvEjecut(i).State = sckConnected Then
      WinsockSrvEjecut(i).SendData Socketsend
    End If
  Next
  
  TerminalServidor.SelStart = Len(TerminalServidor.Text)  ' Desplazamos el ScrollBarr
  TerminalServidor.Text = TerminalServidor.Text & "Server: >" & Socketsend & vbCrLf ' Presentamos el Dato Enviado
  TerminalServidor.SelStart = Len(TerminalServidor.Text) ' Desplazamos el ScrollBarr al final del contenido

ErrorExit:

End Sub


Private Sub Form_Load()
  Dim iphost As String
  
   
  iphost = frmWpcMain.WinsockSrvRecep.LocalIP
  Label4.Caption = "IP.HOST :"
  Label5.Caption = iphost
  Form_Servidor.lbl_SrvPort = Form_Config.Txt_Port_Http
  frmWpcMain.WinsockSrvRecep.Close                         'Cerramos cualquier posible conexion anterior
  frmWpcMain.WinsockSrvRecep.LocalPort = Form_Servidor.lbl_SrvPort    'Asignamos el Puerto por donde escucha en Servidor
  frmWpcMain.WinsockSrvRecep.Listen                        'Activamos el Servidor en modo escucha
  Form_Servidor.TerminalServidor.Text = ""
  Form_Servidor.TerminalServidor.Text = Form_Servidor.TerminalServidor.Text & "***Escuhando Conexiones de Clientes.. !!! ***" & vbCrLf
  Form_Servidor.TerminalServidor.SelStart = Len(Form_Servidor.TerminalServidor.Text) ' Desplazamos el ScrollBarr (Barra de desplazamiento) para el nuevo texto
    
  
End Sub


Private Sub Form_QueryUnload(Cancel As Integer, UnloadMode As Integer)
  
  If UnloadMode = vbFormControlMenu Then
  ' El formulario está siendo cerrado desde el menú de control (botón X)
    MsgBox "No se permite cerrar el formulario de esta manera. Cerrar mediante el boton 'Servidor'"
    Cancel = 1 ' Cancelar el cierre del formulario
  End If
End Sub




