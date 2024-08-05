###   This is a documentation file for the following workflow : 3D rendering of a random face, export of this face's ground truth, inpaint of the face   ###

###   Introduction   ###

It is highly recommended to use the script random_face_full_process.py in order to generate random faces without having to dive into the scripts details. 

This script will call in cascade : random_face_renderer.py, shape_keys_exporter_single_frame.py, vertices_positions_single_image.py, random_face_inpainter.py while passing the arguments correctly.

You can use this command in a blender rez configured environment in order to launch random_face_full_process : python path/to/random_face_full_process.py --seed <number_of_the_frame> --outDir <path_to_output> 

Optionnal arguments : --batch = total image number to generate, default 1
					  --hairProbability = probability of inpainting hair in %, default 50
					  --eyebrowsProbability = probability of inpainting eyebrows in %, default 100
					  --beardProbability = probability of inpainting beard in %, default 20
					  --clothProbability = probability of inpainting cloth in %, default 100
					  --minFov = minimum focal length of blender's camera in mm, default 8
					  --maxFov = maximum focal length of blender's camera in mm, default 200

###   I - 3D rendering   ###

	###   1 - Features overview   ###

	The 3D rendering is triggered by random_face_renderer.py.
	The script is designed to work with a given scene, that you can find here : /s/prods/research/io/in/from_prod/face_dataset/blends/comparison.blend 
	This scene has texture dependencies : the Hdris envmaps (/s/prods/research/io/in/from_prod/downloads/Hdris/) and the skin textures (/s/prods/research/io/in/from_prod/face_dataset/textures/Napoleon/)
	The script does the following steps :
		
		- Set the current frame to the one given in parameter, or to a random one if the given one is -1. The current frame will condition the random view angle of the camera and the random hdri used to light the scene and the background, as well as the random eyes rotation

		- Will place automatically fit the eyes in orbits using predefined orbital vertex groups

		- Will pick random blendshapes of the predefined groups and set them to random values, resulting in random facial expression
		
		- Set the output path to the given one and append the current frame number to it, with the 6 digits format (frame 1 will be saved in directory/000001, frame 3000 will be saved in directory/003000)
		
		- Activate / deactivate shadow casters with a given treshold (30% chance of activating shadows currently, the parameter is not exposed for now, but you can change it in the call of gamble_shadows_visibility(percentage_visible, catsers_collection_name))

		- Set the random depth of field of the camera, between the minimum and maximum values defined in parameters
		
		- Setup a duplicate of the scene, used to generate procedural masks for stable diffusion later on. The following masks are  created :
			
			- Background mask
			- Beard-zone mask
			- Clothes-zone mask
			- Hair-zone mask
			- Shoulder edges mask

		- Render the beauty image and the masks in the precedently defined directory.

	###   2 - Usage   ###

	In a blender rez-configured environment, you can execute this command to launch the random face renderer : blender -b /s/prods/research/io/in/from_prod/face_dataset/blends/comparison.blend  -P path/to/random_face_renderer.py -- <wanted_current_frame> <wanted_output_path> <minimum_fov> <maximum_fov> <total_number_of_frames> 

###   II - Ground truth export   ###

The following ground truths are exported : facial expression blendshapes values, and vertices positions (in 3d space, and in screen space)

	###   1 - Facial expression blendshapes   ###

	The facial expression blendshapes are exported in JSON format thank to the script shape_keys_exporter_single_frame.py.
	The output JSON file contains the name of non-zero valued blendshapes and their value : 
	[
		{
			"name" : blendshape_1_name,
			"value" : blendshape_1_value
		},
		{
			"name" : blendshape_2_name,
			"value" : blendshape_2_value		
		}

	]

	###   2 - Vertices positions   ###

	The vertices positions are exported in the .npz format thank to the script vertices_positions_single_image.py.
	The format is as follows :
	[
		[
			[screen_coord_x1, screen_coord_y1],
			[screen_coord_x2, screen_coord_y2]
		],
		[
			[world_coord_x1, world_coord_y1, world_coord_z1],
			[world_coord_x2, world_coord_y2, world_coord_z2]
		]
	]
	To access this data easily : import the numpy library. Load the data as follows : data = numpy.load(path/to/vertices_positions.npy).
	The screen coordinates can then be accessed with data['screen_positions'], and the world coordinates with data['world_positions']

	###   3 - Vertices visibility   ###

	The vertices visibility is exported in a .npy format. It is an array of booleans, saying whether the vertex at i index is visible (True) or culled (False)

	###   4 - Eyes rotation   ###

	The eyes rotation is stored in a 3 component npy vector, representing [x rotation, y rotation, z rotation] in radians. The neutral point [0,0,0] is the eyes aligned with -Y vector. Note there is only one vector for both eyes, because both of them are bound together, so they share the same rotation data.

	###   5 - Camera attributes   ###

	Some camera attributes are exported within the file camera_attributes.json : the "fov" representing the focal length of the camera, in mm, the "location" representing the location of the camera in the 3D space, and the "sensor_size" representing [sensor_width, sensor_height] of the camera's sensor.



###   III - Stable diffusion inpainting   ###

Prerequesite : having stable diffusion webui running with the --api flag. You'll need to retrieve the server port number to be able to use it : in random_face_inpainter.py replace the default webui_server_url = 'http://127.0.0.1:7860' by your url. It should be http://127.0.0.1:+port number.

	###   1 - Features overview   ###

	The random_face_inpainter.py script uses the output image and masks generated in step I to inpaint on the 3D render :

		- Inpaint eyebrows with --eyebrowsProbability % chance: if generated, the image will be in the outPutDir/step_1 directory.
		- Inpaint hair with --hairProbability % chance: if generated, the image will be in the outPutDir/step_2 directory.
		- Inpaint beard with --beardProbability % chance: if generated, the image will be in the outPutDir/step_3 directory.
		- Inpaint random clothes with --eyebrowsProbability % chance: the image will be in the outPutDir/step_4 directory, and copied to the root of the outPutDir

	You can specify the --seed and --batch to match the number chose in the 3D render script. If you do so, a number of --batch image will be generated, starting from --seed image. You can enable the --debug True flag to keep the outDir/step_# folders to check at intermediate steps.
	In order to change the random options of the prompt, you can edit the dictionnaries or add some : pg.PromptSetting('Your Property Name', {"Option 1": probability_1, "Option 2": probability_2})

	###   2 - Usage   ###

	After launching stable-diffusion-webui and correctly changing your webui_server_url, you can use the following command : python path/to/random_face_inpainter.py --inputDir <path_of_input_images> --outDir <path_to_output_images>

	Optionnal arguments : --batch = total image number to generate, default 1
						  --seed = starting frame number, default 1
					  	  --hairProbability = probability of inpainting hair in %, default 50
					  	  --eyebrowsProbability = probability of inpainting eyebrows in %, default 100
					  	  --beardProbability = probability of inpainting beard in %, default 20
					  	  --clothProbability = probability of inpainting cloth in %, default 100