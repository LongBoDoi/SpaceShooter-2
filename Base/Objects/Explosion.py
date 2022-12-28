from Base.Objects import BaseObject
from Base.Constants import ObjectConstants
from Base.Animation import Animations

class Explosion(BaseObject):
    def __init__(self, obj):
        if obj.Name == "Meteor":
            super(Explosion, self).__init__((obj.X + ObjectConstants.EXPLOSION_ROCK_OFFSET_X,
                                            obj.Y + ObjectConstants.EXPLOSION_ROCK_OFFSET_Y,
                                            ObjectConstants.EXPLOSION_ROCK_SCREEN_WIDTH,
                                            ObjectConstants.EXPLOSION_ROCK_SCREEN_HEIGHT),
                                            Animations.ExplosionAnimation,
                                            obj.Gameplay)
        if obj.Name == "Spaceship":
            super(Explosion, self).__init__((obj.X + ObjectConstants.EXPLOSION_SPACESHIP_OFFSET_X,
                                            obj.Y + ObjectConstants.EXPLOSION_SPACESHIP_OFFSET_Y,
                                            ObjectConstants.EXPLOSION_SPACESHIP_SCREEN_WIDTH,
                                            ObjectConstants.EXPLOSION_SPACESHIP_SCREEN_HEIGHT),
                                            Animations.SpaceshipExplosionAnimation,
                                            obj.Gameplay)

    def update(self):
        super().update()

        if self.Animation.isEnd():
            self.Inactive = True