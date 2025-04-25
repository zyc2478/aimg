import asyncio
import json
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from app.utils.comfyui_client import ComfyUIClient

async def main():
    # 使用FLUX原生工作流配置
    workflow = {
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": 1024,
                "height": 1024,
                "batch_size": 1
            }
        },
        "22": {
            "class_type": "BasicGuider",
            "inputs": {
                "model": ["12", 0],
                "conditioning": ["6", 0]
            }
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["13", 0],
                "vae": ["10", 0]
            }
        },
        "25": {
            "class_type": "RandomNoise",
            "inputs": {
                "width": 1024,
                "height": 1024,
                "batch_size": 1,
                "noise_seed": 782619153058034
            }
        },
        "11": {
            "class_type": "DualCLIPLoader",
            "inputs": {
                "clip_name1": "t5xxl_fp16.safetensors",
                "clip_name2": "clip_l.safetensors",
                "type": "flux",
                "mode": "default"
            }
        },
        "10": {
            "class_type": "VAELoader",
            "inputs": {
                "vae_name": "ae.sft"
            }
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {
                "images": ["8", 0],
                "filename_prefix": "ComfyUI"
            }
        },
        "17": {
            "class_type": "BasicScheduler",
            "inputs": {
                "model": ["12", 0],
                "scheduler": "normal",
                "steps": 20,
                "denoise": 1
            }
        },
        "16": {
            "class_type": "KSamplerSelect",
            "inputs": {
                "sampler_name": "euler"
            }
        },
        "13": {
            "class_type": "SamplerCustomAdvanced",
            "inputs": {
                "noise": ["25", 0],
                "guider": ["22", 0],
                "sampler": ["16", 0],
                "sigmas": ["17", 0],
                "latent_image": ["5", 0]
            }
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "clip": ["11", 0],
                "text": "Central Theme\nTheme: Epic fantasy battle scene with a young girl riding a majestic dragon.\nStyle: Dramatic and dynamic, with rich details and atmospheric lighting.\nScene Description:\nMain Character: A brave young girl, around 10-12 years old, with flowing hair and determined expression, wearing fantasy armor.\nDragon: A magnificent dragon with iridescent scales, powerful wings, and fierce features. The dragon is in mid-flight, breathing fire.\nSetting: An active volcano in the background, with lava flows and ash clouds creating an apocalyptic atmosphere.\nAction: The girl and dragon are engaged in an epic battle against various mythical creatures.\nCreatures: Multiple fantasy monsters including:\n- Fire elementals emerging from lava\n- Winged demons circling in the sky\n- Rock golems emerging from the volcanic terrain\n- Magma serpents coiling through the air\nLighting:\n- Dramatic red-orange glow from the volcano and lava\n- Flashes of dragon fire illuminating the scene\n- Contrasting cool blue light from magical effects\nAtmosphere:\n- Dynamic composition with the dragon and girl as the focal point\n- Epic scale showing the vastness of the battle\n- Dramatic clouds of ash and smoke\n- Magical energy effects and particle systems\nDetails:\n- Intricate details on the dragon's scales and the girl's armor\n- Expressive faces showing determination and courage\n- Dynamic poses capturing the intensity of battle\n- Rich environmental details in the volcanic landscape"
            }
        },
        "12": {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": "FLUX\\flux1-dev.sft",
                "weight_dtype": "fp8_e4m3fn"
            }
        }
    }
    
    # 使用异步上下文管理器，指定服务器地址
    async with ComfyUIClient(host="223.104.3.2", port=8188) as client:
        try:
            # 提交工作流
            prompt_id = await client.submit_prompt(workflow)
            print(f"工作流已提交，ID: {prompt_id}")
            
            # 连接WebSocket并等待结果
            await client.connect_websocket()
            result = await client.listen_websocket()
            
            if "image" in result:
                # 保存生成的图像
                output_path = Path("output.png")
                with open(output_path, "wb") as f:
                    f.write(result["image"])
                print(f"图像已保存到: {output_path}")
            else:
                print("生成图像失败")
                
        except Exception as e:
            print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 