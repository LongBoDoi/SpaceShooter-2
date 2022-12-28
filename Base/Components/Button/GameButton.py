from kivy.uix.button import Button
from kivy.core.window import Window

from Base.Constants import ComponentConstants

class GameButton(Button):
    def __init__(self, menu, text, pos, callback, **kwargs):
        super(GameButton, self).__init__(**kwargs)
        
        self.text = text
        self.size_hint = len(text) * ComponentConstants.TEXT_WIDTH_MULTIPLIER, ComponentConstants.BUTTON_HEIGHT
        x, y = pos
        if x is None:
            x = 0.5 + self.size_hint_x / 2
        self.pos_hint = {"right": x, "top": y}

        self.font_name = ComponentConstants.GAME_FONT
        self.font_size = ComponentConstants.TEXT_FONT_SIZE

        self.background_color = 0, 0, 0, 0

        self.Callback = callback
        Window.bind(mouse_pos=self.onHover)

        self.Menu = menu
        menu.add_widget(self)
    
    def onHover(self, window, pos):
        if self.collide_point(*pos):
            self.color = ComponentConstants.BUTTON_HOVER_COLOR
        else:
            self.color = ComponentConstants.BUTTON_COLOR

    def on_press(self):
        self.color = ComponentConstants.BUTTON_CLICK_COLOR

    def on_release(self):
        self.color = ComponentConstants.BUTTON_HOVER_COLOR
        if self.Callback is not None:
            self.Callback()

    def free(self):
        self.Menu.remove_widget(self)