import socket
from .FramedConnection import FramedConnection

##
# Phía Join. Kết nối tới Host rồi bọc socket vào FramedConnection.
###
class Client:
    def __init__(self):
        self.Port = 2812
        self.Client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.IsConnected = False
        self.Connection = None

    def startConnection(self, ip):
        try:
            # 3s đủ để bắt tay TCP hoàn tất (cũ đặt 0.001s nên chỉ nối được localhost).
            self.Client.settimeout(3.0)
            self.Client.connect((ip, self.Port))
            self.Connection = FramedConnection(self.Client)
            self.IsConnected = True
        except socket.error:
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

    def isConnected(self):
        return self.IsConnected

    def close(self):
        if self.Connection is not None:
            self.Connection.close()
        else:
            try:
                self.Client.close()
            except OSError:
                pass
