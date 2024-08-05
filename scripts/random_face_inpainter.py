from datetime import datetime
import urllib.request
import base64
import json
import time
import os, shutil
import argparse
import random

import promptGen as pg

webui_server_url = 'http://127.0.0.1:7860'

parser = argparse.ArgumentParser(
    description     = "Inpainting with Stable Diffusion",
    formatter_class = argparse.ArgumentDefaultsHelpFormatter
    )

parser.add_argument('--inputDir',  type=str,   required=True,    help='3D render directory')
parser.add_argument('--outputDir', type =str, required=True, help='Output directory for inpainting')
parser.add_argument('--hairProbability', type=int, required=False, help='Probability of triggering hair inpainting', default=50)
parser.add_argument('--eyebrowsProbability', type=int, required=False, help='Probability of triggering eyebrows inpainting', default=100)
parser.add_argument('--beardProbability', type=int, required=False, help='Probability of triggering beard inpainting', default=20)
parser.add_argument('--clothProbability', type=int, required=False, help='Probability of triggering cloth inpainting', default=100)

parser.add_argument('--hairDenoise', type=float, required=False, help='Denoise of hair inpainting', default=0.9)
parser.add_argument('--eyebrowsDenoise', type=float, required=False, help='Denoise of eyebrows inpainting', default=0.5)
parser.add_argument('--beardDenoise', type=float, required=False, help='Denoise of beard inpainting', default=0.75)
parser.add_argument('--clothDenoise', type=float, required=False, help='Denoise of cloth inpainting', default=1)
parser.add_argument('--debug', type=str, default="False", help='Use this flag to keep all intermediate inpainting steps')

parser.add_argument('--seed', type=int, default=1, help='Number of the first frame you want to inpaint')
parser.add_argument('--batch', type=int, default=1, help='Total number of frames you want to inpaint. Make sure the folder numbers follow eachother')
args = parser.parse_args()

in_dir               = args.inputDir
out_dir              = args.outputDir

hair_probability     = args.hairProbability
eyebrows_probability = args.eyebrowsProbability
beard_probability    = args.beardProbability
cloth_probability    = args.clothProbability

hair_denoise     = args.hairDenoise
eyebrows_denoise = args.eyebrowsDenoise
beard_denoise    = args.beardDenoise
cloth_denoise    = args.clothDenoise

debug                = args.debug
seed                 = args.seed
batch                = args.batch

out_dir_step1 = os.path.join(out_dir, 'step_1')
out_dir_step2 = os.path.join(out_dir, 'step_2')
out_dir_step3 = os.path.join(out_dir, 'step_3')
out_dir_step4 = os.path.join(out_dir, 'step_4')
os.makedirs(out_dir_step1, exist_ok=True)
os.makedirs(out_dir_step2, exist_ok=True)
os.makedirs(out_dir_step3, exist_ok=True)
os.makedirs(out_dir_step4, exist_ok=True)

def folder_number(path):
    number = os.path.basename(path)
    return number

def timestamp():
    return datetime.fromtimestamp(time.time()).strftime("%Y%m%d-%H%M%S")


def encode_file_to_base64(path):
    with open(path, 'rb') as file:
        return base64.b64encode(file.read()).decode('utf-8')


def decode_and_save_base64(base64_str, save_path):
    with open(save_path, "wb") as file:
        file.write(base64.b64decode(base64_str))


def call_api(api_endpoint, **payload):
    data = json.dumps(payload).encode('utf-8')
    request = urllib.request.Request(
        f'{webui_server_url}/{api_endpoint}',
        headers={'Content-Type': 'application/json'},
        data=data,
    )
    response = urllib.request.urlopen(request)
    return json.loads(response.read().decode('utf-8'))


def call_img2img_api(output_path, output_name, **payload):
    response = call_api('sdapi/v1/img2img', **payload)
    for index, image in enumerate(response.get('images')): # Ensures that we export only the beauty image and not the masks
        if index < 1:
            save_path = os.path.join(output_path, f'{output_name}.png')
            decode_and_save_base64(image, save_path)
        else:   break

def generate_payload(prompt, negative_prompt, denoising_strength, source_image, mask_image, mask_blur, canny_mask_image=None, depth_mask_image=None):
    payload = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "sampler_name": "Heun",
        "seed": -1,
        "cfg_scale": 10,
        "steps": 30,
        "width": 512,
        "height": 512,
        "denoising_strength": denoising_strength,
        "n_iter": 1,
        "init_images": init_images,
        "batch_size": 1,
        "mask": mask_image,
        "mask_blur": mask_blur,
        "inpainting_fill": 0,
        "override_settings" : {
            "sd_model_checkpoint": "inpaintingByZenityxAI_v10.safetensors [8583ee9022]"
            #"sd_model_checkpoint": "v1-5-pruned-emaonly.safetensors [6ce0161689]"
        },
        "alwayson_scripts": {
            "ControlNet": {
                "args": [
                    {
                        "enabled": True if canny_mask_image is not None else False,
                        "image": canny_mask_image,
                        "control_mode": "ControlNet is more important",
                        "module": "canny",
                        "model": "control_v11p_sd15_canny [d14c016b]",
                        "resize_mode": "Crop and Resize",
                        "weight": 1
                    },
                    {
                        "enabled": True if depth_mask_image is not None else False,
                        "image": depth_mask_image,
                        "control_mode": "ControlNet is more important",
                        "preprocessor": "none",
                        "module": "depth",
                        "model": "control_v11f1p_sd15_depth [cfd03158]",
                        "resize_mode": "Crop and Resize",
                        "weight": 1
                    }
                ]
            },
        }
    }
    return payload

if __name__ == '__main__':

    for i in range(seed, seed + batch):
        in_dir_post        = in_dir + f'/{i:06}'
        last_created_image = f'{in_dir_post}/beauty_render_'+str(folder_number(in_dir_post))+'.png'

        # Eyebrow inpaint ################################################################################################
        if (random.randint(1, 100) <= eyebrows_probability): # We draw a random number to determine if we should inpaint or not according to the user-defined probabilty
            options = [
            #pg.PromptSetting('Hair Color',{'auburn':0.05,'dark':0.32, 'dark blond':0.32, 'blond':0.2,'white':0.1,'skin':0.01}),
            pg.PromptSetting('Hair Color', {"Black": 0.15, "Dark Brown": 0.14, "Medium Brown": 0.12, "Light Brown": 0.10, "Chestnut": 0.08, "Auburn": 0.07, "Dark Blonde": 0.06, "Dirty Blonde": 0.05, "Strawberry Blonde": 0.04, "Blonde": 0.05, "Platinum Blonde": 0.02, "Ash Blonde": 0.02, "Red": 0.03, "Ginger": 0.02, "Copper": 0.02, "Silver": 0.01, "Grey": 0.01, "White": 0.01, "Dark Red": 0.01, "Honey Blonde": 0.01}),
            #pg.PromptSetting('Hair style',{'curly hair':0.25, 'frizz hair':0.25, 'hair braids':0.25, 'short hair':0.25})
            pg.PromptSetting('Eyebrows style', {"Straight eyebrows": 0.05,"Arched eyebrows": 0.05,"Rounded eyebrows": 0.05,"Angled eyebrows": 0.05,"S-shaped eyebrows": 0.05,"Flat eyebrows": 0.05,"Soft Angled eyebrows": 0.05,"High Arched eyebrows": 0.05,"Curved eyebrows": 0.05,"Thick eyebrows": 0.05,"Thin eyebrows": 0.05,"Feathered eyebrows": 0.05,"Tapered eyebrows": 0.05,"Natural eyebrows": 0.05,"Bushy eyebrows": 0.05,"Short eyebrows": 0.05,"Long eyebrows": 0.05,"Sparse eyebrows": 0.05,"Defined eyebrows": 0.05,"Soft Curved eyebrows": 0.05})
            ]

            prompt_generator = pg.PromptGenerator(options)

            positive, negative = prompt_generator.random_pick()

            init_images = [ encode_file_to_base64(last_created_image) ]

            mask_image = encode_file_to_base64(f'{in_dir_post}/'+'eyebrows_mask_'+str(folder_number(in_dir_post))+".png")

            eyebrows_payload = generate_payload(positive, negative, 
                eyebrows_denoise, init_images, mask_image, 2)

            print('###   Inpainting eyebrows with parameters : '+positive+'   ###')
            call_img2img_api(out_dir_step1, folder_number(in_dir_post), **eyebrows_payload)
            last_created_image = f'{out_dir_step1}/'+str(folder_number(in_dir_post))+'.png'

        else:   print('###   Skipping eyebrows inpainting  ###')

        # Hair inpaint ################################################################################################
        if (random.randint(1, 100) <= hair_probability): # We draw a random number to determine if we should inpaint or not according to the user-defined probabilty
            options = [
            #pg.PromptSetting('Hair Color',{'auburn':0.05,'dark':0.32, 'dark blond':0.32, 'blond':0.2,'white':0.1,'skin':0.01}),
            pg.PromptSetting('Hair Color', {"Black": 0.15, "Dark Brown": 0.14, "Medium Brown": 0.12, "Light Brown": 0.10, "Chestnut": 0.08, "Auburn": 0.07, "Dark Blonde": 0.06, "Dirty Blonde": 0.05, "Strawberry Blonde": 0.04, "Blonde": 0.05, "Platinum Blonde": 0.02, "Ash Blonde": 0.02, "Red": 0.03, "Ginger": 0.02, "Copper": 0.02, "Silver": 0.01, "Grey": 0.01, "White": 0.01, "Dark Red": 0.01, "Honey Blonde": 0.01}),
            #pg.PromptSetting('Hair style',{'curly hair':0.25, 'frizz hair':0.25, 'hair braids':0.25, 'short hair':0.25})
            pg.PromptSetting('Hair Style', {"Straight hair": 0.15, "Wavy hair": 0.14, "Curly hair": 0.12, "Coily hair": 0.10, "Buzz Cut hair": 0.08, "Bob hair": 0.07, "Pixie Cut hair": 0.06, "Braided hair": 0.05, "Ponytail hair": 0.04, "Bun hair": 0.05, "Mohawk hair": 0.02, "Dreadlocks hair": 0.02, "Afro hair": 0.03, "Undercut hair": 0.02, "Shag hair": 0.02, "Layered hair": 0.01, "Perm hair": 0.01, "Updo hair": 0.01, "Pompadour hair": 0.01, "Side Part hair": 0.01})
            ]

            prompt_generator = pg.PromptGenerator(options)

            positive, negative = prompt_generator.random_pick()

            init_images = [encode_file_to_base64(last_created_image)]

            mask_image = encode_file_to_base64(f'{in_dir_post}/'+'hair_mask_'+str(folder_number(in_dir_post))+".png")

            hair_payload = generate_payload(positive, negative, 
                hair_denoise, init_images, mask_image, 10)

            print('###   Inpainting hair with parameters : '+positive+'   ###')
            call_img2img_api(out_dir_step2, folder_number(in_dir_post), **hair_payload)
            last_created_image = f'{out_dir_step2}/'+str(folder_number(in_dir_post))+'.png'

        else:   print('###   Skipping hair inpainting   ###')

        # Beard inpaint ################################################################################################
        if (random.randint(1, 100) <= beard_probability): # We draw a random number to determine if we should inpaint or not according to the user-defined probabilty
            options = [
            #pg.PromptSetting('Beard type',{'short beard':0.25, 'dense beard':0.25, 'shaved beard':0.25, 'moustache':0.25}),
            pg.PromptSetting('Beard type',{"Full beard": 0.15, "Goatee beard": 0.14, "Van Dyke beard": 0.12, "Short beard": 0.10, "Stubble beard": 0.08, "Mutton Chops beard": 0.07, "Soul Patch beard": 0.06, "Chinstrap beard": 0.05, "Circle beard": 0.04, "Anchor beard": 0.05, "Handlebar mustache": 0.02, "Horseshoe mustache": 0.02, "Pencil mustache": 0.03, "Balbo beard": 0.02, "Imperial mustache": 0.02, "Chevron mustache": 0.01, "English mustache": 0.01, "French Fork beard": 0.01, "Ducktail beard": 0.01, "Five-o-clock shadow beard": 0.01}),
            #pg.PromptSetting('Beard color',{'Blonde':1})
            #pg.PromptSetting('Beard Color', {"Black": 0.15, "Dark Brown": 0.14, "Medium Brown": 0.12, "Light Brown": 0.10, "Chestnut": 0.08, "Auburn": 0.07, "Dark Blonde": 0.06, "Dirty Blonde": 0.05, "Strawberry Blonde": 0.04, "Blonde": 0.05, "Platinum Blonde": 0.02, "Ash Blonde": 0.02, "Red": 0.03, "Ginger": 0.02, "Copper": 0.02, "Silver": 0.01, "Grey": 0.01, "White": 0.01, "Dark Red": 0.01, "Honey Blonde": 0.01})
            ]

            prompt_generator = pg.PromptGenerator(options)

            positive, negative = prompt_generator.random_pick()
            
            init_images = [encode_file_to_base64(last_created_image)]

            beard_mask = encode_file_to_base64(f'{in_dir_post}/'+'beard_mask_'+str(folder_number(in_dir_post))+".png")
            depth_mask = encode_file_to_base64(f'{in_dir_post}/'+'depth_mask_'+str(folder_number(in_dir_post))+".png")

            beard_payload = generate_payload(positive, negative, 
                beard_denoise, init_images, beard_mask, 1, None, depth_mask)

            print('###   Inpainting beard with parameters : '+positive+'   ###')
            call_img2img_api(out_dir_step3, folder_number(in_dir_post), **beard_payload)
            last_created_image = f'{out_dir_step3}/'+str(folder_number(in_dir_post))+'.png'

        else:   print('###   Skipping beard inpainting   ###')

        # Cloth inpaint ################################################################################################
        if (random.randint(1, 100) <= cloth_probability): # We draw a random number to determine if we should inpaint or not according to the user-defined probabilty
            options = [
            #pg.PromptSetting('Cloth type',{'shirt':0.25, 'tshirt':0.25, 'jacket':0.25, 'sweatshirt':0.25}),
            pg.PromptSetting('Cloth type',{"T-shirt clothing": 0.05, "Dress shirt clothing": 0.05, "Polo shirt clothing": 0.05, "Sweater clothing": 0.05, "Hoodie clothing": 0.05, "Jacket clothing": 0.05, "Blouse clothing": 0.05, "Tank top clothing": 0.05, "Sweatshirt clothing": 0.05, "Cardigan clothing": 0.05, "Vest clothing": 0.05, "Coat clothing": 0.05, "Camisole clothing": 0.05, "Turtleneck clothing": 0.05, "Henley shirt clothing": 0.05, "Peacoat clothing": 0.05, "Flannel shirt clothing": 0.05, "Leather jacket clothing": 0.05, "Windbreaker clothing": 0.05, "Blazer clothing": 0.05}),
            #pg.PromptSetting('Clothes style',{'casual clothes':0.5, 'colorful clothes':0.2, 'classy clothes':0.2, 'old clothes':0.1})
            pg.PromptSetting('Clothes style',{"Casual": 0.05, "Formal": 0.05, "Striped": 0.05, "Plaid": 0.05, "Floral": 0.05, "Polka-dotted": 0.05, "Checked": 0.05, "Embroidered": 0.05, "Graphic": 0.05, "Vintage": 0.05, "Modern": 0.05, "Elegant": 0.05, "Sporty": 0.05, "Luxurious": 0.05, "Comfortable": 0.05, "Rugged": 0.05, "Chic": 0.05, "Bohemian": 0.05, "Minimalist": 0.05, "Bold": 0.05})
            ]

            prompt_generator = pg.PromptGenerator(options)

            positive, negative = prompt_generator.random_pick()

            init_images = [encode_file_to_base64(last_created_image)]

            clothes_mask = encode_file_to_base64(f'{in_dir_post}/'+'clothes_mask_'+str(folder_number(in_dir_post))+".png")
            clothes_edges = encode_file_to_base64(f'{in_dir_post}/'+'edges_clothes_'+str(folder_number(in_dir_post))+".png")

            cloth_payload = generate_payload(positive, negative, 
                cloth_denoise, init_images, clothes_mask, 10, clothes_edges)
            
            print('###   Inpainting clothes with parameters : '+positive+'   ###')
            call_img2img_api(out_dir_step4, str(folder_number(in_dir_post)), **cloth_payload)
            last_created_image = f'{out_dir_step4}/'+str(folder_number(in_dir_post))+'.png'

        else:   print('###   Skipping cloth inpainting   ###')

        # We copy the file so it's easily accessible from the output directory
        decode_and_save_base64(encode_file_to_base64(last_created_image), out_dir+'/inpaint_'+folder_number(in_dir_post)+'.png')

    if debug == "False":
        shutil.rmtree(out_dir_step1)
        shutil.rmtree(out_dir_step2)
        shutil.rmtree(out_dir_step3)
        shutil.rmtree(out_dir_step4)

