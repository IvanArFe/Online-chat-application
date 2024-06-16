import threading
import grpc
import chat_pb2 as chat
import chat_pb2_grpc as rpc
import sys
import socket
import argparse
import name_server_pb2
import name_server_pb2_grpc
import pika
import json
import time
import tkinter as tk
from tkinter import scrolledtext


address = 'localhost'
port = 33333
direccion_NameServer = 'localhost:50051'



class Client:

    def __init__(self, username: str, partner: str):
        self.username = username
        self.partner = partner
        # Crear un canal gRPC y un stub
        channel = grpc.insecure_channel(address + ':' + str(port))
        self.conn = rpc.ChatServerStub(channel)
        # Crear un hilo nuevo para escuchar mensajes entrantes
        threading.Thread(target=self.__listen_for_messages, daemon=True).start()
        self.send_message()

    def __listen_for_messages(self):
        for note in self.conn.ChatStream(chat.UserPair(sender=self.username, receiver=self.partner)):
            print("[{}] {}".format(note.name, note.message))

    def send_message(self):
        while True:
            message = input()
            if message:
                n = chat.Note()
                n.name = self.username
                n.message = message
                n.receiver = self.partner
                self.conn.SendNote(n)
                
class GroupChatClient:
    def __init__(self, username):
        self.username = username
        self.connection = None
        self.channel = None
        self.exchange_name = 'group_chat'
        self.queues = {}  #Colas suscritas
        self.consume_threads = {}  #Hilos de consumo
        self.reconnecting = False 

    def conectar(self):
        try:
            self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            self.channel = self.connection.channel()
            print("Conectado al servidor RabbitMQ.")
        except Exception as e:
            print(f"Error al conectar al servidor RabbitMQ: {e}")
            self.reconectar()

    def message_callback(self, ch, method, properties, body):
        try:
            sender = properties.headers['username']
            message = body.decode()
            print(f"[{sender}]: {message}")
        except Exception as e:
            print(f"Error en callback de mensaje: {e}")

    def consumir_mensajes(self, queue_name):
        try:
            self.channel.basic_consume(queue=queue_name, on_message_callback=self.message_callback, auto_ack=True)
            self.channel.start_consuming()
        except pika.exceptions.ConnectionClosedByBroker:
            print("Conexión cerrada por el broker, intentando reconectar...")
            self.reconectar()
        except pika.exceptions.AMQPChannelError as e:
            print(f"Error en el canal AMQP: {e}")
            self.reconectar()
        except pika.exceptions.AMQPConnectionError:
            print("Error de conexión AMQP, intentando reconectar...")
            self.reconectar()
        except Exception as e:
            print(f"Error al consumir mensajes del chat grupal: {e}")
            self.reconectar()

    def start_consuming(self, queue_name):
        if queue_name in self.consume_threads and self.consume_threads[queue_name].is_alive():
            print("El hilo de consumo ya está en ejecución.")
            return

        self.consume_threads[queue_name] = threading.Thread(target=self.consumir_mensajes, args=(queue_name,), daemon=True)
        self.consume_threads[queue_name].start()

    def crear_chat_grupal(self, chat_name):
        try:
            self.channel.exchange_declare(exchange=chat_name, exchange_type='fanout')
            print(f"Chat grupal '{chat_name}' creado.")
        except Exception as e:
            print(f"Error al crear chat grupal: {e}")

    def suscribirse_chat(self, chat_name):
        try:
            self.channel.exchange_declare(exchange=chat_name, exchange_type='fanout')
            result = self.channel.queue_declare('', exclusive=True)
            queue_name = result.method.queue
            self.channel.queue_bind(exchange=chat_name, queue=queue_name)
            self.queues[chat_name] = queue_name
            self.start_consuming(queue_name)
            print(f"Suscrito al chat grupal '{chat_name}'.")
        except Exception as e:
            print(f"Error al suscribirse al chat grupal: {e}")

    def enviarMensaje_grupo(self, chat_name, message):
        try:
            if self.channel.is_open:
                self.channel.basic_publish(
                    exchange=chat_name,
                    routing_key='',
                    body=message,
                    properties=pika.BasicProperties(headers={'username': self.username})
                )
                print(f"You: {message}")
            else:
                print("El canal no está abierto para enviar el mensaje.")
                self.reconectar()
        except Exception as e:
            print(f"Error al enviar mensaje al chat grupal: {e}")
            self.reconectar()

    def desuscribirse_chat(self, chat_name):
        try:
            if chat_name in self.queues:
                queue_name = self.queues[chat_name]
                self.channel.queue_unbind(exchange=chat_name, queue=queue_name)
                del self.queues[chat_name]
                print(f"Desuscrito del chat grupal '{chat_name}'.")
            else:
                print(f"No estás suscrito al chat grupal '{chat_name}'.")
        except Exception as e:
            print(f"Error al desuscribirse del chat grupal: {e}")

    def close_connection(self):
        try:
            for queue_name in self.queues.values():
                self.channel.queue_unbind(exchange=self.exchange_name, queue=queue_name)
            if self.channel:
                self.channel.stop_consuming()
                self.channel.close()
                self.channel = None
            if self.connection:
                self.connection.close()
                self.connection = None
            print("Conexión cerrada.")
        except Exception as e:
            print(f"Error al cerrar la conexión: {e}")

    def reconectar(self):
      if not self.reconnecting:
        self.reconnecting = True
        print("Intentando reconectar")
        time.sleep(2)  # Esperar antes de intentar reconectar
        try:
            self.conectar()
            for chat_name in self.queues.keys():
                self.suscribirse_chat(chat_name)
        except Exception as e:
            print(f"Error al intentar reconectar: {e}")
        finally:
            self.reconnecting = False
      

def registrar_usuari(username):
    ip = socket.gethostbyname(socket.gethostname())
    with grpc.insecure_channel(direccion_NameServer) as channel:
        stub = name_server_pb2_grpc.ServidorNombresStub(channel)
        request = name_server_pb2.RegisterRequest(username=username, ip=ip, port=port)
        response = stub.Register(request)
        print("Usuari registrat")
class InsultChat:
    def __init__(self, username):
        self.username = username
        self.connection = None
        self.channel = None
        self.connect_to_rabbitmq()

    def connect_to_rabbitmq(self):
        try:
            self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            self.channel = self.connection.channel()

            # Declare a queue to send and receive insults
            self.channel.queue_declare(queue='insults')
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Error connecting to RabbitMQ: {e}")
            self.reconnect()

    def reconnect(self):
        print("Attempting to reconnect...")
        while True:
            try:
                self.connect_to_rabbitmq()
                break
            except pika.exceptions.AMQPConnectionError:
                time.sleep(5)
                print("Retrying connection...")

    def send_message_to_group(self, message):
        try:
            # Send message to the 'insults' queue
            self.channel.basic_publish(exchange='',
                                       routing_key='insults',
                                       body=json.dumps({'username': self.username, 'message': message}))
        except (pika.exceptions.StreamLostError, pika.exceptions.ConnectionClosed) as e:
            print(f"Stream lost error: {e}")
            self.reconnect()
            self.send_message_to_group(message)

    def start_consuming(self):
        def callback(ch, method, properties, body):
            message = json.loads(body)
            print(f"{message['username']}: {message['message']}")

        def consume():
            while True:
                try:
                    # Start consuming messages from the 'insults' queue
                    self.channel.basic_consume(queue='insults',
                                               on_message_callback=callback,
                                               auto_ack=True)
                    self.channel.start_consuming()
                except (pika.exceptions.StreamLostError, pika.exceptions.ConnectionClosed) as e:
                    print(f"Stream lost error: {e}")
                    self.reconnect()

        print(f"Usuario {self.username}. Escribe tu mensaje")
        thread = threading.Thread(target=consume)
        thread.start()

    def close_connection(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()
class DiscoverChats:
    def __init__(self, username):
        self.username = username
        self.exchange_name = 'discovery'
        self.connection_params = pika.ConnectionParameters('localhost')
        self.response_queue = None

    def enviarEvento(self):
        connection = pika.BlockingConnection(self.connection_params)
        channel = connection.channel()
        channel.exchange_declare(exchange=self.exchange_name, exchange_type='fanout')
        
        discovery_event = {
            'username': self.username,
            'type': 'discovery'
        }
        
        channel.basic_publish(exchange=self.exchange_name, routing_key='', body=json.dumps(discovery_event))
        
        connection.close()

    def escucharEventos(self):
        connection = pika.BlockingConnection(self.connection_params)
        channel = connection.channel()
        
        channel.exchange_declare(exchange=self.exchange_name, exchange_type='fanout')
        result = channel.queue_declare(queue='', exclusive=True)
        self.response_queue = result.method.queue
        
        channel.queue_bind(exchange=self.exchange_name, queue=self.response_queue)
        
        def callback(ch, method, properties, body):
            event = json.loads(body)
            if event['username'] != self.username:
                if event['type'] == 'discovery':
                    # Responder al evento de descubrimiento
                    self.enviarRespuesta(event['username'])
        
        channel.basic_consume(queue=self.response_queue, on_message_callback=callback, auto_ack=True)
        print(f"Escuchando eventos de descubrimiento para {self.username}")
        channel.start_consuming()

    def enviarRespuesta(self, target_username):
        connection = pika.BlockingConnection(self.connection_params)
        channel = connection.channel()
        channel.exchange_declare(exchange=self.exchange_name, exchange_type='fanout')
        
        discovery_response = {
            'username': self.username,
            'type': 'response',
            'target': target_username
        }
        
        channel.basic_publish(exchange=self.exchange_name, routing_key='', body=json.dumps(discovery_response))
        print(f"Respuesta de descubrimiento enviada de {self.username} a {target_username}")
        
        connection.close()

    def escucharRespuestas(self):
        connection = pika.BlockingConnection(self.connection_params)
        channel = connection.channel()
        
        channel.exchange_declare(exchange=self.exchange_name, exchange_type='fanout')
        result = channel.queue_declare(queue='', exclusive=True)
        response_queue = result.method.queue
        
        channel.queue_bind(exchange=self.exchange_name, queue=response_queue)
        
        def callback(ch, method, properties, body):
            response = json.loads(body)
            if response['username'] != self.username and response['type'] == 'response' and response['target'] == self.username:
                print(f"Respuesta de descubrimiento recibida por: {response['username']}")
        
        channel.basic_consume(queue=response_queue, on_message_callback=callback, auto_ack=True)
        print(f"Esperando respuestas de descubrimiento para {self.username}")
        channel.start_consuming()

    def start(self):
        discovery_thread = threading.Thread(target=self.escucharEventos)
        discovery_thread.start()

        response_thread = threading.Thread(target=self.escucharRespuestas)
        response_thread.start()
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Cliente de chat privado gRPC')
    parser.add_argument('--username', required=True, help='Nombre de usuario')
    args = parser.parse_args()
    username = args.username


    registrar_usuari(username)

    option = None
    while option not in ["1", "2", "3", "4", "5"]:
        print("----- Menú de Opciones -----")
        print("1. Conectarse a un chat privado")
        print("2. Conectarse a un chat grupal")
        print("3. Descubrir chats")
        print("4. Conectarse a un chat de insultos")
        print("5. Salir")
        option = input("Seleccione una opción (1-5): ").strip()

    if option == "1":
        partner = None
        while not partner:
           partner = input("Ingresa el nombre del usuario con el que quieres conectarte: ").strip()

        Client(username, partner)
        
        
    elif option == "2":
            try:
                    client = GroupChatClient(username)
                    client.conectar()
                    
                    while True:
                         print("1. Crear chat grupal")
                         print("2. Suscribirse a chat grupal")
                         print("3. Enviar mensaje a chat grupal")
                         print("4. Desuscribirse de chat grupal")
                         print("5. Salir")
                         choice = input("Seleccione una opción: ")
                         if choice == "1":
                             chat_name = input("Escribe el nombre del grupo: ")
                             client.crear_chat_grupal(chat_name)
                         elif choice == "2":
                             chat_name = input("Escribe el nombre del grupo: ")
                             client.suscribirse_chat(chat_name)
                         elif choice == "3":
                             chat_name = input("Escribe el nombre del grupo: ")
                             while True:
                                 message = input("")
                                 if message.lower() == 'salir':
                                      break
                                 client.enviarMensaje_grupo(chat_name, message)
                         elif choice == "4":
                             chat_name = input("Escribe el nombre del grupo: ")
                             client.desuscribirse_chat(chat_name)
                         elif choice == "5":
                             client.close_connection()
                             break
                         else:
                             print("Opción no válida.")       
            except KeyboardInterrupt:
                pass
            finally:
                client.close_connection()
    elif option == "3":
        discover = DiscoverChats(username)
        discover.start()
        input("Enter para enviar un evento de descubrimiento")
        discover.enviarEvento()
        
    elif option == "4":
        group_client = InsultChat(username)
        group_client.connect_to_rabbitmq()
        group_client.start_consuming()

        try:
            while True:
                  message = input("")
                  if message.lower() == 'salir':
                      break
                  group_client.send_message_to_group(message)
        except KeyboardInterrupt:
            pass
        finally:
            group_client.close_connection()
        
    elif option == "5":
        print("Saliendo...")
        sys.exit()

