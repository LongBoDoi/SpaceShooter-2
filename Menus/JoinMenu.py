from .Menu import Menu
from .Gameplay import Gameplay
from Utility import GameUtility
from Base.Textures import Textures
from Base.Constants import ComponentConstants, SocketData
from Base.Components import GameButton, GameTextInput, GameLabel
from Socket import Client

class JoinMenu(Menu):
    def __init__(self, app):
        super(JoinMenu, self).__init__(app)

        self.Client = Client()
        
        # Vẽ game Logo
        GameUtility.drawTexture(self, Textures.GameLogo, (0.76, 0.9, 0.5, 0.2))

        # Vẽ input địa chỉ IP và button Join
        self.IPInput = GameTextInput(self, "IP Address:", ComponentConstants.IP_TEXT_INPUT_POS)
        self.JoinButton = GameButton(self, "Join", ComponentConstants.JOIN_BUTTON_POS, self.joinConnection)

    def joinConnection(self):
        self.Client.startConnection(self.IPInput.getText())
        if self.Client.isConnected():
            self.IPInput.free()
            self.JoinButton.free()
            GameLabel(self, "Connected. Waiting for the host to start game.", ComponentConstants.WAITING_HOST_START_POS)

    def goToPreviousMenu(self):
        if self.Client is not None:
            self.Client.close()

        from .MultiplayMenu import MultiplayMenu
        GameUtility.openMenu(MultiplayMenu(self.App))

    def update(self, dt):
        # Nếu nhận được thông báo bắt đầu game từ phía chủ phòng thì bắt đầu trò chơi
        if self.Client.receiveData() == SocketData.START_GAME_CODE:
            self.Client.sendData(SocketData.CLIENT_DATA_RECEIVED_CODE)
            GameUtility.openMenu(Gameplay(self.App, self.Client))