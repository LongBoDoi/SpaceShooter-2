from .Menu import Menu
from .MainMenu import MainMenu
from .HostMenu import HostMenu
from .JoinMenu import JoinMenu
from Utility import GameUtility
from Base.Textures import Textures
from Base.Constants import ComponentConstants
from Base.Components import GameButton

class MultiplayMenu(Menu):
    def __init__(self, app):
        super(MultiplayMenu, self).__init__(app)
        
        GameUtility.drawTexture(self, Textures.GameLogo, (0.76, 0.9, 0.5, 0.2))
        GameButton(self, "Host", ComponentConstants.MULTIPLAY_HOST_BUTTON_POS, self.openHostMenu)
        GameButton(self, "Join", ComponentConstants.MULTIPLAY_JOIN_BUTTON_POS, self.openJoinMenu)
        GameButton(self, "Back", ComponentConstants.MULTIPLAY_BACK_BUTTON_POS, self.goToPreviousMenu)

    def openHostMenu(self):
        GameUtility.openMenu(HostMenu(self.App))

    def openJoinMenu(self):
        GameUtility.openMenu(JoinMenu(self.App))

    def goToPreviousMenu(self):
        GameUtility.openMenu(MainMenu(self.App))