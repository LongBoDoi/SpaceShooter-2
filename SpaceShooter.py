from kivy.app import App
from kivy.core.window import Window
from kivy.config import Config

from Menus import MainMenu

Config.set('kivy', 'exit_on_escape', '0')
Window.size = (1920, 1080)
Window.fullscreen = True

if __name__ == '__main__':
    mainApp = App()
    mainApp.root = MainMenu(mainApp)
    mainApp.run()