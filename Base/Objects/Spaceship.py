
from Base.Objects.BaseObject import BaseObject
from Base.Objects.Bullet import Bullet
from Base.Objects.Explosion import Explosion
from Base.Objects.Effects import OverheatEffect, DeadEffect
from Base.Animation import Animations
from Base.Constants import ObjectConstants, ImageConstants
from Base.Textures import Textures

from Utility import GameUtility

##
# Đối tượng người chơi
# Properties:
#   IsShooting: Có đang bắn hay không
#   ShootingDelay: Delay tốc độ bắn
#   Overheat: Quá tải bắn
#   BulletCount: Số lượng đạn trong một lần bắn (1-3)
###
class Spaceship(BaseObject):
    def __init__(self, gameplay, playerIndex=0):
        super(Spaceship, self).__init__(ObjectConstants.SPACESHIP_SCREEN_RECT[playerIndex],          # Rect
                                        Animations.SpaceshipAnimation,                  # Animation
                                        gameplay)                                       # Gameplay
        self.PlayerIndex = playerIndex
        self.ListEffects = []

        self.IsShooting = False
        self.ShootingDelay = 0
        self.Overheat = False
        self.OverheatLevel = 0
        self.OverheatCooldownRate = ObjectConstants.SPACESHIP_OVERHEAT_STEP * 2 / 3
        self.BulletCount = 1

        self.Lives = 3
        self.Alive = True
        self.Invulnerable = False

        self.Name = "Spaceship"

        # Vẽ thanh máu, thanh overheat
        self.LifeBar = Textures.LifeBar.clone()
        self.LifeBar.setRect(ImageConstants.LIFEBAR_CLIP_RECT[3])
        self.OverheatFrame = Textures.OverheatFrame.clone()
        self.OverheatBar = Textures.OverheatBar.clone()
        
        GameUtility.drawTexture(gameplay, self.LifeBar, ImageConstants.LIFEBAR_SCREEN_RECT[playerIndex])
        GameUtility.drawTexture(gameplay, self.OverheatBar, ImageConstants.OVERHEAT_FRAME_SCREEN_RECT[playerIndex])
        GameUtility.drawTexture(gameplay, self.OverheatFrame, ImageConstants.OVERHEAT_FRAME_SCREEN_RECT[playerIndex])
        self.OverheatBar.setSize(0, ImageConstants.OVERHEAT_BAR_SCREEN_HEIGHT)

    ##
    # Thực hiện bắn
    ###
    def doShooting(self):
        if not self.Inactive and self.IsShooting and not self.Overheat:
            self.ShootingDelay += ObjectConstants.SPACESHIP_SHOOTING_SPEED
            if self.ShootingDelay > ObjectConstants.SPACESHIP_SHOOTING_INTERVAL:
                self.ShootingDelay = 0
                # Tạo thực thể Bullet mới
                Bullet(self)

    ##
    # OVERRIDES
    # Xử lý va chạm với các vật thể khác
    ###
    def handleCollision(self, otherObject):
        if otherObject.Name == "Meteor" and not self.Invulnerable:
            if self.collidesWith(otherObject):
                otherObject.Inactive = True
                DeadEffect(self)
                Explosion(self)

    def update(self):
        if self.Alive:
            super().update()

        # Gán lại tọa độ để không bị tràn ra ngoài viền màn hình
        if self.X < ObjectConstants.SPACESHIP_SCREEN_BORDER_LEFT:
            self.X = ObjectConstants.SPACESHIP_SCREEN_BORDER_LEFT
        if self.X > ObjectConstants.SPACESHIP_SCREEN_BORDER_RIGHT:
            self.X = ObjectConstants.SPACESHIP_SCREEN_BORDER_RIGHT
        if self.Y < ObjectConstants.SPACESHIP_SCREEN_BORDER_BOTTOM:
            self.Y = ObjectConstants.SPACESHIP_SCREEN_BORDER_BOTTOM
        if self.Y > ObjectConstants.SPACESHIP_SCREEN_BORDER_TOP:
            self.Y = ObjectConstants.SPACESHIP_SCREEN_BORDER_TOP

        for effect in self.ListEffects:
            effect.update()

        # Check shooting
        if not self.Overheat:
            if self.IsShooting and self.Alive:
                self.doShooting()
                self.OverheatCooldownRate = ObjectConstants.SPACESHIP_OVERHEAT_STEP * 2 / 3
                self.OverheatLevel += ObjectConstants.SPACESHIP_OVERHEAT_STEP
                if self.OverheatLevel >= 1:
                    self.OverheatLevel = 1
                    OverheatEffect(self)
            else:
                self.ShootingDelay = ObjectConstants.SPACESHIP_SHOOTING_INTERVAL
                self.OverheatLevel -= self.OverheatCooldownRate
                if self.OverheatLevel < 0:
                    self.OverheatLevel = 0
        
        if self.OverheatLevel != 0:
            self.OverheatBar.setRect(ImageConstants.OVERHEAT_BAR_CLIP_RECT(self.OverheatLevel))
            self.OverheatBar.setPos(ImageConstants.OVERHEAT_BAR_POS_X(self.OverheatLevel, self.PlayerIndex), ImageConstants.OVERHEAT_BAR_POS_Y)
            self.OverheatBar.setSize(ImageConstants.OVERHEAT_BAR_SCREEN_WIDTH * self.OverheatLevel, ImageConstants.OVERHEAT_BAR_SCREEN_HEIGHT)