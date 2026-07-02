# Spaceship
SPACESHIP_SCREEN_RECT = [(0.5, 0.2, 1/24, 0.075), (0.3, 0.2, 1/24, 0.075), (0.7, 0.2, 1/24, 0.075)]

SPACESHIP_SCREEN_BORDER_LEFT = 0.05
SPACESHIP_SCREEN_BORDER_RIGHT = 0.995
SPACESHIP_SCREEN_BORDER_BOTTOM = 0.08
SPACESHIP_SCREEN_BORDER_TOP = 0.99

SPACESHIP_SPEED_X = 0.005
SPACESHIP_SPEED_Y = 0.005

SPACESHIP_SHOOTING_SPEED = 0.25
SPACESHIP_SHOOTING_INTERVAL = 2

SPACESHIP_OVERHEAT_STEP = 3/1500.0
SPACESHIP_OVERHEAT_COOLDOWN = 2 / 700.0

SPACESHIP_DEAD_COOLDOWN = 2 / 500.0
SPACESHIP_RESPAWN_COOLDOWN = 2 / 500.0

# Màu phân biệt người chơi trong multiplayer: nhân vào sprite tàu + tô nhãn P1/P2.
# Chỉ mục theo playerIndex (nhất quán hai máy: 1 = host, 2 = client). 0 = chơi đơn
# (trắng = không đổi màu).
PLAYER_COLORS = [
    (1, 1, 1, 1),           # 0 - chơi đơn (trắng)
    (0.4, 1.0, 0.5, 1),     # 1 - xanh lá (tránh trùng nền/đạn xanh dương cũ)
    (1.0, 0.6, 0.2, 1),     # 2 - cam
]
# Nhãn "P1"/"P2" đặt phía trên tàu một khoảng (theo trục Y màn hình).
PLAYER_BADGE_Y_OFFSET = 0.055

# Số khung chờ sau khi tất cả người chơi chết trước khi hiện màn Game Over
# (để vụ nổ cuối kịp chạy). ~1s ở 60fps.
GAME_OVER_DELAY = 60

# Bullet
BULLET_SCREEN_OFFSET_X = [-0.0105, -0.0035, 0.0033]
BULLET_SCREEN_OFFSET_Y = 0.045
BULLET_SCREEN_WIDTH = 25/1200
BULLET_SCREEN_HEIGHT = 0.05875

BULLET_SPEED_Y = 0.0075
BULLET_INACTIVE_POS_Y = 1.055

# Meteor
METEOR_CREATION_POOL = 200
METEOR_CREATION_CHANCE = 4

# Power-ups (rơi ra từ thiên thạch bị bắn hạ; do Host/chơi đơn quyết định).
POWERUP_TYPE_POWER = 0     # nâng cấp đạn (đạn to/mạnh hơn) - vĩnh viễn
POWERUP_TYPE_SPEED = 1     # tăng tốc di chuyển - có hạn giờ
POWERUP_TYPE_REPAIR = 2    # hồi +1 mạng (tối đa mức nền 3) - tức thời
POWERUP_TYPE_SHIELD = 3    # bất tử tạm thời - có hạn giờ
POWERUP_TYPE_RAPID = 4     # bắn nhanh + không quá tải - có hạn giờ
POWERUP_TYPE_HEART = 5     # +1 mạng phụ (vượt mức nền 3, tới MAX_LIVES) - tức thời
POWERUP_TYPES = [POWERUP_TYPE_POWER, POWERUP_TYPE_SPEED, POWERUP_TYPE_REPAIR,
                 POWERUP_TYPE_SHIELD, POWERUP_TYPE_RAPID, POWERUP_TYPE_HEART]
# Các loại có hạn giờ -> hiện ở HUD hiệu ứng đang chạy (kèm nhấp nháy sắp hết).
POWERUP_TIMED_TYPES = [POWERUP_TYPE_SPEED, POWERUP_TYPE_SHIELD, POWERUP_TYPE_RAPID]
# Mạng: mức nền (thanh máu sprite hiện tối đa 3) và mức tối đa nhờ tim phụ.
SPACESHIP_BASE_LIVES = 3
SPACESHIP_MAX_LIVES = 5
# Tỉ lệ rơi khi hạ một thiên thạch: DROP_CHANCE / (DROP_POOL+1).
POWERUP_DROP_POOL = 9
POWERUP_DROP_CHANCE = 4                    # ~40% khi hạ thiên thạch (tăng lên)
# Ngoài ra vật phẩm còn tự rơi ngẫu nhiên theo thời gian (không cần bắn đá).
# Xác suất mỗi khung = RANDOM_CHANCE / (RANDOM_POOL+1); ~1 vật phẩm mỗi ~3.5s.
POWERUP_RANDOM_POOL = 209
POWERUP_RANDOM_CHANCE = 1
POWERUP_RANDOM_SPAWN_Y = 1.0              # rơi từ đỉnh màn hình
POWERUP_SCREEN_WIDTH = 0.04               # to hơn cho dễ thấy / dễ hứng
POWERUP_SCREEN_HEIGHT = 0.06
POWERUP_FALL_SPEED_Y = -0.0035            # rơi xuống chậm để người chơi kịp hứng
POWERUP_INACTIVE_BOTTOM = 0.0
POWERUP_HITBOX_SCALE = 0.9                # hộp hứng rộng rãi
# Đạn tối đa khi nâng cấp POWER (đã có sẵn 3 mức sprite/độ rộng).
POWERUP_MAX_BULLET_COUNT = 3
# Thời lượng các hiệu ứng có hạn giờ (số khung, 60fps) - kéo dài thêm nữa.
POWERUP_SPEED_BOOST_FRAMES = 900          # ~15s
POWERUP_SHIELD_FRAMES = 900               # ~15s
POWERUP_RAPID_FRAMES = 1080               # ~18s
POWERUP_SPEED_BOOST_FACTOR = 1.7          # hệ số nhân tốc độ khi có SPEED
POWERUP_RAPID_FIRE_FACTOR = 2.6           # hệ số nhân nhịp bắn khi có RAPID

# HUD hiệu ứng đang chạy (chỉ hiển thị của người chơi cục bộ; theo playerIndex).
# Đặt ngay DƯỚI thanh quá tải: thanh ở top=0.94, cao 0.03 -> đáy ~0.91; căn theo
# mép thanh (P1/đơn neo mép trái 0.005, P2 neo mép phải 0.995).
BUFF_ICON_SIZE = (0.025, 0.044)
BUFF_HUD_Y = 0.905                        # top pos_hint hàng icon (ngay dưới đáy thanh 0.91)
BUFF_HUD_START_X = [0.03, 0.03, 0.995]    # right pos_hint icon đầu (mép trái thanh + bề rộng icon / mép phải thanh)
BUFF_HUD_STEP_X = [0.032, 0.032, -0.032]  # bước ngang (P1/đơn sang phải, P2 sang trái)
BUFF_BLINK_THRESHOLD = 90                 # còn dưới ~1.5s thì nhấp nháy báo sắp hết
BUFF_BLINK_PERIOD = 8                     # số khung mỗi lần bật/tắt

# Tim phụ (mạng vượt mức nền 3) hiện thành icon cạnh thanh máu, theo playerIndex.
EXTRA_HEART_SIZE = (0.02, 0.035)
EXTRA_HEART_Y = 0.99
EXTRA_HEART_START_X = [0.16, 0.16, 0.86]  # right pos_hint tim đầu (bên phải thanh máu / bên trái)
EXTRA_HEART_STEP_X = [0.024, 0.024, -0.024]

# Aura quanh tàu theo hiệu ứng: {loại: (cell aura, màu tô RGBA)}. cell 0 vòng, 1 quầng.
AURA_TYPES = [POWERUP_TYPE_SHIELD, POWERUP_TYPE_SPEED, POWERUP_TYPE_RAPID]
AURA_SPECS = {
    POWERUP_TYPE_SHIELD: (0, (0.72, 0.5, 1.0, 1)),   # vòng tím
    POWERUP_TYPE_SPEED:  (1, (0.3, 0.82, 1.0, 1)),   # quầng cyan
    POWERUP_TYPE_RAPID:  (1, (1.0, 0.42, 0.42, 1)),  # quầng đỏ
}
AURA_SIZE = (0.10, 0.17)                  # bao quanh tàu (rộng hơn tàu)
AURA_PULSE_PERIOD = 44                    # số khung một nhịp phập phồng
AURA_OPACITY_MIN = 0.35
AURA_OPACITY_MAX = 0.8

METEOR_SCREEN_Y = 1.035
METEOR_SCREEN_WIDTH = 0.04
METEOR_SCREEN_HEIGHT = 0.06

METEOR_INACTIVE_BOTTOM = 0.005
METEOR_INACTIVE_RIGHT = 1.04
METEOR_INACTIVE_LEFT = 0

# Explosion
EXPLOSION_ROCK_OFFSET_X = 0.085
EXPLOSION_ROCK_OFFSET_Y = 0.13
EXPLOSION_ROCK_SCREEN_WIDTH = 256/1200.0
EXPLOSION_ROCK_SCREEN_HEIGHT = 256/800.0

EXPLOSION_SPACESHIP_OFFSET_X = 0.085
EXPLOSION_SPACESHIP_OFFSET_Y = 0.13
EXPLOSION_SPACESHIP_SCREEN_WIDTH = 256/1200.0
EXPLOSION_SPACESHIP_SCREEN_HEIGHT = 256/800.0

EXPLOSION_BOSS_OFFSET_X = 0.045
EXPLOSION_BOSS_OFFSET_Y = 0.09
EXPLOSION_BOSS_SCREEN_WIDTH = 384/1200.0
EXPLOSION_BOSS_SCREEN_HEIGHT = 384/800.0

# Small spark where a bullet hits the boss.
EXPLOSION_BULLET_OFFSET_X = 0.03
EXPLOSION_BULLET_OFFSET_Y = 0.03
EXPLOSION_BULLET_SCREEN_WIDTH = 96/1200.0
EXPLOSION_BULLET_SCREEN_HEIGHT = 96/800.0

# Boss
# Spawned by the host (or single player) after this many meteors are shot down.
BOSS_SPAWN_EVERY = 15
# Right-edge X / top Y the boss spawns at (just above the top of the screen).
BOSS_SCREEN_RECT = (0.59, 1.25, 0.18, 0.22)
# Ship art fills the central ~65% of the 256px frame; tighten the hitbox to it.
BOSS_HITBOX_SCALE = 0.65
# Descent: glides down until its top reaches the target, then hovers + attacks.
BOSS_ENTRY_SPEED = 0.004
BOSS_ENTRY_TARGET_Y = 0.95
BOSS_BORDER_LEFT = 0.29
BOSS_BORDER_RIGHT = 0.89
# Per-variant tuning, indexed by variant (0 Marauder, 1 Sentinel, 2 Dreadnought).
BOSS_MAX_HEALTH = [400, 640, 900]
BOSS_PROJECTILE_TYPE = [0, 1, 0]          # 0 = plasma, 1 = void
BOSS_ATTACK_BULLETS = [3, 3, 4]           # projectiles in a fan volley (giảm cho dễ né)

# --- Boss warning banner (telegraph shown before the boss descends) ---
BOSS_WARNING_DURATION = 100               # frames the banner shows (~1.6s @60fps)
BOSS_WARNING_FLASH_PERIOD = 10            # frames per on/off flash
# pos_hint right / top, size_hint w / h. Banner art is 8:1; centred on screen.
BOSS_WARNING_SCREEN_RECT = (0.75, 0.60, 0.5, 0.09)

# --- Boss AI ---
# Health-ratio boundaries: phase 0 (>0.66) -> 1 (>0.33) -> 2 (enraged).
BOSS_PHASE_THRESHOLDS = (0.66, 0.33)
# Movement speeds indexed by phase.
BOSS_STRAFE_SPEED = [0.003, 0.0045, 0.006]
BOSS_HUNT_SPEED = [0.004, 0.006, 0.008]
# Frames between shots inside a state, indexed by phase (lower = more aggressive).
# Đã nới rộng để boss bắn thưa hơn nhiều -> dễ né.
BOSS_ATTACK_COOLDOWN = [85, 70, 55]
# How long (frames) the boss commits to each behaviour before re-choosing.
# Ở lâu hơn trong STRAFE (đòn đơn giản), ngắn lại ở BARRAGE/SPIRAL (đòn nặng đạn).
BOSS_STATE_DURATION = {"STRAFE": 200, "HUNT": 150, "BARRAGE": 110, "SPIRAL": 120}
# Behaviour selection weights per phase - ưu tiên mạnh STRAFE, giảm BARRAGE/SPIRAL.
BOSS_STATE_WEIGHTS = [
    {"STRAFE": 7, "HUNT": 3, "BARRAGE": 1, "SPIRAL": 1},
    {"STRAFE": 6, "HUNT": 4, "BARRAGE": 2, "SPIRAL": 2},
    {"STRAFE": 5, "HUNT": 4, "BARRAGE": 3, "SPIRAL": 3},
]
BOSS_ATTACK_SPREAD = 0.0015               # Dx step between adjacent fan projectiles
BOSS_PROJECTILE_SPEED = 0.0052            # magnitude for directed (aimed/radial/spiral) shots (chậm hơn)
BOSS_AIMED_SPEED = 0.0065                 # aimed shots (chậm hơn cho dễ né)
BOSS_AIMED_BURST = [1, 1, 2]              # aimed shots per trigger, per phase (ít hơn)
BOSS_RADIAL_COUNT = [5, 6, 7]             # bullets per radial barrage, per phase (ít hơn)
BOSS_RADIAL_ARC = 1.5                     # total arc of a radial barrage (radians) - rộng hơn -> khe né to hơn
BOSS_BARRAGE_COOLDOWN = [50, 40, 32]      # frames between radial bursts (thưa hơn nhiều)
BOSS_SPIRAL_STEP = 0.55                   # radians added to the spiral each shot (xoè rộng hơn)
BOSS_SPIRAL_COOLDOWN = 12                 # frames between spiral bullets (một nửa mật độ cũ)

# --- Networking (client-side smoothing of remote entities) ---
# Mô hình mạng tách rời (không lockstep): vòng game chạy full tốc độ nội bộ, còn
# tàu/boss của bên kia được NỘI SUY tiến dần tới vị trí đồng bộ mới nhất cho mượt.
NET_LERP_FACTOR = 0.4                      # phần khoảng cách tiến tới mục tiêu mỗi khung
NET_SNAP_THRESHOLD_SQ = 0.0225            # (0.15)^2: lệch quá xa thì nhảy thẳng (respawn / sync đầu)

# Boss Projectile
BOSS_PROJECTILE_SPEED_Y = -0.0052         # default downward speed (fan volleys) - chậm hơn cho dễ né
BOSS_PROJECTILE_SCREEN_WIDTH = 0.025
BOSS_PROJECTILE_SCREEN_HEIGHT = 0.04
BOSS_PROJECTILE_INACTIVE_BOTTOM = -0.05
BOSS_PROJECTILE_INACTIVE_TOP = 1.05
BOSS_PROJECTILE_INACTIVE_LEFT = -0.05
BOSS_PROJECTILE_INACTIVE_RIGHT = 1.05
