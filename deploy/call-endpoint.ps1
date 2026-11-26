param(
    [Parameter(Mandatory)] [string]$Path,
    [string]$HostName = 'apigless.gless.group',
    [string]$LogDir = 'E:\glessgroupfastapi\logs\scheduled',
    [int]$TimeoutSec = 180
)

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$logName = ($Path.Trim('/') -replace '[^\w]+', '_') + '.log'
$logFile = Join-Path $LogDir $logName
$bodyFile = New-TemporaryFile

$code = & curl.exe -sS -X POST --max-time $TimeoutSec `
    --resolve "${HostName}:443:127.0.0.1" `
    -o $bodyFile.FullName -w '%{http_code}' "https://$HostName$Path"
$curlExit = $LASTEXITCODE

$body = Get-Content $bodyFile.FullName -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
Remove-Item $bodyFile.FullName -Force

$stamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
Add-Content -Path $logFile -Encoding UTF8 -Value "$stamp POST $Path -> HTTP $code (curl exit $curlExit)`r`n$body`r`n"

if ($curlExit -ne 0 -or [int]$code -lt 200 -or [int]$code -ge 300) { exit 1 }
exit 0