#!/bin/bash
# Infinite loop for periodic refresh
while true
do
    echo "🔁 Running auto refresh..."
    python3 task.py
    sleep 600  # Wait 10 minutes
done
