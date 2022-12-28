from .Effect import Effect
from Base.Constants import ObjectConstants

class OverheatEffect(Effect):
    def __init__(self, spaceship):
        super(OverheatEffect, self).__init__(spaceship, ObjectConstants.SPACESHIP_OVERHEAT_COOLDOWN)

    def applyEffects(self):
        self.Spaceship.Overheat = True

    def removeEffects(self):
        self.Spaceship.OverheatCooldownRate = ObjectConstants.SPACESHIP_OVERHEAT_STEP * 2
        self.Spaceship.Overheat = False