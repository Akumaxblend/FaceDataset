import bpy
from mathutils import Vector

obj = bpy.data.objects["Head"]
eye_left = bpy.data.objects["eye_left_location_controller"]
eye_right = bpy.data.objects["eye_right_location_controller"]

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

eye_left.location = mean_location_from_group("eye_left", obj)
eye_right.location = mean_location_from_group("eye_right", obj)