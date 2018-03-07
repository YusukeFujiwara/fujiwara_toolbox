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
import inspect

# import bpy.mathutils.Vector as Vector
from mathutils import Vector

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

from fujiwara_toolbox.modules.main.submodules.json_tools import JsonTools

# 仕様考え直し
class TextureWorkingTools():
    @classmethod
    def make_texture_workingfile(cls, obj, exportname):
        """
            テクスチャ作業用の作業ファイルを作る。
            
        arguments:
            オブジェクト
            
        outputs:
            最終的にどうなるのか
                fjw_work/元blendファイル名/ユニークID/作業タイプ.blend
                metadata.json
                    textures/元blendファイル/ID/作業タイプ
                    テクスチャ出力先
            この後
                選択オブジェクトとターゲット以外削除なりなんなりする
            
        
        """
        
        # 前準備
        #     別ファイルに移動するから現状を保存する
        bpy.ops.wm.save_as_mainfile()
        # 必要な情報
        #     元ファイルパス
        basefilepath = bpy.data.filepath

        dirname = os.path.dirname(basefilepath)
        basename = os.path.basename(basefilepath)
        name, ext = os.path.splitext(basename)

        fjw_id = fjw.id(obj)

        fjw_dir = dirname + os.sep + "fjw" + os.sep + name + os.sep + fjw_id
        os.makedirs(fjw_dir)
        texture_export_dir = dirname + os.sep + "textures" + os.sep + name + os.sep + fjw_id
        os.makedirs(texture_export_dir)

        if ".blend" not in exportname:
            exportname = exportname + ".blend"
        expname, expext = os.path.splitext(exportname)
        fjw_path = fjw_dir + os.sep + expname
        #作業ファイル保存
        bpy.ops.wm.save_as_mainfile(filepath=fjw_path)
        

        #json保存
        #相対パス化
        json = JsonTools()
        json.val("basepath", bpy.path.relpath(basefilepath))
        json.val("texture_export_dir", bpy.path.relpath(texture_export_dir))
        jsonpath = fjw_dir + os.sep + expname + ".json"
        json.save(jsonpath)
        return json


    @classmethod
    def fjw_texture_export_uvmap(cls, obj):
        """
            アクティブオブジェクトのアクティブUVマップ書き出してテクスチャ作業をする。
            
        arguments:
            オブジェクト
            
        outputs:
            アクティブUV画像を書き出し
            作業ディレクトリ/textures/uv名.png
            jsonにテクスチャパスを保存する？いらないかも
            
        
        """
        
        if obj.type != "MESH":
            return

        fjw.activate(obj)

        # UVをチェック
        if len(obj.data.uv_layers) == 0:
            # なければUVを作成
            fjw.mode("EDIT")
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.smart_project()

        uv_layer = obj.data.uv_layers.active

        # テクスチャ作業ファイル作成
        json = cls.make_texture_workingfile(obj, "uv_map")

        dirname = os.path.dirname(bpy.data.filepath)
        basename = os.path.basename(bpy.data.filepath)
        name, ext = os.path.splitext(basename)
        print("filepath:%s"%bpy.data.filepath)

        # UVテクスチャ出力先
        uv_dir = dirname + os.sep + "textures"
        os.makedirs(uv_dir)
        uv_path = uv_dir + os.sep + name + ".png"
        print("uv_path:%s"%uv_path)
        bpy.ops.uv.export_layout(filepath=uv_path, check_existing=False, export_all=False, modified=False, mode='PNG', size=(1024, 1024), opacity=0.25, tessellated=False)

        # 全オブジェクトを削除してUVテクスチャの読み込み
        fjw.delete(bpy.context.scene.objects)
        bpy.ops.mesh.primitive_plane_add(radius=1, calc_uvs=True, view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        plane = fjw.active()

        mat = bpy.data.materials.new("uv_map")
        mat.use_shadeless = True
        tslot = mat.texture_slots.add()
        tex = bpy.data.textures.new("uv_map", "IMAGE")
        tex.image = bpy.data.images.load(uv_path)
        tslot.texture = tex

        plane.data.materials.append(mat)
        bpy.ops.wm.save_as_mainfile()

    def bake_selection_to_active(self):
        """
        選択オブジェクトをアクティブにベイクして、マテリアルに割当てる。
        """