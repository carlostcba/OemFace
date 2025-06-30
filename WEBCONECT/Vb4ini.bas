Attribute VB_Name = "VB4INIModule"
Option Explicit

' Copyright © 1996 by Desaware. All Rights Reserved
'
'   Sample aliases for profile strings
'
#If Win32 Then
' This first line is the declaration from win32api.txt
' Declare Function GetPrivateProfileString Lib "kernel32" Alias "GetPrivateProfileStringA" (ByVal lpApplicationName As String, lpKeyName As Any, ByVal lpDefault As String, ByVal lpReturnedString As String, ByVal nSize As Long, ByVal lpfilename As String) As Long
Declare Function GetPrivateProfileStringByKeyName& Lib "kernel32" Alias "GetPrivateProfileStringA" (ByVal lpApplicationName$, ByVal lpszKey$, ByVal lpszDefault$, ByVal lpszReturnBuffer$, ByVal cchReturnBuffer&, ByVal lpszFile$)
Declare Function GetPrivateProfileStringKeys& Lib "kernel32" Alias "GetPrivateProfileStringA" (ByVal lpApplicationName$, ByVal lpszKey&, ByVal lpszDefault$, ByVal lpszReturnBuffer$, ByVal cchReturnBuffer&, ByVal lpszFile$)
Declare Function GetPrivateProfileStringSections& Lib "kernel32" Alias "GetPrivateProfileStringA" (ByVal lpApplicationName&, ByVal lpszKey&, ByVal lpszDefault$, ByVal lpszReturnBuffer$, ByVal cchReturnBuffer&, ByVal lpszFile$)
' This first line is the declaration from win32api.txt
' Declare Function WritePrivateProfileString Lib "kernel32" Alias "WritePrivateProfileStringA" (ByVal lpApplicationName As String, lpKeyName As Any, lpString As Any, ByVal lplFileName As String) As Long
Declare Function WritePrivateProfileStringByKeyName& Lib "kernel32" Alias "WritePrivateProfileStringA" (ByVal lpApplicationName As String, ByVal lpKeyName As String, ByVal lpString As String, ByVal lplFileName As String)
Declare Function WritePrivateProfileStringToDeleteKey& Lib "kernel32" Alias "WritePrivateProfileStringA" (ByVal lpApplicationName As String, ByVal lpKeyName As String, ByVal lpString As Long, ByVal lplFileName As String)
Declare Function WritePrivateProfileStringToDeleteSection& Lib "kernel32" Alias "WritePrivateProfileStringA" (ByVal lpApplicationName As String, ByVal lpKeyName As Long, ByVal lpString As Long, ByVal lplFileName As String)
#Else
' These are 16 bit declarations based on API16.TXT - some of the parameter names may be different
Declare Function GetPrivateProfileStringByKeyName% Lib "Kernel" Alias "GetPrivateProfileString" (ByVal lpApplicationName$, ByVal lpKeyName$, ByVal lpDefault$, ByVal lpReturnedString$, ByVal nSize%, ByVal lpfilename$)
Declare Function WritePrivateProfileStringByKeyName% Lib "Kernel" Alias "WritePrivateProfileString" (ByVal lpApplicationName$, ByVal lpKeyName$, ByVal lpString$, ByVal lplFileName$)
Declare Function GetPrivateProfileStringKeys% Lib "Kernel" Alias "GetPrivateProfileString" (ByVal lpApplicationName$, ByVal lpKeyName&, ByVal lpDefault$, ByVal lpReturnedString$, ByVal nSize%, ByVal lpfilename$)
Declare Function WritePrivateProfileStringToDeleteKey% Lib "Kernel" Alias "WritePrivateProfileString" (ByVal lpApplicationName$, ByVal lpKeyName$, ByVal lpString&, ByVal lplFileName$)
Declare Function WritePrivateProfileStringToDeleteSection% Lib "Kernel" Alias "WritePrivateProfileString" (ByVal lpApplicationName$, ByVal lpKeyName&, ByVal lpString&, ByVal lplFileName$)
#End If

' End of declarations
'
 
'
' An example of modular programming - This provides a safer
' interface to GetPrivateProfileString
'
Function VBGetPrivateProfileString(section$, key$, file$) As String
    Dim KeyValue$
    #If Win32 Then
        Dim characters As Long
    #Else
        Dim characters As Integer
    #End If
    
    KeyValue$ = String$(128, 0)
    
    characters = GetPrivateProfileStringByKeyName(section$, key$, "", KeyValue$, 127, file$)

    If (characters = 0) Then
        KeyValue$ = ""
    Else
        KeyValue$ = Left$(KeyValue$, characters)
    End If
    
    VBGetPrivateProfileString = KeyValue$

End Function

