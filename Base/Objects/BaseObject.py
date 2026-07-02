from Utility import GameUtility
from Base.Constants import ObjectConstants
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
    # Tên loại vật thể - đặt ở cấp class để đã sẵn sàng ngay khi thêm vào game
    # (được dùng để phân nhóm va chạm trong GameUtility.addNewObject).
    Name = ""
    # Các nhóm vật thể mà đối tượng này cần kiểm tra va chạm. Rỗng = không kiểm
    # tra (đa số vật thể). Chỉ Bullet / Spaceship khai báo mục tiêu thực sự.
    CollisionTargets = ()
    # Tỉ lệ hộp va chạm so với khung ảnh (1.0 = trùng khung widget như cũ). Ảnh
    # sprite thường có viền trong suốt lớn (đặc biệt boss 256px), nên thu nhỏ hộp
    # va chạm về phần thân thực sự để va chạm khớp với hình nhìn thấy.
    HitboxScale = 1.0

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
        # Mục tiêu nội suy (chỉ dùng cho vật thể "remote" phía đối phương).
        self.TargetX = x
        self.TargetY = y
        GameUtility.addNewObject(gameplay, self)

    ##
    # Trượt mượt vị trí hiện tại về (TargetX, TargetY) - dùng cho tàu/boss remote
    # trong mô hình mạng tách rời. Lệch quá xa (respawn / sync đầu) thì nhảy thẳng.
    ###
    def lerpToTarget(self):
        dx = self.TargetX - self.X
        dy = self.TargetY - self.Y
        dist2 = dx * dx + dy * dy
        if dist2 > ObjectConstants.NET_SNAP_THRESHOLD_SQ:
            self.setPos(self.TargetX, self.TargetY)
        elif dist2 > 1e-9:
            self.setPos(self.X + dx * ObjectConstants.NET_LERP_FACTOR,
                        self.Y + dy * ObjectConstants.NET_LERP_FACTOR)

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

        # Chỉ vật thể có mục tiêu va chạm mới quét, và chỉ quét đúng nhóm mục
        # tiêu (thiên thạch / đạn boss / boss) thay vì toàn bộ vật thể trong
        # game. Tránh vòng lặp O(n^2) qua cả những cặp không bao giờ va chạm.
        if self.CollisionTargets:
            collisionGroups = self.Gameplay.CollisionGroups
            for groupName in self.CollisionTargets:
                for otherObject in collisionGroups[groupName]:
                    if otherObject is self:
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
        a = self.Animation.Texture.Image
        b = otherObject.Animation.Texture.Image
        # Thu nhỏ mỗi hộp về tâm theo HitboxScale rồi kiểm tra chồng lấn AABB.
        # Với HitboxScale = 1.0 cho cả hai, công thức trùng khít collide_widget.
        aInsetX = a.width * (1 - self.HitboxScale) / 2
        aInsetY = a.height * (1 - self.HitboxScale) / 2
        bInsetX = b.width * (1 - otherObject.HitboxScale) / 2
        bInsetY = b.height * (1 - otherObject.HitboxScale) / 2
        aLeft, aRight = a.x + aInsetX, a.right - aInsetX
        aBottom, aTop = a.y + aInsetY, a.top - aInsetY
        bLeft, bRight = b.x + bInsetX, b.right - bInsetX
        bBottom, bTop = b.y + bInsetY, b.top - bInsetY
        return not (aRight < bLeft or aLeft > bRight
                    or aTop < bBottom or aBottom > bTop)

    def handleCollision(self, otherObject):
        pass