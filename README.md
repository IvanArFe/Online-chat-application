#Online chat application

## Descripción

Esta práctica trata de desarrollar una aplicación de chat en línea que se centra en trabajar los diferentes patrones de comunicación de un sistema distribuido. La aplicación tiene diversas funcionalidades:

- **Chats privados**: Comunicación directa entre dos usuarios.
- **Chats grupales**: Comunicación entre múltiples usuarios.
- **Descubrimiento de chats**: Descubrir y chats disponibles.
- **Chat insultos**: Comunicación entre múltiples usuarios.

1. Iniciar el servidor gRPC, NameServer y los servicios de Redis y RabbitMQ:
	./start-server.sh
	
2. Iniciar tantos clientes como quieras:
	./start-client.sh
