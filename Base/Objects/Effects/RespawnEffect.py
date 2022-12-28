from .Effect import Effect
from Base.Constants import ObjectConstants
from Base.Animation import Animations

class RespawnEffect(Effect):
    def __init__(self, spaceship):
        super(RespawnEffect, self).__init__(spaceship, ObjectConstants.SPACESHIP_RESPAWN_COOLDOWN)

    def applyEffects(self):
        self.Spaceship.setAnimation(Animations.SpaceshipRespawnAnimation)

    def removeEffects(self):
        self.Spaceship.setAnimation(Animations.SpaceshipAnimation)
        self.Spaceship.Invulnerable = False