# -*- coding: utf-8 -*-

# 同階層ファイルのオートロードスクリプト
# http://flame-blaze.net/archives/4963

import glob
import sys
import os.path
import importlib
import re

self_path = os.path.dirname(os.path.abspath(__file__))

def loadModule():
    mod_self = sys.modules[__name__]

    mod_paths = glob.glob(os.path.join(self_path, '*.py'))
    for mod_path in mod_paths:
        mod_name = os.path.splitext(os.path.basename(mod_path))[0]
        if "__init__" in mod_name:
            continue
        mod = importlib.import_module(__name__+ "." + mod_name)
        for m in mod.__dict__.keys():
            if m in ['__builtins__', '__doc__', '__file__', '__name__', '__package__']:
                continue
            mod_self.__dict__[m] = mod.__dict__[m]

loadModule()

