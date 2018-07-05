import bpy
import sys
import inspect
import os.path
import os
import bmesh
import datetime
import math
import subprocess
import shutil
import time
import copy
import random
from collections import OrderedDict
from mathutils import *

from .main import *



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

