$shell = New-Object -ComObject WScript.Shell
$desktop = [Environment]::GetFolderPath('Desktop')
$shortcut = $shell.CreateShortcut("$desktop\Olala Viajes.lnk")
$shortcut.TargetPath = "wscript.exe"
$shortcut.Arguments = """$env:USERPROFILE\olala-viajes\iniciar_silencioso.vbs"""
$shortcut.WorkingDirectory = "$env:USERPROFILE\olala-viajes"
$shortcut.WindowStyle = 1
$shortcut.Description = "Iniciar Olala Viajes"
$shortcut.Save()
Write-Host "Acceso directo creado en el escritorio."
