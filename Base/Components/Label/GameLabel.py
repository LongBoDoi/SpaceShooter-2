from kivy.uix.label import Label
from Base.Constants import ComponentConstants

class GameLabel(Label):
    def __init__(self, menu, text, pos, **kwargs):
        super(GameLabel, self).__init__(**kwargs)

        self.text = text
        self.size_hint = len(text) * ComponentConstants.TEXT_WIDTH_MULTIPLIER, ComponentConstants.BUTTON_HEIGHT
        x, y = pos
        if x is None:
            x = 0.5 + self.size_hint_x / 2
        self.pos_hint = {"right": x, "top": y}

        self.font_name = ComponentConstants.GAME_FONT
        self.font_size = ComponentConstants.TEXT_FONT_SIZE

        menu.add_widget(self)

    def setText(self, text):
        self.text = text