import bpy
import numpy

obj = bpy.data.objects["Head"]
verts = obj.data.vertices
weighted_indices = []
count = 0

def export_vertices_weight(obj, group_name, out_dir):
	verts = obj.data.vertices
	weighted_indices = []
	for v in verts:
	    weighted_indices.append(obj.vertex_groups[group_name].weight(v.index)) # for the monkey face group 
	with open(out_dir+"monkey_face_vertices.npy", 'wb') as file :
    	numpy.save(file, weighted_indices)
