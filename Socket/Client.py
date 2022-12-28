import socket
from Base.Constants import SocketData

class Client:
    def __init__(self):
        self.Port = 2812

        self.Client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.Client.settimeout(0.001)

        self.IsConnected = False
        self.DataReceivedCode = SocketData.SERVER_DATA_RECEIVED_CODE

    def startConnection(self, ip):
        try:
            self.Client.connect((ip, self.Port))
            self.IsConnected = True
        except socket.error:
            pass

    def sendData(self, data):
        try:
            if self.isConnected():
                self.Client.send(str.encode(data))
        except socket.timeout:
            pass

    def sendDataAndWait(self, data):
        try:
            if self.isConnected():
                self.Client.send(str.encode(data))

                while True:
                    if self.receiveData() == self.DataReceivedCode:
                        break
        except socket.timeout:
            pass

    def receiveData(self):
        try:
            if self.isConnected():
                return self.Client.recv(2048).decode()
        except socket.timeout:
            return ""

    def isConnected(self):
        return self.IsConnected

    def close(self):
        self.Client.close()
