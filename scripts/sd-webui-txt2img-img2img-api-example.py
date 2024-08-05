from datetime import datetime
import urllib.request
import base64
import json
import time
import os
import argparse

webui_server_url = 'http://127.0.0.1:7860'

parser = argparse.ArgumentParser(
    description     = "Inpainting with Stable Diffusion",
    formatter_class = argparse.ArgumentDefaultsHelpFormatter
    )

parser.add_argument('--inputDir',  type=str,   required=True,    help='Output directory')
args = parser.parse_args()

out_dir = args.inputDir
out_dir_step1 = os.path.join(out_dir, 'step_1')
out_dir_step2 = os.path.join(out_dir, 'step_2')
out_dir_step3 = os.path.join(out_dir, 'step_3')
out_dir_step4 = os.path.join(out_dir, 'step_4')
os.makedirs(out_dir_step1, exist_ok=True)
os.makedirs(out_dir_step2, exist_ok=True)
os.makedirs(out_dir_step3, exist_ok=True)
os.makedirs(out_dir_step4, exist_ok=True)

def folder_number():
    number = os.path.basename(out_dir)
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


def call_img2img_api(output_path, **payload):
    response = call_api('sdapi/v1/img2img', **payload)
    for index, image in enumerate(response.get('images')): # Ensures that we export only the beauty image and not the masks
        if index < 1:
            save_path = os.path.join(output_path, f'{folder_number()}.png')
            decode_and_save_base64(image, save_path)
        else:   break


if __name__ == '__main__':
    # payload = {
    #     "prompt": "akumax, masterpiece, (best quality:1.1)",  # extra networks also in prompts
    #     "negative_prompt": "",
    #     "seed": 1,
    #     "steps": 20,
    #     "width": 512,
    #     "height": 512,
    #     "cfg_scale": 7,
    #     "sampler_name": "DPM++ 2M",
    #     "n_iter": 1,
    #     "batch_size": 1,

    #     # example args for x/y/z plot
    #     # "script_name": "x/y/z plot",
    #     # "script_args": [
    #     #     1,
    #     #     "10,20",
    #     #     [],
    #     #     0,
    #     #     "",
    #     #     [],
    #     #     0,
    #     #     "",
    #     #     [],
    #     #     True,
    #     #     True,
    #     #     False,
    #     #     False,
    #     #     0,
    #     #     False
    #     # ],

    #     # example args for Refiner and ControlNet
    #     # "alwayson_scripts": {
    #     #     "ControlNet": {
    #     #         "args": [
    #     #             {
    #     #                 "batch_images": "",
    #     #                 "control_mode": "Balanced",
    #     #                 "enabled": True,
    #     #                 "guidance_end": 1,
    #     #                 "guidance_start": 0,
    #     #                 "image": {
    #     #                     "image": encode_file_to_base64(r"B:\path\to\control\img.png"),
    #     #                     "mask": None  # base64, None when not need
    #     #                 },
    #     #                 "input_mode": "simple",
    #     #                 "is_ui": True,
    #     #                 "loopback": False,
    #     #                 "low_vram": False,
    #     #                 "model": "control_v11p_sd15_canny [d14c016b]",
    #     #                 "module": "canny",
    #     #                 "output_dir": "",
    #     #                 "pixel_perfect": False,
    #     #                 "processor_res": 512,
    #     #                 "resize_mode": "Crop and Resize",
    #     #                 "threshold_a": 100,
    #     #                 "threshold_b": 200,
    #     #                 "weight": 1
    #     #             }
    #     #         ]
    #     #     },
    #     #     "Refiner": {
    #     #         "args": [
    #     #             True,
    #     #             "sd_xl_refiner_1.0",
    #     #             0.5
    #     #         ]
    #     #     }
    #     # },
    #     # "enable_hr": True,
    #     # "hr_upscaler": "R-ESRGAN 4x+ Anime6B",
    #     # "hr_scale": 2,
    #     # "denoising_strength": 0.5,
    #     # "styles": ['style 1', 'style 2'],
    #     # "override_settings": {
    #     #     'sd_model_checkpoint': "sd_xl_base_1.0",  # this can use to switch sd model
    #     # },
    # }
    # call_txt2img_api(**payload)

    # Background inpaint ################################################################################################
    init_images = [
        encode_file_to_base64(f'{out_dir}/beauty_'+str(folder_number())+'.png')
    ]

    payload = {
        "prompt": "realistic background",
        "negative_prompt": "unrealistic, fantasy, people",
        "sampler_name": "DPM++ 2M",
        "seed": -1,
        "cfg_scale": 15,
        "steps": 25,
        "width": 512,
        "height": 512,
        "denoising_strength": 1,
        "inpaint_full_res": False,
        "inpaint_full_res_padding":0,
        "n_iter": 1,
        "init_images": init_images,
        "batch_size": 1,
        "mask_blur": 0,
        "inpainting_fill": 2,
        "mask": encode_file_to_base64(f'{out_dir}/'+'alpha_mask_'+str(folder_number())+".png"),
        "override_settings" : {
            "sd_model_checkpoint": "v1-5-pruned-emaonly.safetensors [6ce0161689]"
        }
    }
    #call_img2img_api(out_dir_step1, **payload)

    
    # Hair inpaint ################################################################################################
    # init_images = [
    #     encode_file_to_base64(f'{out_dir_step1}/'+str(folder_number())+'.png')
    # ]

    payload = {
        "prompt": "blue curly hair, dinstinct from background",
        "negative_prompt": "blending, confuse",
        "sampler_name": "Heun",
        "seed": -1,
        "cfg_scale": 5,
        "steps": 20,
        "width": 512,
        "height": 512,
        "denoising_strength": 0.9,
        "inpaint_full_res": False,
        "inpaint_full_res_padding":10,
        "n_iter": 1,
        "init_images": init_images,
        "batch_size": 1,
        "mask": encode_file_to_base64(f'{out_dir}/'+'hair_mask_'+str(folder_number())+".png"),
        "mask_blur": 10,
        "inpainting_fill": 0,
        "override_settings" : {
            "sd_model_checkpoint": "inpaintingByZenityxAI_v10.safetensors [8583ee9022]"
            #"sd_model_checkpoint": "v1-5-pruned-emaonly.safetensors [6ce0161689]"
        },
        "alwayson_scripts": {
            # "ControlNet": {
            #     "args": [
            #         {
            #             "enabled": False,
            #             "control_mode": "Balanced",
            #             "model": "control_v11p_sd15_inpaint [ebff9138]",
            #             "module":"inpaint_only",
            #             "resize_mode": "Crop and Resize",
            #             "weight": 1
            #         }
            #     ]
            # },
        }
    }
    call_img2img_api(out_dir_step2, **payload)

    # Cloth inpaint ################################################################################################
    #REGARDER POUR QUE LE MASKED CONTENT SOIT VRM DIFFERENT SVP (GENRE INPAINT AREA EN MASKED ONLY PTET) => le probleme vient peut etre d'inpait sur un background full inpainted aussi
    init_images = [
        encode_file_to_base64(f'{out_dir_step2}/'+str(folder_number())+'.png')
    ]

    payload = {
        "prompt": "checked shirt",
        "sampler_name": "Heun",
        "seed": -1,
        "cfg_scale": 5,
        "steps": 25,
        "width": 512,
        "height": 512,
        "denoising_strength": 1,
        "n_iter": 1,
        "init_images": init_images,
        "batch_size": 1,
        "mask": encode_file_to_base64(f'{out_dir}/'+'clothes_mask_'+str(folder_number())+".png"),
        "mask_blur": 0,
        "inpainting_fill": 0,
        "override_settings" : {
            "sd_model_checkpoint": "inpaintingByZenityxAI_v10.safetensors [8583ee9022]"
            #"sd_model_checkpoint": "v1-5-pruned-emaonly.safetensors [6ce0161689]"
        },
        "alwayson_scripts": {
            "ControlNet": {
                "args": [
                    # {
                    #     "enabled": False,
                    #     "control_mode": "ControlNet is more important",
                    #     "model": "control_v11p_sd15_inpaint [ebff9138]",
                    #     "module":"inpaint_only",
                    #     "resize_mode": "Crop and Resize",
                    #     "weight": 0.85
                    # },
                    {
                        "enabled": True,
                        "image": encode_file_to_base64(f'{out_dir}/'+'edges_clothes_'+str(folder_number())+".png"),
                        "control_mode": "Balanced",
                        "module": "canny",
                        "model": "control_v11p_sd15_canny [d14c016b]",
                        "resize_mode": "Crop and Resize",
                        "weight": 1
                    }
                ]
            },
        }
    }
    call_img2img_api(out_dir_step3, **payload)

    # Beard inpaint ################################################################################################
    init_images = [
        encode_file_to_base64(f'{out_dir_step3}/'+str(folder_number())+'.png')
    ]

    payload = {
        "prompt": "beard",
        "sampler_name": "Heun",
        "seed": -1,
        "cfg_scale": 5,
        "steps": 25,
        "width": 512,
        "height": 512,
        "denoising_strength": 0.85,
        "n_iter": 1,
        "init_images": init_images,
        "batch_size": 1,
        "mask": encode_file_to_base64(f'{out_dir}/'+'beard_mask_'+str(folder_number())+".png"),
        "mask_blur": 1,
        "inpainting_fill": 0,
        "override_settings" : {
            "sd_model_checkpoint": "inpaintingByZenityxAI_v10.safetensors [8583ee9022]"
            #"sd_model_checkpoint": "v1-5-pruned-emaonly.safetensors [6ce0161689]"
        },
        "alwayson_scripts": {
            "ControlNet": {
                "args": [
                    # {
                    #     "enabled": False,
                    #     "control_mode": "Balanced",
                    #     "model": "control_v11p_sd15_inpaint [ebff9138]",
                    #     "module":"inpaint_only",
                    #     "resize_mode": "Crop and Resize",
                    #     "weight": 0.85
                    # },
                    {
                        "enabled": True,
                        "control_mode": "Balanced",
                        "module": "canny",
                        "model": "control_v11p_sd15_canny [d14c016b]",
                        "resize_mode": "Crop and Resize",
                        "weight": 1
                    }
                ]
            },
        }
    }
    call_img2img_api(out_dir_step4, **payload)

    # there exist a useful extension that allows converting of webui calls to api payload
    # particularly useful when you wish setup arguments of extensions and scripts
    # https://github.com/huchenlei/sd-webui-api-payload-display
