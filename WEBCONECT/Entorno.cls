VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
  Persistable = 0  'NotPersistable
  DataBindingBehavior = 0  'vbNone
  DataSourceBehavior  = 0  'vbNone
  MTSTransactionMode  = 0  'NotAnMTSObject
END
Attribute VB_Name = "Entorno"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = True
Attribute VB_PredeclaredId = False
Attribute VB_Exposed = False
Option Explicit

Private mvarId_Playa As Integer
Private mvarId_Isleta As Integer
Private mvarId_Dispositivo As Integer
Private mvarUsuarioDefault As Integer

Private mvarRefresh_del_Log As Integer
Private mvarRefresh_Ocupacion As Integer
Private mvarDia_Vto_CtaCte As Integer

Private mvarId_Empleado As Integer
Private mvarTipo_Usuario As String
Private mvarNombre_Usuario As String
Private mvarApellido_Usuario As String

Private mvarUsuario As String
Private mvarPassword As String

Private mvarDSN_MySQL As String


Public Property Get DSN_MySQL() As String
    DSN_MySQL = mvarDSN_MySQL
End Property

Public Property Let UsuarioDefault(ByVal vData As Integer)
    mvarUsuarioDefault = vData
End Property

Public Property Get UsuarioDefault() As Integer
    UsuarioDefault = mvarUsuarioDefault
End Property

Public Property Let Password(ByVal vData As String)
    mvarPassword = vData
End Property

Public Property Get Password() As String
    Password = mvarPassword
End Property

Public Property Let Usuario(ByVal vData As String)
    mvarUsuario = vData
End Property

Public Property Get Usuario() As String
    Usuario = mvarUsuario
End Property

Public Property Let Tipo_Usuario(ByVal vData As String)
    mvarTipo_Usuario = vData
End Property

Public Property Get Tipo_Usuario() As String
    Tipo_Usuario = mvarTipo_Usuario
End Property

Public Property Let Id_empleado(ByVal vData As Integer)
    mvarId_Empleado = vData
End Property

Public Property Get Id_empleado() As Integer
    Id_empleado = mvarId_Empleado
End Property

Public Property Let Id_Dispositivo(ByVal vData As Integer)
    mvarId_Dispositivo = vData
End Property

Public Property Get Id_Dispositivo() As Integer
    Id_Dispositivo = mvarId_Dispositivo
End Property

Public Property Let Id_Isleta(ByVal vData As Integer)
    mvarId_Isleta = vData
End Property

Public Property Get Id_Isleta() As Integer
    Id_Isleta = mvarId_Isleta
End Property

Public Property Let Id_Playa(ByVal vData As Integer)
    mvarId_Playa = vData
End Property

Public Property Get Id_Playa() As Integer
    Id_Playa = mvarId_Playa
End Property

Public Property Let Nombre_Usuario(ByVal vData As String)
    mvarNombre_Usuario = vData
End Property

Public Property Get Nombre_Usuario() As String
    Nombre_Usuario = mvarNombre_Usuario
End Property

Public Property Let Apellido_Usuario(ByVal vData As String)
    mvarApellido_Usuario = vData
End Property

Public Property Get Apellido_Usuario() As String
    Apellido_Usuario = mvarApellido_Usuario
End Property

Public Property Get Dia_Vto_CtaCte() As Integer
    Dia_Vto_CtaCte = mvarDia_Vto_CtaCte
End Property

Public Property Get Refresh_del_Log() As Integer
    Refresh_del_Log = mvarRefresh_del_Log
End Property

Public Property Get Refresh_Ocupacion() As Integer
    Refresh_Ocupacion = mvarRefresh_Ocupacion
End Property




Public Function LeerValoresINI() As Boolean
Dim File As String
Dim Resultado As Boolean
    
    Resultado = True
    File = CurDir() & "\init.ini"
   
    
    mvarRefresh_del_Log = VBGetPrivateProfileString("Config", "Refresh_del_Log", File$)
    mvarRefresh_Ocupacion = VBGetPrivateProfileString("Config", "Refresh_Ocupacion", File$)
    mvarDia_Vto_CtaCte = VBGetPrivateProfileString("Config", "Dia_Vto_CtaCte", File$)
   
    mvarDSN_MySQL = VBGetPrivateProfileString("Config", "DSN_MySQL", File$)
 
    mvarId_Playa = Val(VBGetPrivateProfileString("WorkStation", "Playa", File$))
    mvarId_Isleta = Val(VBGetPrivateProfileString("WorkStation", "Isleta", File$))
    mvarId_Dispositivo = Val(VBGetPrivateProfileString("WorkStation", "Dispositivo", File$))
    mvarUsuarioDefault = VBGetPrivateProfileString("WorkStation", "UsuarioDefault", File$)
  
    LeerValoresINI = Resultado
End Function

