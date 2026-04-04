Set shell = CreateObject("WScript.Shell")
shell.Run "cmd /c """ & Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\")) & "iniciar.bat""", 0, False
