Main()

Sub Main()
	call del_old_hosts
	call cp_hosts
	call del_ins_folder
	call killself
End Sub

Sub del_old_hosts
	on error resume next
	Set objFSO = CreateObject("Scripting.FileSystemObject")
	objFSO.DeleteFile(objFSO.GetSpecialFolder(1)&"\drivers\etc\hosts"), True
End Sub

Sub del_ins_folder
	Set wshShell = CreateObject("WScript.Shell")
	set objFSO=createobject("Scripting.FileSystemObject")
	on error resume next
	objFSO.DeleteFolder(wshShell.ExpandEnvironmentStrings("%PROGRAMFILES%")&"\Huhamhire Technology")
End Sub

Sub cp_hosts
	Const OverwriteExisting = True
	Set objFSO = CreateObject("Scripting.FileSystemObject")
	Set wshShell = CreateObject("WScript.Shell")
	on error resume next
	source = wshShell.ExpandEnvironmentStrings("%PROGRAMFILES%")&"\Huhamhire Technology\hosts file\Install Sources\hosts"
	target = objFSO.GetSpecialFolder(1)&"\drivers\etc\"
	objFSO.CopyFile source , target, OverwriteExisting
End sub

Sub killself
	set objFSO=createobject("Scripting.FileSystemObject")
	on error resume next
	objFSO.DeleteFile(WScript.ScriptName) 
End Sub