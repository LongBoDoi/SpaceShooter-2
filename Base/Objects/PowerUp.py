from Base.Objects.BaseObject import BaseObject
from Base.Constants import ObjectConstants
from Base.Animation import Animations

##
# Vật phẩm tăng sức mạnh rơi ra từ thiên thạch bị bắn hạ. Rơi thẳng xuống chậm;
# người chơi hứng bằng cách chạm vào (xử lý ở Spaceship.handleCollision).
#
# Đồng bộ multiplayer:
#   - Host/chơi đơn quyết định rơi (Bullet -> Gameplay.trySpawnPowerUp), gán ID
#     duy nhất, và gửi sự kiện tạo cho Client qua ListNewObjects.
#   - Khi một người chơi hứng được, ID được gửi qua "Consumed" để máy bên kia gỡ
#     bản sao tương ứng (không để hứng trùng / còn lơ lửng).
###
class PowerUp(BaseObject):
    Name = "PowerUp"
    HitboxScale = ObjectConstants.POWERUP_HITBOX_SCALE

    def __init__(self, gameplay, powerUpId, powerType, x, y):
        super(PowerUp, self).__init__((x,
                                       y,
                                       ObjectConstants.POWERUP_SCREEN_WIDTH,
                                       ObjectConstants.POWERUP_SCREEN_HEIGHT),
                                      Animations.PowerUpAnimations[powerType],
                                      gameplay)
        self.PowerUpId = powerUpId
        self.PowerType = powerType
        self.Dy = ObjectConstants.POWERUP_FALL_SPEED_Y

    def update(self):
        super().update()

        if self.Y < ObjectConstants.POWERUP_INACTIVE_BOTTOM:
            self.Inactive = True
