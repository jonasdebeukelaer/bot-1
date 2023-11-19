#!/bin/bash
set -e

echo "Running bot-1..."

echo ""
echo "check secrets file exists"
ls /mnt2/

echo ""
echo "Load secrets..."
cat /mnt2/secrets.env > .env

echo ""
echo "Start dummy server..."
python src/dummy_server.py 8080 &

echo ""
echo "Start application..."
python src/bot/main.py

echo ""
echo "Stopped gracefully!"
