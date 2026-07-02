
import math

from kivy.uix.label import Label

from Base.Objects.BaseObject import BaseObject
from Base.Objects.Bullet import Bullet
from Base.Objects.Explosion import Explosion
from Base.Objects.Effects import OverheatEffect, DeadEffect
from Base.Animation import Animations
from Base.Constants import ObjectConstants, ImageConstants, ComponentConstants, AnimationConstants
from Base.Textures import Textures

from Utility import GameUtility
from Utility.Settings import Settings

##
# Đối tượng người chơi
# Properties:
#   IsShooting: Có đang bắn hay không
#   ShootingDelay: Delay tốc độ bắn
#   Overheat: Quá tải bắn
#   BulletCount: Số lượng đạn trong một lần bắn (1-3)
###
class Spaceship(BaseObject):
    # Tàu người chơi va chạm với thiên thạch, đạn boss, thân boss và vật phẩm.
    CollisionTargets = ("Meteor", "BossProjectile", "Boss", "PowerUp")

    def __init__(self, gameplay, playerIndex=0, remote=False):
        super(Spaceship, self).__init__(ObjectConstants.SPACESHIP_SCREEN_RECT[playerIndex],          # Rect
                                        Animations.SpaceshipAnimation,                  # Animation
                                        gameplay)                                       # Gameplay
        self.PlayerIndex = playerIndex
        self.ListEffects = []

        # remote = tàu của người chơi bên kia: chỉ hiển thị theo dữ liệu đồng bộ,
        # không tự mô phỏng (di chuyển / va chạm / bắn / quá tải đều do chủ sở
        # hữu quyết định rồi gửi sang). RemoteState theo dõi hoạt cảnh hiện tại.
        self.Remote = remote
        self.RemoteState = "normal"

        self.IsShooting = False
        self.ShootingDelay = 0
        self.Overheat = False
        self.OverheatLevel = 0
        self.OverheatCooldownRate = ObjectConstants.SPACESHIP_OVERHEAT_STEP * 2 / 3
        self.BulletCount = 1

        # Tốc độ di chuyển hiện tại (có thể tăng tạm thời bởi vật phẩm SPEED).
        self.SpeedX = ObjectConstants.SPACESHIP_SPEED_X
        self.SpeedY = ObjectConstants.SPACESHIP_SPEED_Y

        # Hiệu ứng có hạn giờ: {loại: số khung còn lại}. Cờ suy ra mỗi khung.
        self.ActiveBuffs = {}
        self.BuffIcons = {}          # {loại: widget Image trên HUD}
        self.Shielded = False        # SHIELD: bất tử
        self.RapidFire = False       # RAPID: bắn nhanh, không quá tải
        self.Auras = {}              # {loại: widget Image aura quanh tàu}
        self.AuraPulse = 0           # đếm khung để aura phập phồng
        self.RemoteBuffs = set()     # (tàu remote) loại buff đang chạy để vẽ aura
        self.ExtraHeartIcons = []    # tim phụ khi mạng > mức nền 3

        self.Lives = ObjectConstants.SPACESHIP_BASE_LIVES
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

        # Phân biệt người chơi: nhuộm màu sprite tàu + gắn nhãn "P1"/"P2" bay theo.
        # Chỉ áp cho multiplayer (playerIndex 1/2); chơi đơn (0) giữ nguyên trắng.
        self.PlayerColor = ObjectConstants.PLAYER_COLORS[playerIndex]
        self.applyTint()

        self.Badge = None
        self.createBadge()

    ##
    # Tạo nhãn "P1"/"P2" (bỏ qua chơi đơn hoặc nếu đã có). Có thể gọi lại để khôi
    # phục nhãn nếu trước đó bị gỡ nhầm do dữ liệu tồn đọng lúc chơi lại.
    ###
    def createBadge(self):
        if self.PlayerIndex == 0 or self.Badge is not None:
            return
        self.Badge = Label(text="P%d" % self.PlayerIndex,
                           font_name=ComponentConstants.GAME_FONT,
                           font_size=28,
                           bold=True,
                           color=self.PlayerColor,
                           size_hint=(0.05, 0.035))
        self.updateBadge()
        self.Gameplay.add_widget(self.Badge)

    ##
    # Nhuộm màu sprite tàu theo màu người chơi (nhân vào texture). Phải gọi lại
    # sau mỗi setAnimation vì animation mới tạo ra Image mới (mặc định trắng).
    ###
    def applyTint(self):
        self.Animation.Texture.Image.color = self.PlayerColor

    def setAnimation(self, newAnimation):
        super().setAnimation(newAnimation)
        self.applyTint()

    ##
    # Đặt nhãn P1/P2 ngay phía trên tàu (nếu sát mép trên màn hình thì hạ xuống
    # dưới tàu để không bị che khuất).
    ###
    def updateBadge(self):
        if self.Badge is None:
            return
        centerX = self.X - self.Width / 2
        top = self.Y + ObjectConstants.PLAYER_BADGE_Y_OFFSET
        if top > 0.995:
            top = self.Y - self.Height
        self.Badge.pos_hint = {"center_x": centerX, "top": top}

    ##
    # Gỡ nhãn P1/P2 khỏi màn hình (gọi khi người chơi hết mạng hẳn).
    ###
    def removeBadge(self):
        if self.Badge is not None:
            self.Gameplay.remove_widget(self.Badge)
            self.Badge = None

    ##
    # Thực hiện bắn
    ###
    def doShooting(self):
        if not self.Inactive and self.IsShooting and not self.Overheat:
            step = ObjectConstants.SPACESHIP_SHOOTING_SPEED
            if self.RapidFire:
                step *= ObjectConstants.POWERUP_RAPID_FIRE_FACTOR
            self.ShootingDelay += step
            if self.ShootingDelay > ObjectConstants.SPACESHIP_SHOOTING_INTERVAL:
                self.ShootingDelay = 0
                x = self.X + ObjectConstants.BULLET_SCREEN_OFFSET_X[self.BulletCount - 1]
                y = self.Y + ObjectConstants.BULLET_SCREEN_OFFSET_Y
                Bullet(self.Gameplay, x, y, self.BulletCount, self.PlayerColor)
                # Multiplayer: phát viên đạn vừa bắn cho máy bên kia tái tạo, để
                # hai bên thấy y hệt thay vì mỗi bên tự đoán theo IsShooting.
                if self.Gameplay.Socket is not None:
                    self.Gameplay.NewBullets.append((x, y, self.BulletCount))

    ##
    # Áp hiệu ứng khi hứng vật phẩm (chỉ tàu cục bộ gọi -> tự quản trạng thái mình,
    # hiệu ứng tự thể hiện sang máy kia qua đạn/vị trí/mạng đã đồng bộ sẵn).
    ###
    def collectPowerUp(self, powerType):
        if powerType == ObjectConstants.POWERUP_TYPE_POWER:
            if self.BulletCount < ObjectConstants.POWERUP_MAX_BULLET_COUNT:
                self.BulletCount += 1
        elif powerType == ObjectConstants.POWERUP_TYPE_REPAIR:
            # Hồi máu tới mức nền 3.
            if self.Lives < ObjectConstants.SPACESHIP_BASE_LIVES:
                self.Lives += 1
                self.updateLifeDisplay()
        elif powerType == ObjectConstants.POWERUP_TYPE_HEART:
            # Tim phụ: thêm mạng vượt mức nền, tới MAX_LIVES.
            if self.Lives < ObjectConstants.SPACESHIP_MAX_LIVES:
                self.Lives += 1
                self.updateLifeDisplay()
        elif powerType == ObjectConstants.POWERUP_TYPE_SPEED:
            self.ActiveBuffs[powerType] = self.buffDuration(ObjectConstants.POWERUP_SPEED_BOOST_FRAMES)
        elif powerType == ObjectConstants.POWERUP_TYPE_SHIELD:
            self.ActiveBuffs[powerType] = self.buffDuration(ObjectConstants.POWERUP_SHIELD_FRAMES)
        elif powerType == ObjectConstants.POWERUP_TYPE_RAPID:
            self.ActiveBuffs[powerType] = self.buffDuration(ObjectConstants.POWERUP_RAPID_FRAMES)

    ##
    # Thời lượng hiệu ứng sau khi nhân theo độ khó của máy này (tối thiểu 1 khung).
    ###
    def buffDuration(self, base):
        return max(1, int(base * Settings.powerUpDurationMultiplier))

    ##
    # Cập nhật hiển thị mạng: thanh máu sprite cho tới mức nền 3, và mỗi mạng phụ
    # (vượt 3) là một icon tim cạnh thanh. Gọi sau mọi thay đổi Lives.
    ###
    def updateLifeDisplay(self):
        base = ObjectConstants.SPACESHIP_BASE_LIVES
        self.LifeBar.setRect(ImageConstants.LIFEBAR_CLIP_RECT[max(0, min(base, self.Lives))])
        extra = max(0, self.Lives - base)
        while len(self.ExtraHeartIcons) < extra:
            texture = Textures.PowerUps.clone()
            texture.setRect(AnimationConstants.POWERUP_ANIMATION_RECTS[ObjectConstants.POWERUP_TYPE_HEART])
            icon = texture.Image
            icon.size_hint = ObjectConstants.EXTRA_HEART_SIZE
            self.ExtraHeartIcons.append(icon)
            self.Gameplay.add_widget(icon)
        while len(self.ExtraHeartIcons) > extra:
            self.Gameplay.remove_widget(self.ExtraHeartIcons.pop())
        for slot, icon in enumerate(self.ExtraHeartIcons):
            right = ObjectConstants.EXTRA_HEART_START_X[self.PlayerIndex] + slot * ObjectConstants.EXTRA_HEART_STEP_X[self.PlayerIndex]
            icon.pos_hint = {"right": right, "top": ObjectConstants.EXTRA_HEART_Y}

    ##
    # Đưa vận tốc hiện tại về đúng tốc độ hiện hành (giữ hướng đang đi) - dùng khi
    # tốc độ đổi giữa lúc đang di chuyển (bật/tắt tăng tốc).
    ###
    def rescaleVelocity(self):
        if self.Dx > 0:
            self.Dx = self.SpeedX
        elif self.Dx < 0:
            self.Dx = -self.SpeedX
        if self.Dy > 0:
            self.Dy = self.SpeedY
        elif self.Dy < 0:
            self.Dy = -self.SpeedY

    ##
    # Đếm ngược mọi hiệu ứng có hạn giờ, suy ra cờ hiệu ứng, rồi cập nhật HUD.
    ###
    def updateBuffs(self):
        for buffType in list(self.ActiveBuffs):
            self.ActiveBuffs[buffType] -= 1
            if self.ActiveBuffs[buffType] <= 0:
                del self.ActiveBuffs[buffType]
        self.applyBuffEffects()
        self.updateBuffHud()
        self.updateAuras(self.ActiveBuffs)

    ##
    # Suy ra trạng thái hiệu ứng từ các buff đang chạy (idempotent mỗi khung).
    ###
    def applyBuffEffects(self):
        speedActive = ObjectConstants.POWERUP_TYPE_SPEED in self.ActiveBuffs
        targetSpeedX = ObjectConstants.SPACESHIP_SPEED_X * (ObjectConstants.POWERUP_SPEED_BOOST_FACTOR if speedActive else 1)
        if targetSpeedX != self.SpeedX:
            self.SpeedX = targetSpeedX
            self.SpeedY = ObjectConstants.SPACESHIP_SPEED_Y * (ObjectConstants.POWERUP_SPEED_BOOST_FACTOR if speedActive else 1)
            self.rescaleVelocity()
        self.Shielded = ObjectConstants.POWERUP_TYPE_SHIELD in self.ActiveBuffs
        self.RapidFire = ObjectConstants.POWERUP_TYPE_RAPID in self.ActiveBuffs

    ##
    # HUD hiệu ứng của người chơi cục bộ: mỗi buff có hạn giờ = 1 icon xếp hàng
    # cạnh thanh trạng thái; nhấp nháy (mờ dần theo nhịp) khi sắp hết giờ.
    ###
    def updateBuffHud(self):
        # Gỡ icon của buff đã hết.
        for buffType in list(self.BuffIcons):
            if buffType not in self.ActiveBuffs:
                self.Gameplay.remove_widget(self.BuffIcons[buffType])
                del self.BuffIcons[buffType]
        # Vẽ / xếp / nhấp nháy icon của buff đang chạy (thứ tự ổn định theo loại).
        active = sorted(self.ActiveBuffs)
        for slot, buffType in enumerate(active):
            icon = self.BuffIcons.get(buffType)
            if icon is None:
                texture = Textures.PowerUps.clone()
                texture.setRect(AnimationConstants.POWERUP_ANIMATION_RECTS[buffType])
                icon = texture.Image
                icon.size_hint = ObjectConstants.BUFF_ICON_SIZE
                self.BuffIcons[buffType] = icon
                self.Gameplay.add_widget(icon)
            right = ObjectConstants.BUFF_HUD_START_X[self.PlayerIndex] + slot * ObjectConstants.BUFF_HUD_STEP_X[self.PlayerIndex]
            icon.pos_hint = {"right": right, "top": ObjectConstants.BUFF_HUD_Y}
            remaining = self.ActiveBuffs[buffType]
            blinkOff = (remaining < ObjectConstants.BUFF_BLINK_THRESHOLD
                        and (remaining // ObjectConstants.BUFF_BLINK_PERIOD) % 2 == 0)
            icon.opacity = 0.2 if blinkOff else 1.0

    ##
    # Vẽ aura quanh tàu cho các hiệu ứng đang chạy (khiên = vòng, tốc độ/bắn nhanh
    # = quầng sáng), bám theo tàu và phập phồng. activeTypes: tập loại buff đang
    # bật (tàu cục bộ dùng ActiveBuffs; tàu remote dùng RemoteBuffs đã đồng bộ).
    ###
    def updateAuras(self, activeTypes):
        self.AuraPulse += 1
        phase = (self.AuraPulse % ObjectConstants.AURA_PULSE_PERIOD) / ObjectConstants.AURA_PULSE_PERIOD
        wave = 0.5 - 0.5 * math.cos(2 * math.pi * phase)
        opacity = ObjectConstants.AURA_OPACITY_MIN + (ObjectConstants.AURA_OPACITY_MAX - ObjectConstants.AURA_OPACITY_MIN) * wave
        centerX = self.X - self.Width / 2
        centerY = self.Y - self.Height / 2
        for buffType in ObjectConstants.AURA_TYPES:
            if buffType in activeTypes:
                aura = self.Auras.get(buffType)
                if aura is None:
                    cell, color = ObjectConstants.AURA_SPECS[buffType]
                    texture = Textures.Auras.clone()
                    texture.setRect(AnimationConstants.AURA_RECTS[cell])
                    aura = texture.Image
                    aura.size_hint = ObjectConstants.AURA_SIZE
                    aura.color = color
                    self.Auras[buffType] = aura
                    self.Gameplay.add_widget(aura)
                aura.pos_hint = {"center_x": centerX, "center_y": centerY}
                aura.opacity = opacity
            elif buffType in self.Auras:
                self.Gameplay.remove_widget(self.Auras.pop(buffType))

    ##
    # Xoá sạch hiệu ứng + icon HUD + aura (gọi khi người chơi hết mạng hẳn).
    ###
    def clearBuffs(self):
        for icon in self.BuffIcons.values():
            self.Gameplay.remove_widget(icon)
        self.BuffIcons = {}
        for aura in self.Auras.values():
            self.Gameplay.remove_widget(aura)
        self.Auras = {}
        self.ActiveBuffs = {}
        self.RemoteBuffs = set()
        self.Shielded = False
        self.RapidFire = False
        self.SpeedX = ObjectConstants.SPACESHIP_SPEED_X
        self.SpeedY = ObjectConstants.SPACESHIP_SPEED_Y

    ##
    # OVERRIDES
    # Xử lý va chạm với các vật thể khác
    ###
    def handleCollision(self, otherObject):
        # Vật phẩm hứng được kể cả khi đang bất tử (lúc hồi sinh).
        if otherObject.Name == "PowerUp":
            if self.collidesWith(otherObject):
                otherObject.Inactive = True
                self.collectPowerUp(otherObject.PowerType)
                # Multiplayer: báo máy bên kia gỡ bản sao vật phẩm này.
                if self.Gameplay.Socket is not None:
                    self.Gameplay.ConsumedPowerUps.append(otherObject.PowerUpId)
            return

        # Bất tử (đang hồi sinh) hoặc đang có khiên -> không chết, xuyên qua nguy hiểm.
        if self.Invulnerable or self.Shielded:
            return
        if otherObject.Name == "Meteor":
            if self.collidesWith(otherObject):
                otherObject.Inactive = True
                DeadEffect(self)
                Explosion(self)
        elif otherObject.Name == "BossProjectile":
            if self.collidesWith(otherObject):
                otherObject.Inactive = True
                DeadEffect(self)
                Explosion(self)
        elif otherObject.Name == "Boss" and not otherObject.Intro:
            # Va vào thân boss (boss không mất máu, chỉ người chơi chết).
            if self.collidesWith(otherObject):
                DeadEffect(self)
                Explosion(self)

    ##
    # Cập nhật thanh quá tải theo mức OverheatLevel (dùng chung cho tàu cục bộ và
    # tàu remote). Mức 0 -> thu thanh về rỗng.
    ###
    def updateOverheatBar(self):
        if self.OverheatLevel > 0:
            self.OverheatBar.setRect(ImageConstants.OVERHEAT_BAR_CLIP_RECT(self.OverheatLevel))
            self.OverheatBar.setPos(ImageConstants.OVERHEAT_BAR_POS_X(self.OverheatLevel, self.PlayerIndex),
                                    ImageConstants.OVERHEAT_BAR_POS_Y)
            self.OverheatBar.setSize(ImageConstants.OVERHEAT_BAR_SCREEN_WIDTH * self.OverheatLevel,
                                     ImageConstants.OVERHEAT_BAR_SCREEN_HEIGHT)
        else:
            self.OverheatBar.setSize(0, ImageConstants.OVERHEAT_BAR_SCREEN_HEIGHT)

    # --------------------------------------------------- Đồng bộ multiplayer
    ##
    # Trạng thái hoạt cảnh để gửi đi: dead / respawn (đang bất tử) / normal.
    ###
    def getSyncState(self):
        if not self.Alive:
            return "dead"
        if self.Invulnerable:
            return "respawn"
        return "normal"

    ##
    # Gói trạng thái tàu (chủ sở hữu gửi đi mỗi khung). Đồng bộ TOẠ ĐỘ thật thay
    # vì vận tốc -> tàu bên kia khớp tuyệt đối, không trôi lệch dồn theo thời gian.
    ###
    def getSyncData(self):
        return {
            "X": self.X,
            "Y": self.Y,
            "State": self.getSyncState(),
            "Lives": self.Lives,
            "OverheatLevel": self.OverheatLevel,
            # Loại buff đang chạy -> để tàu bên kia vẽ aura (khiên/tốc độ/bắn nhanh).
            "Buffs": list(self.ActiveBuffs)
        }

    ##
    # Áp trạng thái nhận được lên tàu remote (chỉ gọi cho Otherplayer).
    ###
    def applySyncData(self, data):
        # Vị trí -> mục tiêu nội suy (mượt); trạng thái rời rạc -> áp ngay.
        self.TargetX = data["X"]
        self.TargetY = data["Y"]
        self.applyRemoteState(data["State"])
        if data["Lives"] != self.Lives:
            self.Lives = data["Lives"]
            self.updateLifeDisplay()     # thanh máu + tim phụ (mạng > 3)
            if self.Lives <= 0:          # bên kia hết mạng -> gỡ nhãn P1/P2
                self.removeBadge()
            else:                        # còn mạng -> đảm bảo có nhãn (khôi phục nếu cần)
                self.createBadge()
        self.OverheatLevel = data["OverheatLevel"]
        self.updateOverheatBar()
        self.RemoteBuffs = set(data.get("Buffs", []))   # aura vẽ ở remote update

    ##
    # Đổi hoạt cảnh tàu remote khi trạng thái thay đổi (tránh setAnimation mỗi
    # khung). Khi vừa chuyển sang chết thì tạo vụ nổ (hiệu ứng vốn sinh cục bộ ở
    # máy chủ sở hữu, không được đồng bộ nên phải tái tạo tại đây).
    ###
    def applyRemoteState(self, state):
        if state == self.RemoteState:
            return
        self.RemoteState = state
        self.Alive = state != "dead"
        self.Invulnerable = state != "normal"
        if state == "dead":
            self.setAnimation(Animations.SpaceshipDeadAnimation)
            Explosion(self)
        elif state == "respawn":
            self.setAnimation(Animations.SpaceshipRespawnAnimation)
        else:
            self.setAnimation(Animations.SpaceshipAnimation)

    def update(self):
        # Tàu remote: trượt mượt về vị trí đồng bộ mới nhất + chạy hoạt cảnh; mọi
        # thứ khác đã áp trong applySyncData (gọi ở handleDataBeforeUpdate).
        if self.Remote:
            self.lerpToTarget()
            self.Animation.update()
            self.updateBadge()
            self.updateAuras(self.RemoteBuffs)   # aura theo buff đồng bộ từ chủ sở hữu
            return

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

        self.updateBuffs()

        # Check shooting
        if not self.Overheat:
            if self.IsShooting and self.Alive:
                self.doShooting()
                self.OverheatCooldownRate = ObjectConstants.SPACESHIP_OVERHEAT_STEP * 2 / 3
                # RAPID: bắn liên tục không tích quá tải.
                if not self.RapidFire:
                    self.OverheatLevel += ObjectConstants.SPACESHIP_OVERHEAT_STEP
                    if self.OverheatLevel >= 1:
                        self.OverheatLevel = 1
                        OverheatEffect(self)
            else:
                self.ShootingDelay = ObjectConstants.SPACESHIP_SHOOTING_INTERVAL
                self.OverheatLevel -= self.OverheatCooldownRate
                if self.OverheatLevel < 0:
                    self.OverheatLevel = 0

        self.updateOverheatBar()
        self.updateBadge()