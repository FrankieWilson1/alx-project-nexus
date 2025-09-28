#!/bin/sh

# Use arguments provided to the script (e.g., rabbitmq 5672)
# If no arguments are provided, default to db 5432
HOST=${1:-"db"} 
PORT=${2:-"5432"}
TIMEOUT=30 # Increased timeout for robustness

echo "Waiting for service $HOST:$PORT to be ready..."

for i in $(seq $TIMEOUT); do
    # Checks if port is open
    if nc -z $HOST $PORT; then # Use the argument variables
        echo "Service $HOST:$PORT is ready after $i seconds."
        exit 0
    fi
    echo -n "."
    sleep 1
done

echo "Service $HOST:$PORT not ready after $TIMEOUT seconds. Exiting."
exit 1
