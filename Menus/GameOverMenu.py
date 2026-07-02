from .Menu import Menu
from Utility import GameUtility
from Base.Constants import ComponentConstants, SocketData
from Base.Components import GameButton, GameLabel
from Socket import Server

##
# Màn Game Over khi mọi người chơi đã hết mạng.
#   - Chơi đơn : "Play Again" (chơi lại) + "Main Menu".
#   - Host     : "Restart" (chơi lại cho cả hai) + "Main Menu".
#   - Client   : chờ host bấm Restart (poll trong update) + "Main Menu".
# socket = kết nối multiplayer (None nếu chơi đơn); đóng khi về menu chính.
###
class GameOverMenu(Menu):
    def __init__(self, app, socket=None):
        super(GameOverMenu, self).__init__(app)
        self.Socket = socket
        self.IsHost = socket is not None and isinstance(socket, Server)

        title = GameLabel(self, "GAME OVER", ComponentConstants.GAME_OVER_TITLE_POS)
        title.font_size = ComponentConstants.GAME_OVER_TITLE_FONT_SIZE

        if socket is None:
            # Chơi đơn.
            GameButton(self, "Play Again", ComponentConstants.GAME_OVER_BUTTON1_POS, self.playAgain)
            GameButton(self, "Main Menu", ComponentConstants.GAME_OVER_BUTTON2_POS, self.goToMainMenu)
        elif self.IsHost:
            # Chủ phòng có thể chơi lại cho cả hai người.
            GameButton(self, "Restart", ComponentConstants.GAME_OVER_BUTTON1_POS, self.restartMultiplayer)
            GameButton(self, "Main Menu", ComponentConstants.GAME_OVER_BUTTON2_POS, self.goToMainMenu)
        else:
            # Client: chờ host quyết định (update() sẽ bắt tín hiệu chơi lại).
            GameLabel(self, "Waiting for host...", ComponentConstants.GAME_OVER_BUTTON1_POS)
            GameButton(self, "Main Menu", ComponentConstants.GAME_OVER_BUTTON2_POS, self.goToMainMenu)

    ##
    # Chơi đơn: bắt đầu ván mới.
    ###
    def playAgain(self):
        from .Gameplay import Gameplay
        GameUtility.openMenu(Gameplay(self.App))

    ##
    # Host: báo client chơi lại rồi vào ván mới ngay. Nhờ mô hình mạng tách rời
    # (không chặn) nên không cần chờ client xác nhận - client sẽ vào khi nhận tín
    # hiệu; các gói dở của ván cũ nằm lại trong đệm sẽ được bỏ qua đúng chỗ.
    ###
    def restartMultiplayer(self):
        self.Socket.sendMessage(SocketData.START_GAME_CODE)
        from .Gameplay import Gameplay
        GameUtility.openMenu(Gameplay(self.App, self.Socket))

    def goToMainMenu(self):
        if self.Socket is not None:
            self.Socket.close()
        from .MainMenu import MainMenu
        GameUtility.openMenu(MainMenu(self.App))

    ##
    # Esc trên màn Game Over = về menu chính.
    ###
    def goToPreviousMenu(self):
        self.goToMainMenu()

    ##
    # Client: mỗi khung rút hết gói đang chờ, bỏ qua các gói dở của ván cũ; khi
    # gặp tín hiệu bắt đầu từ host thì vào ván mới.
    ###
    def update(self, dt):
        if self.Socket is None or self.IsHost:
            return
        while True:
            message = self.Socket.poll()
            if not message:
                break
            if message == SocketData.START_GAME_CODE:
                from .Gameplay import Gameplay
                GameUtility.openMenu(Gameplay(self.App, self.Socket))
                return
