import os
import requests
import io
import base64
import time
import argparse
from PIL import Image, PngImagePlugin

import promptGen as pg

url = "http://127.0.0.1:7860/"

parser = argparse.ArgumentParser(
    description     = "Inpainting with Stable Diffusion",
    formatter_class = argparse.ArgumentDefaultsHelpFormatter
    )

parser.add_argument('--outputDir',  type=str,   required=True,    help='Output directory')
parser.add_argument('--inputDir',   type=str,   required=True,    help='Input images directory')
parser.add_argument('--maskDir',    type=str,   required=True,    help='Input masks directory')
parser.add_argument('--samples',    type=int,   required=True,    help='Number of data points')
parser.add_argument('--maskBlur',   type=int,   default=8,        help='Mask blur size')
parser.add_argument('--steps',      type=int,   default=50,       help='Number of denoising steps')

args = parser.parse_args()

# PARAMETERS
samples     = args.samples
maskBlur    = args.maskBlur
stepsCount  = args.steps

batchSize   = 1     # generate one image from one blender render
inBatchSize = 1     # in case of multiple input image for the same data point -> DEPRECATED

checkpoint      = '512-inpainting-ema.safetensors [b29e2ed9a8]'
checkpoint      = 'realisticStockPhoto_v30SD15.safetensors [f85affae9a]'
checkpointLoadingTimeLimit = 20

# CONTROL NET SETUP
preprocessor    = 'inpaint_global_harmonious'
controlNet      = 'control_v11p_sd15_inpaint [ebff9138]'
controlWeight   = 1

# PATH SETUP FOR MASK
#backImgPaths    = [os.path.join(args.maskDir,'Image'+str(i).zfill(4)+'.png') for i in range(samples)]
backImgPaths    = [os.path.join(args.maskDir,'beauty_718229.png') for i in range(samples)]
#############################################
# WAITING FOR CONNECTION

waitTime=0

while True :
    try:
        requests.get(url=f"{url}/user/")
        print('-- STARTING GENERATION --------------------')
        time.sleep(1)
        break
    except requests.exceptions.ConnectionError:
        print('   WAITING FOR CONNECTION ' + '-'*(waitTime%50),end="\r", flush=True)
        waitTime += 1
        time.sleep(1)


#############################################
# PROMPT PARAMETERS

options = [
    pg.PromptSetting('Gender',{'man':0.5,'woman':0.5}), 
    pg.PromptSetting('Age',{'very young':0.05, 'young':0.1, 'middle aged':0.45, 'in its fifties':0.25, 'a bit old':0.1, 'very old':0.05}),
    pg.PromptSetting('Hair Color',{'auburn hair':0.05,'dark hair':0.32, 'dark blond hair':0.32, 'blond hair':0.2,'white hair':0.1,'bald':0.01}),
    pg.PromptSetting('Clothes',{'casual clothes':0.5, 'colorful clothes':0.2, 'classy clothes':0.2, 'random clothes':0.1}),
    pg.PromptSetting('Background',{'city background':0.18, 'sky background':0.18, 'landscape background':0.18, 'crop field background':0.18, 'mountain background':0.18, 'random background':0.10}),
    pg.PromptSetting('Color',{'very colored':0.3, 'natural colors':0.4, 'desaturated':0.3})
]

prompt_generator = pg.PromptGenerator(options)

#############################################
# SETTING THE RIGHT CHECKPOINT

for i in range(checkpointLoadingTimeLimit):
    print('Loading checkpoint : ' + checkpoint)

    model_payload = {"sd_model_checkpoint": checkpoint}
    response = requests.post(url=f'{url}/sdapi/v1/options', json=model_payload)
    
    if response.status_code == 200 :
        print('Checkpoint loaded')
        break

    if i == checkpointLoadingTimeLimit :
        raise TimeoutError('Too much time attempting to load checkpoint')
    
    time.sleep(1)

#############################################
# INPAINTING CALLS

tic = time.time()   # to have the total duration of the generation -> toc at the end

#inputImgPaths = [os.path.join(args.inputDir,f'Image{str(i).zfill(4)}.png') for i in range(samples)]
inputImgPaths = [os.path.join(args.inputDir,f'beauty_718229.png')]

for input_indx in range(len(inputImgPaths)):

    positive,negative = prompt_generator.random_pick()
    
    # INPUT IMAGE
    buffer      = io.BytesIO()
    image       = Image.open(inputImgPaths[input_indx])
    image.save(buffer, format='PNG')
    inputImg64  = base64.b64encode(buffer.getvalue()).decode('utf-8')   # must encode the image in UTF-8 base64

    # MASK IMAGE
    buffer      = io.BytesIO()
    mask        = Image.open(backImgPaths[input_indx])
    mask.save(buffer, format='PNG')
    maskImg64   = base64.b64encode(buffer.getvalue()).decode('utf-8')   # must encode the image in UTF-8 base64

    # PAYLOAD CREATION
    payload = {
        "init_images"           : [inputImg64],
        "mask"                  : maskImg64,
        "prompt"                : positive,
        "steps"                 : stepsCount,
        "negative_prompt"       : negative,
        "inpainting_mask_invert": 1,                # inpaint the black zones
        "inpainting_fill"       : 1,                # use the 'orginal' setting for inpaint
        "mask_blur"             : maskBlur,
        "batch_size"            : batchSize,
        "denoising_strength"    : 0.9,              # to have results a bit far from the input
        "seed"                  : -1,               # WIP : Implement the seed
        "inpaint_full_res"      : False,            # magical setting not to have a white halo around the face

        ### CONTROL NET PARAMS -> NOT USED WITH 512-INPAINTING-EMA CHECKPOINT, USEFUL FOR OTHER MODELS
        # "alwayson_scripts": {
        #     "controlnet": {
        #         "args": [
        #             {
        #                 "model": controlNet,
        #                 "module": preprocessor,
        #                 "weight": controlWeight,
        #             }
        #         ]
        #     }
        # }
    }

    # IMAGE API CALL
    response = requests.post(url=f'{url}/sdapi/v1/img2img', json=payload)
    r = response.json()

    # IN CASE THE API IS NOT READY YET
    while 'images' not in r :
        print('Waiting for generation ...')
        time.sleep(1)
        response = requests.post(url=f'{url}/sdapi/v1/img2img', json=payload)
        r = response.json()

    # RETRIEVE STABLE DIFFUSION CONFIG AND MODEL PARAMETERS TO BURN IT IN THE METADATA
    #for i,img in enumerate(r['images'][:]):

    image       = Image.open(io.BytesIO(base64.b64decode(r['images'][0].split(",",1)[0])))
    png_payload = {
        "image": "data:image/png;base64," + r['images'][0]
    }
    
    configCall  = requests.post(url=f'{url}/sdapi/v1/png-info', json=png_payload)

    pnginfo     = PngImagePlugin.PngInfo()
    pnginfo.add_text("parameters", configCall.json().get("info"))   # Stable settings in the metadata
    pnginfo.add_text('pos_prompt', positive)                        # Positive prompt in the metadata
    pnginfo.add_text("neg_prompt", negative)                        # Negative prompt in the metadata

    # SAVE THE IMAGE WITH ITS METADATA
    image.save(os.path.join(args.outputDir,f'output_{input_indx}.png'), pnginfo=pnginfo)
    
    print(f'---- Image #{input_indx} DONE !')

toc = time.time()   # End of the timer 
print("TEMPS ECOULE : " + time.strftime("%H:%M:%S",time.gmtime(toc-tic)))