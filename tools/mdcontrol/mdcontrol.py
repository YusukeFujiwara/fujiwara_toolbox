import sys
import os

args = sys.argv

selfpath = args[0]
selfdir = os.path.dirname(selfpath)

import mdlackey
mdmacro = mdlackey.MDMacro



def sim(avatar_path, animation_path, garment_path, result_path):
    mdmacro.new_file()
    if ".obj" in avatar_path:
        mdmacro.open_avatar(avatar_path)
        mdmacro.wait(0.5)
        mdmacro.add_mdd(animation_path)
        # mdmacro.wait(0.5)

    if ".abc" in avatar_path:
        mdmacro.open_avatar_abc(avatar_path)
        # mdmacro.wait(2)

    mdmacro.add_garment(garment_path)
    mdmacro.simulate(4)
    mdmacro.select_all()
    # mdmacro.export_obj(result_path)
    mdmacro.export_abc(result_path)
    os.remove(avatar_path)
    os.remove(animation_path)
    os.remove(garment_path)

sim(args[1],args[2],args[3],args[4])

print("end")
