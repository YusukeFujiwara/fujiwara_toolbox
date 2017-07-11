import bpy
import os
import re
import fujiwara_toolbox.conf


bl_info = {
    "name": "FJW GreasePencilTools",
    "author": "GhostBrain3dex",
    "version": (1.0),
    "blender": (2, 77, 0),
    'location': '',
    "description": "GreasePencilTools",
    "category": "Object",
}



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



class fjw_GreasePencilToolsPanel(bpy.types.Panel):
    bl_label = "グリペンユーティリティ"
    bl_space_type = "VIEW_3D"
    #bl_region_type = "UI"
    bl_region_type = "TOOLS"
    bl_category = "Grease Pencil"

    def draw(self, context):
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
uiitem().vertical()
#---------------------------------------------
############################################################################################################################
uiitem("準備")
############################################################################################################################
########################################
#セットアップ
########################################
class MYOBJECT_242623(bpy.types.Operator):#セットアップ
    """セットアップ"""
    bl_idname = "object.myobject_242623"
    bl_label = "セットアップ"
    bl_options = {'REGISTER', 'UNDO'}

    uiitem = uiitem()
    uiitem.button(bl_idname,bl_label,icon="",mode="")


    ###################################
    #処理部分
    ###################################
    def execute(self, context):
        #ツール設定
        #bpy.context.space_data.show_backface_culling = True
        bpy.context.scene.tool_settings.use_gpencil_additive_drawing = True
        bpy.context.scene.tool_settings.use_gpencil_continuous_drawing = True
        bpy.context.scene.tool_settings.gpencil_stroke_placement_view3d = 'SURFACE'
        bpy.context.space_data.show_only_render = True
        bpy.context.space_data.viewport_shade = 'MATERIAL'
        bpy.context.space_data.lock_camera = False
        bpy.context.space_data.region_3d.view_perspective = "CAMERA"
        bpy.context.scene.render.resolution_percentage = 100

        if bpy.context.scene.render.use_simplify:
            #bpy.context.scene.render.use_simplify = False
            if bpy.context.scene.render.simplify_subdivision < 2:
                bpy.context.scene.render.simplify_subdivision = 2

 


        #ブラシ準備
        brushname = "漫画ブラシ"
        gpencil_brushes = bpy.context.scene.tool_settings.gpencil_brushes

        if brushname not in gpencil_brushes:
            gpencil_brushes.new(brushname,True)
        cbrush = gpencil_brushes[brushname]
        cbrush.line_width = 3
        cbrush.use_strength_pressure = False
        cbrush.pen_smooth_factor = 0.1

        #グリースペンシルデータブロック
        grease_pencil = bpy.context.scene.grease_pencil
        if grease_pencil is None:
            bpy.ops.gpencil.data_add()
        grease_pencil = bpy.context.scene.grease_pencil

        #レイヤー
        gplayers = grease_pencil.layers
        layername = "ペン入れ"
        if layername not in gplayers:
            gplayers.new(layername)
            gplayer = gplayers[layername]
            gplayers.active = gplayer
            #レイヤー設定
            gplayer.show_x_ray = False
            gppenlayer = gplayer
            gplayers.active = gppenlayer


        layername = "背景"
        if layername not in gplayers:
            gplayers.new(layername)
            gplayer = gplayers[layername]
            #レイヤー設定
            gplayer.show_x_ray = False
            gplayer.tint_factor = 1
            gplayer.line_change = 10

        layername = "オノマトペ"
        if layername not in gplayers:
            gplayers.new(layername)
            gplayer = gplayers[layername]
            #レイヤー設定
            gplayer.show_x_ray = False

        layername = "下書き"
        if layername not in gplayers:
            gplayers.new(layername)
            gplayer = gplayers[layername]
            #レイヤー設定
            gplayer.show_x_ray = False
            gplayer.opacity = 0.2
            gplayer.tint_color = (0, 0.35567, 1)
            gplayer.tint_factor = 1
            gplayer.line_change = 10
            gpshitagakilayer = gplayer
            gplayers.active = gpshitagakilayer



        #パレット
        #パレット生成のためのドロー
        bpy.ops.gpencil.draw(mode='DRAW',wait_for_input=False)
        palette = grease_pencil.palettes.active
        pmain = palette
        pmain.name = "漫画パレット"
        
        colors = pmain.colors

        cname = "メイン"
        if cname not in colors:
            col = colors.new()
            col.name = cname
            col.color = (0,0,0)
            col.alpha = 1
            col.fill_color = (1,1,1)
            col.fill_alpha = 0
            colors.active = col

        cactive = colors.active

        cname = "ホワイト"
        if cname not in colors:
            col = colors.new()
            col.name = cname
            col.color = (1,1,1)
            col.alpha = 1
            col.fill_color = (1,1,1)
            col.fill_alpha = 0
        
        cname = "白消し"
        if cname not in colors:
            col = colors.new()
            col.name = cname
            col.color = (1,1,1)
            col.alpha = 1
            col.fill_color = (1,1,1)
            col.fill_alpha = 1

        cname = "ベタ塗り"
        if cname not in colors:
            col = colors.new()
            col.name = cname
            col.color = (0,0,0)
            col.alpha = 1
            col.fill_color = (0,0,0)
            col.fill_alpha = 1

        cname = "黒フチ白地"
        if cname not in colors:
            col = colors.new()
            col.name = cname
            col.color = (0,0,0)
            col.fill_alpha = 1

        cname = "白フチ黒地"
        if cname not in colors:
            col = colors.new()
            col.name = cname
            col.color = (1,1,1)
            col.fill_color = (0,0,0)
            col.fill_alpha = 1

        colors.active = cactive


        #bpy.ops.gpencil.palette_add()

        ##メイン　白消し　黒フチ白地
        #palettes = grease_pencil.palettes
        #pmainname = "メイン"
        #if pmainname not in palettes:
        #    palettes.new("メイン")
        #pmain = palettes[pmainname]


        #pwhitename = "白消し"
        #pborderedwhitename = "黒フチ白地"

        #パネル設定周り

        #areas = bpy.context.screen.areas
        #for area in areas:
        #    if area.type == "VIEW_3D":
        #        spaces = area.spaces
        #        for space in spaces:
        #            if space.type == "VIEW_3D":
        #→bpy.context.space_dataでアクセスできた…

        #        #regions = area.regions
        #        #for region in regions:
        #        #    #'TOOLS''TOOL_PROPS'
        #        #    if region

        #線幅を戻す
        bpy.ops.object.myobject_347064()
        #下書き表示
        gplayers = bpy.context.scene.grease_pencil.layers
        if "下書き" in gplayers:
            bpy.context.scene.grease_pencil.layers["下書き"].hide = False


        #SSAO設定
        bpy.context.space_data.fx_settings.use_ssao = True
        ssao = bpy.context.space_data.fx_settings.ssao
        ssao.color = (0.0, 0.0, 0.0)
        ssao.factor = 0.5
        ssao.distance_max = 0.1



        #グリペン描画開始
        bpy.ops.gpencil.draw("INVOKE_DEFAULT",mode='DRAW')

        return {'FINISHED'}
########################################
#---------------------------------------------
uiitem().vertical()
#---------------------------------------------

#---------------------------------------------
uiitem().horizontal()
#---------------------------------------------



#########################################
##細く
#########################################
#class MYOBJECT_148957(bpy.types.Operator):#細く
#    """細く"""
#    bl_idname = "object.myobject_148957"
#    bl_label = "細く"
#    bl_options = {'REGISTER', 'UNDO'}

#    uiitem = uiitem()
#    uiitem.button(bl_idname,bl_label,icon="",mode="")


#    ###################################
#    #処理部分
#    ###################################
#    def execute(self, context):
#        bpy.context.scene.grease_pencil.layers.active.line_change = -20
#        bpy.ops.gpencil.stroke_apply_thickness()
#        #GLレンダ
#        bpy.ops.object.myobject_979047()

#        return {'FINISHED'}
#########################################







#########################################
##太く
#########################################
#class MYOBJECT_279333(bpy.types.Operator):#太く
#    """太く"""
#    bl_idname = "object.myobject_279333"
#    bl_label = "太く"
#    bl_options = {'REGISTER', 'UNDO'}

#    uiitem = uiitem()
#    uiitem.button(bl_idname,bl_label,icon="",mode="")


#    ###################################
#    #処理部分
#    ###################################
#    def execute(self, context):
#        bpy.context.scene.grease_pencil.layers.active.line_change = 20
#        bpy.ops.gpencil.stroke_apply_thickness()
#        #GLレンダ
#        bpy.ops.object.myobject_979047()
        
#        return {'FINISHED'}
#########################################









"""
def sub_registration():
    pass

def sub_unregistration():
    pass
"""
def sub_registration():
    #bpy.types.DATA_PT_lens.append(fjw_greasepenciltools_ui)
    pass

def sub_unregistration():
    #bpy.types.DATA_PT_lens.remove(fjw_greasepenciltools_ui)
    pass


def register():
    bpy.utils.register_module(__name__)
    sub_registration()
    


def unregister():
    bpy.utils.unregister_module(__name__)
    sub_unregistration()


if __name__ == "__main__":
    register()

