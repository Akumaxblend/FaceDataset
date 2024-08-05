import bpy
import json
import sys
import os

# # We get the active object we want to retrieve shape keys from
# obj = bpy.data.objects["Head"]
# sk = obj.data.shape_keys.key_blocks

# # We set up the json content and file directory
# json_data = []

# # We write the json content for each shape key, for each frame 
# for i in sk:
#     if i.value != 0:
#         json_data.append(
#         {'name': i.name, 
#         'value': i.value},
#         )
# Argument parsing : we retrieve the output path passed by user. The index is 1 because index 0 is used by the seed when the script is chained with random_face_renderer.py
# argv = sys.argv
# argv = argv[argv.index("--") + 1:]
# seed = int(argv[0])
# directory = argv[1]

# out_dir = directory+f'/{seed:06}'+"/ground_truth/"
# current_frame = bpy.data.scenes[0].frame_current
# os.makedirs(out_dir, exist_ok=True)

# # We save the file in a given directory
# with open(out_dir+"blendshapes.json", "w") as file :
#     json.dump(json_data, file, indent = 4)

def export_shape_keys(obj, seed, directory):
	# We get the active object we want to retrieve shape keys from
	sk = obj.data.shape_keys.key_blocks
	# We set up the json content and file directory
	json_data = []
	# We write the json content for each shape key, for each frame 
	for i in sk:
	    if i.value != 0:
	        json_data.append(
	        {'name': i.name, 
	        'value': i.value},
	        )
    out_dir = directory+f'/{seed:06}'+"/ground_truth/"+''
	current_frame = bpy.data.scenes[0].frame_current
	os.makedirs(out_dir, exist_ok=True)

	# We save the file in a given directory
	with open(out_dir+"blendshapes.json", "w") as file :
	    json.dump(json_data, file, indent = 4)

