$ErrorActionPreference = 'Stop'

$App = 'E:\glessgroupfastapi'
$TaskFolder = '\GlessAPI\'

$Jobs = @(
    @{ Name = 'Активация менеджеров call-центра'; Path = '/api/v1/activatemanagersonday'; At = '01:00' }
)

foreach ($job in $Jobs) {
    $action = New-ScheduledTaskAction -Execute 'powershell.exe' `
        -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$App\deploy\call-endpoint.ps1`" -Path $($job.Path)"
    $trigger = New-ScheduledTaskTrigger -Daily -At $job.At
    $principal = New-ScheduledTaskPrincipal -UserId 'SYSTEM' -LogonType ServiceAccount
    $settings = New-ScheduledTaskSettingsSet `
        -StartWhenAvailable `
        -MultipleInstances IgnoreNew `
        -ExecutionTimeLimit (New-TimeSpan -Minutes 10)

    Register-ScheduledTask -TaskPath $TaskFolder -TaskName $job.Name `
        -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null

    Write-Host "Задача '$($job.Name)': POST $($job.Path) ежедневно в $($job.At)"
}