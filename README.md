# ayto-monitor
# Monitor de citas Ayuntamiento Fuenlabrada

Monitor automático que consulta disponibilidad de citas y avisa mediante ntfy.

## Configuración

Crear un secreto:

Settings → Secrets → Actions

Nombre:

NTFY_TOPIC

Valor:

tu-tema-ntfy

## Ejecución manual

Actions → Monitor citas → Run workflow

## Frecuencia

Cada 5 minutos.

## Funcionamiento

Solo envía aviso cuando aparecen fechas nuevas que no estaban en la consulta anterior.

---

## Programador de tareas de Windows (monitor.ps1)

### 1. Configurar el topic de ntfy

Edita `monitor.ps1` y sustituye `"tu-topic-aqui"` por tu topic real:

```powershell
$NTFY_TOPIC = "mi-topic-real"
```

### 2. Crear la tarea

Abre PowerShell como administrador y ejecuta:

```powershell
$scriptPath = "C:\dv\Dev\Personal\ayto-monitor\monitor.ps1"

$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NonInteractive -ExecutionPolicy Bypass -File `"$scriptPath`""

# Repetir cada 10 minutos indefinidamente
$trigger = New-ScheduledTaskTrigger `
    -Once `
    -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Minutes 10)

$settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 2) `
    -StartWhenAvailable

Register-ScheduledTask `
    -TaskName    "AytoMonitor" `
    -Action      $action `
    -Trigger     $trigger `
    -Settings    $settings `
    -Description "Monitor de citas ayto-fuenlabrada" `
    -RunLevel    Highest `
    -Force
```

Ajusta `-Minutes 10` al intervalo que prefieras.

### 3. Verificar

```powershell
# Ver estado de la tarea
Get-ScheduledTask -TaskName "AytoMonitor" | Select-Object TaskName, State

# Ejecutar manualmente
Start-ScheduledTask -TaskName "AytoMonitor"

# Revisar el log
Get-Content "C:\dv\Dev\Personal\ayto-monitor\monitor.log" -Tail 20
```

### 4. Eliminar la tarea

```powershell
Unregister-ScheduledTask -TaskName "AytoMonitor" -Confirm:$false
```

