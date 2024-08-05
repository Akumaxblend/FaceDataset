import bpy
import os
import random

textures_base_path = "/s/prods/mvg/_source_global/faceCapture/char/mpcHumanFacialRig_modelv023_rigv17/textures/"
color_maps_name = "4k/COL_<UDIM>.exr"
bump_maps_name = "4k/BUMP_<UDIM>.exr"

def random_folder(parent_directory):
    subfolders = [ f.path for f in os.scandir(parent_directory) if f.is_dir() ]
    return random.choice(subfolders)

def set_textures(material_name, textures_base_path):
    material = bpy.data.materials[material_name]
    node_tree = material.node_tree
    color_map = node_tree.nodes['color_map']
    bump_map = node_tree.nodes['bump_map']
    
    color_map.image.filepath = os.path.join(textures_base_path, color_maps_name)
    bump_map.image.filepath = os.path.join(textures_base_path, bump_maps_name)
    print(bump_map.image.filepath)
    
set_textures("color_shader", random_folder(textures_base_path))