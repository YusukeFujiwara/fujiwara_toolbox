import bpy
#パス関連のユーティリティ
#http://xwave.exblog.jp/7155003
import os.path
import os
import re
import bmesh
import datetime
import subprocess
import shutil
import time
import copy
import sys
import mathutils
from collections import OrderedDict

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )


fujiwara_toolbox = __import__(__package__)
try:
    from fujiwara_toolbox import fjw #コード補完用
except:
    fjw = fujiwara_toolbox.fjw


import random
from mathutils import *

# assetdir = fujiwara_toolbox.conf.assetdir
assetdir = ""

class ChildInfo():
    def __init__(self, obj):
        self.obj = obj
        self.parent_type = obj.parent_type
        self.parent_bone = obj.parent_bone
        self.print_info()

    def print_info(self):
        print("%s : %s, %s"%(self.obj.name, self.parent_type, self.parent_bone))

class RiggedObject():
    def __init__(self, obj, rig):
        self.obj = obj
        self.rig = rig
        self.parent_type = obj.parent_type
        self.parent_bone = obj.parent_bone
        self.print_info()

    def parent_clear(self):
        """
        ペアレントをクリアする。
        """
        fjw.deselect()
        fjw.activate(self.obj)
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

    def apply(self):
        """
        アーマチュア変形やボーン相対変形を適用する。
        ペアレントがクリアされている前提。
        """

        obj = self.obj

        fjw.deselect()
        fjw.activate(obj)

        #モディファイアの適用
        if obj.type == "MESH":
            modu = fjw.Modutils(obj)
            arm = modu.find_bytype("ARMATURE")
            modu.apply(arm)

        #トランスフォームの適用
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)


    def reparent(self):
        """
        格納した情報に応じて再ペアレントする。
        """
        rig = self.rig
        obj = self.obj

        modu = fjw.Modutils(self.obj)
        mod_arm = modu.find_bytype("ARMATURE")

        if mod_arm is None:
            fjw.mode("OBJECT")
            fjw.deselect()
            obj.select = True

            fjw.activate(rig)

            if self.parent_type == "OBJECT":
                bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
            elif self.parent_type == "BONE":
                if self.parent_bone in rig.data.bones:
                    fjw.mode("POSE")

                    layerstates = []
                    for state in rig.data.layers:
                        layerstates.append(state)

                    rig.data.layers = [True for i in range(len(rig.data.layers))]

                    rig.data.bones.active = rig.data.bones[self.parent_bone]
                    bpy.ops.object.parent_set(type='BONE_RELATIVE')

                    rig.data.layers = layerstates
        else:
            #既存のアーマチュアmodを除去する
            mod_arms = modu.find_bytype_list("ARMATURE")
            for mod in mod_arms:
                modu.remove(mod)

            fjw.deselect()
            obj.select = True
            fjw.activate(rig)
            if "rigify_parenting" in obj:
                bpy.ops.object.parent_set(type=obj["rigify_parenting"])
            else:
                bpy.ops.object.parent_set(type='ARMATURE_AUTO')
            fjw.activate(obj)
            modu.sort()
        pass

    def print_info(self):
        print("%s : %s, %s"%(self.obj.name, self.parent_type, self.parent_bone))

class RiggedObjects():
    def __init__(self, rig):
        self.rig = rig
        self.rigged_objects = []
        self.setup()
    
    def setup(self):
        obj = self.rig
        for child in obj.children:
            self.rigged_objects.append(RiggedObject(child,obj))
        return self.rigged_objects

    def reset_rig(self, rig):
        for robj in self.rigged_objects:
            robj.rig = rig

    def parent_clear(self):
        for robj in self.rigged_objects:
            robj.parent_clear()

    def apply(self):
        for robj in self.rigged_objects:
            robj.apply()

    def reparent(self):
        for robj in self.rigged_objects:
            robj.reparent()

class EditBoneData():
    def __init__(self, obj, edit_bone):
        # self.edit_bone = edit_bone
        self.obj = obj
        self.name = edit_bone.name
        self.head = edit_bone.head
        self.tail = edit_bone.tail
        self.roll = edit_bone.roll

    def get_ebone(self):
        if fjw.active() != self.obj:
            fjw.activate(self.obj)
        if self.obj.mode != "EDIT":
            fjw.mode("EDIT")
        edit_bones = self.obj.data.edit_bones
        if self.name in edit_bones:
            ebone = edit_bones[self.name]
            return ebone
        return None

    def restore_info(self):
        ebone = self.get_ebone()
        if ebone:
            ebone.name = self.name
            ebone.use_deform = self.use_deform
            ebone.hide = self.hide
    
    def restore_info_from(self, fromdata):
        self.name = fromdata.name
        self.use_deform = fromdata.use_deform
        self.hide = fromdata.hide
        self.restore_info()

    def copy_shape(self, edit_bone_data, head=True, tail=True, roll=True):
        ebone = self.get_ebone()
        if ebone:
            if head:
                ebone.head = edit_bone_data.head
            if tail:
                ebone.tail = edit_bone_data.tail
            if roll:
                ebone.roll = edit_bone_data.roll


    def child_is_connected(self):
        ebone = self.get_ebone()
        if ebone:
            for child in ebone.children:
                if child.use_connect:
                    return True
        return False


class EditBonesData():
    def __init__(self, obj):
        self.obj = obj
        self.edit_bones = []
        self.setup()

        print("EditBonesData:%s, %d"%(self.obj.name, len(self.edit_bones)))

    def setup(self):
        fjw.mode("OBJECT")
        fjw.deselect()
        fjw.activate(self.obj)
        fjw.mode("EDIT")
        for ebone in self.obj.data.edit_bones:
            self.edit_bones.append(EditBoneData(self.obj, ebone))

    def get_ebone_byname(self, name):
        for ebone in self.edit_bones:
            if ebone.name == name:
                return ebone
        return None

    def restore_info_from(self, fromdata):
        """
        ボーン情報を指定オブジェクトから設定する。
        """
        for from_ebone in fromdata.edit_bones:
            ebone = self.get_ebone_byname(from_ebone.name)
            if ebone:
                ebone.restore_info_from(from_ebone)

class ArmatureTool():
    def __init__(self, obj):
        self.obj = obj
        self.name = obj.name
        self.groups = obj.users_group
        self.show_x_ray = obj.show_x_ray
        self.layers = []
        for state in obj.layers:
            self.layers.append(state)

        self.edit_bones_data = EditBonesData(obj)

    def reset_edit_bones(self):
        self.edit_bones_data = EditBonesData(self.obj)

    def restore_settings(self):
        self.obj.name = self.name
        for group in self.groups:
            fjw.group(group.name,[self.obj])
        self.obj.show_x_ray = self.show_x_ray
        self.obj.layers = self.layers

    def restore_settings_from(self, fromdata):
        self.name = fromdata.name
        self.groups = fromdata.groups
        self.show_x_ray = fromdata.show_x_ray
        self.layers = fromdata.layers
        self.restore_settings()

    def testprint(self):
        print("###test print###")
        print(self.name)
        print("%d bones"%(len(self.edit_bones_data.edit_bones)))
        # for ebone in self.edit_bones_data.edit_bones:
        #     print("self:"+ ebone.name)


class Metarig(ArmatureTool):
    """
    ORG-は、子と分断されてたりする
    DEF-の、Head位置だけを反映すればいいのでは？
        子が接続しているボーンはHeadだけ反映、子がないor接続していないボーンはヘッドも反映する。
        Headが親側　Tailが子側
    """
    def __init__(self, obj):
        super().__init__(obj)

    def copy_shapes(self, edit_bones_data, prefix="DEF-"):
        """
        受け取ったデータのデータ通りにメタリグの形状を設定する。
        """
        fjw.activate(self.obj)
        fjw.mode("EDIT")
        for edit_bone in edit_bones_data.edit_bones:
            fixed_name = edit_bone.name.replace(prefix, "")
            self_bone = self.edit_bones_data.get_ebone_byname(fixed_name)
            if not self_bone:
                continue
            # if self_bone.child_is_connected():
            #     #子が接続されているので、Headだけ動かす。
            #     self_bone.copy_shape(edit_bone,True,False,True)
            # else:
            #     #子が接続されていないので、すべてコピー。
            #     self_bone.copy_shape(edit_bone)
            self_bone.copy_shape(edit_bone)
        fjw.mode("OBJECT")

class Rig(ArmatureTool):
    def __init__(self, rig):
        super().__init__(rig)
        self.rigged_objects = RiggedObjects(rig)

    def is_symmetry(self):
        armature = self.obj
        armu = fjw.ArmatureUtils(armature)
        for pbone in armu.pose_bones:
            if "_L" in pbone.name:
                lbone = pbone
                rname = pbone.name.replace("_L", "_R")
                if rname in armu.pose_bones:
                    rbone = armu.pose_bones[rname]
                    #微妙に誤差が出ることがあるので丸める
                    if round(rbone.head.x*100) != round((lbone.head.x * -1)*100):
                        # self.report({"INFO"}, "ボーンが左右非対称です。 %s, %s"%(rbone.name, lbone.name))
                        return False
        return True

    def apply_pose(self):
        """
        ポーズをデフォルトに設定する。トランスフォームも確定する。
        """
        fjw.mode("OBJECT")
        fjw.deselect()
        fjw.activate(self.obj)
        fjw.mode("POSE")
        bpy.ops.pose.visual_transform_apply()
        bpy.ops.pose.armature_apply()
        self.reset_edit_bones()

class RigifyTools():
    def __init__(self):
        self.metarig = None
        self.rig = None

    def set_rig(self, rig):
        if rig:
            self.rig = Rig(rig)
    
    def set_metarig(self, metarig):
        if metarig:
            self.metarig = Metarig(metarig)


    def find_rig(self, rig=None):
        if rig:
            return rig
        
        rigname = ""
        win = bpy.context.window_manager
        if hasattr(win, "rigify_target_rig"):
            rigname = win.rigify_target_rig
        if rigname == "":
            rigname = "rig"

        for obj in bpy.context.scene.objects:
            if obj.type != "ARMATURE":
                continue
            if "rig_id" in obj.data and rigname == obj.name:
                return obj

        return None

    def find_metarig(self, metarig=None):
        if metarig:
            return metarig

        for obj in bpy.context.scene.objects:
            if obj.type != "ARMATURE":
                continue
            if "rig_id" not in obj.data and "rig" in obj.name:
                return obj
        return None

    def gen_rig_and_reparent(self, metarig):
        """
        genrigして再ペアレントする。
        """
        if metarig.type != "ARMATURE":
            return False

        self.set_metarig(metarig)
        self.set_rig(self.find_rig())

        if self.rig:
            self.rig.obj.data.pose_position = 'REST'
            self.rig.rigged_objects.parent_clear()
            fjw.delete([self.rig.obj])

        fjw.deselect()
        fjw.activate(metarig)
        bpy.ops.pose.rigify_generate()

        new_rig = Rig(fjw.active())
        if self.rig:
            new_rig.edit_bones_data.restore_info_from(self.rig.edit_bones_data)
            self.rig.rigged_objects.reset_rig(new_rig.obj)
        bpy.ops.view3d.layers(nr=0, extend=False)
        if self.rig:
            self.rig.rigged_objects.reparent()
        bpy.ops.view3d.layers(nr=0, extend=False)
        metarig.hide = True

        fjw.activate(new_rig.obj)
        fjw.mode("POSE")
        
        return True

    def rig_shape_to_metarig_shape(self,rig):
        if rig.type != "ARMATURE":
            return False

        self.set_rig(rig)
        self.rig.testprint()
        self.set_metarig(self.find_metarig())

        if not self.metarig:
            print("Metarig not found.")
            return False
        self.metarig.testprint()

        self.rig.rigged_objects.parent_clear()    
        self.rig.apply_pose()
        self.rig.reset_edit_bones()
        self.metarig.copy_shapes(self.rig.edit_bones_data,"ORG-")
