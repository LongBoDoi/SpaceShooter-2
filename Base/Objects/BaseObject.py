from Utility import GameUtility
from kivy.graphics import *

##
# Đối tượng base trong game
# Properties:
#   - X, Y, Width, Height: Tọa độ, kích thước đối tượng
#   - Dx, Dy: Tốc độ di chuyển của đối tượng
#   - Animation: Hiệu ứng hoạt cảnh của đối tượng
#   - Gameplay: Gameplay lưu trữ đối tượng
#   - Inactive: Đối tượng còn hoạt động không
###
class BaseObject:
    def __init__(self, rect, animation, gameplay):
        x, y, w, h = rect
        self.X = x
        self.Y = y
        self.Width = w
        self.Height = h
        self.Dx = 0
        self.Dy = 0
        self.Animation = animation.clone()
        self.Gameplay = gameplay
        self.Inactive = False
        self.Name = ""
        GameUtility.addNewObject(gameplay, self)

    # Hàm set vị trí cho đối tượng
    def setPos(self, x, y):
        self.X = x
        self.Y = y
        self.Animation.Texture.Image.pos_hint = {"right": self.X, "top": self.Y}

    # Hàm set animation mới cho đối tượng
    def setAnimation(self, newAnimation):
        self.Gameplay.remove_widget(self.Animation.Texture.Image)
        self.Animation = newAnimation.clone()
        GameUtility.drawTexture(self.Gameplay, self.Animation.Texture, (self.X, self.Y, self.Width, self.Height))

    # Hàm thực hiện cập nhật những thay đổi của đối tượng
    def update(self):
        if self.Inactive:
            return

        if self.Dx != 0 or self.Dy != 0:
            self.setPos(self.X + self.Dx, self.Y + self.Dy)

        self.Animation.update()

        for otherObject in self.Gameplay.ListObjects:
            if (self == otherObject):
                continue
            self.handleCollision(otherObject)

        # with self.Animation.Texture.Image.canvas:
        #     Color(1., 0, 0)
        #     self.Animation.Texture.Image.rect = Line(rectangle=(1920 * (self.X - self.Width), 1080 * (self.Y - self.Height), 1920 * self.Width, 1080 * self.Height), width=1)

    ##
    # Hàm thực hiện kiểm tra xem vật thể hiện tại có va chạm với vật thể khác không
    # @params: otherObject (BaseObject): Vật thể khác
    ###
    def collidesWith(self, otherObject):
        return self.Animation.Texture.Image.collide_widget(otherObject.Animation.Texture.Image)

    def handleCollision(self, otherObject):
        pass