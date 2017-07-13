import bpy
import os
import re


try:
    fujiwara_toolbox = __import__("fujiwara_toolbox")
except:
    fujiwara_toolbox = __import__("fujiwara_toolbox-master")
fjw = fujiwara_toolbox.fjw


bl_info = {
    "name": "FJW cameratools",
    "author": "GhostBrain3dex",
    "version": (1.0),
    "blender": (2, 77, 0),
    'location': 'Properties > Camera > Lens > CameraTools',
    "description": "CameraTools",
    "category": "Object",
}








############################################################################################################################
############################################################################################################################
#カメラプロパティにボタン追加
############################################################################################################################
############################################################################################################################
class setshifttobordercenter(bpy.types.Operator):
    """ボーダーの中心にシフトを設定"""
    bl_idname = "object.setshifttobordercenter"
    bl_label = "ボーダーにシフト"

    def execute(self, context):
        res_x = bpy.context.scene.render.resolution_x
        res_y = bpy.context.scene.render.resolution_y
        
        bdelta_x = bpy.context.scene.render.border_max_x - bpy.context.scene.render.border_min_x
        bdelta_y = bpy.context.scene.render.border_max_y - bpy.context.scene.render.border_min_y
        
        bcenter_x = bpy.context.scene.render.border_min_x + bdelta_x / 2
        bcenter_y = bpy.context.scene.render.border_min_y + bdelta_y / 2
        
        #画面中心を基準にした座標にする
        bcenter_x = bcenter_x - 0.5
        bcenter_y = bcenter_y - 0.5
        
        
        #縦横どっちか長い方をfixする
        if res_y > res_x:
            #横をfix
            fix = res_x / res_y
            bcenter_x = bcenter_x * fix
        else:
            #縦をfix
            fix = res_y / res_x
            bcenter_y = bcenter_y * fix
        
        
        #シフト
        bpy.context.scene.camera.data.shift_x = bcenter_x * -1
        bpy.context.scene.camera.data.shift_y = bcenter_y * -1
        
        
        
        
        return {"FINISHED"}


class extendborder(bpy.types.Operator):
    """ボーダーを拡大"""
    bl_idname = "object.extendborder"
    bl_label = "ボーダーを拡大"

    def execute(self, context):
        ext = 0.1
        bpy.context.scene.render.border_max_x += ext
        bpy.context.scene.render.border_max_y += ext
        bpy.context.scene.render.border_min_x -= ext
        bpy.context.scene.render.border_min_y -= ext
        return {"FINISHED"}



class fromfile(bpy.types.Operator):
    """../komaフォルダから情報を取得して設定"""
    bl_idname = "object.border_fromfile"
    bl_label = "../komaフォルダから設定"

    def execute(self, context):
        filename = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
        koma = re.match("\\d+",filename).group(0)
        komadir = os.path.dirname(bpy.data.filepath) + os.sep + "koma" + os.sep
        komatextpath = komadir + koma + ".txt"
        
        if os.path.exists(komatextpath):
            f = open(komatextpath)
            data = f.read()
            self.report({"INFO"},data)
            f.close()
            
            res_x = bpy.context.scene.render.resolution_x
            res_y = bpy.context.scene.render.resolution_y
            
            x0 = int(data.split(",")[0]) / res_x
            y1 = 1 - int(data.split(",")[1]) / res_y
            x1 = int(data.split(",")[2]) / res_x
            y0 = 1 - int(data.split(",")[3]) / res_y
            

            bpy.context.scene.render.border_min_x = x0
            bpy.context.scene.render.border_min_y = y0
            bpy.context.scene.render.border_max_x = x1
            bpy.context.scene.render.border_max_y = y1
            
            bpy.context.scene.render.use_border = True
            bpy.ops.object.setshifttobordercenter()
            bpy.ops.object.extendborder()
        return {"FINISHED"}


uiitemList = []
class uiitem():
    type = "button"
    idname = ""
    label = ""
    icon = ""
    mode = ""
    #ボタンの表示方向
    direction = ""
    
    #宣言時自動登録
    def __init__(self,label=""):
        global uiitemList
        uiitemList.append(self)
        
        if label != "":
            self.type = "label"
            self.label = label
    
    #簡易セットアップ
    def button(self,idname,label,icon,mode):
        self.idname = idname
        self.label = label
        self.icon = icon
        self.mode = mode
        return

    #フィックス用
    def vertical(self):
        self.type = "fix"
        self.direction = "vertical"
        return
    
    def horizontal(self):
        self.type = "fix"
        self.direction = "horizontal"
        return


def cameratools_ui(self, context):
    layout = self.layout
    col = layout.column(align=True)
    row = col.row(align=True)
    row.operator("object.setshifttobordercenter")
    row.operator("object.extendborder")
    layout.operator("object.border_fromfile")

    l = self.layout
    r = l.row()
    #b = r.box()
    b = r







    #ボタン同士をくっつける
    #縦並び
    cols = b.column(align=True)
    active = cols

    for item in uiitemList:
        #スキップ処理
        if item.mode == "none":
            continue
            
        if item.mode == "edit":
            #編集モード以外飛ばす
            if bpy.context.edit_object != None:
                continue
            
        #縦横
        if item.type == "fix":
            if item.direction == "vertical":
                active = cols.column(align=True)
            if item.direction == "horizontal":
                active = active.row(align=True)
            continue
            
        #描画
        if item.type == "label":
            active.label(text=item.label)
        if item.type == "button":
            if item.icon != "":
                active.operator(item.idname, icon=item.icon)
            else:
                active.operator(item.idname)










#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#ロック
########################################
class MYOBJECT_230314(bpy.types.Operator):#ロック
    """ロック"""
    bl_idname = "object.myobject_230314"
    bl_label = "ロック"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="LOCKED",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        cam = bpy.context.scene.camera
        cam.lock_rotation[0] = True
        cam.lock_rotation[2] = True
        cam.lock_rotation[1] = True
        
        if cam.parent != None:
            cam = cam.parent
            cam.lock_rotation[0] = True
            cam.lock_rotation[2] = True
            cam.lock_rotation[1] = True

        
        return {'FINISHED'}
########################################

########################################
#アンロック
########################################
class MYOBJECT_716321(bpy.types.Operator):#アンロック
    """アンロック"""
    bl_idname = "object.myobject_716321"
    bl_label = "アンロック"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="UNLOCKED",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        cam = bpy.context.scene.camera
        cam.lock_rotation[0] = False
        cam.lock_rotation[2] = False
        cam.lock_rotation[1] = False
        
        if cam.parent != None:
            cam = cam.parent
            cam.lock_rotation[0] = False
            cam.lock_rotation[2] = False
            cam.lock_rotation[1] = False
        
        return {'FINISHED'}
########################################



#---------------------------------------------
uiitem().vertical()
#---------------------------------------------



#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#上下解除
########################################
class MYOBJECT_277099(bpy.types.Operator):#上下解除
    """上下解除"""
    bl_idname = "object.myobject_277099"
    bl_label = "上下解除"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="UNLOCKED",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        cam = bpy.context.scene.camera
        cam.lock_rotation[0] = False

        if cam.parent != None:
            cam = cam.parent
            cam.lock_rotation[0] = False

        
        return {'FINISHED'}
########################################

########################################
#左右解除
########################################
class MYOBJECT_419001(bpy.types.Operator):#左右解除
    """左右解除"""
    bl_idname = "object.myobject_419001"
    bl_label = "左右解除"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="UNLOCKED",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        cam = bpy.context.scene.camera
        cam.lock_rotation[2] = False
        
        if cam.parent != None:
            cam = cam.parent
            cam.lock_rotation[2] = False

        return {'FINISHED'}
########################################

########################################
#回転解除
########################################
class MYOBJECT_671755(bpy.types.Operator):#回転解除
    """回転解除"""
    bl_idname = "object.myobject_671755"
    bl_label = "回転解除"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="UNLOCKED",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        cam = bpy.context.scene.camera
        cam.lock_rotation[1] = False

        if cam.parent != None:
            cam = cam.parent
            cam.lock_rotation[1] = False

        
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


#########################################
##TTパージ
#########################################
#class MYOBJECT_134809(bpy.types.Operator):#TTパージ
#    """TTパージ"""
#    bl_idname = "object.myobject_134809"
#    bl_label = "TTパージ"
#    bl_options = {'REGISTER', 'UNDO'}
#
#
#    #メインパネルのボタンリストに登録
#    ButtonList.append(bl_idname)
#    #テキストラベルの追加
#    LabelList.append("");
#    #アイコンの追加
#    IconList.append("")
#    #モードの追加
#    ModeList.append("")
#
#    ###################################
#    #処理部分
#    ###################################
#    def execute(self, context):
##        bpy.context.scene.objects.active = bpy.data.objects["トラックターゲット"]
#        for obj in bpy.context.selected_objects:
#            obj.select = False
#
#        bpy.data.objects["トラックターゲット"].select = True
#        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
#
#        return {'FINISHED'}
#########################################













########################################
#カメラ初期化
########################################
class MYOBJECT_990292(bpy.types.Operator):#カメラ初期化
    """カメラ初期化"""
    bl_idname = "object.myobject_990292"
    bl_label = "カメラ初期化"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="CAMERA_DATA",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        cam = bpy.context.scene.camera
        cam.rotation_euler[0] = 1.5708
        cam.rotation_euler[1] = 0
        cam.rotation_euler[2] = 0
        cam.data.shift_x = 0
        cam.data.shift_y = 0
        
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------
########################################
#-5mm
########################################
class MYOBJECT_88734(bpy.types.Operator):#-5mm
    """-5mm"""
    bl_idname = "object.myobject_88734"
    bl_label = "-5mm"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        cam = bpy.context.scene.camera
        cam.data.lens -= 5
        
        return {'FINISHED'}
########################################


########################################
#+5mm
########################################
class MYOBJECT_938471(bpy.types.Operator):#+5mm
    """+5mm"""
    bl_idname = "object.myobject_938471"
    bl_label = "+5mm"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        cam = bpy.context.scene.camera
        cam.data.lens += 5
        return {'FINISHED'}
########################################









#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------


########################################
#15mm
########################################
class MYOBJECT_594660(bpy.types.Operator):#15mm
    """15mm"""
    bl_idname = "object.myobject_594660"
    bl_label = "15mm"
    bl_options = {'REGISTER', 'UNDO'}


    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    
    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        cam = bpy.context.scene.camera
        cam.data.lens = 15
        
        return {'FINISHED'}
########################################






########################################
#32mm
########################################
class MYOBJECT_446521(bpy.types.Operator):#32mm
    """32mm"""
    bl_idname = "object.myobject_446521"
    bl_label = "32mm"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        cam = bpy.context.scene.camera
        cam.data.lens = 32
        
        
        return {'FINISHED'}
########################################


########################################
#50mm
########################################
class MYOBJECT_170965(bpy.types.Operator):#50mm
    """50mm"""
    bl_idname = "object.myobject_170965"
    bl_label = "50mm"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        cam = bpy.context.scene.camera
        cam.data.lens = 50
        
        
        return {'FINISHED'}
########################################


########################################
#100mm
########################################
class MYOBJECT_108970(bpy.types.Operator):#100mm
    """100mm"""
    bl_idname = "object.myobject_108970"
    bl_label = "100mm"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        cam = bpy.context.scene.camera
        cam.data.lens = 100
        
        
        return {'FINISHED'}
########################################


#---------------------------------------------
uiitem().vertical()
#---------------------------------------------


#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#1km
########################################
class MYOBJECT_993154(bpy.types.Operator):#1km
    """ビューのクリップを1kmに"""
    bl_idname = "object.myobject_993154"
    bl_label = "1km"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.context.scene.camera.data.clip_end = 1000
        
        return {'FINISHED'}
########################################

########################################
#10km
########################################
class MYOBJECT_114029(bpy.types.Operator):#10km
    """ビューのクリップを10kmに"""
    bl_idname = "object.myobject_114029"
    bl_label = "10km"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")

    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        bpy.context.scene.camera.data.clip_end = 10000
        
        return {'FINISHED'}
########################################

#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

############################################################################################################################
uiitem("高さ")
############################################################################################################################


#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------

########################################
#10cm
########################################
class MYOBJECT_149588(bpy.types.Operator):#10cm
    """10cm"""
    bl_idname = "object.myobject_149588"
    bl_label = "10cm"
    bl_options = {'REGISTER', 'UNDO'}


    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    
    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        cam = bpy.context.scene.camera
        cam.location[2] = 0.1
        
        return {'FINISHED'}
########################################

########################################
#100cm
########################################
class MYOBJECT_326193(bpy.types.Operator):#100cm
    """100cm"""
    bl_idname = "object.myobject_326193"
    bl_label = "100cm"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        cam = bpy.context.scene.camera
        cam.location[2] = 1
        
        return {'FINISHED'}
########################################


########################################
#160cm
########################################
class MYOBJECT_448222(bpy.types.Operator):#160cm
    """160cm"""
    bl_idname = "object.myobject_448222"
    bl_label = "160cm"
    bl_options = {'REGISTER', 'UNDO'}


    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    
    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        cam = bpy.context.scene.camera
        cam.location[2] = 1.6
        
        return {'FINISHED'}
########################################

########################################
#200cm
########################################
class MYOBJECT_116309(bpy.types.Operator):#200cm
    """200cm"""
    bl_idname = "object.myobject_116309"
    bl_label = "200cm"
    bl_options = {'REGISTER', 'UNDO'}


    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")
    
    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        cam = bpy.context.scene.camera
        cam.location[2] = 2
        
        return {'FINISHED'}
########################################















#########################################
##エンプティ設置
#########################################
#class MYOBJECT_46196(bpy.types.Operator):#エンプティ設置
#    """エンプティ設置"""
#    bl_idname = "object.myobject_46196"
#    bl_label = "エンプティ設置"
#    bl_options = {'REGISTER', 'UNDO'}

#    uiitem = uiitem()
#    uiitem.button(bl_idname,bl_label,icon="OUTLINER_OB_EMPTY",mode="")

#    ###################################
#    #処理部分
#    ###################################
#    def execute(self, context):
#        loc = bpy.context.space_data.cursor_location
#        bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False,
#        location=loc, layers=(True, False, False, False, False, False, False,
#        False, False, False, False, False, False, False, False, False, False,
#        False, False, False))
        
#        return {'FINISHED'}
#########################################


"""
def sub_registration():
    pass

def sub_unregistration():
    pass
"""
def sub_registration():
    bpy.types.DATA_PT_lens.append(cameratools_ui)
    pass

def sub_unregistration():
    bpy.types.DATA_PT_lens.remove(cameratools_ui)
    pass


def register():
    bpy.utils.register_module(__name__)
    sub_registration()
    


def unregister():
    bpy.utils.unregister_module(__name__)
    sub_unregistration()


if __name__ == "__main__":
    register()

