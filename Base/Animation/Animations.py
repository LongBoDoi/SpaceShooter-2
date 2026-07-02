from .Animation import Animation
from Base.Textures import Textures
from Base.Constants import AnimationConstants

##
# List Animation
###
SpaceshipAnimation = Animation(Textures.Spaceship,
                               AnimationConstants.SPACESHIP_ANIMATION_RECT,
                               AnimationConstants.SPACESHIP_ANIMATION_ROW_COUNT,
                               AnimationConstants.SPACESHIP_ANIMATION_COL_COUNT,
                               AnimationConstants.SPACESHIP_ANIMATION_SPEED)
SpaceshipDeadAnimation = Animation(Textures.Spaceship,
                               AnimationConstants.SPACESHIP_ANIMATION_DEAD_RECT,
                               AnimationConstants.SPACESHIP_ANIMATION_ROW_COUNT,
                               AnimationConstants.SPACESHIP_ANIMATION_COL_COUNT,
                               AnimationConstants.SPACESHIP_ANIMATION_SPEED)
SpaceshipRespawnAnimation = Animation(Textures.Spaceship, 
                                      AnimationConstants.SPACESHIP_ANIMATION_RESPAWN_RECT,
                                      AnimationConstants.SPACESHIP_RESPAWN_ANIMATION_ROW_COUNT,
                                      AnimationConstants.SPACESHIP_RESPAWN_ANIMATION_COL_COUNT,
                                      AnimationConstants.SPACESHIP_RESPAWN_ANIMATION_SPEED)
BulletAnimation = [Animation(Textures.Bullet,
                            AnimationConstants.BULLET_ANIMATION_RECT[0],
                            AnimationConstants.BULLET_ANIMATION_ROW_COUNT,
                            AnimationConstants.BULLET_ANIMATION_COL_COUNT,
                            AnimationConstants.BULLET_ANIMATION_SPEED),
                   Animation(Textures.Bullet,
                            AnimationConstants.BULLET_ANIMATION_RECT[1],
                            AnimationConstants.BULLET_ANIMATION_ROW_COUNT,
                            AnimationConstants.BULLET_ANIMATION_COL_COUNT,
                            AnimationConstants.BULLET_ANIMATION_SPEED),
                   Animation(Textures.Bullet,
                            AnimationConstants.BULLET_ANIMATION_RECT[2],
                            AnimationConstants.BULLET_ANIMATION_ROW_COUNT,
                            AnimationConstants.BULLET_ANIMATION_COL_COUNT,
                            AnimationConstants.BULLET_ANIMATION_SPEED)]
MeteorAnimation = Animation(Textures.Meteor,
                            AnimationConstants.METEOR_ANIMATION_RECT,
                            AnimationConstants.METEOR_ANIMATION_ROW_COUNT,
                            AnimationConstants.METEOR_ANIMATION_COL_COUNT,
                            AnimationConstants.METEOR_ANIMATION_SPEED)
# Power-up icons, indexed by type (0 power, 1 speed, 2 repair).
PowerUpAnimations = [Animation(Textures.PowerUps,
                               rect,
                               AnimationConstants.POWERUP_ANIMATION_ROW_COUNT,
                               AnimationConstants.POWERUP_ANIMATION_COL_COUNT,
                               AnimationConstants.POWERUP_ANIMATION_SPEED)
                     for rect in AnimationConstants.POWERUP_ANIMATION_RECTS]
ExplosionAnimation = Animation(Textures.Explosion,
                            AnimationConstants.EXPLOSION_ANIMATION_RECT,
                            AnimationConstants.EXPLOSION_ANIMATION_ROW_COUNT,
                            AnimationConstants.EXPLOSION_ANIMATION_COL_COUNT,
                            AnimationConstants.EXPLOSION_ANIMATION_SPEED)
SpaceshipExplosionAnimation = Animation(Textures.SpaceshipExplosion,
                            AnimationConstants.SPACESHIP_EXPLOSION_ANIMATION_RECT,
                            AnimationConstants.SPACESHIP_EXPLOSION_ANIMATION_ROW_COUNT,
                            AnimationConstants.SPACESHIP_EXPLOSION_ANIMATION_COL_COUNT,
                            AnimationConstants.SPACESHIP_EXPLOSION_ANIMATION_SPEED)

# Boss ship animations (single static frame each), indexed by variant.
BossAnimations = [Animation(texture,
                            AnimationConstants.BOSS_ANIMATION_RECT,
                            AnimationConstants.BOSS_ANIMATION_ROW_COUNT,
                            AnimationConstants.BOSS_ANIMATION_COL_COUNT,
                            AnimationConstants.BOSS_ANIMATION_SPEED)
                  for texture in (Textures.BossMarauder,
                                  Textures.BossSentinel,
                                  Textures.BossDreadnought)]

# Boss projectile animations, indexed by projectile type (0 plasma, 1 void).
BossProjectileAnimations = [Animation(Textures.BossProjectiles,
                                AnimationConstants.BOSS_PROJECTILE_PLASMA_RECT,
                                AnimationConstants.BOSS_PROJECTILE_ROW_COUNT,
                                AnimationConstants.BOSS_PROJECTILE_COL_COUNT,
                                AnimationConstants.BOSS_PROJECTILE_SPEED),
                            Animation(Textures.BossProjectiles,
                                AnimationConstants.BOSS_PROJECTILE_VOID_RECT,
                                AnimationConstants.BOSS_PROJECTILE_ROW_COUNT,
                                AnimationConstants.BOSS_PROJECTILE_COL_COUNT,
                                AnimationConstants.BOSS_PROJECTILE_SPEED)]