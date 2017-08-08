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
        # active.operator("",icon="", text="")
        layout = layout.column(align=True)
        active = layout.row(align=True)
        active.operator("fjw_selector.select_camera", icon="CAMERA_DATA")
        active.operator("fjw_selector.select_sun", icon="LAMP_SUN")
        active = layout.row(align=True)
        active.operator("fjw_selector.select_mapcontroller", icon="OUTLINER_OB_ARMATURE")
        active = layout.row(align=True)
        active.label("3Dカーソル選択")
        active = layout.row(align=True)
        active.operator("fjw_selector.select_object_nearest_to_cursor")
        active.operator("fjw_selector.select_bone_nearest_to_cursor")



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




def select_object_nearest_to_cursor(objects):
    fjw.deselect()
    kdu = fjw.KDTreeUtils()
    for obj in objects:
        loc = fjw.get_world_co(obj)
        data = [obj]
        kdu.append_data(loc, data)
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

def select_bone_nearest_to_cursor(objects):
    fjw.deselect()
    kdu = fjw.KDTreeUtils()
    for obj in objects:
        if obj.type != "ARMATURE":
            continue
        armu = fjw.ArmatureUtils(obj)
        for pbone in armu.pose_bones:
            loc = armu.get_pbone_world_co(pbone.head)
            data = [obj, pbone.name]
            kdu.append_data(loc, data)
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
        targets = []
        for obj in bpy.context.scene.objects:
            if obj.type == "ARMATURE":
                targets.append(obj)
        select_bone_nearest_to_cursor(targets)
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