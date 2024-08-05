# Imports used to write png images
from PIL import Image, ImageDraw
import numpy
import argparse

WHITE = (0, 0, 0, 0)
IMG_WIDTH = 512

parser = argparse.ArgumentParser(
    description     = "Inpainting with Stable Diffusion",
    formatter_class = argparse.ArgumentDefaultsHelpFormatter
    )
parser.add_argument('--inpaintDir',  type=str,   required=True,    help='Face Picture Directory')
parser.add_argument('--gtDir',  type=str,   required=True,    help='Ground Truth Directory')
parser.add_argument('--outputDir',  type=str,   required=True,    help='Output Directory')
parser.add_argument('--seed',  type=int,   required=True,    help='Start Frame')
parser.add_argument('--batch',  type=int,   required=True,    help='Total Number Frame')
parser.add_argument('--threshold',  type=float,   required=True,    help='Threshold Under Which A Vertex Is Not Considered In The Monkey Face')
parser.add_argument('--visibleOnly', type=str, default="True", help='Use this flag to check only non-culled points')

args = parser.parse_args()

in_image_dir = args.inpaintDir
in_gt_dir = args.gtDir
out_image_dir = args.outputDir
seed = args.seed
batch = args.batch
threshold = args.threshold
visible_only = args.visibleOnly

for i in range(seed, seed + batch):
    coordspath 	= f"{in_gt_dir}/{i:06}/ground_truth/vertices_positions.npy"
    indicespath = f"{in_gt_dir}/{i:06}/ground_truth/monkey_face_vertices.npy"
    visibilitypath = f"{in_gt_dir}/{i:06}/ground_truth/vertices_visibility.npy"

    data = numpy.load(coordspath)
    screen_positions = data['screen_positions']
    indices = numpy.load(indicespath)
    visibilities = numpy.load(visibilitypath)

    image_back = Image.open(f'{in_image_dir}/inpaint_{i:06}.png')
    image_top = Image.new('RGBA', (IMG_WIDTH, IMG_WIDTH), WHITE)
    draw = ImageDraw.Draw(image_top)

    for i in range (0, len(screen_positions[0])):
        point = screen_positions[0][i]
        if (visible_only == "True"):    visibility = visibilities[i]
        else:   visibility = True
        if(indices[i] >= threshold and visibility):
            draw.point([point[0], point[1]], fill=(0,255,0))

    image_back.paste(image_top, (0,0), image_top)
    image_back.save(out_image_dir+f'/face_check_{i:06}.png', "png")

# Method under allows to convert data from 3D camera relative points to 2d screen coordinates

# campath 	= "/s/prods/research/io/in/from_prod/face_dataset/MeshroomCache/FaceRenderer/420ea13e561508b0ff2268c6891a0546513b96c8/000001/ground_truth/camera_attributes.json"
# coordspath 	= "/s/prods/research/io/in/from_prod/face_dataset/MeshroomCache/FaceRenderer/420ea13e561508b0ff2268c6891a0546513b96c8/000001/ground_truth/vertices_positions.npy"
# file = numpy.load(coordspath)
# local_coords = file["world_positions"]

# file = open(campath)
# frame = json.load(file)[0]['view_frame']
# def screen_coords(co_local, frame, index):

#     z = -co_local[0][index][2]

#     if z == 0.0:
#         return [0.5, 0.5, 0.0]
#     else:
#         frame = [-(v / (v[2] / z)) for v in frame]

#     min_x, max_x = frame[2][0], frame[1][0]
#     min_y, max_y = frame[1][1], frame[0][1]

#     x = (co_local[0][index][0] - min_x) / (max_x - min_x)
#     y = (co_local[0][index][1] - min_y) / (max_y - min_y)

#     return [x, y, z]