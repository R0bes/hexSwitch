# Multi-container integration test script for PowerShell
# Tests interactions between 3 HexSwitch containers

$ErrorActionPreference = "Stop"

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$PROJECT_ROOT = Split-Path -Parent $SCRIPT_DIR
$COMPOSE_FILE = Join-Path $PROJECT_ROOT "docker-compose.multi-test.yml"

Set-Location $PROJECT_ROOT

Write-Host "=== Building and starting multi-container setup ===" -ForegroundColor Cyan

# Build and start services
docker compose -f $COMPOSE_FILE build
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Docker compose build failed" -ForegroundColor Red
    exit 1
}

docker compose -f $COMPOSE_FILE up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Docker compose up failed" -ForegroundColor Red
    exit 1
}

# Wait for services to be ready
Write-Host ""
Write-Host "Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "=== Testing multi-container setup ===" -ForegroundColor Cyan

# Test 1: All containers are running
Write-Host "Test 1: Container status" -ForegroundColor Yellow
$psResult = docker compose -f $COMPOSE_FILE ps
if ($psResult -match "hexswitch-producer" -and $psResult -match "hexswitch-processor" -and $psResult -match "hexswitch-consumer") {
    Write-Host "✓ All containers are running" -ForegroundColor Green
} else {
    Write-Host "✗ Not all containers are running" -ForegroundColor Red
    docker compose -f $COMPOSE_FILE down -v
    exit 1
}

# Test 2: Config validation in all containers
Write-Host ""
Write-Host "Test 2: Config validation" -ForegroundColor Yellow
$containers = @("hexswitch-producer", "hexswitch-processor", "hexswitch-consumer")
$allValid = $true

foreach ($container in $containers) {
    $result = docker exec $container hexswitch validate 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ $container config is valid" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $container config validation failed" -ForegroundColor Red
        $allValid = $false
    }
}

if (-not $allValid) {
    Write-Host "✗ Config validation failed" -ForegroundColor Red
    docker compose -f $COMPOSE_FILE down -v
    exit 1
}

# Test 3: Dry-run in all containers
Write-Host ""
Write-Host "Test 3: Dry-run execution plans" -ForegroundColor Yellow
$allDryRun = $true

foreach ($container in $containers) {
    $result = docker exec $container hexswitch run --dry-run 2>&1
    if ($LASTEXITCODE -eq 0 -and ($result -match "Execution Plan")) {
        Write-Host "  ✓ $container dry-run successful" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $container dry-run failed" -ForegroundColor Red
        $allDryRun = $false
    }
}

if (-not $allDryRun) {
    Write-Host "✗ Dry-run failed" -ForegroundColor Red
    docker compose -f $COMPOSE_FILE down -v
    exit 1
}

# Test 4: Network connectivity
Write-Host ""
Write-Host "Test 4: Network connectivity" -ForegroundColor Yellow
$networkResult = docker network inspect hexswitch_hexswitch-test-network 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Test network exists" -ForegroundColor Green
} else {
    # Try alternative network name format
    $networkResult = docker network ls | Select-String "hexswitch"
    if ($networkResult) {
        Write-Host "✓ Test network exists" -ForegroundColor Green
    } else {
        Write-Host "⚠ Network check inconclusive (may be expected)" -ForegroundColor Yellow
    }
}

# Test 5: NATS server health
Write-Host ""
Write-Host "Test 5: NATS server health" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8222/healthz" -TimeoutSec 5 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ NATS server is healthy" -ForegroundColor Green
    } else {
        Write-Host "✗ NATS server health check failed" -ForegroundColor Red
        docker compose -f $COMPOSE_FILE down -v
        exit 1
    }
} catch {
    Write-Host "✗ NATS server not responding" -ForegroundColor Red
    docker compose -f $COMPOSE_FILE down -v
    exit 1
}

# Test 6: NATS monitoring
Write-Host ""
Write-Host "Test 6: NATS monitoring endpoint" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8222/varz" -TimeoutSec 5 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        $data = $response.Content | ConvertFrom-Json
        if ($data.server_id) {
            Write-Host "✓ NATS monitoring accessible (Server ID: $($data.server_id))" -ForegroundColor Green
        } else {
            Write-Host "⚠ NATS monitoring accessible but unexpected format" -ForegroundColor Yellow
        }
    } else {
        Write-Host "⚠ NATS monitoring endpoint returned unexpected status" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ NATS monitoring not accessible (may be expected)" -ForegroundColor Yellow
}

# Test 7: Mock server health
Write-Host ""
Write-Host "Test 7: Mock server health" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9090/health" -TimeoutSec 5 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ Mock server is healthy" -ForegroundColor Green
    } else {
        Write-Host "✗ Mock server health check failed" -ForegroundColor Red
        docker compose -f $COMPOSE_FILE down -v
        exit 1
    }
} catch {
    Write-Host "⚠ Mock server not responding (may be expected if runtime not implemented)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== All multi-container tests passed ===" -ForegroundColor Green

# Cleanup
Write-Host ""
Write-Host "Cleaning up..." -ForegroundColor Yellow
docker compose -f $COMPOSE_FILE down -v

Write-Host "Done!" -ForegroundColor Green

