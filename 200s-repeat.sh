#!/bin/bash
REPETITIONS=100
echo "Starting generic test..."
for i in $(seq 1 $REPETITIONS); do
  echo "---"
  curl -X GET -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY5MjljY2EyNjZkNDhlMmVjNzBkYjk4MCIsInVzZXJuYW1lIjoidXNlciIsImlhdCI6MTc2NDQwNjQyNCwiZXhwIjoxNzY0NDEwMDI0fQ.OkiCawgJVXDPtU84XYNMcXB0RHeGQiqJ3RWT9CD9AXg" "https://api.eltayeb.online/customers"
  sleep 1 
done
echo "---"
echo "Test finished."