#Requires -Version 5.1
<#
.SYNOPSIS
    Monitor de citas del Ayuntamiento de Fuenlabrada.
    Envía notificación push vía ntfy.sh cuando aparecen citas nuevas.

.NOTES
    Variable de entorno requerida: NTFY_TOPIC
    Ejecutar desde el Programador de tareas de Windows.
#>

# -----------------------------
# Configuración de servicios
# -----------------------------

$SERVICIOS = @(
    @{
        id      = "padron_ayto"
        nombre  = "Padrón (Altas, Cambios, Modif, Renovación)"
        centro  = "Ayuntamiento de Fuenlabrada"
        url     = "https://citaprevia.ayto-fuenlabrada.es/qsige.localizador/citaPrevia/disponible/centro/1/servicio/1/calendario"
        enlace  = "https://citaprevia.ayto-fuenlabrada.es/citaprevia/#/es/home?uuid=0242a-85e2-064a3-a1eb"
    },
    @{
        id      = "padron_jmd_loranca"
        nombre  = "Padrón (Altas, Cambios, Modif, Renovación)"
        centro  = "JMD Loranca"
        url     = "https://citaprevia.ayto-fuenlabrada.es/qsige.localizador/citaPrevia/disponible/centro/3/servicio/1/calendario"
        enlace  = "https://citaprevia.ayto-fuenlabrada.es/citaprevia/#/es/home?uuid=0242a-85e2-064a3-a1eb"
    },
    @{
        id      = "padron_jmd_vivero"
        nombre  = "Padrón (Altas, Cambios, Modif, Renovación)"
        centro  = "JMD Vivero"
        url     = "https://citaprevia.ayto-fuenlabrada.es/qsige.localizador/citaPrevia/disponible/centro/4/servicio/1/calendario"
        enlace  = "https://citaprevia.ayto-fuenlabrada.es/citaprevia/#/es/home?uuid=0242a-85e2-064a3-a1eb"
    }
)

# -----------------------------
# Rutas (relativas al script)
# -----------------------------

$SCRIPT_DIR  = $PSScriptRoot
$ESTADO_FILE = Join-Path $SCRIPT_DIR "estado.json"
$LOG_FILE    = Join-Path $SCRIPT_DIR "monitor.log"

# -----------------------------
# Configuración ntfy
# -----------------------------

$NTFY_TOPIC = "fuenlabrada-padron-abc123"

# -----------------------------
# Logging
# -----------------------------

function Write-Log {
    param(
        [string]$Message,
        [ValidateSet("INFO","ERROR","WARN")]
        [string]$Level = "INFO"
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "$timestamp | $Level | $Message"
    Add-Content -Path $LOG_FILE -Value $line -Encoding UTF8
    Write-Host $line
}

# -----------------------------
# Funciones auxiliares
# -----------------------------

function Get-Estado {
    if (-not (Test-Path $ESTADO_FILE)) {
        return @{}
    }
    try {
        $json = Get-Content $ESTADO_FILE -Raw -Encoding UTF8
        $obj  = $json | ConvertFrom-Json
        # Convertir PSCustomObject a hashtable de arrays de fechas
        $ht = @{}
        $obj.PSObject.Properties | ForEach-Object {
            $ht[$_.Name] = @($_.Value | Where-Object { $_ -is [string] })
        }
        return $ht
    }
    catch {
        Write-Log "Error leyendo estado.json: $_" "WARN"
        return @{}
    }
}

function Save-Estado {
    param([hashtable]$Estado)
    try {
        $Estado | ConvertTo-Json -Depth 3 | Set-Content $ESTADO_FILE -Encoding UTF8
    }
    catch {
        Write-Log "Error guardando estado.json: $_" "ERROR"
    }
}

function Format-Fecha {
    param([string]$Fecha)

    $diasSemana = @("lunes","martes","miércoles","jueves","viernes","sábado","domingo")
    try {
        $fechaObj = [datetime]::ParseExact($Fecha, "yyyy-MM-dd", $null)
        # DayOfWeek: Sunday=0 … Saturday=6; convertimos al índice lunes=0
        $dow = [int]$fechaObj.DayOfWeek
        $idx = if ($dow -eq 0) { 6 } else { $dow - 1 }
        return "$($diasSemana[$idx]) $($fechaObj.ToString('dd/MM'))"
    }
    catch {
        return $Fecha
    }
}

function Invoke-Servicio {
    param([hashtable]$Servicio)

    Write-Log "Consultando $($Servicio.nombre) – $($Servicio.centro)"

    try {
        $respuesta = Invoke-RestMethod -Uri $Servicio.url -Method Get -TimeoutSec 20 -ErrorAction Stop
        $disponibles = @(
            $respuesta.dias |
            Where-Object { $_.estado -eq 0 } |
            Select-Object -ExpandProperty dia
        )
        return $disponibles
    }
    catch {
        Write-Log "Error HTTP en $($Servicio.centro): $_" "ERROR"
        return @()
    }
}

function Send-Ntfy {
    param([string]$Mensaje)

    try {
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($Mensaje)
        $headers = @{
            "Title"    = "Citas disponibles"
            "Priority" = "5"
            "Tags"     = "calendar,white_check_mark"
        }
        Invoke-RestMethod `
            -Uri "https://ntfy.sh/$NTFY_TOPIC" `
            -Method Post `
            -Body $bytes `
            -Headers $headers `
            -ContentType "text/plain; charset=utf-8" `
            -TimeoutSec 10 `
            -ErrorAction Stop | Out-Null

        Write-Log "Notificación enviada"
    }
    catch {
        Write-Log "Error enviando ntfy: $_" "ERROR"
    }
}

# -----------------------------
# Programa principal
# -----------------------------

$estadoAnterior = Get-Estado
$estadoActual   = @{}
$avisos         = @()

foreach ($servicio in $SERVICIOS) {
    $fechas = Invoke-Servicio -Servicio $servicio

    # Guardar las fechas actuales (array de strings)
    $estadoActual[$servicio.id] = $fechas

    if ($fechas.Count -gt 0) {
        $fechasFormateadas = ($fechas | ForEach-Object { Format-Fecha $_ }) -join ", "
        Write-Log "$($servicio.centro) – fechas disponibles: $fechasFormateadas"
    }

    # Fechas que no estaban en la ejecución anterior
    $fechasAnteriores = @($estadoAnterior[$servicio.id])
    $fechasNuevas = @($fechas | Where-Object { $_ -notin $fechasAnteriores })

    if ($fechasNuevas.Count -gt 0) {

        $textoFechas = ($fechasNuevas | ForEach-Object { "• $(Format-Fecha $_)" }) -join "`n"

        $avisos += @"
📍 $($servicio.centro)
📝 $($servicio.nombre)

📅 Fechas nuevas:
$textoFechas

🔗 $($servicio.enlace)
"@
    }
}

if ($avisos.Count -gt 0) {
    $mensaje = "🟢 ¡Hay citas disponibles!`n`n" + ($avisos -join "`n`n")
    Send-Ntfy -Mensaje $mensaje
}
else {
    Write-Log "Sin novedades"
}

Save-Estado -Estado $estadoActual
