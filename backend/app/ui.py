import os
import sys
import json
import base64
import requests
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from io import BytesIO
from typing import Optional, List, Dict, Any
import time
import uuid
from datetime import datetime
import threading

# 配置
COMFYUI_SERVER = "http://127.0.0.1:8188"  # ComfyUI服务器地址
GALLERY_DIR = "gallery"  # 作品库目录
os.makedirs(GALLERY_DIR, exist_ok=True)

# 工作流模板
TEXT_TO_IMAGE_WORKFLOW = {
    "3": {
        "inputs": {
            "text": "a beautiful sunset over mountains, high quality, detailed",
            "clip": ["4", 0]
        },
        "class_type": "CLIPTextEncode"
    },
    "4": {
        "inputs": {
            "ckpt_name": "sd_xl_base_1.0.safetensors"
        },
        "class_type": "CheckpointLoaderSimple"
    },
    "5": {
        "inputs": {
            "text": "ugly, blurry, low quality",
            "clip": ["4", 0]
        },
        "class_type": "CLIPTextEncode"
    },
    "6": {
        "inputs": {
            "samples": ["8", 0],
            "vae": ["4", 2],
            "positive": ["3", 0],
            "negative": ["5", 0],
            "latent_image": ["7", 0],
            "model": ["4", 0],
            "sampler_name": "euler",
            "scheduler": "normal",
            "seed": 8569857,
            "steps": 20,
            "cfg": 7,
            "denoise": 1
        },
        "class_type": "KSampler"
    },
    "7": {
        "inputs": {
            "width": 512,
            "height": 512,
            "batch_size": 1
        },
        "class_type": "EmptyLatentImage"
    },
    "8": {
        "inputs": {
            "samples": ["6", 0],
            "vae": ["4", 2]
        },
        "class_type": "VAEDecode"
    },
    "9": {
        "inputs": {
            "filename_prefix": "ComfyUI",
            "images": ["8", 0]
        },
        "class_type": "SaveImage"
    }
}

IMAGE_TO_IMAGE_WORKFLOW = {
    "3": {
        "inputs": {
            "text": "a beautiful sunset over mountains, high quality, detailed",
            "clip": ["4", 0]
        },
        "class_type": "CLIPTextEncode"
    },
    "4": {
        "inputs": {
            "ckpt_name": "sd_xl_base_1.0.safetensors"
        },
        "class_type": "CheckpointLoaderSimple"
    },
    "5": {
        "inputs": {
            "text": "ugly, blurry, low quality",
            "clip": ["4", 0]
        },
        "class_type": "CLIPTextEncode"
    },
    "6": {
        "inputs": {
            "samples": ["8", 0],
            "vae": ["4", 2],
            "positive": ["3", 0],
            "negative": ["5", 0],
            "latent_image": ["7", 0],
            "model": ["4", 0],
            "sampler_name": "euler",
            "scheduler": "normal",
            "seed": 8569857,
            "steps": 20,
            "cfg": 7,
            "denoise": 0.75
        },
        "class_type": "KSampler"
    },
    "7": {
        "inputs": {
            "image": ["10", 0],
            "vae": ["4", 2]
        },
        "class_type": "VAEEncode"
    },
    "8": {
        "inputs": {
            "samples": ["6", 0],
            "vae": ["4", 2]
        },
        "class_type": "VAEDecode"
    },
    "9": {
        "inputs": {
            "filename_prefix": "ComfyUI",
            "images": ["8", 0]
        },
        "class_type": "SaveImage"
    },
    "10": {
        "inputs": {
            "image": None
        },
        "class_type": "LoadImage"
    }
}

# 保存作品信息
def save_work_info(image_path: str, prompt: str, negative_prompt: str, is_variation: bool = False):
    info = {
        "id": str(uuid.uuid4()),
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "image_path": image_path,
        "is_variation": is_variation,
        "created_at": datetime.now().isoformat()
    }
    
    info_path = os.path.join(GALLERY_DIR, "works.json")
    works = []
    if os.path.exists(info_path):
        with open(info_path, "r", encoding="utf-8") as f:
            works = json.load(f)
    
    works.append(info)
    
    with open(info_path, "w", encoding="utf-8") as f:
        json.dump(works, f, ensure_ascii=False, indent=2)
    
    return info

# 获取作品列表
def get_works():
    info_path = os.path.join(GALLERY_DIR, "works.json")
    if not os.path.exists(info_path):
        return []
    
    with open(info_path, "r", encoding="utf-8") as f:
        works = json.load(f)
    
    return works

# 发送工作流到ComfyUI
def queue_prompt(workflow: Dict[str, Any]) -> str:
    p = {"prompt": workflow}
    data = json.dumps(p).encode('utf-8')
    req = requests.post(f"{COMFYUI_SERVER}/prompt", data=data)
    return req.json()['prompt_id']

# 等待图片生成完成
def wait_for_image(prompt_id: str) -> Optional[str]:
    while True:
        req = requests.get(f"{COMFYUI_SERVER}/history/{prompt_id}")
        if req.status_code == 200:
            history = req.json()
            if prompt_id in history:
                outputs = history[prompt_id]['outputs']
                if outputs:
                    for node_id in outputs:
                        node_output = outputs[node_id]
                        if 'images' in node_output:
                            image_data = node_output['images'][0]
                            return image_data['filename']
        time.sleep(0.5)

# 文生图
def text_to_image(prompt: str, negative_prompt: str, steps: int, cfg: float, width: int, height: int, status_callback=None):
    workflow = TEXT_TO_IMAGE_WORKFLOW.copy()
    
    # 更新工作流参数
    workflow["3"]["inputs"]["text"] = prompt
    workflow["5"]["inputs"]["text"] = negative_prompt
    workflow["6"]["inputs"]["steps"] = steps
    workflow["6"]["inputs"]["cfg"] = cfg
    workflow["7"]["inputs"]["width"] = width
    workflow["7"]["inputs"]["height"] = height
    
    if status_callback:
        status_callback("正在发送工作流到ComfyUI...")
    
    # 发送工作流
    prompt_id = queue_prompt(workflow)
    
    if status_callback:
        status_callback("正在生成图片，请稍候...")
    
    # 等待图片生成
    image_filename = wait_for_image(prompt_id)
    if not image_filename:
        if status_callback:
            status_callback("生成失败，请重试")
        return None, "生成失败，请重试"
    
    # 获取图片
    image_path = os.path.join("ComfyUI", "output", image_filename)
    if not os.path.exists(image_path):
        if status_callback:
            status_callback("图片文件不存在")
        return None, "图片文件不存在"
    
    # 保存到作品库
    gallery_filename = f"{uuid.uuid4()}.png"
    gallery_path = os.path.join(GALLERY_DIR, gallery_filename)
    Image.open(image_path).save(gallery_path)
    
    # 保存作品信息
    work_info = save_work_info(gallery_path, prompt, negative_prompt)
    
    if status_callback:
        status_callback(f"生成成功！作品ID: {work_info['id']}")
    
    return gallery_path, f"生成成功！作品ID: {work_info['id']}"

# 图生图
def image_to_image(image_path: str, prompt: str, negative_prompt: str, steps: int, cfg: float, denoise: float, status_callback=None):
    workflow = IMAGE_TO_IMAGE_WORKFLOW.copy()
    
    # 更新工作流参数
    workflow["3"]["inputs"]["text"] = prompt
    workflow["5"]["inputs"]["text"] = negative_prompt
    workflow["6"]["inputs"]["steps"] = steps
    workflow["6"]["inputs"]["cfg"] = cfg
    workflow["6"]["inputs"]["denoise"] = denoise
    
    # 更新工作流中的图片路径
    workflow["10"]["inputs"]["image"] = image_path
    
    if status_callback:
        status_callback("正在发送工作流到ComfyUI...")
    
    # 发送工作流
    prompt_id = queue_prompt(workflow)
    
    if status_callback:
        status_callback("正在生成图片，请稍候...")
    
    # 等待图片生成
    image_filename = wait_for_image(prompt_id)
    if not image_filename:
        if status_callback:
            status_callback("生成失败，请重试")
        return None, "生成失败，请重试"
    
    # 获取图片
    image_path = os.path.join("ComfyUI", "output", image_filename)
    if not os.path.exists(image_path):
        if status_callback:
            status_callback("图片文件不存在")
        return None, "图片文件不存在"
    
    # 保存到作品库
    gallery_filename = f"{uuid.uuid4()}.png"
    gallery_path = os.path.join(GALLERY_DIR, gallery_filename)
    Image.open(image_path).save(gallery_path)
    
    # 保存作品信息
    work_info = save_work_info(gallery_path, prompt, negative_prompt, is_variation=True)
    
    if status_callback:
        status_callback(f"生成成功！作品ID: {work_info['id']}")
    
    return gallery_path, f"生成成功！作品ID: {work_info['id']}"

# 加载作品
def load_work(work_id: str):
    works = get_works()
    for work in works:
        if work["id"] == work_id:
            if os.path.exists(work["image_path"]):
                return work["image_path"], work["prompt"], work["negative_prompt"]
    return None, None, None

# 创建UI
class AIGCApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AIGC图像生成平台")
        self.root.geometry("800x600")
        
        # 创建标签页
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 文生图标签页
        self.txt2img_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.txt2img_frame, text="文生图")
        self.setup_txt2img_tab()
        
        # 图生图标签页
        self.img2img_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.img2img_frame, text="图生图")
        self.setup_img2img_tab()
        
        # 作品库标签页
        self.gallery_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.gallery_frame, text="作品库")
        self.setup_gallery_tab()
    
    def setup_txt2img_tab(self):
        # 左侧控制面板
        control_frame = ttk.Frame(self.txt2img_frame)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        # 提示词
        ttk.Label(control_frame, text="提示词:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.txt2img_prompt = tk.Text(control_frame, width=30, height=3)
        self.txt2img_prompt.grid(row=0, column=1, pady=5)
        
        # 反向提示词
        ttk.Label(control_frame, text="反向提示词:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.txt2img_negative_prompt = tk.Text(control_frame, width=30, height=3)
        self.txt2img_negative_prompt.grid(row=1, column=1, pady=5)
        
        # 步数
        ttk.Label(control_frame, text="步数:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.txt2img_steps = tk.Scale(control_frame, from_=1, to=100, orient=tk.HORIZONTAL, length=200)
        self.txt2img_steps.set(20)
        self.txt2img_steps.grid(row=2, column=1, pady=5)
        
        # CFG
        ttk.Label(control_frame, text="CFG:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.txt2img_cfg = tk.Scale(control_frame, from_=1, to=20, orient=tk.HORIZONTAL, length=200, resolution=0.5)
        self.txt2img_cfg.set(7)
        self.txt2img_cfg.grid(row=3, column=1, pady=5)
        
        # 宽度
        ttk.Label(control_frame, text="宽度:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.txt2img_width = tk.Scale(control_frame, from_=256, to=1024, orient=tk.HORIZONTAL, length=200, resolution=64)
        self.txt2img_width.set(512)
        self.txt2img_width.grid(row=4, column=1, pady=5)
        
        # 高度
        ttk.Label(control_frame, text="高度:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.txt2img_height = tk.Scale(control_frame, from_=256, to=1024, orient=tk.HORIZONTAL, length=200, resolution=64)
        self.txt2img_height.set(512)
        self.txt2img_height.grid(row=5, column=1, pady=5)
        
        # 生成按钮
        self.txt2img_generate_btn = ttk.Button(control_frame, text="生成", command=self.generate_txt2img)
        self.txt2img_generate_btn.grid(row=6, column=0, columnspan=2, pady=10)
        
        # 右侧预览区域
        preview_frame = ttk.Frame(self.txt2img_frame)
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 状态信息
        self.txt2img_status = ttk.Label(preview_frame, text="就绪")
        self.txt2img_status.pack(fill=tk.X, pady=5)
        
        # 图片预览
        self.txt2img_preview = ttk.Label(preview_frame)
        self.txt2img_preview.pack(fill=tk.BOTH, expand=True)
    
    def setup_img2img_tab(self):
        # 左侧控制面板
        control_frame = ttk.Frame(self.img2img_frame)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        # 输入图片
        ttk.Label(control_frame, text="输入图片:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.img2img_input_path = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.img2img_input_path, width=30).grid(row=0, column=1, pady=5)
        ttk.Button(control_frame, text="浏览", command=self.browse_input_image).grid(row=0, column=2, pady=5)
        
        # 输入图片预览
        self.img2img_input_preview = ttk.Label(control_frame)
        self.img2img_input_preview.grid(row=1, column=0, columnspan=3, pady=5)
        
        # 提示词
        ttk.Label(control_frame, text="提示词:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.img2img_prompt = tk.Text(control_frame, width=30, height=3)
        self.img2img_prompt.grid(row=2, column=1, columnspan=2, pady=5)
        
        # 反向提示词
        ttk.Label(control_frame, text="反向提示词:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.img2img_negative_prompt = tk.Text(control_frame, width=30, height=3)
        self.img2img_negative_prompt.grid(row=3, column=1, columnspan=2, pady=5)
        
        # 步数
        ttk.Label(control_frame, text="步数:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.img2img_steps = tk.Scale(control_frame, from_=1, to=100, orient=tk.HORIZONTAL, length=200, resolution=1)
        self.img2img_steps.set(20)
        self.img2img_steps.grid(row=4, column=1, columnspan=2, pady=5)
        
        # CFG
        ttk.Label(control_frame, text="CFG:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.img2img_cfg = tk.Scale(control_frame, from_=1, to=20, orient=tk.HORIZONTAL, length=200, resolution=0.5)
        self.img2img_cfg.set(7)
        self.img2img_cfg.grid(row=5, column=1, columnspan=2, pady=5)
        
        # 去噪强度
        ttk.Label(control_frame, text="去噪强度:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.img2img_denoise = tk.Scale(control_frame, from_=0, to=1, orient=tk.HORIZONTAL, length=200, resolution=0.05)
        self.img2img_denoise.set(0.75)
        self.img2img_denoise.grid(row=6, column=1, columnspan=2, pady=5)
        
        # 生成按钮
        self.img2img_generate_btn = ttk.Button(control_frame, text="生成", command=self.generate_img2img)
        self.img2img_generate_btn.grid(row=7, column=0, columnspan=3, pady=10)
        
        # 右侧预览区域
        preview_frame = ttk.Frame(self.img2img_frame)
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 状态信息
        self.img2img_status = ttk.Label(preview_frame, text="就绪")
        self.img2img_status.pack(fill=tk.X, pady=5)
        
        # 图片预览
        self.img2img_preview = ttk.Label(preview_frame)
        self.img2img_preview.pack(fill=tk.BOTH, expand=True)
    
    def setup_gallery_tab(self):
        # 左侧作品列表
        list_frame = ttk.Frame(self.gallery_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        ttk.Label(list_frame, text="作品列表:").pack(anchor=tk.W, pady=5)
        
        # 作品列表
        self.works_listbox = tk.Listbox(list_frame, width=50, height=20)
        self.works_listbox.pack(fill=tk.Y, pady=5)
        self.works_listbox.bind("<<ListboxSelect>>", self.on_work_selected)
        
        # 加载作品列表
        self.load_works_list()
        
        # 右侧作品详情
        detail_frame = ttk.Frame(self.gallery_frame)
        detail_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 作品图片
        self.gallery_image = ttk.Label(detail_frame)
        self.gallery_image.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 作品信息
        info_frame = ttk.Frame(detail_frame)
        info_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(info_frame, text="提示词:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.gallery_prompt = tk.Text(info_frame, width=50, height=3)
        self.gallery_prompt.grid(row=0, column=1, pady=5)
        
        ttk.Label(info_frame, text="反向提示词:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.gallery_negative_prompt = tk.Text(info_frame, width=50, height=3)
        self.gallery_negative_prompt.grid(row=1, column=1, pady=5)
    
    def load_works_list(self):
        self.works_listbox.delete(0, tk.END)
        works = get_works()
        for work in works:
            self.works_listbox.insert(tk.END, f"{work['id']} - {work['prompt'][:30]}...")
    
    def on_work_selected(self, event):
        selection = self.works_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        works = get_works()
        if index < len(works):
            work = works[index]
            image_path, prompt, negative_prompt = load_work(work["id"])
            
            if image_path:
                # 显示图片
                img = Image.open(image_path)
                img = self.resize_image(img, 512, 512)
                photo = ImageTk.PhotoImage(img)
                self.gallery_image.configure(image=photo)
                self.gallery_image.image = photo
                
                # 显示提示词
                self.gallery_prompt.delete(1.0, tk.END)
                self.gallery_prompt.insert(tk.END, prompt)
                
                # 显示反向提示词
                self.gallery_negative_prompt.delete(1.0, tk.END)
                self.gallery_negative_prompt.insert(tk.END, negative_prompt)
    
    def browse_input_image(self):
        file_path = filedialog.askopenfilename(
            title="选择输入图片",
            filetypes=[("图片文件", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if file_path:
            self.img2img_input_path.set(file_path)
            
            # 显示预览
            img = Image.open(file_path)
            img = self.resize_image(img, 256, 256)
            photo = ImageTk.PhotoImage(img)
            self.img2img_input_preview.configure(image=photo)
            self.img2img_input_preview.image = photo
    
    def resize_image(self, img, max_width, max_height):
        width, height = img.size
        ratio = min(max_width / width, max_height / height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        return img.resize((new_width, new_height), Image.LANCZOS)
    
    def update_status(self, status_label, message):
        status_label.config(text=message)
        self.root.update()
    
    def generate_txt2img(self):
        prompt = self.txt2img_prompt.get(1.0, tk.END).strip()
        negative_prompt = self.txt2img_negative_prompt.get(1.0, tk.END).strip()
        steps = int(self.txt2img_steps.get())
        cfg = float(self.txt2img_cfg.get())
        width = int(self.txt2img_width.get())
        height = int(self.txt2img_height.get())
        
        if not prompt:
            messagebox.showerror("错误", "请输入提示词")
            return
        
        # 禁用生成按钮
        self.txt2img_generate_btn.config(state=tk.DISABLED)
        
        # 在新线程中生成图片
        def generate():
            def status_callback(message):
                self.root.after(0, lambda: self.update_status(self.txt2img_status, message))
            
            image_path, message = text_to_image(
                prompt, negative_prompt, steps, cfg, width, height, status_callback
            )
            
            if image_path:
                # 显示图片
                img = Image.open(image_path)
                img = self.resize_image(img, 512, 512)
                photo = ImageTk.PhotoImage(img)
                self.root.after(0, lambda: self.txt2img_preview.configure(image=photo))
                self.root.after(0, lambda: setattr(self.txt2img_preview, 'image', photo))
            
            # 启用生成按钮
            self.root.after(0, lambda: self.txt2img_generate_btn.config(state=tk.NORMAL))
            
            # 刷新作品列表
            self.root.after(0, self.load_works_list)
        
        threading.Thread(target=generate).start()
    
    def generate_img2img(self):
        input_path = self.img2img_input_path.get()
        prompt = self.img2img_prompt.get(1.0, tk.END).strip()
        negative_prompt = self.img2img_negative_prompt.get(1.0, tk.END).strip()
        steps = int(self.img2img_steps.get())
        cfg = float(self.img2img_cfg.get())
        denoise = float(self.img2img_denoise.get())
        
        if not input_path:
            messagebox.showerror("错误", "请选择输入图片")
            return
        
        if not prompt:
            messagebox.showerror("错误", "请输入提示词")
            return
        
        # 禁用生成按钮
        self.img2img_generate_btn.config(state=tk.DISABLED)
        
        # 在新线程中生成图片
        def generate():
            def status_callback(message):
                self.root.after(0, lambda: self.update_status(self.img2img_status, message))
            
            image_path, message = image_to_image(
                input_path, prompt, negative_prompt, steps, cfg, denoise, status_callback
            )
            
            if image_path:
                # 显示图片
                img = Image.open(image_path)
                img = self.resize_image(img, 512, 512)
                photo = ImageTk.PhotoImage(img)
                self.root.after(0, lambda: self.img2img_preview.configure(image=photo))
                self.root.after(0, lambda: setattr(self.img2img_preview, 'image', photo))
            
            # 启用生成按钮
            self.root.after(0, lambda: self.img2img_generate_btn.config(state=tk.NORMAL))
            
            # 刷新作品列表
            self.root.after(0, self.load_works_list)
        
        threading.Thread(target=generate).start()

# 启动UI
def run_ui():
    root = tk.Tk()
    app = AIGCApp(root)
    root.mainloop()

if __name__ == "__main__":
    run_ui() 