import math
import random

from Base.Objects.BaseObject import BaseObject
from Base.Objects.BossProjectile import BossProjectile
from Base.Objects.Explosion import Explosion
from Base.Components import GameLabel
from Base.Animation import Animations
from Base.Constants import ObjectConstants, ImageConstants
from Base.Textures import Textures

from Utility import GameUtility
from Utility.Settings import Settings

##
# Boss - trùm cuối xuất hiện sau mỗi vài đợt thiên thạch.
# Vòng đời:
#   1. Intro : lao từ trên xuống vị trí hover, bất tử trong lúc này.
#   2. Hover : AI trạng thái (strafe / hunt / barrage / spiral) - xem updateAI.
#   3. Death : hết máu -> nổ, dọn dẹp thanh máu, thưởng mạng cho người chơi.
#
# AI chỉ chạy ở Host / chơi đơn. Boss phía Client (Remote) chỉ vẽ theo vị trí và
# máu được đồng bộ; đạn do Host tạo và gửi xuống qua ListNewObjects. Nhờ vậy AI
# có thể phức tạp tùy ý mà không cần thêm trường đồng bộ nào và không gây lệch.
#
# Properties:
#   Variant        : 0 Marauder / 1 Sentinel / 2 Dreadnought (đổi texture, máu, đạn)
#   CurrentHealth  : Máu hiện tại
#   MaxHealth      : Máu tối đa
#   Phase          : 0/1/2 theo % máu còn lại - càng thấp càng hung hãn
#   Intro          : Đang trong pha lao xuống (bất tử) hay không
#   Remote         : True nếu là boss "ảo" phía Client
###
class Boss(BaseObject):
    Name = "Boss"
    # Thân tàu chỉ chiếm phần giữa khung 256px -> thu nhỏ hộp va chạm cho khớp.
    HitboxScale = ObjectConstants.BOSS_HITBOX_SCALE

    def __init__(self, gameplay, variant=0, remote=False):
        super(Boss, self).__init__(ObjectConstants.BOSS_SCREEN_RECT,
                                   Animations.BossAnimations[variant],
                                   gameplay)
        self.Variant = variant
        self.Remote = remote

        # Độ khó (cài đặt) nhân vào máu boss. Với boss ảo phía Client, giá trị này
        # sẽ được ghi đè theo dữ liệu đồng bộ từ Host (applyBossSync).
        self.MaxHealth = ObjectConstants.BOSS_MAX_HEALTH[variant] * Settings.bossHealthMultiplier
        self.CurrentHealth = self.MaxHealth
        self.ProjectileType = ObjectConstants.BOSS_PROJECTILE_TYPE[variant]

        self.Intro = True
        self.Dead = False

        # Trạng thái AI.
        self.Phase = 0
        self.AiState = "STRAFE"
        self.AiTimer = 0            # số khung còn lại của hành vi hiện tại
        self.AttackCooldown = 0     # số khung tới lượt bắn tiếp theo
        self.SpiralAngle = 0.0      # góc quay hiện tại của đòn xoắn ốc

        # Thanh máu: vẽ thanh máu trước, khung viền đè lên trên, rồi tới số máu.
        self.HealthBar = Textures.BossHealthBar.clone()
        self.HealthFrame = Textures.BossHealthFrame.clone()
        GameUtility.drawTexture(gameplay, self.HealthBar, ImageConstants.BOSS_HEALTH_FRAME_SCREEN_RECT)
        GameUtility.drawTexture(gameplay, self.HealthFrame, ImageConstants.BOSS_HEALTH_FRAME_SCREEN_RECT)
        self.HealthText = GameLabel(gameplay, str(int(self.MaxHealth)), ImageConstants.BOSS_HEALTH_TEXT_POS)
        self.updateHealthBar()

    ##
    # Cập nhật thanh máu theo tỉ lệ máu còn lại (rút cạn từ phải qua trái).
    ###
    def updateHealthBar(self):
        ratio = self.CurrentHealth / self.MaxHealth
        self.HealthBar.setRect(ImageConstants.BOSS_HEALTH_BAR_CLIP_RECT(ratio))
        self.HealthBar.setPos(ImageConstants.BOSS_HEALTH_BAR_POS_X(ratio), ImageConstants.BOSS_HEALTH_BAR_POS_Y)
        self.HealthBar.setSize(ImageConstants.BOSS_HEALTH_BAR_SCREEN_WIDTH * ratio,
                               ImageConstants.BOSS_HEALTH_BAR_SCREEN_HEIGHT)
        self.HealthText.setText(str(int(self.CurrentHealth)))

    ##
    # Nhận sát thương từ đạn người chơi (chỉ chạy ở Host / chơi đơn).
    ###
    def takeDamage(self, amount):
        if self.Intro or self.Dead:
            return
        self.CurrentHealth -= amount
        if self.CurrentHealth <= 0:
            self.CurrentHealth = 0
            self.die()
            return
        self.updateHealthBar()

    # ----------------------------------------------------------------- Bắn đạn
    ##
    # Tạo một viên đạn boss và (nếu là Host nhiều người) ghi lại để đồng bộ.
    ###
    def spawnProjectile(self, x, y, dx, dy):
        BossProjectile(self.Gameplay, x, y, dx, dy, self.ProjectileType)
        if self.Gameplay.Socket is not None and not self.Gameplay.IsClient:
            self.Gameplay.ListNewObjects.append({
                "Name": "BossProjectile",
                "Data": (x, y, dx, dy, self.ProjectileType)
            })

    ##
    # Vector vận tốc từ một góc đo so với trục thẳng xuống (dương = lệch phải).
    ###
    def velFromAngle(self, speed, angle):
        return speed * math.sin(angle), -speed * math.cos(angle)

    ##
    # Người chơi còn sống gần boss nhất (theo trục X). None nếu không còn ai.
    ###
    def nearestPlayer(self):
        players = [p for p in (self.Gameplay.Player, self.Gameplay.Otherplayer)
                   if p is not None and p.Alive]
        if not players:
            return None
        myX = self.X - self.Width / 2
        return min(players, key=lambda p: abs((p.X - p.Width / 2) - myX))

    ##
    # Toạ độ họng súng (giữa - đáy boss).
    ###
    def muzzle(self):
        return self.X - self.Width / 2, self.Y - self.Height

    ##
    # Số đạn / tốc độ đạn sau khi nhân theo độ khó (của HOST - nơi chạy AI boss).
    ###
    def scaledCount(self, base):
        return max(1, round(base * Settings.bossBulletCountMultiplier))

    def scaledSpeed(self, base):
        return base * Settings.bossProjectileSpeedMultiplier

    ##
    # Rẻ quạt cố định hướng xuống (đòn cơ bản).
    ###
    def fireFan(self):
        count = self.scaledCount(ObjectConstants.BOSS_ATTACK_BULLETS[self.Variant])
        fromX, fromY = self.muzzle()
        dy = self.scaledSpeed(ObjectConstants.BOSS_PROJECTILE_SPEED_Y)
        middle = (count - 1) / 2.0
        for i in range(count):
            dx = (i - middle) * ObjectConstants.BOSS_ATTACK_SPREAD
            self.spawnProjectile(fromX, fromY, dx, dy)

    ##
    # Loạt đạn ngắm thẳng vào người chơi gần nhất (có tản nhẹ khi bắn nhiều viên).
    ###
    def fireAimed(self):
        fromX, fromY = self.muzzle()
        target = self.nearestPlayer()
        if target is None:
            baseAngle = 0.0
        else:
            baseAngle = math.atan2(target.X - target.Width / 2 - fromX,
                                   fromY - target.Y)
        burst = self.scaledCount(ObjectConstants.BOSS_AIMED_BURST[self.Phase])
        speed = self.scaledSpeed(ObjectConstants.BOSS_AIMED_SPEED)
        middle = (burst - 1) / 2.0
        for i in range(burst):
            angle = baseAngle + (i - middle) * 0.12
            dx, dy = self.velFromAngle(speed, angle)
            self.spawnProjectile(fromX, fromY, dx, dy)

    ##
    # Bắn tỏa hình quạt rộng (radial barrage) hướng xuống nửa dưới.
    ###
    def fireRadial(self):
        fromX, fromY = self.muzzle()
        count = self.scaledCount(ObjectConstants.BOSS_RADIAL_COUNT[self.Phase])
        speed = self.scaledSpeed(ObjectConstants.BOSS_PROJECTILE_SPEED)
        arc = ObjectConstants.BOSS_RADIAL_ARC
        step = arc / (count - 1) if count > 1 else 0.0
        start = -arc / 2
        for i in range(count):
            dx, dy = self.velFromAngle(speed, start + i * step)
            self.spawnProjectile(fromX, fromY, dx, dy)

    ##
    # Hai cánh tay đạn quay dần tạo hình xoắn ốc.
    ###
    def fireSpiral(self):
        fromX, fromY = self.muzzle()
        speed = self.scaledSpeed(ObjectConstants.BOSS_PROJECTILE_SPEED)
        for arm in (0.0, math.pi):
            dx, dy = self.velFromAngle(speed, self.SpiralAngle + arm)
            self.spawnProjectile(fromX, fromY, dx, dy)
        self.SpiralAngle += ObjectConstants.BOSS_SPIRAL_STEP

    # -------------------------------------------------------------------- AI
    ##
    # Bật/tắt cooldown và bắn khi tới lượt (đòn dùng cooldown theo phase).
    ###
    def tickAttack(self, fireMethod, cooldown):
        self.AttackCooldown -= 1
        if self.AttackCooldown <= 0:
            fireMethod()
            # Độ khó điều chỉnh nhịp bắn: cooldown dài hơn (Easy) -> bắn thưa hơn.
            self.AttackCooldown = max(1, round(cooldown * Settings.bossFireCooldownMultiplier))

    ##
    # Giữ boss trong khung: nếu bước kế tiếp vượt biên thì ép về biên và dừng.
    ###
    def clampBorders(self):
        nextX = self.X + self.Dx
        if nextX >= ObjectConstants.BOSS_BORDER_RIGHT:
            self.X = ObjectConstants.BOSS_BORDER_RIGHT
            self.Dx = 0
        elif nextX <= ObjectConstants.BOSS_BORDER_LEFT:
            self.X = ObjectConstants.BOSS_BORDER_LEFT
            self.Dx = 0

    ##
    # Đi ngang qua lại, dội biên; bắn rẻ quạt theo nhịp.
    ###
    def stateStrafe(self):
        speed = ObjectConstants.BOSS_STRAFE_SPEED[self.Phase]
        self.Dx = speed if self.Dx >= 0 else -speed
        if self.X >= ObjectConstants.BOSS_BORDER_RIGHT:
            self.X = ObjectConstants.BOSS_BORDER_RIGHT
            self.Dx = -speed
        elif self.X <= ObjectConstants.BOSS_BORDER_LEFT:
            self.X = ObjectConstants.BOSS_BORDER_LEFT
            self.Dx = speed
        self.tickAttack(self.fireFan, ObjectConstants.BOSS_ATTACK_COOLDOWN[self.Phase])

    ##
    # Truy đuổi: bám theo trục X của người chơi và bắn đạn ngắm.
    ###
    def stateHunt(self):
        speed = ObjectConstants.BOSS_HUNT_SPEED[self.Phase]
        target = self.nearestPlayer()
        if target is None:
            self.Dx = 0
        else:
            myX = self.X - self.Width / 2
            tx = target.X - target.Width / 2
            if tx > myX + speed:
                self.Dx = speed
            elif tx < myX - speed:
                self.Dx = -speed
            else:
                self.Dx = 0
        self.clampBorders()
        self.tickAttack(self.fireAimed, ObjectConstants.BOSS_ATTACK_COOLDOWN[self.Phase])

    ##
    # Đứng yên và nhả các đợt đạn tỏa rộng.
    ###
    def stateBarrage(self):
        self.Dx = 0
        self.tickAttack(self.fireRadial, ObjectConstants.BOSS_BARRAGE_COOLDOWN[self.Phase])

    ##
    # Trôi chậm dội biên trong khi phun đạn xoắn ốc.
    ###
    def stateSpiral(self):
        speed = ObjectConstants.BOSS_STRAFE_SPEED[self.Phase] * 0.5
        self.Dx = speed if self.Dx >= 0 else -speed
        if self.X >= ObjectConstants.BOSS_BORDER_RIGHT:
            self.X = ObjectConstants.BOSS_BORDER_RIGHT
            self.Dx = -speed
        elif self.X <= ObjectConstants.BOSS_BORDER_LEFT:
            self.X = ObjectConstants.BOSS_BORDER_LEFT
            self.Dx = speed
        self.tickAttack(self.fireSpiral, ObjectConstants.BOSS_SPIRAL_COOLDOWN)

    ##
    # Chọn hành vi kế tiếp theo trọng số của phase hiện tại.
    ###
    def chooseState(self):
        weights = ObjectConstants.BOSS_STATE_WEIGHTS[self.Phase]
        states = list(weights.keys())
        self.AiState = random.choices(states, weights=[weights[s] for s in states])[0]
        self.AiTimer = ObjectConstants.BOSS_STATE_DURATION[self.AiState]
        self.AttackCooldown = 0        # nổ phát đầu ngay khi vào trạng thái
        self.SpiralAngle = 0.0

    ##
    # Bộ não boss: cập nhật phase, đổi hành vi khi hết giờ, rồi chạy hành vi.
    ###
    def updateAI(self):
        ratio = self.CurrentHealth / self.MaxHealth
        low, lower = ObjectConstants.BOSS_PHASE_THRESHOLDS
        self.Phase = 0 if ratio > low else (1 if ratio > lower else 2)

        if self.AiTimer <= 0:
            self.chooseState()
        self.AiTimer -= 1

        if self.AiState == "STRAFE":
            self.stateStrafe()
        elif self.AiState == "HUNT":
            self.stateHunt()
        elif self.AiState == "BARRAGE":
            self.stateBarrage()
        else:
            self.stateSpiral()

    def update(self):
        # Boss phía Client: trượt mượt về vị trí đồng bộ mới nhất + chạy hoạt cảnh
        # (máu/pha đã áp trong Gameplay.applyBossSync). Không AI, không va chạm.
        if self.Remote:
            self.lerpToTarget()
            self.Animation.update()
            return

        if self.Intro:
            self.Dy = -ObjectConstants.BOSS_ENTRY_SPEED
            if self.Y <= ObjectConstants.BOSS_ENTRY_TARGET_Y:
                self.Y = ObjectConstants.BOSS_ENTRY_TARGET_Y
                self.Dy = 0
                self.Intro = False
        else:
            self.Dy = 0
            self.updateAI()

        super().update()

    ##
    # Boss chết: nổ, dọn thanh máu, thưởng mạng cho người chơi còn sống.
    ###
    def die(self):
        if self.Dead:
            return
        self.Dead = True

        Explosion(self)

        self.Gameplay.remove_widget(self.HealthBar.Image)
        self.Gameplay.remove_widget(self.HealthFrame.Image)
        self.Gameplay.remove_widget(self.HealthText)

        self.Inactive = True
        self.Gameplay.Boss = None
        self.Gameplay.BossActive = False

        # Thưởng: hồi 1 mạng cho mỗi người chơi còn sống (tối đa mức nền 3).
        for player in (self.Gameplay.Player, self.Gameplay.Otherplayer):
            if player is not None and player.Alive and player.Lives < ObjectConstants.SPACESHIP_BASE_LIVES:
                player.Lives += 1
                player.updateLifeDisplay()

        # Chỉ Host / chơi đơn mới đếm số boss đã hạ (quyết định biến thể tiếp theo).
        if not self.Remote:
            self.Gameplay.BossesDefeated += 1

    ##
    # Va chạm với boss được xử lý ở Bullet / Spaceship, boss không tự xử lý.
    ###
    def handleCollision(self, otherObject):
        pass
