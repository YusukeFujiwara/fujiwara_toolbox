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

class ChildInfo:
    def __init__(self, obj):
        self.obj = obj
        self.parent_type = obj.parent_type
        self.parent_bone = obj.parent_bone
        self.print_info()

    def print_info(self):
        print("%s : %s, %s"%(self.obj.name, self.parent_type, self.parent_bone))

class RiggedObject:
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


class BoneInfo:
    def __init__(self, bone):
        self.name = bone.name
        self.use_deform = bone.use_deform
        self.hide = bone.hide

class Metarig:
    def __init__(self):
        pass

class Rig:
    def __init__(self):
        pass

    def check_symetry(self):
        pass

