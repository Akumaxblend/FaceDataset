import bpy

obj1 = bpy.data.objects["spi_build_charKraven_rigModel_kravenA_lodA_facialShapes_532331e"]

def deleteShapekeyByName(oObject, sShapekeyName):
    
    # setting the active shapekey
    iIndex = oObject.data.shape_keys.key_blocks.keys().index(sShapekeyName)
    oObject.active_shape_key_index = iIndex
    
    # delete it
    bpy.ops.object.shape_key_remove()


