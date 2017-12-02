import bpy
import sys
import inspect
#パス関連のユーティリティ
#http://xwave.exblog.jp/7155003
import os.path
import os
import bmesh
import datetime
import math
import subprocess
import shutil
import time
import copy
from collections import OrderedDict
from mathutils import *

fujiwara_toolbox = __import__(__package__)
# try:
#     from fujiwara_toolbox import fjw #コード補完用
# except:
#     fjw = fujiwara_toolbox.fjw


############################################################################################################################
############################################################################################################################
#ユーティリティ
############################################################################################################################
############################################################################################################################

import traceback
def print_exception():
    """
    except:で使う。
    """
    traceback.print_exc()

#ダブルクォーテーション
def qq(str):
    return '"' + str + '"'


def get_resourcesdir():
    scrdir = os.path.dirname(__file__)
    resourcesdir = scrdir + os.sep + "resources" + os.sep
    return resourcesdir

def getdirs(path):
    dirs = []
    for item in os.listdir(path):
        if os.path.isdir(os.path.join(path,item)):
            dirs.append(item)
    return dirs

def get_dir(path):
    dirlist = path.split(os.sep)

    result = ""
    for i in range(len(dirlist) - 1):
        result += dirlist[i] + os.sep
    return result

def get_root(obj):
    parent = obj.parent
    if parent == None:
        return obj
    return get_root(parent)

def get_world_co(obj):
    return obj.matrix_world * obj.matrix_basis.inverted() * obj.location

def cursor():
    return bpy.context.space_data.cursor_location
def set_cursor(pos):
    bpy.context.space_data.cursor_location = pos

def blendname():
    name = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
    return name

def blenddir():
    dir = os.path.dirname(bpy.data.filepath)
    return dir


# def group(name, objects):
#     group = None
#     for gr in bpy.data.groups:
#         if name == gr.name:
#             if gr.library is None:
#                 group = gr
#                 break
    
#     if group is None:
#         group = bpy.data.groups.new(name)

#     for ob in selection:
#         if ob.name not in group.objects:
#             group.objects.link(ob)

#     return group

def find(name):
    for obj in bpy.data.objects:
        if name in obj.name:
            return obj
    return None

def find_list(name,targetlist=None):
    if targetlist == None:
        targetlist = bpy.data.objects
    result = []
    for obj in targetlist:
        if name in obj.name:
            result.append(obj)
    return result

def find_child_bytype(parent,type):
    for obj in parent.children:
        if obj.type == type:
            return obj

    for obj in parent.children:
        result = find_child_bytype(obj,type)
        if result is not None:
            return result
    return None

def find_parent_bytype(obj,type):
    parent = obj.parent

    if parent is None:
        return None

    if parent.type == type:
        return parent
    
    return find_parent_bytype(parent, type)

def object(name):
    #オブジェクトが突っ込まれたらそのままかえす
    if type(name) == bpy.types.Object:
        return name

    if name in bpy.data.objects:
        return bpy.data.objects[name]
    else:
        return None

def objects_filter(objects, type="", name=""):
    result = []
    for obj in objects:
        if type != "":
            if obj.type != type:
                continue
        if name != "":
            if obj.name != name:
                continue
        result.append(obj)
    return result


def in_localview():
    #bpy.data.screens[0].areas[1].spaces[0].local_view
    if bpy.context.space_data.local_view == None:
        return False
    else:
        return True

def localview():
    if not in_localview():
        bpy.ops.view3d.localview()

def globalview():
    if in_localview():
        bpy.ops.view3d.localview()

def add_mod(mod_type):
    result = None

    obj = active()

    if obj != None:
        bpy.ops.object.modifier_add(type=mod_type)

        result = getnewmod(obj)
    return result

def get_mod(mod_type):
    result = None

    obj = active()

    if obj != None:
       for mod in obj.modifiers:
           if mod.type == mod_type:
               result = mod
               return result
    return result


def is_in_visible_layer(obj):
    #表示レイヤーに含まれているか
    for index, value in enumerate(bpy.context.scene.layers):
        if value:
            if obj.layers[index]:
                return True
    return False

class Modutils():
    def __init__(self, obj):
        self.object = obj
        self.mods = obj.modifiers
        pass

    def add(self,name,mod_type):
        return self.mods.new(name, mod_type)

    def remove_byname(self,name):
        mod = self.find(name)
        if mod != None:
            self.object.modifiers.remove(mod)
    
    def remove(self, mod):
        if mod != None:
            self.object.modifiers.remove(mod)

    def apply(self, mod):
        if mod != None:
            activate(self.object)
            print("apply:%s"%mod.name)
            try:
                #ほんとはシェイプキー残しときたかったけど、無理。うまくいかない。全部除去したほうがいい。
                shape_keys = self.object.data.shape_keys
                if shape_keys and len(shape_keys.key_blocks) > 0:
                    self.object.active_shape_key_index = 0
                    bpy.ops.object.shape_key_remove(all=True)

                # #シェイプキーが一つだけだったら削除しちゃう
                # if len(shape_keys.key_blocks) == 1:
                #     bpy.ops.object.shape_key_remove(all=False)

                # print("try1")
                bpy.ops.object.modifier_apply(modifier=mod.name)
                # print("success!")
            except:
                import traceback
                traceback.print_exc()
                pass
                # try:
                #     # print("try2")
                #     shape_keys = self.object.data.shape_keys
                #     if shape_keys and len(shape_keys.key_blocks) > 0:
                #         mod_name = mod.name
                #         bpy.ops.object.modifier_apply(apply_as='SHAPE',modifier=mod.name)
                #         #アクティブをかえないといけない
                #         #該当シェイプキーの検索
                #         for i in range(len(shape_keys.key_blocks)):
                #             key = shape_keys.key_blocks[i]
                #             if key.name == mod_name:
                #                 self.object.active_shape_key_index = i
                #                 bpy.ops.object.shape_key_move(type='TOP')
                #                 self.object.active_shape_key_index = 0
                #                 break
                #         for i in range(len(shape_keys.key_blocks)):
                #             key = shape_keys.key_blocks[i]
                #             if key.name == "Basis":
                #                 self.object.active_shape_key_index = i
                #                 bpy.ops.object.shape_key_remove(all=False)
                #                 break
                #         self.object.active_shape_key_index = 0
                #         self.object.active_shape_key.name = "Basis"
                #         # self.object.active_shape_key_index = len(shape_keys.key_blocks) - 1
                #         # bpy.ops.object.shape_key_move(type='TOP')
                #         # self.object.active_shape_key_index = 0
                #         # bpy.ops.object.shape_key_remove(all=False)
                #         # self.object.active_shape_key.name = "Basis"
                #         # print("success!")
                # except:
                #     print("Failed:%s"%mod.name)
                #     pass


    def find(self,name):
        for mod in self.mods:
            if name in mod.name:
                return mod
        return None

    def find_list(self,name):
        result = []
        for mod in self.mods:
            if name in mod.name:
                result.append(mod)
        return result
    
    def find_bytype(self, type):
        for mod in self.mods:
            if type == mod.type:
                return mod
        return None

    def find_bytype_list(self, type):
        result = []
        for mod in self.mods:
            if type == mod.type:
                result.append(mod)
        return result

    def move_up(self,mod):
        if mod != None:
            activate(self.object)
            bpy.ops.object.modifier_move_up(modifier=mod.name)

    def move_down(self,mod):
        if mod != None:
            activate(self.object)
            bpy.ops.object.modifier_move_down(modifier=mod.name)

    def move_top(self, mod):
        if mod == None:
            return

        activate(self.object)
        last = len(self.object.modifiers) - 1
        mod_md = mod
        mod_n = last
        for i in range(mod_n - 1, -1, -1):
            bpy.ops.object.modifier_move_up(modifier=mod.name)

    def move_bottom(self, mod):
        if mod == None:
            return

        activate(self.object)
        last = len(self.object.modifiers) - 1
        modi = self.object.modifiers.find(mod.name)

        for i in range(modi,last):
            bpy.ops.object.modifier_move_down(modifier=mod.name)

    def show(self, mod):
        if mod != None:
            mod.show_viewport = True
            mod.show_render = True

    def hide(self, mod):
        if mod != None:
            mod.show_viewport = False
            mod.show_render = False

    def get_last(self):
        lastindex = len(self.object.modifiers) - 1
        lastmod = self.object.modifiers[lastindex]
        return lastmod

    def indexof(self, mod):
        index = self.object.modifiers.find(mod)
        return index

    def getbyindex(self, index):
        if index < len(self.object.modifiers):
            return self.object.modifiers[index]
        else:
            return None

    def sort(self):
        #後にやる方が上にくる
        modlist = self.find_bytype_list("MESH_DEFORM")
        for mod in modlist:
            self.move_top(mod)
        modlist = self.find_bytype_list("SURFACE_DEFORM")
        for mod in modlist:
            self.move_top(mod)
        modlist = self.find_bytype_list("ARMATURE")
        for mod in modlist:
            self.move_top(mod)
        modlist = self.find_bytype_list("MIRROR")
        for mod in modlist:
            self.move_top(mod)
        self.move_top(self.find("Parented Mirror"))
        self.move_top(self.find("Target Mirror"))


        self.move_bottom(self.find("分離エッジ_EDGE_SPLIT"))
        self.move_bottom(self.find("分離エッジ_SOLIDIFY"))
        self.move_bottom(self.find("裏ポリエッジ"))

        pass

    def func(self):
        pass

class ArmatureUtils():
    def __init__(self, obj):
        if obj.type != "ARMATURE":
            return None

        self.armature = obj
        self.pose_bones = self.armature.pose.bones
        self.data_bones = self.armature.data.bones
        self.edit_bones = self.armature.data.edit_bones
    
    @property
    def is_proxy(self):
        if self.armature.proxy is None:
            return False
        else:
            return True

    def findname(self, name):#該当するボーンの名前を返す
        for bone in self.armature.data.bones:
            if name in bone.name:
                return bone.name
        return None

    def is_selected(self, bone):
        databone = self.databone(bone.name)
        return databone.select

    def posebone(self, name):#名前のポーズボーンを返す
        return self.armature.pose.bones[name]
    def databone(self, name):
        return self.armature.data.bones[name]
    def editbone(self, name):
        return self.armature.data.edit_bones[name]

    def get_pbone_world_co(self, co):#ボーンのワールド座標を返す
        # loc = self.armature.matrix_world * self.armature.matrix_basis.inverted() * co
        loc = self.armature.matrix_world * co
        return loc

    # def world_to_local_co(self, co):
    #     return

    def dataactive(self):
        return self.armature.data.bones.active

    def poseactive(self):#アクティブボーンを返す
        return self.posebone(self.dataactive().name)

    def activate(self,bone):#アクティブボーンを設定する
        self.armature.data.bones.active = self.armature.data.bones[bone.name]
        pass

    def select(self,bones):
        selection = []
        for bone in bones:
            self.databone(bone.name).select = True
            selection.append(bone)

        return selection
        pass

    def select_all(self):
        selection = []
        for bone in self.armature.data.bones:
            bone.select = True
            selection.append(bone)

        return selection

    def get_selected_list(self):
        selection = []
        for bone in self.armature.data.bones:
            if bone.select:
                selection.append(bone)
        return selection

    def deselect(self):
        for bone in self.armature.data.bones:
            bone.select = False
        pass

    def clearTrans(self, bones):
        for bone in bones:
            pbone = self.posebone(bone.name)
            pbone.location = (0,0,0)
            pbone.rotation_euler.zero()
            qzero = pbone.rotation_euler.to_quaternion()
            pbone.rotation_quaternion = qzero
        pass


    def GetGeometryBone(self):
        geoname = self.findname("Geometry")

        if geoname == None:
            geoname = self.findname("geometry")

        if geoname == None:
            geoname = self.findname("geo")

        if geoname == None:
            geoname = self.findname("Root")

        if geoname == None:
            geoname = self.findname("root")

        if geoname == None:
            #head位置が0,0,0のものを探してやればいいのでは？
            for ebone in self.armature.data.bones:
                if ebone.head == Vector((0,0,0)):
                    geoname = ebone.name
                    break

        #それでもなければアクティブをジオメトリに使う
        if geoname == None:
            geoname = self.poseactive().name

        #それでもなければ0番をジオメトリに使う
        if geoname == None:
            geoname = self.self.armature.data.bones[0].name

        geo = self.posebone(geoname)
        return geo


    def func(self):
        pass

class ArmatureActionUtils():
    def __init__(self, armature):
        self.armature = armature
        self.action = armature.pose_library
        return

    def new_action(self, name):
        action = bpy.data.actions.new(name)
        self.armature.pose_library = action
        self.action = self.armature.pose_library
        pass

    def get_action(self):
        self.action = self.armature.pose_library
        return self.action

    def set_action(self,name):
        #nameが現在のポーズに含まれていればそれを返す
        if self.action is not None:
            if name in self.action.name:
                return self.action

        #なければ作成する
        self.new_action(name)
        return self.action

    

    def get_poselist(self):
        if self.get_action() is None:
            return None
        return self.action.pose_markers

    def store_pose(self,frame,name):
        mode("POSE")
        bpy.ops.poselib.pose_add(frame=frame, name=name)
        pass

    def apply_pose(self, name):
        if name not in self.action.pose_markers:
            print("no pose found")
            return
        for index, pose in enumerate(self.action.pose_markers):
            if pose.name == name:
                bpy.ops.poselib.apply_pose(pose_index=index)
                break

    def delete_pose(self, name):
        if name in self.action.pose_markers:
            bpy.ops.poselib.pose_remove(pose=name)
        pass

class ActionConstraintUtils():
    def __init__(self, obj):
        self.armature = obj
        self.constraint_name = "ActionforConstraint"
        self.action_frame = 60

    def make_action(self):
        action = bpy.data.actions.new(self.constraint_name)
        self.armature.pose_library = action
        mode("POSE")
        bpy.ops.poselib.pose_add(frame=self.action_frame, name="EndPose")
        bpy.ops.pose.transforms_clear()
        bpy.ops.poselib.pose_add(frame=1, name="StartPose")
        bpy.ops.poselib.apply_pose(pose_index=1)
        return action

    def add_pose(self,frame,name):
        action = self.armature.pose_library
        mode("POSE")
        bpy.ops.poselib.pose_add(frame=frame, name=name)
        bpy.ops.pose.transforms_clear()

    def set_action_constraint(self, action):
        armu = ArmatureUtils(self.armature)
        active_pbone = armu.poseactive()

        for pbone in armu.pose_bones:
            if not armu.is_selected(pbone):
                continue
            if pbone.name == active_pbone.name:
                continue
            #コンストレイントを設定する
            constraint = pbone.constraints.new("ACTION")
            constraint.target = self.armature
            constraint.subtarget = active_pbone.name
            constraint.transform_channel = 'SCALE_Z'
            constraint.target_space = 'LOCAL_WITH_PARENT'
            constraint.min = 0.5
            constraint.max = 1
            constraint.frame_start = 60
            constraint.frame_end = 1
            constraint.action = action
        pass
    def auto_execute(self):
        action = self.make_action()
        self.set_action_constraint(action)
        pass

class ConstraintUtils():
    def __init__(self,obj):
        self.obj = obj
        self.constraints = obj.constraints
    
    def add(self, name, type):
        constraint = self.constraints.new(type)
        if name != "":
            constraint.name = name
        return constraint

    def remove(self, constraint):
        self.constraints.remove(constraint)

    def remove_byname(self, name):
        if name not in self.constraints:
            return
        constraint = self.constraints[name]
        self.remove(constraint)

    def find(self, name):
        for constraint in self.constraints:
            if name in constraint.name:
                return constraint
        return None

    def find_list(self, name):
        result = []
        for constraint in self.constraints:
            if name in constraint.name:
                result.append(constraint)
        return result
        
    def find_bytype(self, type):
        for constraint in self.constraints:
            if type == constraint.type:
                return constraint
        return None

    def show(self, constraint):
        if constraint != None:
            constraint.mute = False

    def hide(self, mod):
        if constraint != None:
            constraint.mute = True



class MeshUtils():
    def __init__(self, obj):
        if obj.type != "MESH":
            return None

        self.object = obj
        self.vertices = obj.data.vertices

    def deselect(self):
        activate(self.object)
        mode("EDIT")
        bpy.ops.mesh.select_all(action='DESELECT')

    def selectall(self):
        activate(self.object)
        mode("EDIT")
        bpy.ops.mesh.select_all(action='SELECT')


    def bmesh(self):
        data = self.object.data
        bm = bmesh.from_edit_mesh(data)
        return bm

    def update(self):
        bmesh.update_edit_mesh(self.object.data)

    def tolocal_cordinate(self, loc):
        return self.object.matrix_world.inverted() * loc

    def toworld_cordinate(self, loc):
        return self.object.matrix_world * self.object.matrix_basis.inverted() * loc

    def select_byaxis(self, axis="+X", world=False, basepoint=(0,0,0)):
        activate(self.object)
        mode("EDIT")
        bpy.ops.mesh.select_all(action='DESELECT')

        axs = 0
        direction = 1
        
        if "x" in axis or "X" in axis :
            axs = 0
        if "y" in axis or "Y" in axis :
            axs = 1
        if "z" in axis or "Z" in axis :
            axs = 2

        if "+" in axis:
            direction = 1
        if "-" in axis:
            direction = -1

        data = self.object.data
        bm = self.bmesh()
        bm.faces.active = None

        #選択リフレッシュ
        for v  in bm.verts:
            v.select = False
        for e in bm.edges:
            e.select = False
        for f in bm.faces:
            f.select = False

        for face in bm.faces:
            for v in face.verts:
                co = v.co
                if world:
                    co = self.toworld_cordinate(co)
                if(co[axs] * direction < basepoint[axs]):
                    face.select = True
                    selectflag = True
                    continue
        for edge in bm.edges:
            for v in edge.verts:
                co = v.co
                if world:
                    co = self.toworld_cordinate(co)
                if(co[axs] * direction < basepoint[axs]):
                    edge.select = True
                    selectflag = True
                    continue
        for v in bm.verts:
                co = v.co
                if world:
                    co = self.toworld_cordinate(co)
                if(co[axs] * direction < basepoint[axs]):
                    v.select = True
                    selectflag = True
                    continue
        self.update()
        mode("OBJECT")
        
    def delete(self, deltype="FACE"):
        mode("EDIT")
        bpy.ops.mesh.delete(type=deltype)
        mode("OBJECT")
    def duplicate(self):
        mode("EDIT")
        bpy.ops.mesh.duplicate()
        mode("OBJECT")
    def separete(self):
        mode("EDIT")
        bpy.ops.mesh.separate(type='SELECTED')
        mode("OBJECT")
    def remove_doubles(self):
        mode("EDIT")
        bpy.ops.mesh.remove_doubles()
        mode("OBJECT")


def match(name, type="MESH"):
    result = None

    for obj in bpy.data.objects:
        if obj.type != type:
            continue
        if name in obj.name:
            result = obj
            break

    return result

def matches(name, type="MESH"):
    result = []

    for obj in bpy.data.objects:
        if obj.type != type:
            continue
        if name in obj.name:
            result.append(obj)
            continue
    return result

def getnewmod(obj):
    mods = obj.modifiers
    if len(mods) == 0:
        return None
    else:
        return mods[len(mods) - 1]

def removeall_mod():
    for obj in bpy.context.selected_objects:
       if obj.type == "MESH":
           bpy.context.scene.objects.active = obj
           for mod in obj.modifiers:
                bpy.ops.object.modifier_remove(modifier=mod.name)


"""
        #メッシュ以外除外
        if(reject_notmesh() == False):
            self.report({"WARNING"},"メッシュオブジェクトを選択して下さい:"+self.bl_idname)
            return {'CANCELLED'}

"""
def reject_notmesh():
    #メッシュ以外除外
    for obj in bpy.data.objects:
        if obj.type != "MESH":
            obj.select = False
    if len(bpy.context.selected_objects) == 0:
        return False
    else:
        return True


def active_exists():
    if bpy.context.scene.objects.active == None:
        return False
    else:
        return True

def deselect():
    #選択リフレッシュ
    for obj in bpy.data.objects:
        obj.select = False


def select(objects):
    for obj in objects:
        if obj != None:
            obj.select = True

def delete(objects):
    if objects == None:
        return

    if len(objects) == 0:
        return

    if type(objects) == "list":
        if len(objects) == 0:
            return

    if type(objects) == bpy.types.Object:
        tmp = []
        tmp.append(objects)
        objects = tmp

    for obj in objects:
        bpy.data.objects.remove(obj,True)

    # deselect()

    # for obj in objects:
    #     obj.hide_select = False
    #     obj.select = True
    #     activate(obj)
    #     mode("OBJECT")

    # bpy.ops.object.delete(use_global=False)

def origin_floorize():
    #原点を下に
    objlist = []
    for obj in bpy.context.selected_objects:
        objlist.append(obj)
        
    for obj in bpy.context.selected_objects:
        obj.select = False
        
    for obj in objlist:
        bpy.context.scene.objects.active = obj
        obj.select = True
        
        bpy.ops.view3d.snap_cursor_to_selected()
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bottom = 1000
        for v in obj.data.vertices:
            if v.co.z < bottom:
                bottom = v.co.z
        bpy.context.space_data.cursor_location[2] = bottom
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        obj.select = False
        
    for obj in objlist:
        obj.select = True
    return

def apply_mods():
    active = bpy.context.scene.objects.active
    #bpy.context.window_manager.progress_begin(0,len(bpy.context.selected_objects))
    #prog = 0
    for obj in bpy.context.selected_objects:
        #bpy.context.window_manager.progress_update(prog)
        #prog+=1
        if obj.type == "MESH":
            bpy.context.scene.objects.active = obj
            for mod in obj.modifiers:
                mod.show_viewport = True

                #エラー出さないように個別処理
                if mod.type == "BOOLEAN":
                    if mod.object == None:
                        continue

                bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.context.scene.objects.active = active
    #bpy.context.window_manager.progress_end()
    return


def activate(obj):
    bpy.context.scene.objects.active = obj
    #あんまり意識しない形にするとマズいか？
    if obj is not None:
        obj.select = True
    return obj

def active():
    return bpy.context.scene.objects.active


def objectmode():
    if active() != None:
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

def editmode():
    if active() != None:
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

def mode(modeto):
    if active() != None:
        bpy.ops.object.mode_set(mode=modeto, toggle=False)



#指定レイヤーをTrueにしたレイヤー群を返す。引数がなければ全部False。
def layers(put_layer=-1,put_visible_last=False,not_visible=False):
    ls = [False for i in range(20)]

    #対象レイヤーをオン
    if -1 < put_layer < 20:
        ls[put_layer] = True

    #最後のレイヤーをオンに
    if put_visible_last:
        lastlayer = 0
        for l in range(0,20):
            if bpy.context.scene.layers[l]:
                lastlayer = l

        ls[lastlayer] = True

    #配置レイヤーを自動的に表示する
    if not not_visible:
        for l in range(0,20):
            if ls[l]:
                bpy.context.scene.layers[l] = True

    return ls

def get_selected_list(type="ALL"):
    list = []
    for obj in bpy.context.selected_objects:
        if type == "ALL":
            list.append(obj)
        else:
            if obj.type == type:
                list.append(obj)
    return list


#指定名でプロクシを作成する
def make_proxy(name):
    obj = active()
    if obj.type != "EMPTY":
        #self.report({"INFO"},"リンクしたオブジェクトを指定して下さい。")
        return None

    #リンクデータのオブジェクト
    inlinkobjects = obj.dupli_group.objects

    if name not in inlinkobjects:
        return None

    #対象のオブジェクトがあった
    bpy.ops.object.proxy_make(object=name)
    pobj = active()
    obj.select = True

    #元オブジェクトを親子つける
    bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
    bpy.ops.object.mode_set(mode='POSE', toggle=False)


    return pobj

def make_proxy_type(type):
    linkobj = active()
    result = []
    result.append(linkobj)
    for obj in linkobj.dupli_group.objects:
        if obj.type == type:
            bpy.ops.object.proxy_make(object=obj.name)
            active().name = obj.name + "_proxy"
            result.append(active())
            activate(linkobj)


    return result


def get_linkedfilename(obj):
    linkedpath = bpy.path.abspath(obj.dupli_group.library.filepath)
    linkedfilename = os.path.splitext(os.path.basename(linkedpath))[0]
    return linkedfilename

def make_proxy_all():
    linkobj = active()
    result = []
    result.append(linkobj)
    for obj in linkobj.dupli_group.objects:
        if obj.type == "ARMATURE" or obj.type == "EMPTY":
            proxyname = get_linkedfilename(linkobj) + "/" + obj.name + "_proxy"
            if proxyname not in bpy.data.objects:
                bpy.ops.object.proxy_make(object=obj.name)
                active().name = proxyname
                result.append(active())
                activate(linkobj)


    return result




#ノードツリーのインポート
#現状ノードツリーは同一ディレクトリに置くような運用してないので、使用すべきではない
#def link_nodetree(name):
#    if name not in bpy.data.node_groups:
#        dir = fujiwara_toolbox.conf.assetdir + os.sep + "ノード"

#        _dataname = name
#        _filename = name + ".blend"
#        _directory = dir + os.sep + _filename + os.sep + "NodeTree" + os.sep
#        _filepath = _directory + _filename
#        bpy.ops.wm.link(filepath=_filepath, filename=_dataname,
#        directory=_directory)
    
#    return bpy.data.node_groups[name]

def append_nodetree(name):
    #既にある場合はそれを使用する
    if name in bpy.data.node_groups:
        for ng in bpy.data.node_groups:
            if ng.library is not None:
                #リンクは使わない
                continue
            if name == ng.name:
                return ng

    # なかったのでアペンド
    dir = get_resourcesdir() + "nodes"

    _dataname = name
    _filename = name + ".blend"
    # _directory = dir + os.sep + _filename + os.sep + "NodeTree" + os.sep
    _filepath = dir + os.sep + _filename
    # bpy.ops.wm.append(filepath=_filepath, filename=_dataname, directory=_directory)
    #↑これだと既にリンク済みのものがある場合、それをひっぱってしまう！自前実装！
    with bpy.data.libraries.load(_filepath, link=False, relative=True) as (data_from, data_to):
        if _dataname in data_from.node_groups:
            data_to.node_groups = [_dataname]
    if len(data_to.node_groups) != 0:
        print("appended node_group:"+data_to.node_groups[0].name)
        return data_to.node_groups[0]
    return None


def append_material(name):
    if name not in bpy.data.materials:
        dir = get_resourcesdir() + "materials"

        _dataname = name
        _filename = name + ".blend"
        _directory = dir + os.sep + _filename + os.sep + "Material" + os.sep
        _filepath = _directory + _filename
        bpy.ops.wm.append(filepath=_filepath, filename=_dataname, directory=_directory)

    return bpy.data.materials[name]

def append_particlesetting(name):
    if name not in bpy.data.particles:
        dir =get_resourcesdir() + "パーティクル設定"

        _dataname = name
        _filename = name + ".blend"
        _directory = dir + os.sep + _filename + os.sep + "ParticleSettings" + os.sep
        _filepath = _directory + _filename
        bpy.ops.wm.append(filepath=_filepath, filename=_dataname, directory=_directory)
    
    return bpy.data.particles[name]

def append_group(name):
    dir =get_resourcesdir()

    _dataname = name
    _filename = name + ".blend"
    _directory = dir + os.sep + _filename + os.sep + "Group" + os.sep
    _filepath = _directory + _filename
    bpy.ops.wm.append(filepath=_filepath, filename=_dataname, directory=_directory)

def nodegroup_instance(basetree, group):
    node = basetree.nodes.new("ShaderNodeGroup")
    node.node_tree = group

    return node


def ismesh(obj):
    return obj.type == "MESH"

#リンクオブジェクトならパスを返す
def checkLink(obj):
    if obj.type != "EMPTY":
        return None

    ##リンクされてる側のオブジェクト
    #if obj.is_library_indirect:
    #    return None

    if not obj.is_duplicator:
        return None

    if obj.dupli_group is not None:
        if obj.dupli_group.library is not None:
            if obj.dupli_group.library is not None:
                if obj.dupli_group.library.filepath is not None:
                    return obj.dupli_group.library.filepath

    return None


def group(name, objects=None):
    group = None
    if objects is None:
        objects = get_selected_list()
    for gr in bpy.data.groups:
        if name == gr.name:
            if gr.library is None:
                group = gr
                break
    
    if group is None:
        group = bpy.data.groups.new(name)

    for ob in objects:
        if ob.name not in group.objects:
            group.objects.link(ob)

    return group

def ungroup(name, objects):
    for g in bpy.data.groups:
        if g.name == name and g.library is None:
            for obj in objects:
                if obj.name in g.objects:
                    g.objects.unlink(obj)
            break

#def TransferPose(src, dest):
#    if src.type == "ARMATURE" and dest.type == "ARMATURE":
#        #mode("OBJECT")
#        #activate(src)
#        #mode("POSE")
#        #bpy.ops.pose.select_all(action='SELECT')
#        #bpy.ops.pose.copy()
#        #mode("OBJECT")

#        #activate(dest)
#        #mode("POSE")
#        #bpy.ops.pose.select_all(action='SELECT')
#        #bpy.ops.pose.paste(flipped=False)
#        #bpy.ops.anim.keyframe_insert_menu(type='WholeCharacter')
#        #mode("OBJECT")

#        activate(dest)
#        mode("POSE")
#        bpy.ops.pose.select_all(action='SELECT')

#        count = len(src.pose.bones)
#        for i in range(count):
#            dest.pose.bones[i].location = src.pose.bones[i].location
#            dest.pose.bones[i].rotation_axis_angle =
#            src.pose.bones[i].rotation_axis_angle
#            dest.pose.bones[i].rotation_euler =
#            src.pose.bones[i].rotation_euler
#            dest.pose.bones[i].rotation_quaternion =
#            src.pose.bones[i].rotation_quaternion
#            dest.pose.bones[i].scale = src.pose.bones[i].scale

#        bpy.ops.anim.keyframe_insert_menu(type='WholeCharacter')
#        mode("OBJECT")

def framejump(frameto):
    bpy.ops.screen.frame_jump(end=False)
    bpy.ops.screen.frame_offset(delta=frameto - 1)


def get_freezed_mesh(obj):
    mesh = obj.to_mesh(bpy.context.scene, True, "PREVIEW")
    return mesh

#https://blender.stackexchange.com/questions/38016/stereoscopic-camera-how-to-see-objects-visible-only-from-the-right-and-left-cam
from bpy_extras.object_utils import world_to_camera_view

def checkLocationisinCameraView(loc, camera_extend=False):
    cam = bpy.context.scene.camera
    x, y, z = world_to_camera_view(bpy.context.scene, cam, loc)

    #奥行きでリジェクト
    if z < 0:
        return False

    min = 0.0
    max = 1.0
    if camera_extend:
        min = -1.0
        max = 2.0

    if (min <= x <= max and min <= y <= max):
        return True
    return False

def checkIfIsInCameraView(obj,freeze=True,camera_extend=False):
    #if obj.type != "MESH":
    #    return False
    #cam = bpy.context.scene.camera
    #if freeze:
    #    mesh = get_freezed_mesh(obj)
    #else:
    #    mesh = obj.data
    #for v in mesh.vertices:
    #    x, y, z = world_to_camera_view(bpy.context.scene, cam,
    #    obj.matrix_world * v.co)

    #    min = 0.0
    #    max = 1.0
    #    if camera_extend:
    #        min = -1.0
    #        max = 2.0

    #    if (min <= x <= max and min <= y <= max):
    #        return True
    #return False
    if obj.type != "MESH":
        return False
    if freeze:
        mesh = get_freezed_mesh(obj)
    else:
        mesh = obj.data
    for v in mesh.vertices:
        if checkLocationisinCameraView(obj.matrix_world * v.co):
            return True
    return False

class NodeUtils():
    def __init__(self, node):
        self.node = node
        pass

    def get_socket_by_name(self, sockets, name):
        for socket in sockets:
            if name in socket.name:
                return socket
        return None

    def input(self, name):
        return self.get_socket_by_name(self.node.inputs, name)

    def output(self, name):
        return self.get_socket_by_name(self.node.outputs, name)

    pass

class NodetreeUtils():
    def __init__(self, treeholder):
        self.treeholder = treeholder
        self.tree = None
        self.nodes = None
        self.links = None

        self.posx = 0
        self.posy = 0
        pass

    def activate(self):
        self.treeholder.use_nodes = True
        self.tree = self.treeholder.node_tree
        self.nodes = self.treeholder.node_tree.nodes
        self.links = self.treeholder.node_tree.links

    def deactivate(self):
        self.treeholder.use_nodes = False

    def cleartree(self):
        for node in self.tree.nodes:
            self.tree.nodes.remove(node)

    """
    bpy.context.space_data.tree_type = 'CompositorNodeTree'
    "CompositorNodeRLayers" 入力　レンダーレイヤー
    "CompositorNodeComposite"出力　コンポジット出力
    "CompositorNodeMixRGB"カラーミックス
    "CompositorNodeCurveRGB"トーンカーブ
    "CompositorNodeValToRGB"カラーランプ
    add時の名前はbl_idnameでみれる

    """


    def add(self,type,label):
        node = self.nodes.new(type)
        node.label = label

        node.location = self.posx,self.posy
        self.posx += 200

        return node

    def group_instance(self, group):
        node = None
        if type(self.treeholder) == bpy.types.Scene:
            node = self.add("CompositorNodeGroup","Group")
        else:
            node = self.add("ShaderNodeGroup","Group")

        node.node_tree = group
        return node

    def link(self, output, input):
        self.links.new(output, input)


class VertexGroupUtils():
    #https://blender.stackexchange.com/questions/39653/how-to-set-vertex-weights-from-python
    def __init__(self, obj, groupname):
        self.obj = obj
        self.groupname = groupname
        activate(obj)
        mode("OBJECT")
        pass

    def select_allverts(self):
        bpy.ops.mesh.select_all(action='SELECT')

    def get_group(self,name):
        if name not in self.obj.vertex_groups:
            vg = self.obj.vertex_groups.new(name)
        else:
            vg = self.obj.vertex_groups[name]

        return vg

    # def get_vertice(self,index):
    #     if index < 0:
    #         return None
    #     if index >= len(obj.data.vertices):
    #         return None
    #     return obj.data.vertices[index]

    def get_vertices(self):
        return self.obj.data.vertices

    def set_weight(self,index,group_name, weight):
        vg = self.get_group(group_name)
        vg.add([index],weight,"REPLACE")

def load_img(filepath):
    filename = os.path.basename(filepath)
    if filename not in bpy.data.images:
        bpy.data.images.load(filepath)
    return bpy.data.images[filename]

def get_material(matname):
    if matname not in bpy.data.materials:
        mat = bpy.data.materials.new(name=matname)
        mat.diffuse_color = (1, 1, 1)
    return bpy.data.materials[matname]


class ViewState():
    def store_current_viewstate(self):
        for obj in bpy.data.objects:
            self.viewstates.append([obj,obj.hide,obj.hide_render])

    def __init__(self):
        self.viewstates = []
        self.store_current_viewstate()
        pass

    def restore_viewstate(self):
        for viewstate in self.viewstates:
            obj = viewstate[0]
            obj.hide = viewstate[1]
            obj.hide_render = viewstate[2]

    def delete(self):
        del self.viewstates


class KDTreeUtils():
    #https://docs.blender.org/api/blender_python_api_2_78c_release/mathutils.kdtree.html
    def __init__(self):
        self.items = []
        self.kd = None

    def append_data(self, co, item):
        self.items.append([co,item])

    def construct_kd_tree(self):
        self.kd = kdtree.KDTree(len(self.items))
        for index, value in enumerate(self.items):
            self.kd.insert(value[0], index)
        self.kd.balance()

    def get_item(self, index):
        print(self.items[index])
        return self.items[index][1]

    def find(self, co):
        kddata = self.kd.find(co)
        return self.get_item(kddata[1])

    def find_n(self, co, n):
        kddatas = self.kd.find_n(co, n)
        result = []
        for kddata in kddatas:
            result.append(self.get_item(kddata[1]))
        return result

    def find_range(self, co, radius):
        kddatas = self.kd.find_range(co, radius)
        result = []
        for kddata in kddatas:
            result.append(self.get_item(kddata[1]))
        return result
        
    def finish(self):
        self.kd = kdtree.KDTree(0)


class ShapeKeyUtils():
    def __init__(self, obj):
        self.obj = obj
        if obj.data.shape_keys is None:
            obj.shape_key_add(name="Basis")
        self.shape_keys = obj.data.shape_keys
        self.key_blocks = obj.data.shape_keys.key_blocks

    def get_key_block(self, name):
        if name not in self.key_blocks:
            self.obj.shape_key_add(name=name)
        return self.key_blocks[name]

    def add_key(self, name):
        return self.get_key_block(name)
    
    def find_key(self, name):
        if name not in self.key_blocks:
            return None
        return self.key_blocks[name]

    def set_mute(self, name, state):
        kb = self.get_key_block(name)
        if kb is None:
            return False
        kb.mute = state
        return True

    def set_value(self, name, value):
        kb = self.get_key_block(name)
        if kb is None:
            return False
        kb.value = value
        return True
    
    def set_value_and_key(self, name, value, mute):
        self.set_value(name, value)
        self.set_mute(name, mute)

    def get_key_index(self, name):
        return self.key_blocks.find(name)

    def set_active_key(self, name):
        index = self.get_key_index(name)
        self.obj.active_shape_key_index = index
    


# class OnetimeHandler():
#     func = None
#     def __init__(self, func):
#         self.func = func
#         self.store()
    
#     def execute(self, context):
#         self.func()
#         bpy.app.handlers.scene_update_post.remove(self.execute)

#     def store(self):
#         bpy.app.handlers.scene_update_post.append(self.execute)

# OnetimeHandler_Func = None
# def OnetimeHandler(func):
#     global OnetimeHandler_Func
#     OnetimeHandler_Func = func
#     bpy.app.handlers.scene_update_post.append(OnetimeHandler_Exec)

# def OnetimeHandler_Exec(context):
#     global OnetimeHandler_Func
#     OnetimeHandler_Func()
#     bpy.app.handlers.scene_update_post.remove(OnetimeHandler_Exec)

def get_area(areatype):
    for area in bpy.context.screen.areas:
        if area.type == areatype:
            return area
    return None

def get_override(areatype):
    override = bpy.context.copy()
    override['area'] = get_area(areatype)
    return override

def dummy():
    return



