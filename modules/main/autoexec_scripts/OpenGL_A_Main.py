blendname = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
renderdir = os.path.dirname(bpy.data.filepath) + os.sep + "render" + os.sep
renderpath = renderdir + blendname +"_layerAll_OpenGL_A_Main" + ".png"
bpy.context.scene.render.filepath = renderpath
bpy.ops.render.opengl(view_context=True,write_still=True)
