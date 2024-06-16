#!/bin/bash

echo "Iniciando Redis"
if pgrep -x "redis-server" > /dev/null
then
    echo "Redis ya está ejecutándose."
else
    redis-server &
    sleep 5
    if pgrep -x "redis-server" > /dev/null
    then
        echo "Redis iniciado correctamente."
    else
        echo "Error al iniciar Redis."
        exit 1
    fi
fi

echo "Iniciando RabbitMQ..."
sudo systemctl start rabbitmq-server &
sleep 10
if sudo systemctl is-active --quiet rabbitmq-server
then
    echo "RabbitMQ iniciado correctamente."
else
    echo "Error al iniciar RabbitMQ."
    exit 1
fi

echo "Iniciando el servidor gRPC..."
python3 server.py &
sleep 5
if pgrep -f "python3 server.py" > /dev/null
then
    echo "Servidor gRPC iniciado correctamente."
else
    echo "Error al iniciar el servidor gRPC."
    exit 1
fi

echo "Iniciando NameServer..."
python3 NameServer.py &
sleep 5
if pgrep -f "python3 NameServer.py" > /dev/null
then
    echo "NameServer iniciado correctamente."
else
    echo "Error al iniciar NameServer."
    exit 1
fi

wait

