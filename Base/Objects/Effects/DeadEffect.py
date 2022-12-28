from .Effect import Effect
from .RespawnEffect import RespawnEffect
from Base.Constants import ObjectConstants, ImageConstants
from Base.Animation import Animations

class DeadEffect(Effect):
    def __init__(self, spaceship):
        super(DeadEffect, self).__init__(spaceship, ObjectConstants.SPACESHIP_DEAD_COOLDOWN)

    def applyEffects(self):
        self.Spaceship.Alive = False
        self.Spaceship.Invulnerable = True
        self.Spaceship.setAnimation(Animations.SpaceshipDeadAnimation)
        self.Spaceship.Lives -= 1
        self.Spaceship.LifeBar.setRect(ImageConstants.LIFEBAR_CLIP_RECT[self.Spaceship.Lives])

        if self.Spaceship.Lives == 0:
            self.Spaceship.Inactive = True

    def removeEffects(self):
        self.Spaceship.Alive = True
        RespawnEffect(self.Spaceship)