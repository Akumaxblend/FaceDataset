import bpy
import random
import sys
from mathutils import Vector
import numpy as np
import os

dir = "/s/prods/research/io/in/from_prod/face_dataset/scripts/"
if not dir in sys.path:
    sys.path.append(dir) # So blender looks up this directory while importing next scripts
from vertices_positions_single_image import export_all_ground_truth

MAX_FRAME = 1000000
obj       = bpy.data.objects["Head"]
cam       = bpy.data.cameras["Camera"]
eye_left  = bpy.data.objects["eye_left_location_controller"]
eye_right = bpy.data.objects["eye_right_location_controller"]

textures_base_path = "/s/prods/mvg/_source_global/faceCapture/char/mpcHumanFacialRig_modelv023_rigv17/textures/"
color_maps_name = "4k/COL_<UDIM>.exr"
bump_maps_name = "4k/BUMP_<UDIM>.exr"

# Declaration of mouth related shape keys
sk_initial_jaw      = ["JawOpen80"]
sk_mouth_corners    = ["lipCornerPuller", "Dimpler", "PuckerUpper", "PuckerLower",  "lipStretcher", "LipCornerDepressor", "SharpLipPuller"]
sk_lip_eversion     = ["lipFunnelerUpper", "lipFunnelerLower" ]
sk_tooth_show       = ["UpperLidRaiser", "LowerLipDepressor"]
sk_chin_muzzle      = ["ChinRaiser50", "ChinRaiserLower", "mouthPressorUpper", "mouthPressorLower"]
sk_sealing_lips     = ["LipPressor", "lipTightener"]
sk_inflation_muzzle = ["lipPuff"]
sk_nose_region      = ["noseWrinkler", "nasolabialDeepener", "nostrilCompressor", "nostrilDilator", "noseDepressor"]
sk_inflation_cheek  = ["cheekPuff", "CheekSuck"]
sk_jaw_motion       = ["jawOpen_lipsToward", "ljawSlide", "rjawSlide", "jawThrust"]
sk_lip_line         = ["mouthUp", "mouthDown"] 

sk_mouth_global     = [sk_initial_jaw, sk_mouth_corners, sk_lip_eversion, sk_tooth_show, sk_chin_muzzle, sk_sealing_lips, 
                       sk_inflation_muzzle, sk_nose_region, sk_inflation_cheek, sk_jaw_motion, sk_lip_line]

# Declaration of eyes related shape keys
sk_eye_blink        = ["eyeClosed", "LidPull"]
sk_eye_direction    = ["eyeUp", "eyeDown", "eyeLeft", "eyeRight"]
sk_eye_widening     = ["upperLidRaiser", "upperLidDown"]
sk_eye_compression  = ["lidTightener", "cheekRaiser"] 
sk_brow_pass_1      = ["browLowerer", "BrowSqueeze", "OuterBrowRaiser", "Procerus"]

sk_eyes_global      = [sk_eye_blink, sk_eye_direction, sk_eye_widening, sk_eye_compression, sk_brow_pass_1]
 
# Sets current frame to a chosen / random one (seed=-1) on every scene
def set_frame(seed):
    scenes = bpy.data.scenes
    if (seed == -1):
        frame = random.randint(1, MAX_FRAME)
    else:   
        frame = seed
    for s in scenes:
        s.frame_set(frame)
    return frame

# Resets every blendshape to 0
def reset_shape_keys(obj): 
    shape_keys = obj.data.shape_keys.key_blocks
    for s in shape_keys:
        s.value = 0 

# Sets shapes_nb random shape keys to a random value between min_value and max_value on the "obj" object defined above
def randomize_shape_key(blendshape_group, min_value, max_value, shapes_nb):
    shape_keys = obj.data.shape_keys.key_blocks
    picked_group = [] # To store already picked group
    for i in range (0, shapes_nb):
        is_key_found = False # Will check that a blendshape has been found
        try_limit = 10
        if len(picked_group) == len(blendshape_group): # If we already picked a blendshape in everygroup, exit
            break
        else:
            random_group = random.choice(blendshape_group)
            while random_group in picked_group: # We only pick 1 blendshape for each group
                random_group = random.choice(blendshape_group)
            picked_group.append(random_group)
            random_blendshape = random.choice(random_group)
            while (not is_key_found and try_limit > 0): # We only stop if a key is found or that we tried too many times
                for s in shape_keys:
                    if (random_blendshape.lower() in s.name.lower() and "_" not in s.name): 
                        if ("l" + random_blendshape.lower() in s.name.lower() or "r" + random_blendshape.lower() in s.name.lower()): # In case we have a symmetrical blendshape 
                            blendshape_name = s.name
                            if random.randint(1, 2) % 2 == 0: # If random is even, we activate the right side. Else, we activate the left side. 
                                new_blendshape_name = blendshape_name.replace(blendshape_name[:1], "r", 1)
                                shape_keys[new_blendshape_name].value = random.randint(min_value*100, max_value*100) / 100
                            else:
                                new_blendshape_name = blendshape_name.replace(blendshape_name[:1], "l", 1)
                                shape_keys[new_blendshape_name].value = random.randint(min_value*100, max_value*100) / 100
                            print("Blendshape found : "+ new_blendshape_name)
                        else:
                            s.value = random.randint(min_value*100, max_value*100) / 100
                            print("Blendshape found : "+ s.name)
                        is_key_found = True
                        break
                try_limit -= 1
                random_blendshape = random.choice(random_group)   
            if (try_limit == 0):
                print("Unable to find : "+ random_blendshape)

# Sets ouput paths for every mask and 3D render output
def set_output_path(path, frame_number):
    scene = bpy.data.scenes["Beauty"]
    path = path + f'/{frame_number:06}'
    bpy.context.scene.render.filepath = path + "/beauty_render_" + f'{frame_number:06}'
    scene.node_tree.nodes["alpha_mask"].base_path = path
    scene.node_tree.nodes["hair_mask"].base_path = path
    scene.node_tree.nodes["beard_mask"].base_path = path
    scene.node_tree.nodes["clothes_mask"].base_path = path
    scene.node_tree.nodes["edges_clothes"].base_path = path
    scene.node_tree.nodes["eyebrows_mask"].base_path = path
    scene.node_tree.nodes["depth_mask"].base_path = path
    scene.node_tree.nodes["depth_map"].base_path = path + "/ground_truth"

# Returns an object matching a string, used to return a copied object for instance
def get_object_matching_string(str, scene):
    for o in scene.objects:
        if str in o.name:
            return o

# Setups the masks scene with correct modifiers and materials
def setup_masks_scene():
    
    # If a copied scene already exists, we delete it 
    if len(bpy.data.scenes) > 1:
        bpy.context.window.scene = bpy.data.scenes[1]
        bpy.ops.scene.delete()
        
    # We copy the scene and rename it 
    bpy.ops.scene.new(type='FULL_COPY')
    bpy.data.scenes[1].name = 'Masks'
    
    # We locate the copy Head object
    obj_copy = get_object_matching_string('Head', bpy.data.scenes['Masks'])
    obj_copy.active_material = bpy.data.materials['mask']
    
    # We locate the copy Head object
    eyer_copy = get_object_matching_string('eye_right.', bpy.data.scenes['Masks'])
    eyer_copy.active_material = bpy.data.materials['mask']
    eyel_copy = get_object_matching_string('eye_left.', bpy.data.scenes['Masks'])
    eyel_copy.active_material = bpy.data.materials['mask']
    
    
    
    # Needed modifiers to create the masks
    modifier = obj_copy.modifiers.new(name = 'cloth_modifier', type='NODES')
    modifier.node_group = bpy.data.node_groups['cloth_mask']
    modifier = obj_copy.modifiers.new(name = 'vertex_modifier', type='NODES')
    modifier.node_group = bpy.data.node_groups['vertex_group_transfer']
    
    # We update the render layers output
    bpy.data.scenes['Beauty'].node_tree.nodes['Render Layers'].scene = bpy.data.scenes['Masks']
    # We get back to the Beauty layer so we can render it
    bpy.context.window.scene = bpy.data.scenes['Beauty']
    
def gamble_shadows_visibility(percentage_show, collection_name):
    if random.randint(0, 100) <= percentage_show:
        bpy.data.collections[collection_name].hide_render = False
    else: bpy.data.collections[collection_name].hide_render = True

def select_vertices_from_group(group_name, object):
    for v in object.data.vertices:
        if obj.vertex_groups[group_name].weight(v.index) == 1:
            v.select = True
            
def mean_location_from_group(group_name, object):
    vertices_locations = []
    for v in object.data.vertices:
        if obj.vertex_groups[group_name].weight(v.index) == 1:
            vertices_locations.append (object.matrix_world @ v.co)
    return sum([l for l in vertices_locations], Vector()) / len(vertices_locations)

def random_vector_normalized(dimension, adjustment):
    d = dimension
    inv_d = 1.0 / d
    for i in range(0,d):
        gauss = np.random.normal(size=d)
        length = np.linalg.norm(gauss)
        if length == 0.0:
            vec = gauss
        else:
            r = np.random.rand() ** inv_d
            vec = np.multiply(gauss, r / length)
    return vec * adjustment

def change_face(dimension, adjustment, obj):
    sk = obj.data.shape_keys.key_blocks

    vec = random_vector_normalized(dimension, adjustment)
    for i in range (0,100):
        name = f'id{i:03}_'
        sk[name].value = vec[i]

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
    print(("textures loaded: "+bump_map.image.filepath))

def set_camera_amplitude(camera_rotation_master_name, axis, amplitude):
    master = bpy.data.objects[camera_rotation_master_name]
    action = master.animation_data.action
    fc = action.fcurves[axis]

    offseted_amplitude = amplitude / 25.7 # 180 degrees correspond to an amplitude of 7 in the fcurves modifiers
    fc.modifiers[0].strength = offseted_amplitude

def set_world_rotation(world_name, amplitude_x, amplitude_y, amplitude_z, frame):
    material = bpy.data.worlds[world_name]
    node = material.node_tree.nodes["Mapping"]
    sockets = node.inputs['Rotation'].default_value

    offseted_amplitude_x = amplitude_x / 25.7 # 180 degrees correspond to an amplitude of 7 in the fcurves modifiers
    offseted_amplitude_y = amplitude_y / 25.7 
    offseted_amplitude_z = amplitude_z / 25.7 

    sockets[0] = np.sin(3 * frame) * offseted_amplitude_x * 3.1415 / 180
    sockets[1] = np.sin(7 * frame) * offseted_amplitude_y * 3.1415 / 180
    sockets[2] = np.sin(11 * frame) * offseted_amplitude_z * 3.1415 / 180


######################################### EXECUTION PART ###################################################

# Argument parsing
argv = sys.argv
argv = argv[argv.index("--") + 1:]
seed = int(argv[0])
output_path = argv[1]
min_fov = int(argv[2])
max_fov = int(argv[3])
batch = int(argv[4])
model_range = float(argv[5])
offset_x = float(argv[6])
offset_y = float(argv[7])
offset_z = float(argv[8])
blendshapes_range_min = float (argv[9])
blendshapes_range_max = float (argv[10])
camera_amplitude_x = int(argv[11])
camera_amplitude_y = int(argv[12])
camera_amplitude_z = int(argv[13])
world_amplitude_x = int(argv[14])
world_amplitude_y = int(argv[15])
world_amplitude_z = int(argv[16])

obj.matrix_world.translation += Vector((offset_x, offset_y, offset_z))
set_camera_amplitude("camera_rotation_master", 0, camera_amplitude_x)
set_camera_amplitude("camera_rotation_master", 1, camera_amplitude_y)
set_camera_amplitude("camera_rotation_master", 2, camera_amplitude_z)

for i in range(seed, seed + batch):
    # Scene setup
    random_frame = set_frame(i)
    random.seed(i)
    np.random.seed(i) # 2 seeds are defined here, one for the random module, another one for numpy.random module
    set_world_rotation("World", world_amplitude_x, world_amplitude_y, world_amplitude_z, i)
    reset_shape_keys(obj)
    change_face(100, model_range, obj)
    randomize_shape_key(sk_mouth_global, blendshapes_range_min, blendshapes_range_max, 5)
    randomize_shape_key(sk_eyes_global, blendshapes_range_min, blendshapes_range_max, 3)
    eye_left.location = mean_location_from_group("eye_left", obj)
    eye_right.location = mean_location_from_group("eye_right", obj)
    set_output_path(output_path, random_frame)
    gamble_shadows_visibility(30, "shadows") # Shadow percentage. Inaccurate because of the HDRI rotation
    cam.lens = random.randrange(min_fov, max_fov+1)
    setup_masks_scene()
    #set_textures("color_shader", random_folder(textures_base_path)) # A reactiver si on reçoit les textures un jour :)

    print('###   3D rendering frame '+str(random_frame)+'   ###')
    bpy.ops.render.render(write_still=True)

    export_all_ground_truth(obj, i, output_path)
