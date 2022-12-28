from Utility import GameUtility, JSONUtility
from Base.Objects import Spaceship, Meteor
from Base.Constants import ObjectConstants, SocketData
from .Menu import Menu
from Socket import Server, Client

##
# Class gameplay chính
###
class Gameplay(Menu):
    # Danh sách tất cả vật thể trong game
    ListObjects = []
    # Người chơi chính
    Player = None
    # Người chơi tham gia
    Otherplayer = None
    # Socket dùng để truyền nhận dữ liệu (chơi 2 người)
    Socket = None
    # Danh sách những vật thể mới, dùng để gửi từ Host xuống Client
    ListNewObjects = []
    IsClient = False
    # Tỉ lệ tạo thiên thạch
    MeteorCreationChance = ObjectConstants.METEOR_CREATION_CHANCE

    def __init__(self, app, socket=None):
        super(Gameplay, self).__init__(app)

        self.Socket = socket

        # Tạo người chơi
        if socket is None:
            self.Player = Spaceship(self)
        else:
            self.Socket.Client.settimeout(None)
            if isinstance(socket, Server):
                self.Player = Spaceship(self, playerIndex=1)
                self.Otherplayer = Spaceship(self, playerIndex=2)
                self.MeteorCreationChance *= 2
            else:
                self.IsClient = True
                self.Player = Spaceship(self, playerIndex=2)
                self.Otherplayer = Spaceship(self, playerIndex=1)

    ##
    # Sự kiện nhấn phím xuống
    ###
    def onKeyDown(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'd':
            self.Player.Dx = ObjectConstants.SPACESHIP_SPEED_X
        if keycode[1] == 'a':
            self.Player.Dx = -ObjectConstants.SPACESHIP_SPEED_X
        if keycode[1] == 'w':
            self.Player.Dy = ObjectConstants.SPACESHIP_SPEED_Y
        if keycode[1] == 's':
            self.Player.Dy = -ObjectConstants.SPACESHIP_SPEED_Y
        if keycode[1] == 'spacebar':
            self.Player.IsShooting = True
        return True

    ##
    # Sự kiện nhả phím
    ###
    def onKeyUp(self, keyboard, keycode):
        if keycode[1] == 'd':
            if self.Player.Dx > 0:
                self.Player.Dx = 0
        if keycode[1] == 'a':
            if self.Player.Dx < 0:
                self.Player.Dx = 0
        if keycode[1] == 'w':
            if self.Player.Dy > 0:
                self.Player.Dy = 0
        if keycode[1] == 's':
            if self.Player.Dy < 0:
                self.Player.Dy = 0
        if keycode[1] == 'spacebar':
            self.Player.IsShooting = False
        return True
        

    def update(self, dt):
        self.handleDataBeforeUpdate()

        # Update các vật thể trong game
        for obj in self.ListObjects:
            if not obj.Inactive:
                obj.update()
            else:
                GameUtility.removeObject(self, obj)

        # Tạo thiên thạch
        if not self.IsClient:
            GameUtility.randomCreateObject(self, Meteor, ObjectConstants.METEOR_CREATION_POOL, self.MeteorCreationChance)

    def handleDataBeforeUpdate(self):
        if self.Socket is None:
            return
        
        if not self.IsClient:
            # Gửi dữ liệu cho Client
            serverData = {
                "HostPlayer": {
                    "MovementSpeed": (self.Player.Dx, self.Player.Dy),
                    "IsShooting": self.Player.IsShooting
                },
                "ListNewObjects": self.ListNewObjects
            }
            self.Socket.sendDataAndWait(JSONUtility.encode(serverData))

            self.ListNewObjects = []

            # Nhận dữ liệu từ client
            clientData = JSONUtility.decode(self.Socket.receiveData())
            otherPlayerData = clientData["ClientPlayer"]
            self.Otherplayer.Dx, self.Otherplayer.Dy = otherPlayerData["MovementSpeed"]
            self.Otherplayer.IsShooting = otherPlayerData["IsShooting"]

            self.Socket.sendData(SocketData.SERVER_DATA_RECEIVED_CODE)
        else:
            serverData = JSONUtility.decode(self.Socket.receiveData())

            # Nhận dữ liệu từ server
            otherPlayerData = serverData["HostPlayer"]
            self.Otherplayer.Dx, self.Otherplayer.Dy = otherPlayerData["MovementSpeed"]
            self.Otherplayer.IsShooting = otherPlayerData["IsShooting"]
            # Tạo vật thể mới
            listNewObjects = serverData["ListNewObjects"]
            for newObjects in listNewObjects:
                if (newObjects["Name"] == "Meteor"):
                    x, dx, dy = newObjects["Data"]
                    Meteor(self, x, dx, dy)

            self.Socket.sendData(SocketData.CLIENT_DATA_RECEIVED_CODE)

            # Gửi lại dữ liệu cho host
            clientData = {
                "ClientPlayer": {
                    "MovementSpeed": (self.Player.Dx, self.Player.Dy),
                    "IsShooting": self.Player.IsShooting
                }
            }
            self.Socket.sendDataAndWait(JSONUtility.encode(clientData))