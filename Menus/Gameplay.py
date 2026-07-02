import random

from Utility import GameUtility, JSONUtility
from Utility.Settings import Settings
from Base.Objects import Spaceship, Meteor
from Base.Objects.Boss import Boss
from Base.Objects.Bullet import Bullet
from Base.Objects.BossProjectile import BossProjectile
from Base.Objects.PowerUp import PowerUp
from Base.Constants import ObjectConstants, SocketData
from Base.Textures import Textures
from .Menu import Menu
from Socket import Server, Client

##
# Class gameplay chính
###
class Gameplay(Menu):
    # Danh sách tất cả vật thể trong game
    ListObjects = []
    # Người chơi chính
    Player = None
    # Người chơi tham gia
    Otherplayer = None
    # Socket dùng để truyền nhận dữ liệu (chơi 2 người)
    Socket = None
    # Danh sách những vật thể mới, dùng để gửi từ Host xuống Client
    ListNewObjects = []
    IsClient = False
    # Tỉ lệ tạo thiên thạch
    MeteorCreationChance = ObjectConstants.METEOR_CREATION_CHANCE

    def __init__(self, app, socket=None):
        super(Gameplay, self).__init__(app)

        self.Socket = socket

        # Khởi tạo trạng thái riêng cho từng ván (tránh rò rỉ giữa các lần chơi).
        self.ListObjects = []
        self.ListNewObjects = []
        # Nhóm va chạm theo loại vật thể, để vật thể tấn công chỉ quét đúng mục
        # tiêu. Phải khởi tạo trước khi tạo bất kỳ vật thể nào (addNewObject).
        self.CollisionGroups = {"Meteor": [], "BossProjectile": [], "Boss": [], "PowerUp": []}
        self.Otherplayer = None
        # Trạng thái boss
        self.MeteorsDestroyed = 0
        self.BossActive = False
        self.Boss = None
        self.BossesDefeated = 0
        self.NextBossThreshold = ObjectConstants.BOSS_SPAWN_EVERY

        # Cảnh báo trước khi boss xuất hiện (biển nhấp nháy telegraph).
        self.BossWarningActive = False          # Host/chơi đơn đang đếm ngược
        self.WarningTexture = Textures.BossWarning.clone()
        self.WarningShown = False               # biển đang hiển thị hay không
        self.WarningTimer = 0
        self.WarningFlash = 0

        # Độ khó (cài đặt) nhân vào tỉ lệ tạo thiên thạch. Nhánh Host x2 thêm bên dưới.
        self.MeteorCreationChance = ObjectConstants.METEOR_CREATION_CHANCE * Settings.meteorChanceMultiplier

        # Đạn người chơi bản thân bắn ra trong khung này, chờ phát cho máy bên kia.
        self.NewBullets = []

        # Vật phẩm: bộ đếm cấp ID (Host/chơi đơn) và danh sách ID vừa hứng trong
        # khung này (gửi cho máy kia để gỡ bản sao tương ứng).
        self.PowerUpCounter = 0
        self.ConsumedPowerUps = []

        # Game over: khi tất cả người chơi hết mạng. Chờ GameOverTimer khung cho
        # vụ nổ cuối kịp chạy rồi mới chuyển màn.
        self.GameOver = False
        self.GameOverTimer = ObjectConstants.GAME_OVER_DELAY

        # Tạo người chơi. Otherplayer luôn là tàu "remote" - chỉ hiển thị theo dữ
        # liệu đồng bộ từ chủ sở hữu, không tự mô phỏng (tránh lệch trạng thái).
        if socket is None:
            self.Player = Spaceship(self)
        else:
            if isinstance(socket, Server):
                # Bỏ các gói dở của ván trước còn tồn trong đệm (khi host chơi lại
                # trên cùng kết nối) để không áp nhầm trạng thái cũ vào ván mới.
                socket.flush()
                self.Player = Spaceship(self, playerIndex=1)
                self.Otherplayer = Spaceship(self, playerIndex=2, remote=True)
                self.MeteorCreationChance *= 2
            else:
                self.IsClient = True
                self.Player = Spaceship(self, playerIndex=2)
                self.Otherplayer = Spaceship(self, playerIndex=1, remote=True)

    ##
    # Sự kiện nhấn phím xuống
    ###
    def onKeyDown(self, keyboard, keycode, text, modifiers):
        # Dùng tốc độ hiện hành của tàu (có thể đang được vật phẩm SPEED tăng).
        if keycode[1] == 'd':
            self.Player.Dx = self.Player.SpeedX
        if keycode[1] == 'a':
            self.Player.Dx = -self.Player.SpeedX
        if keycode[1] == 'w':
            self.Player.Dy = self.Player.SpeedY
        if keycode[1] == 's':
            self.Player.Dy = -self.Player.SpeedY
        if keycode[1] == 'spacebar':
            self.Player.IsShooting = True
        return True

    ##
    # Sự kiện nhả phím
    ###
    def onKeyUp(self, keyboard, keycode):
        if keycode[1] == 'd':
            if self.Player.Dx > 0:
                self.Player.Dx = 0
        if keycode[1] == 'a':
            if self.Player.Dx < 0:
                self.Player.Dx = 0
        if keycode[1] == 'w':
            if self.Player.Dy > 0:
                self.Player.Dy = 0
        if keycode[1] == 's':
            if self.Player.Dy < 0:
                self.Player.Dy = 0
        if keycode[1] == 'spacebar':
            self.Player.IsShooting = False
        return True
        

    def update(self, dt):
        # Nếu vừa chuyển sang ván mới (host restart) thì dừng update ván cũ ngay.
        if self.handleDataBeforeUpdate():
            return

        # Cập nhật vật thể và dọn vật thể đã chết trong cùng một lượt duyệt:
        #   - Dựng lại danh sách (O(n)) thay vì list.remove() từng phần tử
        #     (O(n) mỗi lần -> O(n^2)) và tránh lỗi bỏ sót do xóa phần tử ngay
        #     trong lúc đang lặp.
        #   - Dựng lại luôn các nhóm va chạm từ những vật thể còn sống.
        # Vật thể mới sinh ra giữa lượt (đạn, vụ nổ...) được append vào
        # ListObjects và vẫn được vòng lặp này duyệt tới, giữ nguyên hành vi cũ.
        survivors = []
        collisionGroups = {"Meteor": [], "BossProjectile": [], "Boss": [], "PowerUp": []}
        for obj in self.ListObjects:
            if obj.Inactive:
                self.remove_widget(obj.Animation.Texture.Image)
                continue
            obj.update()
            if obj.Inactive:
                self.remove_widget(obj.Animation.Texture.Image)
                continue
            survivors.append(obj)
            group = collisionGroups.get(obj.Name)
            if group is not None:
                group.append(obj)
        self.ListObjects = survivors
        self.CollisionGroups = collisionGroups

        # Nhấp nháy biển cảnh báo (chạy ở cả Host lẫn Client khi biển hiển thị).
        self.updateWarningFlash()

        # Boss (Host / chơi đơn quyết định): đủ số thiên thạch -> hiện cảnh báo
        # -> đếm ngược -> sinh boss. Client hiển thị cảnh báo theo cờ đồng bộ
        # trong handleDataBeforeUpdate.
        if not self.IsClient and not self.BossActive:
            if self.BossWarningActive:
                self.updateBossWarning()
            elif self.MeteorsDestroyed >= self.NextBossThreshold:
                self.startBossWarning()

        # Tạo thiên thạch (tạm dừng khi đang cảnh báo hoặc đang đánh boss).
        if not self.IsClient and not self.BossActive and not self.BossWarningActive:
            GameUtility.randomCreateObject(self, Meteor, ObjectConstants.METEOR_CREATION_POOL, self.MeteorCreationChance)

        # Vật phẩm tự rơi ngẫu nhiên theo thời gian (kể cả lúc đánh boss).
        self.randomSpawnPowerUp()

        self.checkGameOver()

    ##
    # Hết game khi MỌI người chơi đã hết mạng (Lives <= 0). Máu của người chơi bên
    # kia là dữ liệu đồng bộ nên cả hai máy đều tự phát hiện được. Chờ một nhịp cho
    # vụ nổ cuối chạy xong rồi mở màn Game Over.
    ###
    def checkGameOver(self):
        if self.GameOver:
            return
        if self.Player.Lives > 0:
            return
        if self.Otherplayer is not None and self.Otherplayer.Lives > 0:
            return

        self.GameOverTimer -= 1
        if self.GameOverTimer <= 0:
            self.GameOver = True
            from .GameOverMenu import GameOverMenu
            GameUtility.openMenu(GameOverMenu(self.App, self.Socket))

    ##
    # --- Biển cảnh báo trước khi boss xuất hiện ---
    ###
    def showWarningBanner(self):
        if self.WarningShown:
            return
        GameUtility.drawTexture(self, self.WarningTexture, ObjectConstants.BOSS_WARNING_SCREEN_RECT)
        self.WarningShown = True
        self.WarningFlash = 0

    def hideWarningBanner(self):
        if not self.WarningShown:
            return
        self.remove_widget(self.WarningTexture.Image)
        self.WarningShown = False

    def updateWarningFlash(self):
        if not self.WarningShown:
            return
        self.WarningFlash += 1
        on = (self.WarningFlash // ObjectConstants.BOSS_WARNING_FLASH_PERIOD) % 2 == 0
        self.WarningTexture.Image.opacity = 1.0 if on else 0.25

    ##
    # Host / chơi đơn: bắt đầu pha cảnh báo (hiện biển + đặt đồng hồ đếm ngược).
    ###
    def startBossWarning(self):
        self.BossWarningActive = True
        self.WarningTimer = ObjectConstants.BOSS_WARNING_DURATION
        self.showWarningBanner()

    ##
    # Host / chơi đơn: đếm ngược cảnh báo; hết giờ thì ẩn biển và sinh boss.
    ###
    def updateBossWarning(self):
        self.WarningTimer -= 1
        if self.WarningTimer <= 0:
            self.BossWarningActive = False
            self.hideWarningBanner()
            self.spawnBoss()

    ##
    # Client: hiện/ẩn biển cảnh báo theo cờ đồng bộ từ Host.
    ###
    def applyWarningSync(self, active):
        if active:
            self.showWarningBanner()
        else:
            self.hideWarningBanner()

    ##
    # Sinh boss mới (chỉ Host / chơi đơn). Biến thể xoay vòng theo số boss đã hạ.
    ###
    def spawnBoss(self):
        variant = self.BossesDefeated % 3
        self.Boss = Boss(self, variant)
        self.BossActive = True
        self.NextBossThreshold += ObjectConstants.BOSS_SPAWN_EVERY

    ##
    # Tạo một vật phẩm tại (x, y) (loại ngẫu nhiên) - chỉ Host / chơi đơn, và gửi
    # sự kiện cho Client để hai máy thấy giống nhau.
    ###
    def spawnPowerUp(self, x, y):
        powerType = random.choice(ObjectConstants.POWERUP_TYPES)
        powerUpId = self.PowerUpCounter
        self.PowerUpCounter += 1
        PowerUp(self, powerUpId, powerType, x, y)
        if self.Socket is not None:
            self.ListNewObjects.append({
                "Name": "PowerUp",
                "Data": (powerUpId, powerType, x, y)
            })

    ##
    # Cơ hội rơi vật phẩm tại (x, y) khi hạ thiên thạch (theo tỉ lệ DROP).
    ###
    def trySpawnPowerUp(self, x, y):
        if self.IsClient:
            return
        # Độ khó (của Host) điều chỉnh tần suất rơi vật phẩm.
        if random.randint(0, ObjectConstants.POWERUP_DROP_POOL) < ObjectConstants.POWERUP_DROP_CHANCE * Settings.powerUpSpawnMultiplier:
            self.spawnPowerUp(x, y)

    ##
    # Vật phẩm tự rơi ngẫu nhiên theo thời gian (không cần bắn đá). Mỗi khung có
    # xác suất nhỏ sinh một vật phẩm ở toạ độ x ngẫu nhiên, rơi từ đỉnh màn hình.
    ###
    def randomSpawnPowerUp(self):
        if self.IsClient:
            return
        if random.randint(0, ObjectConstants.POWERUP_RANDOM_POOL) < ObjectConstants.POWERUP_RANDOM_CHANCE * Settings.powerUpSpawnMultiplier:
            x = random.randint(5, 95) / 100.0
            self.spawnPowerUp(x, ObjectConstants.POWERUP_RANDOM_SPAWN_Y)

    ##
    # Dữ liệu boss Host gửi cho Client mỗi khung hình (None nếu không có boss).
    ###
    def getBossSyncData(self):
        if self.Boss is None:
            return None
        boss = self.Boss
        return {
            "Variant": boss.Variant,
            "X": boss.X,
            "Y": boss.Y,
            "Health": boss.CurrentHealth,
            "MaxHealth": boss.MaxHealth,
            "Intro": boss.Intro
        }

    ##
    # Client áp dụng trạng thái boss nhận từ Host:
    #   - None  : boss đã chết -> dọn dẹp boss ảo.
    #   - dict  : tạo boss ảo nếu chưa có, rồi cập nhật vị trí / máu.
    ###
    def applyBossSync(self, bossData):
        if bossData is None:
            if self.Boss is not None:
                self.Boss.die()
            return
        justCreated = False
        if self.Boss is None:
            self.Boss = Boss(self, bossData["Variant"], remote=True)
            self.BossActive = True
            justCreated = True
        self.Boss.Intro = bossData["Intro"]
        # Máu tối đa lấy theo Host để thanh máu đúng dù độ khó hai bên khác nhau.
        self.Boss.MaxHealth = bossData["MaxHealth"]
        self.Boss.CurrentHealth = bossData["Health"]
        # Vị trí -> mục tiêu nội suy; lần đầu thì nhảy thẳng để khỏi trượt từ xa.
        self.Boss.TargetX = bossData["X"]
        self.Boss.TargetY = bossData["Y"]
        if justCreated:
            self.Boss.setPos(bossData["X"], bossData["Y"])
        self.Boss.updateHealthBar()

    ##
    # Trao đổi dữ liệu KHÔNG CHẶN (mô hình tách rời, không lockstep): vòng game
    # chạy full 60fps nội bộ bất kể độ trễ mạng; tàu/boss bên kia được nội suy
    # cho mượt. TCP (đóng khung, TCP_NODELAY) vẫn bảo đảm mọi SỰ KIỆN (đạn, thiên
    # thạch, đạn boss) tới đủ và đúng thứ tự - ta chỉ đọc bất đồng bộ.
    #
    #   1. Gửi ảnh chụp trạng thái của mình + sự kiện khung này.
    #   2. Rút HẾT gói đang chờ: SỰ KIỆN áp cho mọi gói (không được bỏ sót);
    #      TRẠNG THÁI (vị trí/máu/cờ) chỉ lấy gói mới nhất (ghi đè, idempotent).
    ###
    def handleDataBeforeUpdate(self):
        if self.Socket is None:
            return

        # 1) Gửi ảnh chụp của mình (không chặn game loop).
        payload = {
            "Player": self.Player.getSyncData(),
            "Bullets": self.NewBullets,
            "Consumed": self.ConsumedPowerUps      # ID vật phẩm mình vừa hứng
        }
        if not self.IsClient:
            # Host còn quyền quản thế giới: thiên thạch/đạn boss/vật phẩm + boss.
            payload["NewObjects"] = self.ListNewObjects
            payload["Boss"] = self.getBossSyncData()
            payload["Warning"] = self.BossWarningActive
            self.ListNewObjects = []
        self.Socket.sendMessage(JSONUtility.encode(payload))
        self.NewBullets = []
        self.ConsumedPowerUps = []

        # 2) Rút hết gói đang chờ (không chặn). Sự kiện áp mọi gói, trạng thái lấy mới nhất.
        latest = None
        while True:
            raw = self.Socket.poll()
            if not raw:
                break
            # Host bấm "Restart" trong khi mình còn ở nhịp chờ Game Over: vào ván
            # mới ngay (hiếm, do độ trễ; xử lý ở đây để không vỡ JSON decode).
            if raw == SocketData.START_GAME_CODE:
                GameUtility.openMenu(Gameplay(self.App, self.Socket))
                return True
            message = JSONUtility.decode(raw)
            self.createBullets(message.get("Bullets", []))
            self.removeConsumedPowerUps(message.get("Consumed", []))
            if self.IsClient:
                for newObject in message.get("NewObjects", []):
                    if newObject["Name"] == "Meteor":
                        x, dx, dy = newObject["Data"]
                        Meteor(self, x, dx, dy)
                    elif newObject["Name"] == "BossProjectile":
                        x, y, dx, dy, projectileType = newObject["Data"]
                        BossProjectile(self, x, y, dx, dy, projectileType)
                    elif newObject["Name"] == "PowerUp":
                        powerUpId, powerType, x, y = newObject["Data"]
                        PowerUp(self, powerUpId, powerType, x, y)
            latest = message

        # 3) Áp trạng thái mới nhất (mục tiêu nội suy tàu/boss + cờ boss/cảnh báo).
        if latest is not None:
            self.Otherplayer.applySyncData(latest["Player"])
            if self.IsClient:
                self.applyBossSync(latest.get("Boss"))
                self.applyWarningSync(latest.get("Warning", False))

    ##
    # Tái tạo đạn của người chơi bên kia từ dữ liệu đồng bộ (toạ độ + số nòng).
    ###
    def createBullets(self, bulletsData):
        # Đạn nhận qua đồng bộ là của người chơi bên kia -> tô theo màu tàu họ.
        color = self.Otherplayer.PlayerColor if self.Otherplayer is not None else (1, 1, 1, 1)
        for x, y, bulletCount in bulletsData:
            Bullet(self, x, y, bulletCount, color)

    ##
    # Gỡ các vật phẩm mà máy bên kia vừa hứng (theo ID) để không còn lơ lửng /
    # bị hứng trùng trên máy này.
    ###
    def removeConsumedPowerUps(self, consumedIds):
        if not consumedIds:
            return
        consumedSet = set(consumedIds)
        for powerUp in self.CollisionGroups["PowerUp"]:
            if powerUp.PowerUpId in consumedSet:
                powerUp.Inactive = True