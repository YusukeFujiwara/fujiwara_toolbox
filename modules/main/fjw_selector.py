import bpy
import sys
import inspect
import os.path
import os
import bmesh
import datetime
import math
import shutil
import re
import subprocess

from bpy.app.handlers import persistent

fujiwara_toolbox = __import__(__package__)
try:
    from fujiwara_toolbox import fjw #コード補完用
except:
    fjw = fujiwara_toolbox.fjw



bl_info = {
    "name": "FJW Selector",
    "description": "オブジェクト選択等の効率化ツール",
    "author": "藤原佑介",
    "version": (1, 0),
    "blender": (2, 77, 0),
    "location": "View3D > Object",
    "warning": "", # 警告アイコンとテキストのために使われます
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"}


############################################################################################################################
############################################################################################################################
#パネル部分 メインパネル登録
############################################################################################################################
############################################################################################################################

#メインパネル
class FJWSelector(bpy.types.Panel):#メインパネル
    bl_label = "セレクタ"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Fujiwara Tool Box"

    @classmethod
    def poll(cls, context):
        pref = fujiwara_toolbox.conf.get_pref()
        return pref.fjwselector

    def draw(self, context):
        filename = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
        dir = os.path.dirname(bpy.data.filepath)

        layout = self.layout
        layout = layout.column(align=True)
        # active.operator("",icon="", text="")
        active = layout.row(align=True)

        active = layout.row(align=True)
        active.label("セレクタ")
        active = layout.row(align=True)
        active.operator("fjw_selector.select_camera", icon="CAMERA_DATA")
        active.operator("fjw_selector.select_sun", icon="LAMP_SUN")
        # active = layout.row(align=True)
        # active.operator("fjw_selector.select_mapcontroller", icon="OUTLINER_OB_ARMATURE")
        # active = layout.row(align=True)
        # active.label("3Dカーソル選択")
        # active = layout.row(align=True)
        # active.operator("fjw_selector.select_object_nearest_to_cursor")
        # active.operator("fjw_selector.select_bone_nearest_to_cursor")

        if bpy.context.scene.objects.active == bpy.context.scene.camera:
            if bpy.context.scene.objects.active.select:
                #便利ツール
                active = layout.row(align=True)
                active.label("")
                box = layout.box()
                box.label("Camera Prop")
                cam = bpy.context.scene.camera.data
                split = box.split()
                active = split.column(align=True)
                if hasattr(bpy.context.scene, "ct_dz_camera_lens"):
                    active.label("dolly zoom")
                    active.prop(bpy.context.scene, "ct_dz_camera_lens")
                active = split.column(align=True)
                active.label("焦点距離")
                active.prop(cam, "lens")

                split = box.split()
                col = split.column(align=True)
                col.label(text="Shift:")
                col.prop(cam, "shift_x", text="X")
                col.prop(cam, "shift_y", text="Y")

                col = split.column(align=True)
                col.label(text="Clipping:")
                col.prop(cam, "clip_start", text="Start")
                col.prop(cam, "clip_end", text="End")
                active = box.row(align=True)
                active.operator("object.setshift_to_cursor")
                active.operator("object.border_fromfile")


        active = layout.row(align=True)
        active.label("3Dカーソル付近選択")

        mc = False
        for obj in bpy.context.scene.objects:
            if "MapController" in obj.name:
                mc = True
        if mc:
            active = layout.row(align=True)
            active.label("マップ", icon="OUTLINER_OB_ARMATURE")
            box = layout.box()
            boxlayout = box.column(align=True)
            active = boxlayout.row(align=True)
            active.operator("fjw_selector.select_bone_nearest_to_cursor_top")
            active = boxlayout.row(align=True)
            active.label("")
            active.operator("fjw_selector.select_bone_nearest_to_cursor_north")
            active.label("")
            active = boxlayout.row(align=True)
            active.operator("fjw_selector.select_bone_nearest_to_cursor_west")
            active.label("")
            active.operator("fjw_selector.select_bone_nearest_to_cursor_east")
            active = boxlayout.row(align=True)
            active.label("")
            active.operator("fjw_selector.select_bone_nearest_to_cursor_south")
            active.label("")
            active = boxlayout.row(align=True)
            active.operator("fjw_selector.select_bone_nearest_to_cursor_bottom")

        active = layout.row(align=True)
        active.label("人体", icon="OUTLINER_OB_ARMATURE")
        box = layout.box()
        boxlayout = box.column(align=True)
        active = boxlayout.row(align=True)
        active.operator("fjw_selector.select_bone_nearest_to_cursor_eyetarget")
        active = boxlayout.row(align=True)
        active.label("右")
        active.operator("fjw_selector.select_bone_nearest_to_cursor_eyetop_r")
        active.label("")
        active.operator("fjw_selector.select_bone_nearest_to_cursor_eyetop_l")
        active.label("左")
        active = boxlayout.row(align=True)
        active.label("")
        active.operator("fjw_selector.select_bone_nearest_to_cursor_eyebottom_r")
        active.label("")
        active.operator("fjw_selector.select_bone_nearest_to_cursor_eyebottom_l")
        active.label("")
        active = boxlayout.row(align=True)
        active.label("右")
        active.label("")
        active.operator("fjw_selector.select_bone_nearest_to_cursor_head")
        active.label("")
        active.label("左")
        active = boxlayout.row(align=True)
        active.operator("fjw_selector.select_bone_nearest_to_cursor_shoulder_r")
        active.label("")
        active.operator("fjw_selector.select_bone_nearest_to_cursor_neck")
        active.label("")
        active.operator("fjw_selector.select_bone_nearest_to_cursor_shoulder_l")
        active = boxlayout.row(align=True)
        active.operator("fjw_selector.select_bone_nearest_to_cursor_elbow_r")
        active.label("")
        active.operator("fjw_selector.select_bone_nearest_to_cursor_chest")
        active.label("")
        active.operator("fjw_selector.select_bone_nearest_to_cursor_elbow_l")
        active = boxlayout.row(align=True)
        active.operator("fjw_selector.select_bone_nearest_to_cursor_hand_r")
        active.label("")
        active.operator("fjw_selector.select_bone_nearest_to_cursor_spine")
        active.label("")
        active.operator("fjw_selector.select_bone_nearest_to_cursor_hand_l")
        active = boxlayout.row(align=True)
        active.operator("fjw_selector.select_bone_nearest_to_cursor_body_master")
        active = boxlayout.row(align=True)
        active.label("")
        active.operator("fjw_selector.select_bone_nearest_to_cursor_knee_r")
        active.label("")
        active.operator("fjw_selector.select_bone_nearest_to_cursor_knee_l")
        active.label("")
        active = boxlayout.row(align=True)
        active.label("")
        active.operator("fjw_selector.select_bone_nearest_to_cursor_foot_r")
        active.label("")
        active.operator("fjw_selector.select_bone_nearest_to_cursor_foot_l")
        active.label("")
        active = boxlayout.row(align=True)
        active.operator("fjw_selector.select_bone_nearest_to_cursor_geometry")



############################################################################################################################
#ユーティリティ関数
############################################################################################################################

############################################################################################################################
############################################################################################################################
#各ボタンの実装
############################################################################################################################
############################################################################################################################
'''
class cls(bpy.types.Operator):
    """説明"""
    bl_idname="fjw_selector.cls"
    bl_label = "ラベル"
    def execute(self,context):
        self.report({"INFO"},"")
        return {"FINISHED"}
'''

class Dummy(bpy.types.Operator):
    """説明"""
    bl_idname="fjw_selector.dummy"
    bl_label = ""
    def execute(self,context):
        return {"FINISHED"}


class SelectCamera(bpy.types.Operator):
    """カメラを選択する"""
    bl_idname="fjw_selector.select_camera"
    bl_label = "カメラ"
    def execute(self,context):
        fjw.deselect()
        camera = bpy.context.scene.camera
        if camera is not None:
            fjw.activate(camera)
        return {"FINISHED"}

class SelectSun(bpy.types.Operator):
    """SUNを選択する"""
    bl_idname="fjw_selector.select_sun"
    bl_label = "SUN"
    def execute(self,context):
        fjw.deselect()
        sun = None
        for obj in bpy.context.scene.objects:
            if obj.type == "LAMP":
                if "Sun" in obj.name:
                    sun = obj
                    fjw.activate(sun)
                    break

        return {"FINISHED"}

class SelectMapController(bpy.types.Operator):
    """マップコントローラ"""
    bl_idname="fjw_selector.select_mapcontroller"
    bl_label = "マップコントローラ"
    def execute(self,context):
        fjw.deselect()
        mc = None
        for obj in bpy.context.scene.objects:
            if obj.type == "ARMATURE":
                if "MapController" in obj.name:
                    mc = obj
                    fjw.activate(mc)
                    fjw.mode("POSE")
                    break
        return {"FINISHED"}




def select_object_nearest_to_cursor(objects, namepattern=".*"):
    name_re = re.compile(namepattern, re.IGNORECASE)

    fjw.deselect()
    kdu = fjw.KDTreeUtils()
    for obj in objects:
        #名前でフィルタリング
        if name_re.search(obj.name) is None:
            continue
        loc = fjw.get_world_co(obj)
        data = [obj]
        kdu.append_data(loc, data)
    #ターゲットがなければ終了
    if len(kdu.items) == 0:
        return

    kdu.construct_kd_tree()
    result_data = kdu.find(bpy.context.space_data.cursor_location)
    kdu.finish()
    fjw.mode("OBJECT")
    fjw.activate(result_data[0])
    

class SelectObjectNearestToCursor(bpy.types.Operator):
    """3Dカーソルに一番近いオブジェクトを選択する"""
    bl_idname="fjw_selector.select_object_nearest_to_cursor"
    bl_label = "オブジェクト"
    def execute(self,context):
        select_object_nearest_to_cursor(bpy.context.scene.objects)
        return {"FINISHED"}

def select_bone_nearest_to_cursor(objects, namepattern=".*"):
    name_re = re.compile(namepattern, re.IGNORECASE)

    fjw.deselect()
    kdu = fjw.KDTreeUtils()
    for obj in objects:
        if obj.type != "ARMATURE":
            continue
        armu = fjw.ArmatureUtils(obj)
        for pbone in armu.pose_bones:
            if name_re.search(pbone.name) is None:
                continue
            loc = armu.get_pbone_world_co(pbone.head)
            data = [obj, pbone.name]
            kdu.append_data(loc, data)
    #ターゲットがなければ終了
    if len(kdu.items) == 0:
        return

    kdu.construct_kd_tree()
    result_data = kdu.find(bpy.context.space_data.cursor_location)
    kdu.finish()

    obj = result_data[0]
    bonename = result_data[1]
    armu = fjw.ArmatureUtils(obj)
    fjw.activate(obj)
    fjw.mode("POSE")
    armu.deselect()
    armu.activate(armu.posebone(bonename))


class SelectBoneNearestToCursor(bpy.types.Operator):
    """カーソルに一番近いボーンを選択する"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor"
    bl_label = "ボーン"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.scene.objects)
        return {"FINISHED"}


class SelectBoneNearestToCursor_Top(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_top"
    bl_label = "天"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.scene.objects, "天")
        return {"FINISHED"}

class SelectBoneNearestToCursor_Bottom(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_bottom"
    bl_label = "地"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.scene.objects, "地")
        return {"FINISHED"}

class SelectBoneNearestToCursor_North(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_north"
    bl_label = "北"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.scene.objects, "北")
        return {"FINISHED"}

class SelectBoneNearestToCursor_South(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_south"
    bl_label = "南"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.scene.objects, "南")
        return {"FINISHED"}

class SelectBoneNearestToCursor_East(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_east"
    bl_label = "東"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.scene.objects, "東")
        return {"FINISHED"}

class SelectBoneNearestToCursor_West(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_west"
    bl_label = "西"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.scene.objects, "西")
        return {"FINISHED"}




#人体ボーン選択
class SelectBoneNearestToCursor_Eyetarget(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_eyetarget"
    bl_label = "視線"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.scene.objects, "eyetarget")
        return {"FINISHED"}

class SelectBoneNearestToCursor_EyetopR(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_eyetop_r"
    bl_label = "上"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.scene.objects, "eyetop_r")
        return {"FINISHED"}

class SelectBoneNearestToCursor_EyetopL(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_eyetop_l"
    bl_label = "上"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.scene.objects, "eyetop_l")
        return {"FINISHED"}

class SelectBoneNearestToCursor_EyebottomR(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_eyebottom_r"
    bl_label = "下"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.scene.objects, "eyebottom_r")
        return {"FINISHED"}

class SelectBoneNearestToCursor_EyebottomL(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_eyebottom_l"
    bl_label = "下"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.scene.objects, "eyebottom_l")
        return {"FINISHED"}


class SelectBoneNearestToCursor_Geometry(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_geometry"
    bl_label = "ジオメトリ"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.scene.objects, "geometry")
        return {"FINISHED"}

class SelectBoneNearestToCursor_Head(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_head"
    bl_label = "頭"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.scene.objects, "head")
        return {"FINISHED"}
class SelectBoneNearestToCursor_Neck(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_neck"
    bl_label = "首"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.scene.objects, "neck")
        return {"FINISHED"}
class SelectBoneNearestToCursor_Chest(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_chest"
    bl_label = "胸"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.scene.objects, "chest")
        return {"FINISHED"}
class SelectBoneNearestToCursor_BodyMaster(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_body_master"
    bl_label = "ボディ親"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.scene.objects, "ボディ親")
        return {"FINISHED"}
class SelectBoneNearestToCursor_Spine(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_spine"
    bl_label = "腰"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.scene.objects, "spine")
        return {"FINISHED"}


#腕・脚
class SelectBoneNearestToCursor_ShoulderR(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_shoulder_r"
    bl_label = "肩"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.scene.objects, "肩\.R")
        return {"FINISHED"}
class SelectBoneNearestToCursor_ShoulderL(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_shoulder_l"
    bl_label = "肩"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.scene.objects, "肩\.L")
        return {"FINISHED"}

class SelectBoneNearestToCursor_ElbowR(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_elbow_r"
    bl_label = "肘"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.scene.objects, "肘\.R")
        return {"FINISHED"}
class SelectBoneNearestToCursor_ElbowL(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_elbow_l"
    bl_label = "肘"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.scene.objects, "肘\.L")
        return {"FINISHED"}
class SelectBoneNearestToCursor_HandR(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_hand_r"
    bl_label = "手"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.scene.objects, "腕\.R")
        return {"FINISHED"}
class SelectBoneNearestToCursor_HandL(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_hand_l"
    bl_label = "手"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.scene.objects, "腕\.L")
        return {"FINISHED"}


class SelectBoneNearestToCursor_KneeR(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_knee_r"
    bl_label = "膝"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.scene.objects, "脚\.R")
        return {"FINISHED"}
class SelectBoneNearestToCursor_KneeL(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_knee_l"
    bl_label = "膝"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.scene.objects, "脚\.L")
        return {"FINISHED"}
class SelectBoneNearestToCursor_FootR(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_foot_r"
    bl_label = "足"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.scene.objects, "足\.R")
        return {"FINISHED"}
class SelectBoneNearestToCursor_FootL(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_foot_l"
    bl_label = "足"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.scene.objects, "足\.L")
        return {"FINISHED"}



############################################################################################################################
############################################################################################################################
#オペレータークラスやUIボタンの登録
############################################################################################################################
############################################################################################################################
def sub_registration():
    pass

def sub_unregistration():
    pass


def register():    #登録
    bpy.utils.register_module(__name__)
    sub_registration()

def unregister():    #登録解除
    bpy.utils.unregister_module(__name__)
    sub_unregistration()

if __name__ == "__main__":
    register()