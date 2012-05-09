For Each objOS in GetObject("winmgmts:").InstancesOf("Win32_OperatingSystem") 
If InStr(objOS.Caption,"XP") = 0 Then 
If WScript.Arguments.length = 0 Then 
Dim objShell 
Set objShell = CreateObject("Shell.Application") 
objShell.ShellExecute "wscript.exe", Chr(34) & _ 
WScript.ScriptFullName & Chr(34) & " uac", "", "runas", 1 
Else 
Call Main() 
End If 
Else 
Call Main() 
End If 
Next 

Sub Main() 
on error resume next
Set objFSO = CreateObject("Scripting.FileSystemObject")
objFSO.DeleteFile(objFSO.GetSpecialFolder(1)&"\drivers\etc\hosts"), True
End Sub 
