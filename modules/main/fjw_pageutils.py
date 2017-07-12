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
from bpy.app.handlers import persistent
import fujiwara_toolbox.conf
from fujiwara_toolbox.fjw import *



bl_info = {
    "name": "FJW PageUtils",
    "description": "ページ構成のためのユーティリティ。",
    "author": "藤原佑介",
    "version": (1, 0),
    "blender": (2, 77, 0),
    "location": "View3D > Object",
    "warning": "", # 警告アイコンとテキストのために使われます
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/Scripts/My_Script",
    "tracker_url": "http://projects.blender.org/tracker/index.php?func=detail&aid=",
    "category": "Object"}







############################################################################################################################
############################################################################################################################
#パネル部分 メインパネル登録
############################################################################################################################
############################################################################################################################

#メインパネル
class PageUtils(bpy.types.Panel):#メインパネル
    bl_label = "ページユーティリティ"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    #bl_category = "Relations"
    bl_category = "Fujiwara Tool Box"


    def draw(self, context):
        filename = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
        dir = os.path.dirname(bpy.data.filepath)

        layout = self.layout
        layout.operator("pageutils.popen")
        layout.operator("pageutils.bgopen")

        if "page" in filename:
            layout.label("ページセットアップ")
            row = layout.row(align=True)
            row.operator("pageutils.deploy_pages")
            layout.label("ページモード")
            #layout.operator("pageutils.refresh")
            row = layout.row(align=True)
            row.operator("pageutils.tocell")
            row.operator("pageutils.tocell_newwindwow")
            row = layout.row(align=True)
            row.prop(bpy.context.scene, "newcell_name",text="")
            row.operator("pageutils.newcell")
            row.operator("pageutils.newcell_copy")
            row = layout.row(align=True)
            col = layout.column(align=True)
            col.label("ページ:" + os.path.splitext(os.path.basename(dir))[0])
            row = col.row(align=True)
            #漫画のとじ順
            row.operator("pageutils.opennextpage")
            row.operator("pageutils.openprevpage")
            
        else:
            layout.label("コマモード")
            row = layout.row(align=True)
            row.label("ページ:" + os.path.splitext(os.path.basename(dir))[0])
            row.label("コマ:" + filename)
            layout = layout.column(align=True)
            layout.operator("pageutils.topage")
            row = layout.row(align=True)
            row.operator("pageutils.opennextcell")
            row.operator("pageutils.openprevcell")


############################################################################################################################
#ユーティリティ関数
############################################################################################################################
def in_localview():
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



def qq(str):
    return '"' + str + '"'


def render(renderpath, komarender=False):
        #レンダリング
        bpy.context.space_data.viewport_shade = 'MATERIAL'
        bpy.context.scene.render.use_simplify = True
        #特にレベル変更はしない？
        bpy.context.scene.render.simplify_subdivision = 2
        bpy.context.scene.render.simplify_subdivision_render = 2
        bpy.context.scene.render.resolution_percentage = 10
        bpy.context.space_data.show_only_render = True

        #高過ぎる奴対策：レンダ解像度をプレビュー解像度にあわせる！
        for obj in bpy.data.objects:
           if obj.type == "MESH":
               bpy.context.scene.objects.active = obj
               for mod in obj.modifiers:
                   if mod.type == "SUBSURF":
                       mod.render_levels = mod.levels

        bpy.context.scene.render.layers["RenderLayer"].use_solid = True
        bpy.context.scene.render.layers["RenderLayer"].use_edge_enhance = False
        bpy.context.scene.render.layers["RenderLayer"].use_ztransp = True
        bpy.context.scene.render.use_raytrace = True
        bpy.context.scene.render.use_textures = True
        bpy.context.scene.render.use_antialiasing = False


        bpy.data.scenes["Scene"].render.filepath = renderpath
        #bpy.ops.render.render(write_still=True)

        bpy.context.space_data.viewport_shade = 'MATERIAL'
        bpy.ops.view3d.viewnumpad(type='CAMERA')
        bpy.ops.render.opengl(write_still=True,view_context=False)

        if komarender:
            #プレビューレンダをバックグラウンドに投げとく
            #↓コレじゃダメ　abspathが特にマズい
            blenderpath = sys.argv[0]
            #scrpath = sys.argv[0] + os.sep + "" + os.sep + "utils" + os.sep +  "pagerender.py"
            scrpath = get_dir(__file__) + "utils" + os.sep +  "pagerender.py"
            cmdstr = qq(blenderpath) + " " + qq(bpy.data.filepath) + " -b " + " -P " + qq(scrpath)
            #cmdstr = qq(cmdstr)
            print("********************")
            print("__file__:"+__file__)
            print("scrpath:"+scrpath)
            print("cmdstr:"+cmdstr)
            print("********************")
            subprocess.Popen(cmdstr)

############################################################################################################################
############################################################################################################################
#各ボタンの実装
############################################################################################################################
############################################################################################################################
'''
class cls(bpy.types.Operator):
    """説明"""
    bl_idname="pageutils.cls"
    bl_label = "ラベル"
    def execute(self,context):
        self.report({"INFO"},"")
        return {"FINISHED"}


'''





############################################################################################################################
#共通
############################################################################################################################
class popen(bpy.types.Operator):
    """親フォルダを開く"""
    bl_idname = "pageutils.popen"
    bl_label = "親フォルダを開く"
    def execute(self,context):
        dir = os.path.dirname(bpy.data.filepath)
        os.system("EXPLORER " + dir)
        return {"FINISHED"}

class bgopen(bpy.types.Operator):
    """background.pngを開きます。"""
    bl_idname = "pageutils.bgopen"
    bl_label = "背景を開く"
    def execute(self,context):
        dir = os.path.dirname(bpy.data.filepath)
        os.system("EXPLORER " + dir + os.sep + "background.png")
        return {"FINISHED"}

############################################################################################################################
#ページモード
############################################################################################################################
class refresh(bpy.types.Operator):
    """コマ画像をスキャンして追加"""
    bl_idname = "pageutils.refresh"
    bl_label = "リフレッシュ"
    def execute(self,context):
        filename = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
        if "page" not in filename:
            return {'CANCELLED'}
        #pageutils/img/を調べる
        dir = os.path.dirname(bpy.data.filepath)
        imgdir = dir + os.sep + "pageutils" + os.sep + "img" + os.sep
        files = os.listdir(imgdir)

        #カメラの縦を1とした時の横方向の比率
        wr = bpy.context.scene.render.resolution_x / bpy.context.scene.render.resolution_y

        #カメラの設定
        camera = bpy.context.scene.camera
        camera.data.type = 'ORTHO'
        camera.data.ortho_scale = 2
        camera.location[0] = 0
        camera.location[1] = -2
        camera.location[2] = 0

        #bpy.context.space_data.lock_camera = False

        yoffset = 0
        for file in files:
            yoffset += 0.3
            #拡張子除去
            fname = file.replace(".png","")

            #存在確認 あったらスキップ
            if fname in bpy.data.objects:
                obj = bpy.data.objects[fname]
                obj.location[0] = 0
                #あえて移動したやつは変更しない
                #obj.location[1] = yoffset
                obj.location[2] = 0
                obj.show_wire = True
                continue

            self.report({"INFO"},file)
            #板追加
            bpy.ops.mesh.primitive_plane_add(radius=1, view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
            obj = bpy.context.scene.objects.active
            obj.name = fname
            obj.show_wire = True

            #UVマップ　変形する前に展開しておくべき
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            #bpy.ops.uv.smart_project()
            bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

            #板を立てる
            obj.rotation_euler[0] = 1.5708
            #上下も反転
            obj.rotation_euler[1] = 3.14159

            #比率をカメラに合わせる
            obj.scale[0] = wr
            #トランスフォームのアプライ
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
            ##サイズをあわせる
            #obj.dimensions = (obj.dimensions[0],obj.dimensions[1], 2)
            #obj.scale[0] = obj.scale[2]
            #比率が1以上＝横長
            if wr > 1:
                obj.scale = (1/wr,1/wr,1/wr)
                #トランスフォームのアプライ
                bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


            obj.rotation_euler[1] = 3.14159
            #トランスフォームのアプライ
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

            #オブジェクトに位置オフセットをつける
            obj.location[0] = 0
            obj.location[1] = yoffset
            obj.location[2] = 0

            #マテリアル関係
            matname = "コマ_" + fname
            mat = bpy.data.materials.new(name=matname)
            mat.use_transparency = True
            mat.alpha = 0
            mat.use_shadeless = True

            obj.data.materials.append(mat)


            #テクスチャ
            tex = bpy.data.textures.new(file, "IMAGE")
            load_img(imgdir+file)

            tex.image = load_img(imgdir+file)

            texture_slot = mat.texture_slots.add()
            texture_slot.texture = tex
            texture_slot.texture = tex
            texture_slot.use_map_alpha = True
            #obj.material_slots[0].material.texture_slots[0].texture = tex

            bpy.context.space_data.viewport_shade = 'MATERIAL'


        return {"FINISHED"}
    def invoke(self, context, event):
#        return context.window_manager.invoke_props_dialog(self)
        return {'RUNNING_MODAL'}



class deploy_pages(bpy.types.Operator):
    """このフォルダをテンプレートとして、上のフォルダ内にある画像をページフォルダとして展開します。\n既存のフォルダは無視されます。png以外はbackground.pngとしてコピーされません。"""
    bl_idname = "pageutils.deploy_pages"
    bl_label = "ページ展開"
    def execute(self,context):
        self_dir = os.path.dirname(bpy.data.filepath)
        parent_dir = os.path.dirname(self_dir)
        #self.report({"INFO"},parent_dir + ":" + self_dir )

        files = os.listdir(parent_dir)

        done = []
        for file in files:
            name, ext = os.path.splitext(file)
            if re.search("bmp|jpg|jpeg|png", ext, re.IGNORECASE) is None:
                continue

            #ファイル名から連番を抽出 _は残しておく(見開きのため)
            name = re.sub(r"(?![0-9_]).","",name)
            #頭と尻に残った_を削除
            name = re.sub(r"^_+","",name)
            name = re.sub(r"_+$","",name)

            destdir = parent_dir + os.sep + name + os.sep

            if os.path.exists(destdir):
                continue

            shutil.copytree(self_dir, destdir)

            #background.pngのコピー
            if re.search("png", ext, re.IGNORECASE) is not None:
                pageimgpath = parent_dir + os.sep + file
                destbgimgpath = destdir + os.sep + "background.png"
                shutil.copy(pageimgpath, destbgimgpath)
            
            done.append(name)

        if len(done) == 0:
            self.report({"INFO"},"新規作成フォルダはありません")
        else:
            self.report({"INFO"},",".join(done)+"を作成しました")
        return {"FINISHED"}

class tocell(bpy.types.Operator):
    """コマへ"""
    bl_idname = "pageutils.tocell"
    bl_label = "コマへ"
    def execute(self,context):
        #self.report({"INFO"},"")
        obj = bpy.context.scene.objects.active
        if obj.type != "MESH":
            self.report({"INFO"},"コマを選択してください")
            return {'CANCELLED'}

        dir = os.path.dirname(bpy.data.filepath)
        cellname = obj.name + ".blend"
        cellpath = dir + os.sep + cellname

        if not os.path.exists(cellpath):
            self.report({"INFO"},"ファイルが存在しません。")
            return {'CANCELLED'}

        #保存
        bpy.ops.wm.save_mainfile()

        obj.hide_render = True

        #レンダリング
        renderpath = dir + os.sep + "page.png"
        render(renderpath)


        #ページファイルを開く
        bpy.ops.wm.open_mainfile(filepath=cellpath)


        return {"FINISHED"}

class tocell_newwindwow(bpy.types.Operator):
    """コマへ"""
    bl_idname = "pageutils.tocell_newwindwow"
    bl_label = "新窓"
    def execute(self,context):
        obj = bpy.context.scene.objects.active
        if obj.type != "MESH":
            self.report({"INFO"},"コマを選択してください")
            return {'CANCELLED'}

        dir = os.path.dirname(bpy.data.filepath)
        cellname = obj.name + ".blend"
        cellpath = dir + os.sep + cellname

        if not os.path.exists(cellpath):
            self.report({"INFO"},"ファイルが存在しません。")
            return {'CANCELLED'}

        #bpy.ops.wm.open_mainfile(filepath=cellpath)
        subprocess.Popen("EXPLORER " + cellpath)

        return {"FINISHED"}

class newcell(bpy.types.Operator):
    """コマを新規作成　未登録のコマが既に存在した場合はそのコマを開く"""
    bl_idname = "pageutils.newcell"
    bl_label = "新規コマ"
    def execute(self,context):
        dir = os.path.dirname(bpy.data.filepath)
        templatepath = get_resourcesdir() + "pageutils" + os.sep + "cell.blend"

        #保存
        bpy.ops.wm.save_mainfile()


        #ファイル名
        blendname = bpy.context.scene.newcell_name
        if blendname == "":
            for n in range(1,20):
                if str(n) not in bpy.data.objects:
                    blendname = str(n) + ".blend"
                    #存在しなければコピーする。
                    if not os.path.exists(dir + os.sep + blendname):
                        shutil.copyfile(templatepath, dir + os.sep + blendname)
                    break
        else:
            blendname += ".blend"
            #存在しなければコピーする。
            if not os.path.exists(dir + os.sep + blendname):
                shutil.copyfile(templatepath, dir + os.sep + blendname)


        #レンダリング
        #レンダ設定
        #renderpath = dir + os.sep + "pageutils" + os.sep + "page.png"
        renderpath = dir + os.sep + "page.png"
        render(renderpath)


        #ページファイルを開く
        bpy.ops.wm.open_mainfile(filepath=dir + os.sep + blendname)

        return {"FINISHED"}

class newcell_copy(bpy.types.Operator):
    """コマをコピーして新規作成　未登録のコマが既に存在した場合はそのコマを開く"""
    bl_idname = "pageutils.newcell_copy"
    bl_label = "コピーして新規コマ"
    def execute(self,context):
        dir = os.path.dirname(bpy.data.filepath)
        #templatepath = r"Z:\Google Drive\C#\VS2015projects\3D作業セットアップ\3D作業セットアップ\bin\Debug\単ページ Z固定 レイ影 簡略化オン.blend"
        templatepath = dir + os.sep + bpy.context.scene.objects.active.name + ".blend"

        #保存
        bpy.ops.wm.save_mainfile()


        #ファイル名
        blendname = bpy.context.scene.newcell_name
        if blendname == "":
            for n in range(1,20):
                if str(n) not in bpy.data.objects:
                    blendname = str(n) + ".blend"
                    #存在しなければコピーする。
                    if not os.path.exists(dir + os.sep + blendname):
                        shutil.copyfile(templatepath, dir + os.sep + blendname)
                    break
        else:
            blendname += ".blend"
            #存在しなければコピーする。
            if not os.path.exists(dir + os.sep + blendname):
                shutil.copyfile(templatepath, dir + os.sep + blendname)


        #レンダリング
        #レンダ設定
        #renderpath = dir + os.sep + "pageutils" + os.sep + "page.png"
        renderpath = dir + os.sep + "page.png"
        render(renderpath)


        #ページファイルを開く
        bpy.ops.wm.open_mainfile(filepath=dir + os.sep + blendname)

        return {"FINISHED"}


class openprevpage(bpy.types.Operator):
    """前のページを開く"""
    bl_idname = "pageutils.openprevpage"
    bl_label = "前のページを開く"
    def execute(self,context):
        selfdir = os.path.dirname(bpy.data.filepath)
        parentdir = os.path.dirname(selfdir)

        self.report({"INFO"},"parentdir:" + parentdir)

        #親フォルダ内のディレクトリリスト
        dirs = getdirs(parentdir)

        targetdir = ""
        for n in range(0, len(dirs)):
            self.report({"INFO"},dirs[n])
            if dirs[n] == os.path.splitext(os.path.basename(selfdir))[0]:
                if n > 0:
                    targetdir = dirs[n - 1]
                break
                    

        target = parentdir + os.sep + targetdir + os.sep + "page.blend"
        if not os.path.exists(target):
            self.report({"INFO"},"ページファイルが存在しません:" + target)
            return {'CANCELLED'}

        #保存
        bpy.ops.wm.save_mainfile()
        #ページファイルを開く
        bpy.ops.wm.open_mainfile(filepath=target)

        #self.report({"INFO"},"")
        return {"FINISHED"}


class opennextpage(bpy.types.Operator):
    """次のページを開く"""
    bl_idname = "pageutils.opennextpage"
    bl_label = "次のページを開く"
    def execute(self,context):
        selfdir = os.path.dirname(bpy.data.filepath)
        parentdir = os.path.dirname(selfdir)

        self.report({"INFO"},"parentdir:" + parentdir)

        #親フォルダ内のディレクトリリスト
        dirs = getdirs(parentdir)

        targetdir = ""
        for n in range(0, len(dirs)):
            self.report({"INFO"},dirs[n])
            if dirs[n] == os.path.splitext(os.path.basename(selfdir))[0]:
                if n < len(dirs) - 1:
                    targetdir = dirs[n + 1]
                break
                    

        target = parentdir + os.sep + targetdir + os.sep + "page.blend"
        if not os.path.exists(target):
            self.report({"INFO"},"ページファイルが存在しません:" + target)
            return {'CANCELLED'}

        #保存
        bpy.ops.wm.save_mainfile()
        #ページファイルを開く
        bpy.ops.wm.open_mainfile(filepath=target)

        #self.report({"INFO"},"")
        return {"FINISHED"}


class openprevcell(bpy.types.Operator):
    """前のコマを開く"""
    bl_idname = "pageutils.openprevcell"
    bl_label = "前のコマ"
    def execute(self,context):
        selfdir = os.path.dirname(bpy.data.filepath)
        filename = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
        #http://uxmilk.jp/8662
        selfcellindex = int(re.sub(r"[a-z]+", "", filename))

        index = selfcellindex-1

        target = selfdir + os.sep + str(index) + ".blend"
        if not os.path.exists(target):
            self.report({"INFO"},"ファイルが存在しません:" + target)
            return {'CANCELLED'}

        #保存
        bpy.ops.wm.save_mainfile()
        #ページファイルを開く
        bpy.ops.wm.open_mainfile(filepath=target)
        return {"FINISHED"}

class opennextcell(bpy.types.Operator):
    """次のコマを開く"""
    bl_idname = "pageutils.opennextcell"
    bl_label = "次のコマ"
    def execute(self,context):
        selfdir = os.path.dirname(bpy.data.filepath)
        filename = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
        #http://uxmilk.jp/8662
        selfcellindex = int(re.sub(r"[a-z]+", "", filename))

        index = selfcellindex+1

        target = selfdir + os.sep + str(index) + ".blend"
        if not os.path.exists(target):
            self.report({"INFO"},"ファイルが存在しません:" + target)
            return {'CANCELLED'}

        #保存
        bpy.ops.wm.save_mainfile()
        #ページファイルを開く
        bpy.ops.wm.open_mainfile(filepath=target)
        return {"FINISHED"}

############################################################################################################################
#コマモード
############################################################################################################################
class topage(bpy.types.Operator):
    """ページファイルを開く"""
    bl_idname = "pageutils.topage"
    bl_label = "page.blendへ"
    def execute(self,context):
        if bpy.data.filepath == "":
            self.report({"INFO"},"一度も保存されていません")
            return {'CANCELLED'}
        #self.report({"INFO"},"")

        #カメラにキー入れる
        globalview()
        mode("OBJECT")
        deselect()
        activate(bpy.data.objects["Camera"])
        bpy.ops.anim.keyframe_insert_menu(type='LocRotScale')


        selfname = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
        dir = os.path.dirname(bpy.data.filepath)
        pname = "page.blend"
        ppath = dir + os.sep + pname

        #ページファイルの存在確認
        if not os.path.exists(ppath):
            self.report({"INFO"},"ページファイルが存在しません")
            return {'CANCELLED'}

        #キーフレーム対策
        #キーフレームオンだと、ツールでカメラ動かした時にトランスフォームが保存されないことがある
        for obj in bpy.data.objects:
            if obj.type == "CAMERA":
                deselect()
                obj.select = True
                try:
                    bpy.ops.anim.keyframe_insert_menu(type='LocRotScale')
                except :
                    pass



        #保存
        bpy.ops.wm.save_mainfile()

        globalview()
        #レンダリング
        #レンダ設定
        renderpath = dir + os.sep + "pageutils" + os.sep + "img" + os.sep + selfname + ".png"
        render(renderpath,True)


        #ページファイルを開く
        bpy.ops.wm.open_mainfile(filepath=ppath)

        return {"FINISHED"}

@persistent
def scene_update_pre(context):
    bpy.app.handlers.scene_update_pre.remove(scene_update_pre)
    bpy.ops.pageutils.refresh()
@persistent
def load_post(context):
    bpy.app.handlers.scene_update_pre.append(scene_update_pre)
    #bpy.ops.pageutils.refresh()

@persistent
def save_pre(context):
    #カメラにキー入らんでどうしようもないからこれでいれる！！！
    #カメラにキー入れる
    if bpy.context.scene.tool_settings.use_keyframe_insert_auto:
        if bpy.context.scene.camera != None:
            if not in_localview():
                current = active()
                current_mode = "OBJECT"
                if current  != None:
                    current_mode = active().mode
                mode("OBJECT")
                selection = get_selected_list()
                deselect()
                activate(bpy.context.scene.camera)
                bpy.ops.anim.keyframe_insert_menu(type='LocRotScale')
                if current  != None:
                    deselect()
                    select(selection)
                    activate(current)
                    mode(current_mode)



############################################################################################################################
############################################################################################################################
#オペレータークラスやUIボタンの登録
############################################################################################################################
############################################################################################################################
def sub_registration():
    bpy.app.handlers.load_post.append(load_post)
    bpy.types.Scene.newcell_name = bpy.props.StringProperty()
    bpy.app.handlers.save_pre.append(save_pre)
    pass

def sub_unregistration():
    pass


def register():    #登録
    bpy.utils.register_module(__name__)
    sub_registration()

def unregister():    #登録解除
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()