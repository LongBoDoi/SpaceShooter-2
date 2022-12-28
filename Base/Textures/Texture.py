from kivy.uix.image import Image

##
# Class lưu trữ hình ảnh dưới dạng texture
# Properties
#   Source: Đường dẫn lưu trữ ảnh
#   Image: Hình ảnh dùng để hiển thị của texture
#   SourceImage: Hình ảnh gốc của texture, dùng để vẽ lại hình ảnh hiển thị
#   X, Y, Width, Height: Tọa độ, kích thước của texture
###
class Texture:
    #region Constructor
    def __init__(self, source):
        self.Source = source
        self.SourceImage = Image(source=source, allow_stretch=True, keep_ratio=False)
        self.Image = Image(source=source, allow_stretch=True, keep_ratio=False)
    #endregion

    def setRect(self, rect):
        x, y, w, h = rect
        self.Image.texture = self.SourceImage.texture.get_region(x, y, w, h)

    def setPos(self, x, y):
        self.Image.pos_hint = {"right": x, "top": y}

    def setSize(self, w, h):
        self.Image.size_hint = w, h

    def clone(self):
        return Texture(self.Source)
#-------------------------------------------------------------------------------------------