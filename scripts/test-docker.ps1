# Docker integration test script for PowerShell
# Tests the Docker image with various scenarios

$ErrorActionPreference = "Stop"

$IMAGE_NAME = "hexswitch:test"
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$PROJECT_ROOT = Split-Path -Parent $SCRIPT_DIR

Set-Location $PROJECT_ROOT

Write-Host "=== Building Docker image ===" -ForegroundColor Cyan
docker build -f docker/Dockerfile -t $IMAGE_NAME .

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Docker build failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== Testing Docker image ===" -ForegroundColor Cyan

# Test 1: Version command
Write-Host "Test 1: Version command" -ForegroundColor Yellow
$result = docker run --rm $IMAGE_NAME hexswitch version
if ($LASTEXITCODE -eq 0 -and $result -match "HexSwitch") {
    Write-Host "✓ Version command passed" -ForegroundColor Green
} else {
    Write-Host "✗ Version command failed" -ForegroundColor Red
    exit 1
}

# Test 2: Help command
Write-Host ""
Write-Host "Test 2: Help command" -ForegroundColor Yellow
$result = docker run --rm $IMAGE_NAME hexswitch --help
if ($LASTEXITCODE -eq 0 -and $result -match "HexSwitch") {
    Write-Host "✓ Help command passed" -ForegroundColor Green
} else {
    Write-Host "✗ Help command failed" -ForegroundColor Red
    exit 1
}

# Test 3: Init command
Write-Host ""
Write-Host "Test 3: Init command" -ForegroundColor Yellow
$result = docker run --rm $IMAGE_NAME hexswitch init 2>&1
if ($LASTEXITCODE -eq 0 -and ($result -match "Created example configuration")) {
    Write-Host "✓ Init command passed" -ForegroundColor Green
} else {
    Write-Host "✗ Init command failed" -ForegroundColor Red
    exit 1
}

# Test 4: Validate with mounted config
Write-Host ""
Write-Host "Test 4: Validate with mounted config" -ForegroundColor Yellow
if (Test-Path "hex-config.yaml") {
    $configPath = (Resolve-Path "hex-config.yaml").Path
    $result = docker run --rm -v "${configPath}:/app/hex-config.yaml:ro" $IMAGE_NAME hexswitch validate 2>&1
    if ($LASTEXITCODE -eq 0 -and ($result -match "valid")) {
        Write-Host "✓ Validate command passed" -ForegroundColor Green
    } else {
        Write-Host "✗ Validate command failed" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "⚠ hex-config.yaml not found, skipping validate test" -ForegroundColor Yellow
}

# Test 5: Dry-run with mounted config
Write-Host ""
Write-Host "Test 5: Dry-run with mounted config" -ForegroundColor Yellow
if (Test-Path "hex-config.yaml") {
    $configPath = (Resolve-Path "hex-config.yaml").Path
    $result = docker run --rm -v "${configPath}:/app/hex-config.yaml:ro" $IMAGE_NAME hexswitch run --dry-run 2>&1
    if ($LASTEXITCODE -eq 0 -and ($result -match "Execution Plan")) {
        Write-Host "✓ Dry-run command passed" -ForegroundColor Green
    } else {
        Write-Host "✗ Dry-run command failed" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "⚠ hex-config.yaml not found, skipping dry-run test" -ForegroundColor Yellow
}

# Test 6: Python module import
Write-Host ""
Write-Host "Test 6: Python module import" -ForegroundColor Yellow
$result = docker run --rm $IMAGE_NAME python -c "import hexswitch; print(hexswitch.__version__)"
if ($LASTEXITCODE -eq 0 -and $result -match "0.1.0") {
    Write-Host "✓ Python module import passed" -ForegroundColor Green
} else {
    Write-Host "✗ Python module import failed" -ForegroundColor Red
    exit 1
}

# Test 7: Non-root user
Write-Host ""
Write-Host "Test 7: Non-root user check" -ForegroundColor Yellow
$userId = docker run --rm $IMAGE_NAME id -u
if ($LASTEXITCODE -eq 0 -and $userId.Trim() -eq "1000") {
    Write-Host "✓ Non-root user check passed (UID: $($userId.Trim()))" -ForegroundColor Green
} else {
    Write-Host "✗ Non-root user check failed (UID: $($userId.Trim()), expected 1000)" -ForegroundColor Red
    exit 1
}

# Test 8: Default command
Write-Host ""
Write-Host "Test 8: Default command (help)" -ForegroundColor Yellow
$result = docker run --rm $IMAGE_NAME
if ($LASTEXITCODE -eq 0 -and $result -match "HexSwitch") {
    Write-Host "✓ Default command passed" -ForegroundColor Green
} else {
    Write-Host "✗ Default command failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== All Docker tests passed ===" -ForegroundColor Green

