from .Effect import Effect
from .RespawnEffect import RespawnEffect
from Base.Constants import ObjectConstants
from Base.Animation import Animations

class DeadEffect(Effect):
    def __init__(self, spaceship):
        super(DeadEffect, self).__init__(spaceship, ObjectConstants.SPACESHIP_DEAD_COOLDOWN)

    def applyEffects(self):
        self.Spaceship.Alive = False
        self.Spaceship.Invulnerable = True
        self.Spaceship.setAnimation(Animations.SpaceshipDeadAnimation)
        self.Spaceship.Lives -= 1
        self.Spaceship.updateLifeDisplay()   # thanh máu + tim phụ (mạng > 3)

        if self.Spaceship.Lives == 0:
            self.Spaceship.Inactive = True
            self.Spaceship.removeBadge()     # hết mạng hẳn -> gỡ nhãn P1/P2
            self.Spaceship.clearBuffs()      # và xoá hiệu ứng + HUD đang chạy

    def removeEffects(self):
        self.Spaceship.Alive = True
        RespawnEffect(self.Spaceship)