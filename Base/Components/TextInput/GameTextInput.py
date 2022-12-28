from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from Base.Constants import ComponentConstants

class GameTextInput():
    def __init__(self, menu, text, pos):
        x, y = pos

        # Create text input
        self.TextInput = TextInput()
        self.TextInput.size_hint = ComponentConstants.TEXT_INPUT_WIDTH, ComponentConstants.TEXT_INPUT_HEIGHT
        self.TextInput.font_size = ComponentConstants.TEXT_INPUT_FONT_SIZE
        self.TextInput.font_name = ComponentConstants.GAME_FONT
        self.TextInput.multiline = False
        self.TextInput.background_color = ComponentConstants.TEXT_INPUT_BACKGROUND_COLOR

        # Create label if has label
        self.InputLabel = None
        if text is not None and text != "":
            self.InputLabel = Label()
            self.InputLabel.text = text
            self.InputLabel.size_hint = len(text) * ComponentConstants.TEXT_WIDTH_MULTIPLIER, ComponentConstants.TEXT_INPUT_HEIGHT
            self.InputLabel.font_size = ComponentConstants.TEXT_FONT_SIZE
            self.InputLabel.font_name = ComponentConstants.GAME_FONT
        
        if x is None:
            x = 0.5 + (self.TextInput.size_hint_x + self.InputLabel.size_hint_x if self.InputLabel is not None else 0) / 2
        self.TextInput.pos_hint = {"right": x, "top": y}
        if self.InputLabel is not None:
            self.InputLabel.pos_hint = {"right": x - self.TextInput.size_hint_x - 0.01, "top": y}

        self.Menu = menu
        menu.add_widget(self.TextInput)
        menu.add_widget(self.InputLabel)

    def getText(self):
        return self.TextInput._get_text()

    def free(self):
        self.Menu.remove_widget(self.TextInput)
        self.Menu.remove_widget(self.InputLabel)
        