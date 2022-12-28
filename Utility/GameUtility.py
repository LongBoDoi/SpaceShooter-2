import random
from kivy.clock import Clock

##
# Class thực hiện các tiện ích trong game
###
class GameUtility:
    ##
    # Hàm thực hiện vẽ một texture tại một tọa độ, kích thước cụ thể
    ###
    def drawTexture(gameplay, texture, rect):
        x, y, width, height = rect
        if x != None and y != None:
            texture.Image.pos_hint = {"right": x, "top": y}
        if width != None and height != None:
            texture.Image.size_hint = width, height
        gameplay.add_widget(texture.Image)

    ##
    # Hàm thực hiện thêm một vật thể mới vào game
    # @params: newObject (BaseObject): Vật thể cần thêm
    ###
    def addNewObject(gameplay, newObject):
        newObject.ObjectIndex = gameplay.ListObjects.__len__()
        gameplay.ListObjects.append(newObject)
        GameUtility.drawTexture(gameplay, newObject.Animation.Texture, (newObject.X, newObject.Y, newObject.Width, newObject.Height))

    ##
    # Hàm thực hiện tạo ngẫu nhiên một vật thể trong game
    # @params: gameplay (Gameplay): Gameplay
    # @params: object (BaseObject): Loại vật thể
    # @params: pool: Rải tần ngẫu nhiên để tạo vật thể
    # @params: chance: Tỉ lệ tạo vật thể
    ###
    def randomCreateObject(gameplay, objectType, pool, chance):
        success = random.randint(0, pool)
        if success < chance:
            newObject = objectType(gameplay)
            gameplay.ListNewObjects.append({
                "Name": newObject.Name,
                "Data": (newObject.X, newObject.Dx, newObject.Dy)
            })
    
    ##
    # Hàm thực hiện xóa một vật thể khỏi game
    # @params: object (BaseObject): Vật thể cần xóa
    ###
    def removeObject(gameplay, oldObject):
        gameplay.remove_widget(oldObject.Animation.Texture.Image)
        gameplay.ListObjects.remove(oldObject)

    def openMenu(menu):
        Clock.schedule_interval(menu.update, 1.0 / 60.0)
        menu.App.root = menu
        menu.App._run_prepare()



