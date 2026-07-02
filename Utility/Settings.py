import os
import json

from kivy.core.window import Window

##
# Cấu hình người chơi tùy chỉnh, lưu ra file JSON ở thư mục home để giữ lại giữa
# các lần chạy (ghi được cả khi chạy dưới dạng .exe đóng gói - thư mục _MEIPASS
# chỉ đọc, còn home ghi được).
#
# Hai tùy chọn đều có tác dụng thật:
#   - Difficulty : nhân nhiều thông số gameplay (thiên thạch, máu + độ hung hãn
#     của boss, tần suất & thời lượng vật phẩm...). "Normal" = giá trị gốc (x1).
#   - Fullscreen : bật/tắt toàn màn hình cửa sổ Kivy ngay lập tức.
#
# Lưu ý multiplayer: độ khó là cài đặt riêng mỗi máy. Thế giới dùng chung (boss,
# thiên thạch, sinh vật phẩm) do Host quản nên theo độ khó của HOST; thời lượng
# hiệu ứng vật phẩm áp cho từng người chơi nên theo độ khó của chính máy đó.
###
class _Settings:
    DIFFICULTIES = ["Easy", "Normal", "Hard"]

    _METEOR_MULTIPLIER = {"Easy": 0.6, "Normal": 1.0, "Hard": 1.6}
    _BOSS_HEALTH_MULTIPLIER = {"Easy": 0.7, "Normal": 1.0, "Hard": 1.4}
    # Boss bắn thưa/dày: >1 = cooldown dài hơn -> bắn ÍT hơn (dễ).
    _BOSS_FIRE_COOLDOWN_MULTIPLIER = {"Easy": 1.45, "Normal": 1.0, "Hard": 0.72}
    # Số đạn mỗi đòn của boss.
    _BOSS_BULLET_COUNT_MULTIPLIER = {"Easy": 0.7, "Normal": 1.0, "Hard": 1.35}
    # Tốc độ đạn boss.
    _BOSS_PROJECTILE_SPEED_MULTIPLIER = {"Easy": 0.82, "Normal": 1.0, "Hard": 1.2}
    # Tần suất rơi / tự sinh vật phẩm.
    _POWERUP_SPAWN_MULTIPLIER = {"Easy": 1.6, "Normal": 1.0, "Hard": 0.6}
    # Thời lượng hiệu ứng vật phẩm có hạn giờ.
    _POWERUP_DURATION_MULTIPLIER = {"Easy": 1.4, "Normal": 1.0, "Hard": 0.7}

    def __init__(self):
        self.Difficulty = "Normal"
        self.Fullscreen = True
        self.load()

    @property
    def filePath(self):
        return os.path.join(os.path.expanduser("~"), "SpaceShooterSettings.json")

    ##
    # Đọc cấu hình đã lưu (bỏ qua nếu thiếu file / hỏng - dùng mặc định).
    ###
    def load(self):
        try:
            with open(self.filePath, "r") as f:
                data = json.load(f)
            if data.get("Difficulty") in self.DIFFICULTIES:
                self.Difficulty = data["Difficulty"]
            self.Fullscreen = bool(data.get("Fullscreen", self.Fullscreen))
        except (OSError, ValueError):
            pass

    def save(self):
        try:
            with open(self.filePath, "w") as f:
                json.dump({"Difficulty": self.Difficulty, "Fullscreen": self.Fullscreen}, f)
        except OSError:
            pass

    ##
    # Áp dụng chế độ hiển thị (toàn màn hình / cửa sổ) lên cửa sổ Kivy.
    ###
    def applyDisplay(self):
        if self.Fullscreen:
            Window.size = (1920, 1080)
            Window.fullscreen = True
        else:
            Window.fullscreen = False
            Window.size = (1280, 720)

    def cycleDifficulty(self):
        i = self.DIFFICULTIES.index(self.Difficulty)
        self.Difficulty = self.DIFFICULTIES[(i + 1) % len(self.DIFFICULTIES)]
        self.save()

    def toggleFullscreen(self):
        self.Fullscreen = not self.Fullscreen
        self.applyDisplay()
        self.save()

    @property
    def meteorChanceMultiplier(self):
        return self._METEOR_MULTIPLIER[self.Difficulty]

    @property
    def bossHealthMultiplier(self):
        return self._BOSS_HEALTH_MULTIPLIER[self.Difficulty]

    @property
    def bossFireCooldownMultiplier(self):
        return self._BOSS_FIRE_COOLDOWN_MULTIPLIER[self.Difficulty]

    @property
    def bossBulletCountMultiplier(self):
        return self._BOSS_BULLET_COUNT_MULTIPLIER[self.Difficulty]

    @property
    def bossProjectileSpeedMultiplier(self):
        return self._BOSS_PROJECTILE_SPEED_MULTIPLIER[self.Difficulty]

    @property
    def powerUpSpawnMultiplier(self):
        return self._POWERUP_SPAWN_MULTIPLIER[self.Difficulty]

    @property
    def powerUpDurationMultiplier(self):
        return self._POWERUP_DURATION_MULTIPLIER[self.Difficulty]


# Singleton dùng chung toàn game.
Settings = _Settings()
