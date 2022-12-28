from Base.Objects import BaseObject
from Base.Objects.Meteor import Meteor
from Base.Objects.Explosion import Explosion
from Base.Constants import ObjectConstants
from Base.Animation import Animations

class Bullet(BaseObject):
    def __init__(self, player):
        super(Bullet, self).__init__((player.X + ObjectConstants.BULLET_SCREEN_OFFSET_X[player.BulletCount - 1],
                                         player.Y + ObjectConstants.BULLET_SCREEN_OFFSET_Y,
                                         ObjectConstants.BULLET_SCREEN_WIDTH,
                                         ObjectConstants.BULLET_SCREEN_HEIGHT),
                                         Animations.BulletAnimation[player.BulletCount - 1],
                                         player.Gameplay)
        self.Dy = ObjectConstants.BULLET_SPEED_Y
        self.Name = "Bullet"

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