from .Menu import Menu
from .Gameplay import Gameplay
from Utility import GameUtility
from Base.Textures import Textures
from Base.Constants import ComponentConstants, SocketData
from Base.Components import GameButton, GameLabel
from Socket import Server

class HostMenu(Menu):
    def __init__(self, app):
        super(HostMenu, self).__init__(app)

        self.Server = Server()

        self.IPLabel = GameLabel(self, "Your IP: " + self.Server.getIPAddress() + "\nWaiting for another player to join...", ComponentConstants.IP_INFO_POS)
        self.IPLabel.halign = "center"

        self.StartButton = None
        
        GameUtility.drawTexture(self, Textures.GameLogo, (0.76, 0.9, 0.5, 0.2))

    def startMultiplayerGame(self):
        self.Server.sendDataAndWait(SocketData.START_GAME_CODE)
        GameUtility.openMenu(Gameplay(self.App, self.Server))

    def goToPreviousMenu(self):
        self.Server.close()

        from .MultiplayMenu import MultiplayMenu
        GameUtility.openMenu(MultiplayMenu(self.App))

    def update(self, dt):
        if self.Server.isConnected():
            self.IPLabel.setText("Your IP: " + self.Server.getIPAddress() + "\nPlayer 2 connected.")
            if (self.StartButton is None):
                self.StartButton = GameButton(self, "Start", ComponentConstants.START_BUTTON_POS, self.startMultiplayerGame)
        else:
            self.Server.waitForConnection()