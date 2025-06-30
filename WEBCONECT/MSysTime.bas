Attribute VB_Name = "MSysTime"
Option Explicit
'**********************************
'**  Type Definitions:

#If Win32 Then
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

Public Type TIME_ZONE_INFORMATION
        Bias As Long
        StandardName As String * 64
        StandardDate As SYSTEMTIME
        StandardBias As Long
        DaylightName As String * 64
        DaylightDate As SYSTEMTIME
        DaylightBias As Long
End Type

#End If 'WIN32 Types

'**********************************
'**  Function Declarations:

#If Win32 Then
Public Declare Sub GetSystemTime Lib "kernel32" (lpSystemTime As SYSTEMTIME)
#End If 'WIN32
