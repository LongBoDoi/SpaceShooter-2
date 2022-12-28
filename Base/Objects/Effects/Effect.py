class Effect:
    def __init__(self, spaceship, interval):
        self.Spaceship = spaceship
        self.Interval = interval

        self.Cooldown = 0
        self.Spaceship.ListEffects.append(self)
        self.applyEffects()

    def applyEffects(self):
        pass

    def removeEffects(self):
        pass

    def update(self):
        self.Cooldown += self.Interval
        if self.Cooldown > 1:
            self.removeEffects()
            self.Spaceship.ListEffects.remove(self)
