import bpy
import bpy_extras
from bpy import context
import bmesh
import numpy
import sys
import os
import json

scene = bpy.data.scenes[0]
resolution_x = scene.render.resolution_x
resolution_y = scene.render.resolution_y

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

def is_vertex_visible(obj, world_coords, camera):
   # Ray cast from the vertex to the camera
    direction = (camera.matrix_world.translation - world_coords).normalized()
    result, location, normal, index, object, matrix = bpy.context.scene.ray_cast( 
       bpy.context.view_layer.depsgraph,
       world_coords + 0.00001 * direction, 
       direction,
       distance=10
    )
    if result: return False
    else:      return True

def export_rotation(obj_name, path):
    to_export = bpy.data.objects[obj_name]
    rotation = to_export.rotation_euler
    with open(path, 'wb') as file :
        try:
            numpy.save(file, rotation)
        except Exception as e:
            print("ERROR HERE: {}".format(e))

def export_location(obj_name, path):
    to_export = bpy.data.objects[obj_name]
    location = to_export.matrix_world.translation
    with open(path, 'wb') as file :
        try:
            numpy.save(file, location)
        except Exception as e:
            print("ERROR HERE: {}".format(e))

def export_fov(obj_name, path):
    to_export = bpy.data.cameras[obj_name]
    fov = to_export.lens
    with open(path+"camera_fov_mm.npy", 'wb') as file :
        try:
            numpy.save(file, fov)
        except Exception as e:
            print("ERROR HERE: {}".format(e))

def export_camera_gt(camera_name, path):
    to_export_obj = bpy.data.objects[camera_name]
    to_export_cam = bpy.data.cameras[camera_name]
    fov = to_export_cam.lens
    location = to_export_obj.matrix_world.translation
    sensor_width = to_export_cam.sensor_width
    sensor_height = to_export_cam.sensor_height
    view_frame = [v.to_tuple() for v in to_export_cam.view_frame(scene=bpy.data.scenes[0])[:3]]
    json_data = []
    json_data.append({"fov":fov, "location":[location[0],location[1],location[2]], "sensor_size":[sensor_width, sensor_height], "view_frame":view_frame})
    with open(path, "w") as file :
        json.dump(json_data, file, indent = 4)
    print(fov)

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
    out_dir = directory+f'/{seed:06}'+"/ground_truth/"
    current_frame = bpy.data.scenes[0].frame_current
    os.makedirs(out_dir, exist_ok=True)

    # We save the file in a given directory
    with open(out_dir+"blendshapes.json", "w") as file :
        json.dump(json_data, file, indent = 4)

def export_vertices_weight(obj, group_name, out_dir):
    verts = obj.data.vertices
    weighted_indices = []
    for v in verts:
        weighted_indices.append(obj.vertex_groups[group_name].weight(v.index))
    with open(out_dir+"monkey_face_vertices.npy", 'wb') as file :
        numpy.save(file, weighted_indices)

def export_all_ground_truth(obj, seed, directory):

    # Geometry declarations
    eye_name = "eye_right"
    camera_name = "Camera"
    camera = bpy.data.objects.get(camera_name)

    frames_screen = []
    frames_world = []
    points_screen = []
    points_world = []
    visible_points = []

    # Export declarations
    json_data = []
    fstart = scene.frame_start
    fend = scene.frame_end

    print('###   Exporting vertices positions   ###')
    current_frame = bpy.data.scenes[0].frame_current # Will be used later on to set the output directory
    for i in range (current_frame, current_frame + 1):
        tmp = get_modified_mesh(obj, i)
        for vert in tmp.vertices:
            world_coords = obj.matrix_world @ vert.co
            camera_relative_coords = camera.matrix_world.normalized().inverted() @ world_coords
            visible_points.append(is_vertex_visible(obj, world_coords, camera))
            screen_coords = get_screen_coordinates(camera, world_coords)
            points_screen.append(screen_coords)
            points_world.append(camera_relative_coords)
        frames_screen.append(points_screen)
        frames_world.append(points_world)
        points_screen = []
        points_world = []

    out_dir = directory+f'/{seed:06}'+"/ground_truth/"
    os.makedirs(out_dir, exist_ok=True)

    with open(out_dir+"vertices_positions.npy", 'wb') as file :
        numpy.savez(file, screen_positions=frames_screen, world_positions=frames_world)

    with open(out_dir+"vertices_visibility.npy", 'wb') as file :
        numpy.save(file, visible_points)

    print('###   Exporting eyes rotation   ###')
    export_rotation(eye_name, out_dir+"eye_rotation.npy")

    print('###   Exporting camera attributes   ###')
    export_camera_gt(camera_name, out_dir+"camera_attributes.json")

    print('###   Exporting object blendshapes   ###')
    export_shape_keys(obj, seed, directory)

    print('###   Exporting monkey face weights   ###')
    export_vertices_weight(obj, "monkey_face", out_dir)
