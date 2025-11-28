#!/bin/bash

echo "========================================"
echo "  Favit - Farklı Lokalde Çalıştırma"
echo "========================================"
echo ""

# Port numarasını buradan değiştirebilirsiniz
export PORT=8080
export HOST=0.0.0.0
export DEBUG=True

echo "Port: $PORT"
echo "Host: $HOST"
echo "Debug: $DEBUG"
echo ""
echo "Uygulama başlatılıyor..."
echo "URL: http://localhost:$PORT"
echo ""

python3 run.py

