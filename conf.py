#各コンフィグを一括で記述する
import os

assetdir = r"Z:\WORKSPACE\3D\Asset"



#maintools
maintools_vrexportdir = r"Z:\Unity\VRTest\New Unity Project\Assets"
maintools_vrexportpath = r"Z:\Unity\VRTest\New Unity Project\Assets\VRRoom.blend"

#MarvelousDesigner
MarvelousDesigner_dir = "G:" + os.sep + "MarvelousDesigner" + os.sep

def dummy():
    return


#Addon Preferences
#https://docs.blender.org/api/blender_python_api_2_67_1/bpy.types.AddonPreferences.html

import bpy
from bpy.types import Operator, AddonPreferences
from bpy.props import StringProperty, IntProperty, BoolProperty


print("package:"+__package__)#fuijwara_toolbox
print("name:"+__name__)#fuijwara_toolbox.conf

class ExampleAddonPreferences(AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__

    filepath = StringProperty(
            name="Example File Path",
            subtype='FILE_PATH',
            )
    number = IntProperty(
            name="Example Number",
            default=4,
            )
    boolean = BoolProperty(
            name="Example Boolean",
            default=False,
            )

    def draw(self, context):
        layout = self.layout
        layout.label(text="This is a preferences view for our addon")
        layout.prop(self, "filepath")
        layout.prop(self, "number")
        layout.prop(self, "boolean")


class OBJECT_OT_addon_prefs_example(Operator):
    """Display example preferences"""
    bl_idname = "object.addon_prefs_example"
    bl_label = "Addon Preferences Example"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences

        info = ("Path: %s, Number: %d, Boolean %r" %
                (addon_prefs.filepath, addon_prefs.number, addon_prefs.boolean))

        self.report({'INFO'}, info)
        print(info)

        return {'FINISHED'}





# Registration
def sub_registration():
    # bpy.utils.register_class(OBJECT_OT_addon_prefs_example)
    # bpy.utils.register_class(ExampleAddonPreferences)
    pass

def sub_unregistration():
    # bpy.utils.unregister_class(OBJECT_OT_addon_prefs_example)
    # bpy.utils.unregister_class(ExampleAddonPreferences)
    pass
    

def register():
    bpy.utils.register_module(__name__)
    sub_registration()
    


def unregister():
    bpy.utils.unregister_module(__name__)
    sub_unregistration()


if __name__ == "__main__":
    register()










