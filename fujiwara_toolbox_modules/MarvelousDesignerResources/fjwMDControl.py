# exec('import fjwMDControl\nfjwMDControl.run(mdsa)')

from PythonQt import QtCore, QtGui, MarvelousDesignerAPI
from PythonQt.MarvelousDesignerAPI import *
import sys

def log(line):
    sys.stdout.write(line+"\n")
    sys.stdout.flush()

class MD():
    def __init__(self, mdsa):
        self.mdsa = mdsa
    
    def simulate(self, abc_path, cloth_path, output_path):
        mdsa = self.mdsa

        mdsa.clear_console()
        mdsa.initialize() 
        # unit = "none", fps = 30
        mdsa.set_open_option("m", 30) 
        # unit = "none", fps = 30, unified = False, thin = True, weld = False
        mdsa.set_save_option("m", 30, False)

        mdsa.set_alembic_format_type(True)

        mdsa.set_garment_file_path(cloth_path)
        mdsa.set_avatar_file_path(abc_path)
        mdsa.set_animation_file_path(abc_path)
        # obj_type = 0, simulation_quality = 0, simulation_delay_time = 5000, process_simulation = True
        mdsa.set_simulation_options(0, 0, 0) 
        mdsa.set_save_file_path(output_path)
        mdsa.set_auto_save(True)
        mdsa.process()

def run(mdsa):
    mddata = MD(mdsa)
    sys.path.append(r"C:\mdtemp")
    import mdcode
    mdcode.run()
    # mddata.simulate(r"C:\Users\ysksa\Desktop\test\MDtest\data\avatar.abc", r"C:\Users\ysksa\Desktop\test\MDtest\data\cloth.zpac", r"C:\Users\ysksa\Desktop\test\MDtest\data\result.obj")
