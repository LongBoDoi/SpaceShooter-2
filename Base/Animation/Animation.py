##
# Class dùng để tạo hiệu ứng chuyển động cho vật thể
# Properties:
#   Texture (Texture): Texture dùng để gen animation
#   ListFrames (List): List khung hình của animation
#   CurrentSpeed: Animation đang dừng ở khung hình nào
#   Speed: Tốc độ animation
###
class Animation:
    def __init__(self, texture, rect, row, col, speed):
        self.Texture = texture.clone()

        x, y, w, h = rect
        self.Rect = rect
        
        self.ListFrames = []
        for i in range(row):
            for j in range(col):
                self.ListFrames.append((x + j * w, y + (row - i - 1) * h, w, h))

        # Tính sẵn vùng texture cho từng khung hình một lần duy nhất. Trước đây
        # mỗi khung hình khi chạy đều gọi get_region (tạo mới một texture) — với
        # animation lặp vô hạn (thiên thạch, đạn...) đó là hàng nghìn lần cấp
        # phát mỗi giây. Giờ chỉ đổi tham chiếu texture đã dựng sẵn.
        sourceTexture = self.Texture.SourceImage.texture
        self.Frames = [sourceTexture.get_region(fx, fy, fw, fh)
                       for (fx, fy, fw, fh) in self.ListFrames]
        self.FrameCount = len(self.Frames)
        self.Texture.Image.texture = self.Frames[0]

        self.CurrentSpeed = 0.0
        self.Speed = speed

        self.Row = row
        self.Col = col

    ##
    # Animation đã kết thúc chưa
    ###
    def isEnd(self):
        return self.CurrentSpeed + self.Speed >= self.FrameCount

    def update(self):
        if self.Speed > 0:
            newSpeed = self.CurrentSpeed + self.Speed
            if newSpeed >= self.FrameCount:
                newSpeed -= self.FrameCount

            if int(newSpeed) != int(self.CurrentSpeed):
                self.Texture.Image.texture = self.Frames[int(newSpeed)]
            self.CurrentSpeed = newSpeed

    def clone(self):
        return Animation(self.Texture.clone(), self.Rect, self.Row, self.Col,
                         self.Speed)