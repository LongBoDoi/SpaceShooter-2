from Base.Objects import BaseObject
from Base.Objects.Meteor import Meteor
from Base.Objects.Explosion import Explosion
from Base.Constants import ObjectConstants
from Base.Animation import Animations

class Bullet(BaseObject):
    # Đạn người chơi chỉ va chạm với thiên thạch và boss.
    CollisionTargets = ("Meteor", "Boss")
    # Viên đạn là tia mảnh nằm giữa khung -> hộp va chạm nhỏ.
    HitboxScale = 0.5

    ##
    # Tạo đạn tại toạ độ cho trước. Nhận toạ độ tường minh (thay vì đối tượng
    # player) để phía nhận dữ liệu multiplayer tái tạo lại đúng viên đạn của
    # người chơi bên kia. Xem Spaceship.doShooting / Gameplay.createBullets.
    ###
    def __init__(self, gameplay, x, y, bulletCount, color=(1, 1, 1, 1)):
        super(Bullet, self).__init__((x,
                                      y,
                                      ObjectConstants.BULLET_SCREEN_WIDTH,
                                      ObjectConstants.BULLET_SCREEN_HEIGHT),
                                     Animations.BulletAnimation[bulletCount - 1],
                                     gameplay)
        self.Dy = ObjectConstants.BULLET_SPEED_Y
        # Sát thương lên boss tỉ lệ với số nòng đạn hiện tại.
        self.Damage = bulletCount * 2
        self.Name = "Bullet"
        # Tô đạn theo màu tàu đã bắn (sprite gốc trung tính nên tô ra màu sạch).
        self.Animation.Texture.Image.color = color

    ##
    # OVERRIDES
    # Xử lý va chạm với các vật thể khác
    ###
    def handleCollision(self, otherObject):
        if isinstance(otherObject, Meteor):
            if self.collidesWith(otherObject):
                self.Inactive = True
                otherObject.Inactive = True
                Explosion(otherObject)
                # Đếm số thiên thạch bị bắn hạ để kích hoạt boss.
                self.Gameplay.MeteorsDestroyed += 1
                # Cơ hội rơi vật phẩm tại vị trí thiên thạch (Host/chơi đơn quyết định).
                self.Gameplay.trySpawnPowerUp(otherObject.X, otherObject.Y)
        elif otherObject.Name == "Boss" and not otherObject.Intro:
            if self.collidesWith(otherObject):
                self.Inactive = True
                Explosion(self)
                # Máu boss là dữ liệu do Host quản lý; Client chỉ tạo hiệu ứng.
                if not self.Gameplay.IsClient:
                    otherObject.takeDamage(self.Damage)

    def update(self):
        super().update()

        if self.Y > ObjectConstants.BULLET_INACTIVE_POS_Y:
            self.Inactive = True

    #    for e in game_play.entities:
    #        if e == self:
    #            continue
    #        if isinstance(e, Rock):
    #            if self.collides_with(e, offset_rock[self.count], 0):
    #                e.active = False
    #                self.active = False
    #                bonus_chance = random.randint(0, 10)
    #                if bonus_chance < 3:
    #                    Bonus(e, bonus_chance, game_play)
    #                Explosion(e, game_play)
    #        if isinstance(e, Boss):
    #            if not e.intro:
    #                if self.collides_with(e, offset_boss[self.count], 0.15):
    #                    self.active = False
    #                    Explosion(self, game_play)
    #                    if not e.special_attack:
    #                        e.current_health -= self.count * 2
    #                        e.health_bar_img.set_rect(0, 0, 1200 * e.current_health / e.max_health, 70)
    #                        e.health_bar_img.set_size(e.width * e.current_health / e.max_health, 20 / 800)
    #                        e.health_text.text = str(e.current_health)
    #                        if e.current_health <= 0:
    #                            e.active = False
    #                            e.health_frame_img.free(game_play)
    #                            e.health_bar_img.free(game_play)
    #                            game_play.remove_widget(e.health_text)
    #                            game_play.boss_appearing = False
    #                            Explosion(e, game_play)