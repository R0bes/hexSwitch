#!/bin/bash
# Docker integration test script
# Tests the Docker image with various scenarios

set -e

IMAGE_NAME="hexswitch:test"
TEST_DIR=$(dirname "$0")/..
cd "$TEST_DIR"

echo "=== Building Docker image ==="
docker build -f docker/Dockerfile -t "$IMAGE_NAME" .

echo ""
echo "=== Testing Docker image ==="

# Test 1: Version command
echo "Test 1: Version command"
docker run --rm "$IMAGE_NAME" hexswitch version
echo "✓ Version command passed"

# Test 2: Help command
echo ""
echo "Test 2: Help command"
docker run --rm "$IMAGE_NAME" hexswitch --help | grep -q "HexSwitch" && echo "✓ Help command passed"

# Test 3: Init command
echo ""
echo "Test 3: Init command"
docker run --rm "$IMAGE_NAME" hexswitch init | grep -q "Created example configuration" && echo "✓ Init command passed"

# Test 4: Validate with mounted config
echo ""
echo "Test 4: Validate with mounted config"
if [ -f hex-config.yaml ]; then
    docker run --rm -v "$(pwd)/hex-config.yaml:/app/hex-config.yaml:ro" "$IMAGE_NAME" hexswitch validate | grep -q "valid" && echo "✓ Validate command passed"
else
    echo "⚠ hex-config.yaml not found, skipping validate test"
fi

# Test 5: Dry-run with mounted config
echo ""
echo "Test 5: Dry-run with mounted config"
if [ -f hex-config.yaml ]; then
    docker run --rm -v "$(pwd)/hex-config.yaml:/app/hex-config.yaml:ro" "$IMAGE_NAME" hexswitch run --dry-run | grep -q "Execution Plan" && echo "✓ Dry-run command passed"
else
    echo "⚠ hex-config.yaml not found, skipping dry-run test"
fi

# Test 6: Python module import
echo ""
echo "Test 6: Python module import"
docker run --rm "$IMAGE_NAME" python -c "import hexswitch; print(hexswitch.__version__)" | grep -q "0.1.0" && echo "✓ Python module import passed"

# Test 7: Non-root user
echo ""
echo "Test 7: Non-root user check"
USER_ID=$(docker run --rm "$IMAGE_NAME" id -u)
if [ "$USER_ID" = "1000" ]; then
    echo "✓ Non-root user check passed (UID: $USER_ID)"
else
    echo "✗ Non-root user check failed (UID: $USER_ID, expected 1000)"
    exit 1
fi

# Test 8: Default command
echo ""
echo "Test 8: Default command (help)"
docker run --rm "$IMAGE_NAME" | grep -q "HexSwitch" && echo "✓ Default command passed"

echo ""
echo "=== All Docker tests passed ==="

