import sys
import os

args = sys.argv

selfpath = args[0]
selfdir = os.path.dirname(selfpath)

import mdlackey
mdmacro = mdlackey.MDMacro



def sim(avatar_path, animation_path, garment_path, result_path):
    mdmacro.new_file()
    mdmacro.open_avatar(avatar_path)
    mdmacro.add_garment(garment_path)
    mdmacro.wait(0.5)
    mdmacro.add_mdd(animation_path)
    mdmacro.wait(0.5)
    mdmacro.simulate(10)
    mdmacro.select_all()
    mdmacro.export_obj(result_path)

sim(args[1],args[2],args[3],args[4])

print("end")
