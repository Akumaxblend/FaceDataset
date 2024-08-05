import bpy
import bpy_extras
from bpy import context
import bmesh
import numpy
import sys
import os

# Geometry declarations
obj_name = "Head"
camera_name = "Camera"
obj = bpy.data.objects.get(obj_name)
camera = bpy.data.objects.get(camera_name)
scene = bpy.data.scenes[0]
resolution_x = scene.render.resolution_x
resolution_y = scene.render.resolution_y

frames_screen = []
frames_world = []
points_screen = []
points_world = []

# Export declarations
json_data = []
fstart = scene.frame_start
fend = scene.frame_end

def get_modified_mesh(ob, frame, cage=False):
    bpy.context.scene.frame_set(frame)
    bm = bmesh.new()
    bm.from_object(
            ob,
            context.evaluated_depsgraph_get(),
            cage=cage,
            )
    #bm.transform(ob.matrix_world)
    me = bpy.data.meshes.new("Deformed")
    bm.to_mesh(me)
    return me

def get_screen_coordinates(camera, world_coords):
    
    scene = bpy.data.scenes[0]
    coords = bpy_extras.object_utils.world_to_camera_view(scene, camera, world_coords)
    # Translation to standard image coordinates with (0,0) at the top left corner 
    coords.y = 1 - coords.y
    # Absolute screen coordinates 
    coords.x *= resolution_x
    coords.y *= resolution_y
    return (coords.x, coords.y)

# In order to export only the visible vertices, not the hidden ones. Currently useless and not working. 
def is_vertex_visible(obj, world_coords, camera):
#    # Ray cast from the camera to the vertex
#    direction = (world_coords - camera.matrix_world.translation).normalized()
#    result, location, normal, index, object, matrix = bpy.context.scene.ray_cast(
#        bpy.context.view_layer.depsgraph,
#        camera.matrix_world.translation, 
#        direction,
#    )
#    print(direction, result)
#    # Check if the hit location is the same as the vertex location (within a tolerance)
#    if result and (world_coords - location).length < 0.0001:
#        #print(location ," true")
#        return True
#    #print(location)
#    return False
    return True

print('###   Exporting vertices positions   ###')

current_frame = bpy.data.scenes[0].frame_current # Will be used later on to set the output directory

for i in range (current_frame, current_frame + 1):
    tmp = get_modified_mesh(obj, i)
    for vert in tmp.vertices:
        world_coords = obj.matrix_world @ vert.co
        if is_vertex_visible(obj, world_coords, camera):
            screen_coords = get_screen_coordinates(camera, world_coords)
            points_screen.append(screen_coords)
            points_world.append(world_coords)
    frames_screen.append(points_screen)
    frames_world.append(points_world)
    points_screen = []
    points_world = []

# Argument parsing : we retrieve the output path passed by user. The index is 1 because index 0 is used by the seed when the script is chained with random_face_renderer.py
argv = sys.argv
argv = argv[argv.index("--") + 1:]
directory = argv[1]

out_dir = directory+f'{current_frame:06}'+"/ground_truth/"
os.makedirs(out_dir, exist_ok=True)

with open(out_dir+"vertices_positions.npy", 'wb') as file :
    numpy.savez(file, screen_positions=frames_screen, world_positions=frames_world)
