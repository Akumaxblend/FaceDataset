import bpy 

def deleteShapekeyByName(oObject, sShapekeyName):
    
    # setting the active shapekey
    try:
        iIndex = oObject.data.shape_keys.key_blocks.keys().index(sShapekeyName)
        oObject.active_shape_key_index = iIndex
    
        # delete it
        bpy.ops.object.shape_key_remove()
    except:
        print('key not found')

obj1 = bpy.data.objects["spi_build_charKraven_rigModel_kravenA_lodA_facialShapes_532331e"]
obj2 = bpy.data.objects["assetLibrary_digidoubles_charNapoleon_rigModel_napoleon_ce7317b"]

sk1 = obj1.data.shape_keys.key_blocks
sk2 = obj2.data.shape_keys.key_blocks

sk1_list = []
sk2_list = []
skcommon = []
skdiff = []

for i in sk1:
    sk1_list.append(i.name)
for i in sk2:
    sk2_list.append(i.name)

for s1 in sk1_list:
    for s2 in sk2_list:
        if s2 == s1:
            skcommon.append(s2)
            
skdiff = list(set(sk1_list) - set(skcommon))

print("Nb of shape keys for Napoleon: " + str(len(sk2_list)))
print("Nb of shape keys for Kraven  : " + str(len(sk1_list)))
print("Nb of common keys            : " + str(len(skcommon)))
print("Nb of different keys         : " + str(len(skdiff)))

for s in skcommon:
    print(s)
    
for s in skdiff:
    deleteShapekeyByName(obj1, s)