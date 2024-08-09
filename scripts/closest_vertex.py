import bpy
from math import sqrt

def reset_shape_keys(obj): 
    shape_keys = obj.data.shape_keys.key_blocks
    for s in shape_keys:
        s.value = 0 
        
def deleteShapekeyByName(oObject, sShapekeyName):
    
    # setting the active shapekey
    iIndex = oObject.data.shape_keys.key_blocks.keys().index(sShapekeyName)
    oObject.active_shape_key_index = iIndex
    
    # delete it
    bpy.ops.object.shape_key_remove()
        
def delete_shape_keys(obj): 
    shape_keys = obj.data.shape_keys.key_blocks
    for s in shape_keys:
        deleteShapekeyByName(obj, s.name) 
        
def distance(obj1, vert1, obj2, vert2):
    vector = obj2.matrix_world @ vert2.co -  obj1.matrix_world @ vert1.co
    return sqrt(vector.x ** 2 + vector.y ** 2 + vector.z ** 2)
        
def closest_points(obj1, obj2, vertex_group_name):
    verts_1 = obj1.data.vertices
    verts_2 = obj2.data.vertices
    minimum_distance = 1000
    minimum_distance_index = 0
    indexes = []
    for v1 in verts_1:
        if obj1.vertex_groups[vertex_group_name].weight(v1.index) >= 0.5:
            for v2 in verts_2:
                tmp_distance = distance(obj1, v1, obj2, v2)
                if tmp_distance < minimum_distance:
                    minimum_distance = tmp_distance
                    minimum_distance_index = v2.index
            indexes.append(minimum_distance_index)
            minimum_distance = 1000
    return indexes

def apply_weights_to_indexes(obj, indexes, vertex_group_name):
    all_verts = []
    for v in obj.data.vertices:
        all_verts.append(v.index)
    obj.vertex_groups[vertex_group_name].add(all_verts, 0, 'REPLACE')
    obj.vertex_groups[vertex_group_name].add(indexes, 1, 'REPLACE')
        
head_low = bpy.data.objects["Head_decimated"]
head_high = bpy.data.objects["Head"]

monkey_face_indexes = (closest_points(head_low, head_high, "monkey_face"))
apply_weights_to_indexes(head_high, monkey_face_indexes, "monkey_face")