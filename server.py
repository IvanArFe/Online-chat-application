from concurrent import futures
import grpc
import time

import chat_pb2 as chat
import chat_pb2_grpc


class ChatServer(chat_pb2_grpc.ChatServerServicer):

    def __init__(self):
        self.chats = []

    def ChatStream(self, request, context):
        lastindex = 0
        while True:
            while len(self.chats) > lastindex:
                n = self.chats[lastindex]
                #Verificamos si el mensaje es entre el remitente y el receptor especificados
                if (n.name == request.sender and n.receiver == request.receiver) or \
                   (n.name == request.receiver and n.receiver == request.sender):
                    yield n
                lastindex += 1

    def SendNote(self, request, context):
        print("[{} -> {}] {}".format(request.name, request.receiver, request.message))
        self.chats.append(request)
        return chat.Empty()


def serve():
    port = 33333
    servidor = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ChatServerServicer_to_server(ChatServer(), servidor)
    print('Server iniciado')
    servidor.add_insecure_port('[::]:' + str(port))

    servidor.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        servidor.stop(0)

if __name__ == '__main__':
    serve()

