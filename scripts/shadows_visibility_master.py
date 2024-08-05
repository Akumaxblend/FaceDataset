import bpy
import random

def gamble_shadows_visibility(percentage_show, collection_name):
    if random.randint(0, 100) <= percentage_show:
        bpy.data.collections[collection_name].hide_render = False
    else: bpy.data.collections[collection_name].hide_render = True
    
gamble_shadows_visibility(50, "shadows")