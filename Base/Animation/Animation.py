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
        self.Texture.setRect(self.ListFrames[0])

        self.CurrentSpeed = 0.0
        self.Speed = speed
        
        self.Row = row
        self.Col = col
        
    ##
    # Animation đã kết thúc chưa
    ###
    def isEnd(self):
        return self.CurrentSpeed + self.Speed >= len(self.ListFrames)

    def update(self):
        if self.Speed > 0:
            newSpeed = self.CurrentSpeed + self.Speed
            if newSpeed >= self.ListFrames.__len__():
                newSpeed -= self.ListFrames.__len__()

            if int(newSpeed) != int(self.CurrentSpeed):
                self.Texture.setRect(self.ListFrames[int(newSpeed)])
            self.CurrentSpeed = newSpeed

    def clone(self):
        return Animation(self.Texture.clone(), self.Rect, self.Row, self.Col,
                         self.Speed)