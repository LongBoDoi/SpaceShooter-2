from .Menu import Menu
from Utility import GameUtility
from Utility.Settings import Settings
from Base.Textures import Textures
from Base.Constants import ComponentConstants
from Base.Components import GameButton, GameLabel

##
# Màn hình cài đặt. Mỗi tùy chọn là một nút bấm để đổi giá trị:
#   - Difficulty : Easy -> Normal -> Hard (xoay vòng), có hiệu lực ở ván tiếp theo.
#   - Fullscreen : bật/tắt toàn màn hình ngay lập tức.
# Thay đổi được lưu ngay qua Settings.save(). Back / Esc quay lại menu chính.
###
class SettingsMenu(Menu):
    def __init__(self, app):
        super(SettingsMenu, self).__init__(app)

        GameUtility.drawTexture(self, Textures.GameLogo, (0.76, 0.9, 0.5, 0.2))
        GameLabel(self, "Settings", ComponentConstants.SETTINGS_TITLE_POS)

        self.DifficultyButton = GameButton(self, self.difficultyText(),
                                           ComponentConstants.SETTINGS_DIFFICULTY_POS,
                                           self.onDifficulty)
        self.FullscreenButton = GameButton(self, self.fullscreenText(),
                                           ComponentConstants.SETTINGS_FULLSCREEN_POS,
                                           self.onFullscreen)
        GameButton(self, "Back", ComponentConstants.SETTINGS_BACK_POS, self.goToPreviousMenu)

    def difficultyText(self):
        return "Difficulty: " + Settings.Difficulty

    def fullscreenText(self):
        return "Fullscreen: " + ("On" if Settings.Fullscreen else "Off")

    def onDifficulty(self):
        Settings.cycleDifficulty()
        self.DifficultyButton.setText(self.difficultyText())

    def onFullscreen(self):
        Settings.toggleFullscreen()
        self.FullscreenButton.setText(self.fullscreenText())

    def goToPreviousMenu(self):
        from .MainMenu import MainMenu
        GameUtility.openMenu(MainMenu(self.App))
