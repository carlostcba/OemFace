VERSION 5.00
Begin VB.Form Form_Login 
   Caption         =   "Ingreso a Configuracion"
   ClientHeight    =   4215
   ClientLeft      =   60
   ClientTop       =   405
   ClientWidth     =   5535
   LinkTopic       =   "Form1"
   ScaleHeight     =   4215
   ScaleWidth      =   5535
   StartUpPosition =   3  'Windows Default
   Begin VB.CommandButton btn_Cancelar 
      Caption         =   "Cancelar"
      Height          =   375
      Left            =   3600
      TabIndex        =   6
      Top             =   3600
      Width           =   1335
   End
   Begin VB.CommandButton btn_Ingresar 
      Caption         =   "Ingresar"
      Height          =   375
      Left            =   480
      TabIndex        =   5
      Top             =   3600
      Width           =   1335
   End
   Begin VB.Frame Frame_Login 
      Caption         =   "Ingrese Usuario y Contraseña"
      Height          =   1335
      Left            =   120
      TabIndex        =   0
      Top             =   2040
      Width           =   5295
      Begin VB.TextBox Txt_Password 
         Height          =   285
         Left            =   2520
         TabIndex        =   2
         Top             =   840
         Width           =   2415
      End
      Begin VB.TextBox Txt_User 
         Height          =   285
         Left            =   2520
         TabIndex        =   1
         Top             =   360
         Width           =   2415
      End
      Begin VB.Label Label2 
         Caption         =   "Contraseña :"
         Height          =   255
         Left            =   960
         TabIndex        =   4
         Top             =   840
         Width           =   975
      End
      Begin VB.Label Label1 
         Caption         =   "   Usuario :"
         Height          =   255
         Left            =   840
         TabIndex        =   3
         Top             =   360
         Width           =   1095
      End
   End
   Begin VB.Image Image1 
      Height          =   1845
      Left            =   0
      Picture         =   "fmr_Login.frx":0000
      Top             =   0
      Width           =   5790
   End
End
Attribute VB_Name = "Form_Login"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Private Sub btn_Cancelar_Click()
  Unload Me
End Sub

Private Sub btn_Ingresar_Click()
   
  On Error GoTo salir
  
  Dim sql As String
    
  Dim rs0 As ADODB.Recordset
  
  
  If Txt_User.Text = "Oemspot" And Txt_Password.Text = "Oem2017*" Then
    Unload Me
    Form_Config.Show                                      ' Si ingresa con Usuario y Clave Maestra le damos acceso
    Exit Sub
  End If
    
  If conexionActiva.State = adStateOpen Then              ' Esta activa la conexion con la Base de datos ??
    Set rs0 = New ADODB.Recordset                         ' Ejecuta la consulta
    sql = "SELECT * FROM config_webconect WHERE User = '" & Txt_User.Text & "' AND Password = '" & Txt_Password.Text & "'"
    rs0.Open sql, conexionActiva, adOpenStatic, adLockReadOnly
    If Not rs0.EOF Then                                    'Hay un registro donde coincidan Usuario y contraseña?
      Unload Me
      Form_Config.Show
    Else
      MsgBox "Usuario o contraseña incorrectos", vbExclamation
    End If
    rs0.Close
    Else
        MsgBox "El Usuario o la Contraseña son incorrectos !!!! ", vbCritical
    End If
    Exit Sub
    
salir:
 MsgBox "La conexión a la base de datos no está abierta.", vbCritical
End Sub

Private Sub Form_Load()
  Txt_Password.PasswordChar = "*"
End Sub
