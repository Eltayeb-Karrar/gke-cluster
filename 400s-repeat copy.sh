#!/bin/bash
REPETITIONS=100
echo "Starting generic test..."
for i in $(seq 1 $REPETITIONS); do
  echo "---"
  curl -X GET "https://api.eltayeb.online/i-send-wrong"
  sleep 1 
done
echo "---"
echo "Test finished."