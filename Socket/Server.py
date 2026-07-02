import socket
from .FramedConnection import FramedConnection

##
# Phía Host. Lắng nghe kết nối, sau khi có client thì bọc socket vào
# FramedConnection để trao đổi dữ liệu có đóng khung + TCP_NODELAY.
###
class Server:
    def __init__(self):
        self.IP = socket.gethostbyname(socket.gethostname())
        self.Port = 2812

        self.Server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.Server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.Server.settimeout(0.001)      # accept() không chặn để poll trong menu

        self.Connection = None
        self.IsConnected = False

        self.startConnection()

    def startConnection(self):
        try:
            self.Server.bind((self.IP, self.Port))
        except socket.error as e:
            print('Cannot start connection. Error: ', e)
        self.Server.listen()

    def waitForConnection(self):
        try:
            conn, address = self.Server.accept()
            self.Connection = FramedConnection(conn)
            self.IsConnected = True
        except socket.timeout:
            pass

    def sendMessage(self, data):
        if self.Connection is not None:
            self.Connection.sendMessage(data)

    def receiveMessage(self):
        return self.Connection.receiveMessage() if self.Connection is not None else ""

    def poll(self):
        return self.Connection.poll() if self.Connection is not None else ""

    def flush(self):
        if self.Connection is not None:
            self.Connection.flush()

    def getIPAddress(self):
        return self.IP

    def isConnected(self):
        return self.IsConnected

    def close(self):
        try:
            self.Server.close()
        except OSError:
            pass
        if self.Connection is not None:
            self.Connection.close()
