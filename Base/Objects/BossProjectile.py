from Base.Objects.BaseObject import BaseObject
from Base.Constants import ObjectConstants
from Base.Animation import Animations

##
# Đạn của Boss bắn ra
# Bay xuống dưới về phía người chơi. Va chạm với người chơi được xử lý trong
# Spaceship.handleCollision (giống như Meteor).
###
class BossProjectile(BaseObject):
    Name = "BossProjectile"
    # Đầu đạn tròn nằm giữa ô 32px -> hộp va chạm nhỏ hơn khung.
    HitboxScale = 0.6

    def __init__(self, gameplay, x, y, dx, dy, projectileType=0):
        super(BossProjectile, self).__init__((x,                                          # X
                                              y,                                          # Y
                                              ObjectConstants.BOSS_PROJECTILE_SCREEN_WIDTH,   # Width
                                              ObjectConstants.BOSS_PROJECTILE_SCREEN_HEIGHT), # Height
                                              Animations.BossProjectileAnimations[projectileType],
                                              gameplay)
        self.Dx = dx
        self.Dy = dy
        self.ProjectileType = projectileType

    def update(self):
        super().update()

        if (self.Y < ObjectConstants.BOSS_PROJECTILE_INACTIVE_BOTTOM
                or self.Y > ObjectConstants.BOSS_PROJECTILE_INACTIVE_TOP
                or self.X < ObjectConstants.BOSS_PROJECTILE_INACTIVE_LEFT
                or self.X > ObjectConstants.BOSS_PROJECTILE_INACTIVE_RIGHT):
            self.Inactive = True
