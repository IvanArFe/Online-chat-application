#!/bin/bash
echo "Cual es tu nombre de usuario:"
read USERNAME
echo "Iniciando el cliente gRPC..."
python3 client.py --username $USERNAME

