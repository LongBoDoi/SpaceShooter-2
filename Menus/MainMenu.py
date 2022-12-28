from Base.Components import GameButton
from Base.Constants import ComponentConstants
from Base.Textures import Textures
from Utility import GameUtility
from .Menu import Menu

class MainMenu(Menu):
    def __init__(self, app):
        super(MainMenu, self).__init__(app)
        
        GameUtility.drawTexture(self, Textures.GameLogo, (0.76, 0.9, 0.5, 0.2))
        GameButton(self, "Single Player", ComponentConstants.SINGLE_PLAY_BUTTON_POS, self.openSingleplayMenu)
        GameButton(self, "Multiplayer", ComponentConstants.MULTI_PLAY_BUTTON_POS, self.openMultiplayMenu)
        GameButton(self, "Exit", ComponentConstants.EXIT_BUTTON_POS, self.exitGame)

    def openSingleplayMenu(self):
        from .Gameplay import Gameplay
        GameUtility.openMenu(Gameplay(self.App))

    def openMultiplayMenu(self):
        from .MultiplayMenu import MultiplayMenu
        GameUtility.openMenu(MultiplayMenu(self.App))

    def exitGame(self):
        self.App.stop()