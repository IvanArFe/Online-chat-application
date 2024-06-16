import redis
import grpc
import time
import name_server_pb2
import name_server_pb2_grpc
from concurrent import futures 


class NameServer(name_server_pb2_grpc.ServidorNombresServicer):
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)

    def Register(self, request, context):
        username = request.username
        address = f"{request.ip}:{request.port}"
        #Verificar si el usuario ya existe
        if self.redis.exists(username):
            return name_server_pb2.Empty()
        else:
            self.redis.set(username, address)
            return name_server_pb2.Empty()

    def GetAddress(self, request, context):
        username = request.username
        address = self.redis.get(username)
        if address is None:
            return name_server_pb2.GetAddressResponse(status="User not found")
        else:
            return name_server_pb2.GetAddressResponse(address=address.decode('utf-8'), status="Success")
        
def serve():
    servidor = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    name_server_pb2_grpc.add_ServidorNombresServicer_to_server(NameServer(), servidor)
    print('NameServer. Puerto 50051.')
    servidor.add_insecure_port('0.0.0.0:50051')
    servidor.start()

    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        servidor.stop(0)

if __name__ == '__main__':
    serve()

