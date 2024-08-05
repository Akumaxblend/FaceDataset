import bpy
import bmesh
import numpy

def get_modified_mesh(ob, frame, cage=False):
    bpy.context.scene.frame_set(frame)
    bm = bmesh.new()
    bm.from_object(
            ob,
            bpy.context.evaluated_depsgraph_get(),
            cage=cage,
            )
    #bm.transform(ob.matrix_world)
    me = bpy.data.meshes.new("Deformed")
    bm.to_mesh(me)
    return me

# In order to export only the visible vertices, not the hidden ones. Currently useless and not working. 
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

obj = bpy.data.objects["Head"]
camera = bpy.data.objects["Camera"]

tmp = get_modified_mesh(obj, 5000)
visibility = [is_vertex_visible(obj, obj.matrix_world @ vert.co, camera) for vert in tmp.vertices]


for i in range (0, len(obj.data.vertices)):
    if visibility[i]: 
        obj.data.vertices[i].select = True 
    