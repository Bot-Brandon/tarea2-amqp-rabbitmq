param([ValidateSet('todas','P01','P02','P03')][string]$Prueba = 'todas')
$ErrorActionPreference = 'Stop'
Push-Location (Split-Path $PSScriptRoot -Parent)
try {
    docker info --format '{{.ServerVersion}}'
    if ($LASTEXITCODE -ne 0) { throw 'El motor Docker no esta listo. Abre Docker Desktop.' }
    docker compose up -d --wait rabbitmq
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo iniciar RabbitMQ.' }
    docker compose build cliente
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo construir el cliente.' }
    docker compose run --rm cliente $Prueba 2>&1 | Tee-Object -FilePath "evidencias/$Prueba-cliente.log"
    if ($LASTEXITCODE -ne 0) { throw 'Fallo una prueba. Revisar logs.' }
    docker compose logs --no-color rabbitmq | Out-File -Encoding utf8 evidencias/servidor.log
    docker compose images | Out-File -Encoding utf8 evidencias/imagenes.txt
    Write-Output "Pruebas completadas. Captura: evidencias/$Prueba.pcap"
} finally { Pop-Location }
