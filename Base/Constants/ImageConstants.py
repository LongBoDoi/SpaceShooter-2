# Constant LifeBar, Overheat
LIFEBAR_CLIP_RECT = [(0, 192, 215, 64),
                    (0, 128, 215, 64),
                    (0, 64, 215, 64),
                    (0, 0, 215, 64)]
LIFEBAR_SCREEN_RECT = [(0.135, 0.99, 0.13, 0.04),
                        (0.135, 0.99, 0.13, 0.04),
                        (0.995, 0.99, 0.13, 0.04)]
OVERHEAT_FRAME_SCREEN_RECT = [(0.135, 0.94, 0.13, 0.03),
                            (0.135, 0.94, 0.13, 0.03),
                            (0.995, 0.94, 0.13, 0.03)]
OVERHEAT_BAR_SCREEN_WIDTH = 0.13
OVERHEAT_BAR_SCREEN_HEIGHT = 0.03
def OVERHEAT_BAR_CLIP_RECT(overheatLevel):
    return (0, 0, int(1200 * overheatLevel), 70)
BAR_POS_X = [0.135, 0.135, 0.995]
def OVERHEAT_BAR_POS_X(overheatLevel, playerIndex):
    return BAR_POS_X[playerIndex] - OVERHEAT_BAR_SCREEN_WIDTH * (1 - overheatLevel)
OVERHEAT_BAR_POS_Y = 0.94