# Imports used to write png images
from PIL import Image, ImageDraw
import numpy
from numpy import linalg as LA

# Imports used to read exr images 
import os
os.environ["OPENCV_IO_ENABLE_OPENEXR"]="1"
import cv2

WHITE = (0, 0, 0, 0)

coordspath 	= "/s/prods/research/io/in/from_prod/face_dataset/output/meshroom/000006/ground_truth/vertices_positions.npy"
indicespath = "/s/prods/research/io/in/from_prod/face_dataset/output/inpainted/monkey_face_vertices.npy"
campath 	= "/s/prods/research/io/in/from_prod/face_dataset/output/meshroom/000006/ground_truth/camera_location.npy"
depthpath 	= "/s/prods/research/io/in/from_prod/face_dataset/output/meshroom/000006/ground_truth/depth_map_005000.exr"
visibilitypath = "/s/prods/research/io/in/from_prod/face_dataset/output/meshroom/000006/ground_truth/vertices_visibility.npy"

data = numpy.load(coordspath)
screen_positions = data['screen_positions']
world_positions	 = data['world_positions']
indices = numpy.load(indicespath)
cam_position = numpy.load(campath)
visibilities = numpy.load(visibilitypath)

# To paint vertices that are in the monkey face group
count = 0
image = Image.new('RGBA', (512, 512), WHITE)
draw = ImageDraw.Draw(image)

for i in range (0, len(screen_positions[0])):
	if(visibilities[i]):
		point = screen_positions[0][i]
		# print("drawing point "+str(i))
		if indices[i] == 1:	
			draw.point([point[0], point[1]], fill=(0,255,0))		# Common points between monkey face and visible points -> green
			count += 1	
		else:	
			draw.point([point[0], point[1]], fill=(0,0,255))	# Non-culled points not in the monkey face -> blue
			count += 1	
	# else:
	# 	if indices[i] == 1:	
	# 		draw.point([point[0]+1, point[1]], fill=(255,0,0))		# Monkey face points that are culled -> red
	# 		count += 1												# EUUUUH WTF YA DES DOUBLONS JE COMPREND PAS POURQUOI ? LES POINTS VERTS OFFSET DE 1 DEVENANT ROUGES SONT LES DOUBLONS => go investiguer en printant les indices et en regardant ça

image.save(coordspath+'/../visible_vertices.png', "png")

print(len(visibilities))
print(count)

# # To draw only visible points
# depth_image = cv2.imread(depthpath, cv2.IMREAD_UNCHANGED)
# for i in range (0, len(screen_positions[0])):
# 	if(visibilities[i] == 1):
# 		point_x = screen_positions[0][i][0]
# 		point_y = screen_positions[0][i][1]
# 		point_value = depth_image[round(point_x), round(point_y)][0]

# 		point_world = world_positions[0][i]

