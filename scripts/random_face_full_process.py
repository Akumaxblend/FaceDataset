import os
import argparse

parser = argparse.ArgumentParser(
    description     = "Random face rendering with blender and inpainting with Stable Diffusion",
    formatter_class = argparse.ArgumentDefaultsHelpFormatter
    )
parser.add_argument('--seed',  type=int,   required=True,    help='Seed of the random face in blender')
parser.add_argument('--outDir', type=str, required=True, help='Directory where the images will be saved')

parser.add_argument('--hairProbability', type=int, required=False, help='Probability of triggering hair inpainting', default=50)
parser.add_argument('--eyebrowsProbability', type=int, required=False, help='Probability of triggering eyebrows inpainting', default=100)
parser.add_argument('--beardProbability', type=int, required=False, help='Probability of triggering beard inpainting', default=20)
parser.add_argument('--clothProbability', type=int, required=False, help='Probability of triggering cloth inpainting', default=100)

parser.add_argument('--minFov', type=int, required=False, help='Minimum focal length, in mm', default=8)
parser.add_argument('--maxFov', type=int, required=False, help='Maximum focal length, in mm', default=200)

parser.add_argument('--batch', type=int, required=False, default=1)
args = parser.parse_args()

seed 				 = args.seed
outDir 				 = args.outDir

hair_probability     = args.hairProbability
eyebrows_probability = args.eyebrowsProbability
beard_probability    = args.beardProbability
cloth_probability    = args.clothProbability

min_fov 			 = args.minFov
max_fov 			 = args.maxFov

batch 				 = args.batch

blend_directory            	   = "/s/prods/research/io/in/from_prod/face_dataset/blends/comparison.blend"
blender_renderer_directory 	   = '/s/prods/research/io/in/from_prod/face_dataset/scripts/random_face_renderer.py'
positions_exporter_directory   = '/s/prods/research/io/in/from_prod/face_dataset/scripts/vertices_positions_single_image.py'
blendshapes_exporter_directory = "/s/prods/research/io/in/from_prod/face_dataset/scripts/shape_keys_exporter_single_frame.py"
stable_inpainter_directory     = '/s/prods/research/io/in/from_prod/face_dataset/scripts/random_face_inpainter.py'

for i in range(seed, seed + batch):
	print('###   3D rendering with seed '+str(i)+'   ###')
	commandLine = "rez env blender -c 'blender -b "+blend_directory+" -P "+blender_renderer_directory+" -P "+positions_exporter_directory+" -P "+blendshapes_exporter_directory+" -- "+str(i)+" "+outDir+f"{i:06} "+str(min_fov)+" "+str(max_fov)+"'"
	os.system(commandLine)
	#os.system('blender -b '+blend_directory+' -P '+blender_renderer_directory+' -P '+positions_exporter_directory+' -P '+blendshapes_exporter_directory+' -- '+str(i)+' '+outDir+f'{i:06} '+' > /dev/null 2>&1') # The redirect > /dev/null allows to throw blender high verbosity away
	os.system('python '+stable_inpainter_directory+' --inputDir '+outDir+f'{i:06} '+' --hairProbability '+str(hair_probability)+' --eyebrowsProbability '+str(eyebrows_probability)+' --beardProbability '+str(beard_probability)+' --clothProbability '+str(cloth_probability))