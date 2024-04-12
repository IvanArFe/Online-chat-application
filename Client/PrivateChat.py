import grpc

class PrivateChat:
    channel = grpc.insecure_channel('localhost:50051')

    def 