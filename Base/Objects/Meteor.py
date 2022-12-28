import random

from Base.Objects import BaseObject
from Base.Constants import ObjectConstants
from Base.Animation import Animations

class Meteor(BaseObject):
    def __init__(self, gameplay, 
                x=None,
                dx=None,
                dy=None):
        x = random.randint(4,100)/100.0 if x is None else x
        dx = random.randint(-3, 3) / 1200.0 if dx is None else dx
        dy = random.randint(-6, -3) / 800.0 if dy is None else dy
        
        super(Meteor, self).__init__((x,                                      # X
                                     ObjectConstants.METEOR_SCREEN_Y,           # Y
                                     ObjectConstants.METEOR_SCREEN_WIDTH,       # Width
                                     ObjectConstants.METEOR_SCREEN_HEIGHT),      # Height
                                     Animations.MeteorAnimation,                # Animation
                                     gameplay)                                  # Gameplay
        self.Dx = dx
        self.Dy = dy
        self.Name = "Meteor"

    def update(self):
        super().update()

        if self.X > ObjectConstants.METEOR_INACTIVE_RIGHT or self.X < ObjectConstants.METEOR_INACTIVE_LEFT or self.Y < ObjectConstants.METEOR_INACTIVE_BOTTOM:
            self.Inactive = True
