import socket
from Base.Constants import SocketData

class Server:
    def __init__(self):
        self.IP = socket.gethostbyname(socket.gethostname())
        self.Port = 2812

        self.Server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.Server.settimeout(0.001)

        self.Client = None
        self.IsConnected = False
        self.DataReceivedCode = SocketData.CLIENT_DATA_RECEIVED_CODE

        self.startConnection()

    def startConnection(self):
        try:
            self.Server.bind((self.IP, self.Port))
        except socket.error:
            print('Cannot start connection. Error: ', socket.error)

        self.Server.listen()

    def waitForConnection(self):
        try:
            self.Client, address = self.Server.accept()
            self.Client.settimeout(0.001)
            self.IsConnected = True
        except socket.timeout:
            pass

    def sendData(self, data):
        try:
            self.Client.send(str.encode(data))
        except socket.error:
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

    def getIPAddress(self):
        return self.IP

    def isConnected(self):
        return self.IsConnected

    def close(self):
        self.Server.close()
        if self.isConnected():
            self.Client.close()