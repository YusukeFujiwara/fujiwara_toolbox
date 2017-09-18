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


        # if bpy.context.visible_objects.active == bpy.context.scene.camera:
        #     if bpy.context.visible_objects.active.select:
        #便利ツール
        if bpy.context.scene.camera is not None:
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
            active = box.row(align=True)
            active.operator("fujiwara_toolbox.command_990292")
            active.operator("object.set_resolution_to_bgimg")
            

            boxlayout = box.column(align=True)
            active = boxlayout.row(align=True)
            active = boxlayout.row(align=True)
            active.operator("fjw_selector.camera_work", icon="CAMERA_DATA")
            active.operator("fjw_selector.camera_work_look_at")
            active.prop(bpy.context.space_data, "lock_camera", icon="CAMERA_DATA", text="")
            active = boxlayout.row(align=True)
            active.operator("fjw_selector.current_view_to_camera", icon="CAMERA_DATA",)
            active = boxlayout.row(align=True)
            active.operator("fjw_selector.non_camera_work")
            active.operator("fjw_selector.non_camera_work_top")
            active.operator("fjw_selector.non_camera_work_right")


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

        active = layout.row(align=True)
        active.label("")
        active = layout.row(align=True)
        active.operator("fjw_selector.prepare_for_posing", icon="POSE_HLT")
        active.operator("fjw_selector.set_face_lamp", icon="LAMP_POINT")

        active = layout.row()
        active.label("3Dカーソル付近選択")

        active = layout.row(align=True)
        active.operator("fjw_selector.select_bone_nearest_to_cursor_all",icon="GROUP_BONE")
        active.operator("fjw_selector.select_bone_nearest_to_cursor",icon="BONE_DATA")

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
        active.operator("fjw_selector.select_bone_nearest_to_cursor_pupil_r")
        active.label("")
        active.operator("fjw_selector.select_bone_nearest_to_cursor_pupil_l")
        active.label("")
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
        active.operator("fjw_selector.select_bone_nearest_to_cursor_chest")
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
        for obj in bpy.context.visible_objects:
            if obj.type == "LAMP":
                if "Sun" in obj.name:
                    sun = obj
                    fjw.activate(sun)
                    break

        return {"FINISHED"}

class CameraWork(bpy.types.Operator):
    """カメラワークをする。"""
    bl_idname="fjw_selector.camera_work"
    bl_label = "カメラワーク"
    def execute(self,context):
        # bpy.ops.view3d.viewnumpad(type='CAMERA')
        #https://blender.stackexchange.com/questions/30643/how-to-toggle-to-camera-view-via-python
        bpy.context.space_data.region_3d.view_perspective = "CAMERA"
        bpy.context.space_data.lock_camera = True
        return {"FINISHED"}

class CameraWorkLookAt(bpy.types.Operator):
    """カメラワークをする。"""
    bl_idname="fjw_selector.camera_work_look_at"
    bl_label = "注視"
    def execute(self,context):
        # bpy.ops.view3d.viewnumpad(type='CAMERA')
        #https://blender.stackexchange.com/questions/30643/how-to-toggle-to-camera-view-via-python
        bpy.context.space_data.region_3d.view_perspective = "CAMERA"
        bpy.context.space_data.lock_camera = True
        bpy.ops.view3d.view_selected(use_all_regions=False)
        return {"FINISHED"}

class CurrentViewToCamera(bpy.types.Operator):
    """カメラワークをする。"""
    bl_idname="fjw_selector.current_view_to_camera"
    bl_label = "現在の視点を採用"
    def execute(self,context):
        #https://blender.stackexchange.com/questions/30643/how-to-toggle-to-camera-view-via-python
        # bpy.context.space_data.region_3d.view_perspective = "CAMERA"
        bpy.context.space_data.lock_camera = False
        bpy.ops.view3d.camera_to_view()
        return {"FINISHED"}


class NonCameraWork(bpy.types.Operator):
    """ノンカメラワークをする。"""
    bl_idname="fjw_selector.non_camera_work"
    bl_label = "ノンカメラワーク"
    def execute(self,context):
        # bpy.ops.view3d.viewnumpad(type='CAMERA')
        #https://blender.stackexchange.com/questions/30643/how-to-toggle-to-camera-view-via-python
        bpy.context.space_data.region_3d.view_perspective = "ORTHO"
        bpy.context.space_data.lock_camera = False
        return {"FINISHED"}

class NonCameraWorkTop(bpy.types.Operator):
    """ノンカメラワークをする。"""
    bl_idname="fjw_selector.non_camera_work_top"
    bl_label = "↑"
    def execute(self,context):
        bpy.ops.view3d.viewnumpad(type='TOP')
        bpy.context.space_data.lock_camera = False
        return {"FINISHED"}

class NonCameraWorkRight(bpy.types.Operator):
    """ノンカメラワークをする。"""
    bl_idname="fjw_selector.non_camera_work_right"
    bl_label = "→"
    def execute(self,context):
        bpy.ops.view3d.viewnumpad(type='RIGHT')
        bpy.context.space_data.lock_camera = False
        return {"FINISHED"}



class SelectMapController(bpy.types.Operator):
    """マップコントローラ"""
    bl_idname="fjw_selector.select_mapcontroller"
    bl_label = "マップコントローラ"
    def execute(self,context):
        fjw.deselect()
        mc = None
        for obj in bpy.context.visible_objects:
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
        select_object_nearest_to_cursor(bpy.context.visible_objects)
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

        #ジオメトリ用処理
        if namepattern == "geometry":
            #人体判定
            if "neck" in armu.pose_bones:
                gbone = armu.GetGeometryBone()
                if gbone is not None:
                    loc = armu.get_pbone_world_co(gbone.head)
                    data = [obj, gbone.name]
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
        select_bone_nearest_to_cursor(bpy.context.visible_objects)
        return {"FINISHED"}


class SelectBoneNearestToCursor_Top(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_top"
    bl_label = "天"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, "天")
        return {"FINISHED"}

class SelectBoneNearestToCursor_Bottom(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_bottom"
    bl_label = "地"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, "地")
        return {"FINISHED"}

class SelectBoneNearestToCursor_North(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_north"
    bl_label = "北"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, "北")
        return {"FINISHED"}

class SelectBoneNearestToCursor_South(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_south"
    bl_label = "南"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, "南")
        return {"FINISHED"}

class SelectBoneNearestToCursor_East(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_east"
    bl_label = "東"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, "東")
        return {"FINISHED"}

class SelectBoneNearestToCursor_West(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_west"
    bl_label = "西"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, "西")
        return {"FINISHED"}


class SelectBoneNearestToCursor_All(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_all"
    bl_label = "全ボーン"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects)
        bpy.ops.pose.select_all(action='SELECT')
        return {"FINISHED"}


class PrepareForPosing(bpy.types.Operator):
    """ポージング準備"""
    bl_idname = "fjw_selector.prepare_for_posing"
    bl_label = "ポージング準備"
    def execute(self, context):
        bpy.context.space_data.show_only_render = False
        bpy.context.scene.render.use_simplify = True
        bpy.context.scene.render.simplify_subdivision = 1
        bpy.context.space_data.lock_camera = False
        #全部のAO無効化する
        for screen in bpy.data.screens:
            for area in screen.areas:
                for space in area.spaces:
                    if space.type == "VIEW_3D":
                        space.fx_settings.use_ssao = False
        return {"FINISHED"}

class SetFaceLamp(bpy.types.Operator):
    """顔用ランプ設置"""
    bl_idname = "fjw_selector.set_face_lamp"
    bl_label = "顔用ランプ設置"
    def execute(self, context):
        fjw.mode("OBJECT")
        bpy.ops.object.lamp_add(type='POINT', radius=0.2, view_align=True, location=bpy.context.space_data.cursor_location, layers=bpy.context.scene.layers)
        bpy.context.object.data.use_specular = False
        return {"FINISHED"}


#人体ボーン選択
class SelectBoneNearestToCursor_Eyetarget(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_eyetarget"
    bl_label = "視線"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, "eyetarget")
        return {"FINISHED"}

class SelectBoneNearestToCursor_EyetopR(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_eyetop_r"
    bl_label = "上"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, "eyetop_r")
        return {"FINISHED"}

class SelectBoneNearestToCursor_EyetopL(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_eyetop_l"
    bl_label = "上"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, "eyetop_l")
        return {"FINISHED"}

class SelectBoneNearestToCursor_PupilR(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_pupil_r"
    bl_label = "目"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, "pupil_r")
        return {"FINISHED"}

class SelectBoneNearestToCursor_PupilL(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_pupil_l"
    bl_label = "目"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, "pupil_l")
        return {"FINISHED"}


class SelectBoneNearestToCursor_EyebottomR(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_eyebottom_r"
    bl_label = "下"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, "eyebottom_r")
        return {"FINISHED"}

class SelectBoneNearestToCursor_EyebottomL(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_eyebottom_l"
    bl_label = "下"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, "eyebottom_l")
        return {"FINISHED"}


class SelectBoneNearestToCursor_Geometry(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_geometry"
    bl_label = "ジオメトリ"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, "geometry")
        return {"FINISHED"}

class SelectBoneNearestToCursor_Head(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_head"
    bl_label = "頭"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, "head")
        return {"FINISHED"}
class SelectBoneNearestToCursor_Neck(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_neck"
    bl_label = "首"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, "neck")
        return {"FINISHED"}
class SelectBoneNearestToCursor_Chest(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_chest"
    bl_label = "胸"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, "chest")
        return {"FINISHED"}
class SelectBoneNearestToCursor_BodyMaster(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_body_master"
    bl_label = "ボディ親"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, "ボディ親")
        return {"FINISHED"}
class SelectBoneNearestToCursor_Spine(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_spine"
    bl_label = "腰"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, "spine")
        return {"FINISHED"}


#腕・脚
class SelectBoneNearestToCursor_ShoulderR(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_shoulder_r"
    bl_label = "肩"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, "肩\.R")
        return {"FINISHED"}
class SelectBoneNearestToCursor_ShoulderL(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_shoulder_l"
    bl_label = "肩"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, "肩\.L")
        return {"FINISHED"}

class SelectBoneNearestToCursor_ElbowR(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_elbow_r"
    bl_label = "肘"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, "肘\.R")
        return {"FINISHED"}
class SelectBoneNearestToCursor_ElbowL(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_elbow_l"
    bl_label = "肘"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, "肘\.L")
        return {"FINISHED"}
class SelectBoneNearestToCursor_HandR(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_hand_r"
    bl_label = "手"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, "腕\.R")
        return {"FINISHED"}
class SelectBoneNearestToCursor_HandL(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_hand_l"
    bl_label = "手"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, "腕\.L")
        return {"FINISHED"}


class SelectBoneNearestToCursor_KneeR(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_knee_r"
    bl_label = "膝"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, "脚\.R")
        return {"FINISHED"}
class SelectBoneNearestToCursor_KneeL(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_knee_l"
    bl_label = "膝"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, "脚\.L")
        return {"FINISHED"}
class SelectBoneNearestToCursor_FootR(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_foot_r"
    bl_label = "足"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, "足\.R")
        return {"FINISHED"}
class SelectBoneNearestToCursor_FootL(bpy.types.Operator):
    """ボーン選択。"""
    bl_idname="fjw_selector.select_bone_nearest_to_cursor_foot_l"
    bl_label = "足"
    def execute(self,context):
        select_bone_nearest_to_cursor(bpy.context.visible_objects, "足\.L")
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