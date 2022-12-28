from kivy.uix.floatlayout import FloatLayout
from Base.Textures import Textures
from kivy.core.window import Window
from kivy.clock import Clock

class Menu(FloatLayout):
    def __init__(self, app, **kwargs):
        super(Menu, self).__init__(**kwargs)

        self.App = app

        if self.App.root is not None:
            self.App.root.clear_widgets()
            Clock.unschedule(self.App.root.update)

        # Gán sự kiện keyboard
        self._keyboard = Window.request_keyboard(self.keyboardClose, self)
        self._keyboard.bind(on_key_down=self.onKeyDown)
        self._keyboard.bind(on_key_up=self.onKeyUp)

        # Vẽ background
        Textures.GameBackground.Image.size_hint = 1, 1
        self.add_widget(Textures.GameBackground.Image)

    def onKeyDown(self, keyboard, keycode, text, modifiers):
        pass

    def onKeyUp(self, keyboard, keycode):
        if keycode[1] == "escape":
            self.goToPreviousMenu()

    def keyboardClose(self):
        self._keyboard.unbind(on_key_down=self.onKeyDown)
        self._keyboard.unbind(on_key_up=self.onKeyUp)
        self._keyboard = None

    def goToPreviousMenu(self):
        pass

    def update(self, dt):
        pass