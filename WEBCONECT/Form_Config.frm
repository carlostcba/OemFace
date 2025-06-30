VERSION 5.00
Begin VB.Form Form_Config 
   BackColor       =   &H00C0FFC0&
   Caption         =   "Formulario de Configuracion"
   ClientHeight    =   8655
   ClientLeft      =   60
   ClientTop       =   405
   ClientWidth     =   9900
   LinkTopic       =   "Form1"
   ScaleHeight     =   8655
   ScaleWidth      =   9900
   StartUpPosition =   3  'Windows Default
   Begin VB.CommandButton btn_Cfg_Update 
      Caption         =   "Modificar"
      Height          =   255
      Left            =   6000
      TabIndex        =   17
      Top             =   8160
      Width           =   1335
   End
   Begin VB.CommandButton btn_Cfg_Out 
      Caption         =   "Salir"
      Height          =   255
      Left            =   2280
      TabIndex        =   16
      Top             =   8160
      Width           =   1215
   End
   Begin VB.Frame Frame_Servidor_Winsock 
      Caption         =   "Configuracion Servidor Winsock"
      Height          =   1095
      Left            =   480
      TabIndex        =   12
      Top             =   3720
      Width           =   9135
      Begin VB.TextBox Txt_Port_Winsock 
         Height          =   285
         Left            =   2640
         TabIndex        =   19
         Top             =   480
         Width           =   975
      End
      Begin VB.Label Label1 
         Caption         =   "Puerto Servidor Winsock :"
         Height          =   255
         Index           =   5
         Left            =   240
         TabIndex        =   18
         Top             =   480
         Width           =   2175
      End
   End
   Begin VB.Frame Frame_Cfg_Gral 
      Caption         =   "Configuracion General"
      Height          =   2175
      Left            =   480
      TabIndex        =   2
      Top             =   120
      Width           =   9015
      Begin VB.Frame Frame_General 
         Caption         =   "Datos Generales"
         Height          =   1455
         Left            =   360
         TabIndex        =   25
         Top             =   480
         Width           =   4935
         Begin VB.TextBox Txt_IdPlaya 
            Height          =   285
            Left            =   3360
            TabIndex        =   27
            Top             =   360
            Width           =   1215
         End
         Begin VB.Label Label4 
            Caption         =   "Identificador de Playa :"
            Height          =   255
            Left            =   1440
            TabIndex        =   26
            Top             =   360
            Width           =   1695
         End
      End
      Begin VB.Frame Frame_Login 
         Caption         =   "Usuario y Contraseña"
         Height          =   1455
         Left            =   6000
         TabIndex        =   20
         Top             =   480
         Width           =   2775
         Begin VB.TextBox Txt_PassLogin 
            Height          =   285
            Left            =   1200
            TabIndex        =   22
            Top             =   960
            Width           =   1215
         End
         Begin VB.TextBox Txt_UserLogin 
            Height          =   285
            Left            =   1200
            TabIndex        =   21
            Top             =   360
            Width           =   1215
         End
         Begin VB.Label Label3 
            Caption         =   "Contraseña :"
            Height          =   255
            Left            =   120
            TabIndex        =   24
            Top             =   960
            Width           =   975
         End
         Begin VB.Label Label2 
            Caption         =   "Usuario :"
            Height          =   375
            Left            =   120
            TabIndex        =   23
            Top             =   360
            Width           =   735
         End
      End
   End
   Begin VB.Frame Frame_Servidor_Http 
      Caption         =   "Configuracion Servidor Http"
      Height          =   1095
      Left            =   480
      TabIndex        =   1
      Top             =   2520
      Width           =   9135
      Begin VB.TextBox Txt_Port_Http 
         Height          =   285
         Left            =   2280
         TabIndex        =   13
         Top             =   360
         Width           =   975
      End
      Begin VB.Label Label1 
         Caption         =   "Puerto Servidor Http   :"
         Height          =   255
         Index           =   4
         Left            =   240
         TabIndex        =   11
         Top             =   360
         Width           =   2175
      End
   End
   Begin VB.Frame Frame_Cliente 
      Caption         =   "Configuracion Cliente"
      Height          =   2895
      Left            =   480
      TabIndex        =   0
      Top             =   5040
      Width           =   9135
      Begin VB.TextBox Txt_Borrado_Ticket 
         Height          =   285
         Left            =   2880
         TabIndex        =   28
         Top             =   2280
         Width           =   5295
      End
      Begin VB.TextBox Txt_Cierre_Caja 
         Height          =   285
         Left            =   2880
         TabIndex        =   15
         Top             =   1920
         Width           =   5295
      End
      Begin VB.TextBox Txt_CashPay 
         Height          =   285
         Left            =   2880
         TabIndex        =   10
         Top             =   1560
         Width           =   5295
      End
      Begin VB.TextBox Txt_Salida 
         Height          =   285
         Left            =   2880
         TabIndex        =   9
         Top             =   1200
         Width           =   5295
      End
      Begin VB.TextBox Txt_Entrada 
         Height          =   285
         Left            =   2880
         TabIndex        =   8
         Top             =   840
         Width           =   5295
      End
      Begin VB.TextBox Txt_Estado 
         Height          =   285
         Left            =   2880
         TabIndex        =   7
         Top             =   480
         Width           =   5295
      End
      Begin VB.Label Label1 
         Caption         =   "Url EndPoint Borrado Ticket:"
         Height          =   255
         Index           =   7
         Left            =   360
         TabIndex        =   29
         Top             =   2280
         Width           =   2175
      End
      Begin VB.Label Label1 
         Caption         =   "Url EndPoint Cierre de Caja:"
         Height          =   255
         Index           =   6
         Left            =   360
         TabIndex        =   14
         Top             =   1920
         Width           =   2175
      End
      Begin VB.Label Label1 
         Caption         =   "Url EndPoint Pago Efectivo:"
         Height          =   255
         Index           =   3
         Left            =   360
         TabIndex        =   6
         Top             =   1560
         Width           =   2175
      End
      Begin VB.Label Label1 
         Caption         =   "Url EndPoint Salida Vehicular:"
         Height          =   255
         Index           =   2
         Left            =   360
         TabIndex        =   5
         Top             =   1200
         Width           =   2175
      End
      Begin VB.Label Label1 
         Caption         =   "Url EndPoint Entrada Vehicular:"
         Height          =   255
         Index           =   1
         Left            =   360
         TabIndex        =   4
         Top             =   840
         Width           =   2295
      End
      Begin VB.Label Label1 
         Caption         =   "Url EndPoint Estado:"
         Height          =   255
         Index           =   0
         Left            =   360
         TabIndex        =   3
         Top             =   480
         Width           =   2175
      End
   End
End
Attribute VB_Name = "Form_Config"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Private Sub btn_Cfg_Out_Click()                         ' Boton de Salir del formulario de Configuracion
 Unload Me
End Sub

Private Sub btn_Cfg_Update_Click()

  On Error GoTo salir

  Dim sql As String
  Dim command As ADODB.command
  
  If conexionActiva.State = adStateOpen Then
    sql = "UPDATE config_Webconect SET " & _
    "Server_Port_Http = " & Val(Txt_Port_Http.Text) & ", " & _
    "Server_Port_Winsock = " & Val(Txt_Port_Winsock.Text) & ", " & _
    "EndPointHTTP_Alive = '" & Txt_Estado.Text & "', " & _
    "EndPointHTTP_Input = '" & Txt_Entrada.Text & "', " & _
    "EndPointHTTP_Output = '" & Txt_Salida.Text & "', " & _
    "EndPointHTTP_CashPay = '" & Txt_CashPay.Text & "', " & _
    "EndPointHTTP_ClearTicket = '" & Txt_Borrado_Ticket.Text & "', " & _
    "EndPointHTTP_Closebox = '" & Txt_Cierre_Caja.Text & "', " & _
    "User = '" & Txt_UserLogin.Text & "', " & _
    "Password = '" & Txt_PassLogin.Text & "', " & _
    "IdPlaya = '" & Txt_IdPlaya.Text & "'" & _
    " WHERE dispositivo = 1"
  
    Set command = New ADODB.command
    command.ActiveConnection = conexionActiva
    command.CommandText = sql
    command.Execute
    MsgBox "Registro actualizado correctamente.", vbInformation
  Else
    MsgBox "La conexión a la base de datos no está abierta.", vbCritical
  End If
  Exit Sub
  
salir:
    MsgBox "Error: " & Err.Description, vbExclamation, "Error al actualizar la base de datos."
End Sub

Private Sub Form_Load()

 If conexionActiva.State = adStateOpen Then          ' Levantamos los datos de configuracion de la base de Datos
    Dim rs As ADODB.Recordset                        ' y lo presentamos en el formulario de configuracion
    Set rs = New ADODB.Recordset                     ' Esta activa la conexion con la Base de datos ??
    Txt_PassLogin.PasswordChar = "*"                 ' Activamos los "******" en el Password
               
    rs.Open "SELECT * FROM config_Webconect", conexionActiva, adOpenStatic, adLockReadOnly
    If Not rs.EOF Then                             ' Verifica si se encontraron resultados
      Do While Not rs.EOF                          ' Recorreemos las filas del Recordset
        Txt_Port_Http.Text = rs.Fields("Server_Port_Http").Value          'Carga el Server Port Http
        Txt_Port_Winsock.Text = rs.Fields("Server_Port_Winsock").Value    'Carga el Server Port Winsock
        Txt_Estado.Text = rs.Fields("EndPointHTTP_Alive").Value           'Carga la Url de Status
        Txt_Entrada.Text = rs.Fields("EndPointHTTP_Input").Value          'Carga la Url de Entrada Vehiculos
        Txt_Salida.Text = rs.Fields("EndPointHTTP_Output").Value          'Carga la Url de Salida Vehiculos
        Txt_CashPay.Text = rs.Fields("EndPointHTTP_CashPay").Value        'Carga la Url de Pago en Eftvo.
        Txt_Borrado_Ticket.Text = rs.Fields("EndPointHTTP_ClearTicket").Value 'Carga la Url de Borrado de Ticket.
        Txt_Cierre_Caja.Text = rs.Fields("EndPointHTTP_Closebox").Value   'Carga la Url de Cierre de Caja
        Txt_UserLogin.Text = rs.Fields("User").Value                      'Carga el Usuario
        Txt_PassLogin.Text = rs.Fields("Password").Value                  'Carga el Password
        Txt_IdPlaya.Text = rs.Fields("IdPlaya").Value                     'Carga el Identificador de Playa
        rs.MoveNext
      Loop
    Else
      MsgBox "No se encontraron datos en la tabla 'config_Webconect'."
    End If
    rs.Close
 Else
   MsgBox "La conexión a la base de datos no está abierta."
 End If
End Sub

' Aqui verificamos que el Identificador de Playa no supere los 6 digitos numericos

Private Sub Txt_IdPlaya_KeyPress(KeyAscii As Integer)
    ' Verificar si la tecla presionada es un dígito numérico o la tecla Backspace
    If Not (KeyAscii >= 48 And KeyAscii <= 57) And KeyAscii <> 8 Then
        ' Si no es un dígito numérico o Backspace, ignorar la entrada
        KeyAscii = 0
    End If
    
    ' Verificar si ya hay 6 caracteres en el TextBox
    If Len(Txt_IdPlaya.Text) >= 6 And KeyAscii <> 8 Then
        ' Si ya hay 6 caracteres y la tecla presionada no es Backspace, ignorar la entrada
        KeyAscii = 0
    End If
End Sub

' Aqui Verificamos que el SERVER PORT WINSOCK o supere los 4 digitos numericos

Private Sub Txt_Port_Winsock_KeyPress(KeyAscii As Integer)
    ' Verificar si el texto está vacío y la tecla presionada es un dígito numérico
    If Len(Txt_Port_Winsock.Text) = 0 And KeyAscii >= 48 And KeyAscii <= 57 Then
        ' Si el texto está vacío y la tecla presionada es un dígito numérico, permitir la entrada
        Exit Sub
    End If
    
    ' Verificar si la tecla presionada es un dígito numérico o la tecla Backspace
    If Not (KeyAscii >= 48 And KeyAscii <= 57) And KeyAscii <> 8 Then
        ' Si no es un dígito numérico o Backspace, ignorar la entrada
        KeyAscii = 0
    End If
    
    ' Verificar si ya hay 4 caracteres en el TextBox
    If Len(Txt_Port_Winsock.Text) >= 4 And KeyAscii <> 8 Then
        ' Si ya hay 4 caracteres y la tecla presionada no es Backspace, ignorar la entrada
        KeyAscii = 0
    End If
End Sub


' Aqui Verificamos que el SERVER PORT HTTP o supere los 4 digitos numericos

Private Sub Txt_Port_http_KeyPress(KeyAscii As Integer)
    ' Verificar si el texto está vacío y la tecla presionada es un dígito numérico
    If Len(Txt_Port_Http.Text) = 0 And KeyAscii >= 48 And KeyAscii <= 57 Then
        ' Si el texto está vacío y la tecla presionada es un dígito numérico, permitir la entrada
        Exit Sub
    End If
    
    ' Verificar si la tecla presionada es un dígito numérico o la tecla Backspace
    If Not (KeyAscii >= 48 And KeyAscii <= 57) And KeyAscii <> 8 Then
        ' Si no es un dígito numérico o Backspace, ignorar la entrada
        KeyAscii = 0
    End If
    
    ' Verificar si ya hay 4 caracteres en el TextBox
    If Len(Txt_Port_Http.Text) >= 4 And KeyAscii <> 8 Then
        ' Si ya hay 4 caracteres y la tecla presionada no es Backspace, ignorar la entrada
        KeyAscii = 0
    End If
End Sub


