# AIGC图像生成平台开发计划

## 开发路线图

### 第一阶段：核心架构和基础功能

1. **项目结构搭建**
2. **ComfyUI集成模块**
3. **基础UI框架**
4. **文生图基础功能**
5. **图生图基础功能**
6. **作品库基础功能**

### 第二阶段：高级功能

7. **模板系统**
8. **提示词优化功能**
9. **AI引擎选择功能**
10. **一键同款功能**
11. **主题扩写功能**

### 第三阶段：集成和优化

12. **多AI引擎集成**
13. **性能优化**
14. **UI美化**
15. **文档完善**

## 第一阶段开发计划

### 1. 项目结构搭建

首先，我们需要搭建项目的基本结构，包括目录组织、依赖管理和配置文件。

#### 测试代码

```python
# tests/test_project_structure.py
import os
import sys
import unittest

class TestProjectStructure(unittest.TestCase):
    def test_directory_structure(self):
        """测试项目目录结构是否正确"""
        required_dirs = [
            'app',
            'app/api',
            'app/api/v1',
            'app/core',
            'app/database',
            'app/models',
            'app/services',
            'app/ui',
            'app/utils',
            'tests',
            'templates',
            'gallery'
        ]
        
        for dir_path in required_dirs:
            self.assertTrue(os.path.exists(dir_path), f"目录 {dir_path} 不存在")
    
    def test_required_files(self):
        """测试必要文件是否存在"""
        required_files = [
            'requirements.txt',
            'README.md',
            '.env.example',
            'app/main.py',
            'app/core/config.py',
            'app/database/database.py',
            'app/api/v1/api.py'
        ]
        
        for file_path in required_files:
            self.assertTrue(os.path.exists(file_path), f"文件 {file_path} 不存在")

if __name__ == '__main__':
    unittest.main()
```

#### 预期效果

- 项目目录结构完整
- 所有必要文件存在
- 测试通过

### 2. ComfyUI集成模块

接下来，我们需要开发与ComfyUI服务器通信的模块。

#### 测试代码

```python
# tests/test_comfyui_integration.py
import unittest
import json
import requests
from unittest.mock import patch, MagicMock
from app.services.comfyui_service import ComfyUIService

class TestComfyUIService(unittest.TestCase):
    def setUp(self):
        self.service = ComfyUIService()
    
    @patch('requests.post')
    def test_queue_prompt(self, mock_post):
        """测试发送工作流到ComfyUI"""
        # 模拟响应
        mock_response = MagicMock()
        mock_response.json.return_value = {'prompt_id': 'test_prompt_id'}
        mock_post.return_value = mock_response
        
        # 测试数据
        workflow = {
            "3": {
                "inputs": {
                    "text": "test prompt",
                    "clip": ["4", 0]
                },
                "class_type": "CLIPTextEncode"
            }
        }
        
        # 调用方法
        prompt_id = self.service.queue_prompt(workflow)
        
        # 验证结果
        self.assertEqual(prompt_id, 'test_prompt_id')
        mock_post.assert_called_once()
    
    @patch('requests.get')
    def test_wait_for_image(self, mock_get):
        """测试等待图片生成完成"""
        # 模拟响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'test_prompt_id': {
                'outputs': {
                    '9': {
                        'images': [
                            {'filename': 'test_image.png'}
                        ]
                    }
                }
            }
        }
        mock_get.return_value = mock_response
        
        # 调用方法
        image_filename = self.service.wait_for_image('test_prompt_id')
        
        # 验证结果
        self.assertEqual(image_filename, 'test_image.png')
        mock_get.assert_called()

if __name__ == '__main__':
    unittest.main()
```

#### 预期效果

- ComfyUI服务模块能够成功发送工作流
- 能够等待并获取生成的图像
- 测试通过

### 3. 基础UI框架

然后，我们需要开发基础的UI框架，包括主窗口和标签页。

#### 测试代码

```python
# tests/test_ui_framework.py
import unittest
import tkinter as tk
from app.ui.app import AIGCApp

class TestUIFramework(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = AIGCApp(self.root)
    
    def tearDown(self):
        self.root.destroy()
    
    def test_notebook_tabs(self):
        """测试标签页是否正确创建"""
        # 获取所有标签页
        tabs = self.app.notebook.tabs()
        
        # 验证标签页数量
        self.assertEqual(len(tabs), 6, "应该有6个标签页")
        
        # 验证标签页名称
        tab_names = [self.app.notebook.tab(tab)['text'] for tab in tabs]
        expected_names = ['文生图', '图生图', '一键同款', '主题扩写', '提示词优化', '作品库']
        
        for name in expected_names:
            self.assertIn(name, tab_names, f"缺少标签页: {name}")
    
    def test_txt2img_tab(self):
        """测试文生图标签页"""
        # 获取文生图标签页
        txt2img_frame = None
        for tab in self.app.notebook.tabs():
            if self.app.notebook.tab(tab)['text'] == '文生图':
                txt2img_frame = self.app.notebook.select(tab)
                break
        
        self.assertIsNotNone(txt2img_frame, "找不到文生图标签页")
        
        # 验证文生图标签页的组件
        self.assertIsNotNone(self.app.txt2img_prompt, "缺少提示词输入框")
        self.assertIsNotNone(self.app.txt2img_negative_prompt, "缺少反向提示词输入框")
        self.assertIsNotNone(self.app.txt2img_generate_btn, "缺少生成按钮")

if __name__ == '__main__':
    unittest.main()
```

#### 预期效果

- UI框架成功创建
- 所有标签页正确显示
- 文生图标签页包含所有必要组件
- 测试通过

### 4. 文生图基础功能

接下来，我们需要实现文生图的基础功能。

#### 测试代码

```python
# tests/test_txt2img.py
import unittest
import os
import json
from unittest.mock import patch, MagicMock
from app.ui.app import AIGCApp
import tkinter as tk

class TestTextToImage(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = AIGCApp(self.root)
    
    def tearDown(self):
        self.root.destroy()
    
    @patch('app.services.comfyui_service.ComfyUIService.queue_prompt')
    @patch('app.services.comfyui_service.ComfyUIService.wait_for_image')
    @patch('app.services.work_service.WorkService.save_work')
    def test_generate_txt2img(self, mock_save_work, mock_wait_for_image, mock_queue_prompt):
        """测试文生图功能"""
        # 模拟响应
        mock_queue_prompt.return_value = 'test_prompt_id'
        mock_wait_for_image.return_value = 'test_image.png'
        mock_save_work.return_value = {'id': 'test_work_id'}
        
        # 设置输入
        self.app.txt2img_prompt.delete(1.0, tk.END)
        self.app.txt2img_prompt.insert(tk.END, 'test prompt')
        
        self.app.txt2img_negative_prompt.delete(1.0, tk.END)
        self.app.txt2img_negative_prompt.insert(tk.END, 'test negative prompt')
        
        # 调用生成方法
        self.app.generate_txt2img()
        
        # 验证结果
        mock_queue_prompt.assert_called_once()
        mock_wait_for_image.assert_called_once_with('test_prompt_id')
        mock_save_work.assert_called_once()
        
        # 验证工作流参数
        workflow = mock_queue_prompt.call_args[0][0]
        self.assertEqual(workflow['3']['inputs']['text'], 'test prompt')
        self.assertEqual(workflow['5']['inputs']['text'], 'test negative prompt')

if __name__ == '__main__':
    unittest.main()
```

#### 预期效果

- 文生图功能能够成功生成图像
- 提示词和反向提示词正确传递到ComfyUI
- 生成的图像保存到作品库
- 测试通过

### 5. 图生图基础功能

然后，我们需要实现图生图的基础功能。

#### 测试代码

```python
# tests/test_img2img.py
import unittest
import os
import json
from unittest.mock import patch, MagicMock
from app.ui.app import AIGCApp
import tkinter as tk
from PIL import Image
import io

class TestImageToImage(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = AIGCApp(self.root)
        
        # 创建测试图像
        self.test_image = Image.new('RGB', (100, 100), color='red')
        self.test_image_path = 'test_image.png'
        self.test_image.save(self.test_image_path)
    
    def tearDown(self):
        self.root.destroy()
        if os.path.exists(self.test_image_path):
            os.remove(self.test_image_path)
    
    @patch('app.services.comfyui_service.ComfyUIService.queue_prompt')
    @patch('app.services.comfyui_service.ComfyUIService.wait_for_image')
    @patch('app.services.work_service.WorkService.save_work')
    def test_generate_img2img(self, mock_save_work, mock_wait_for_image, mock_queue_prompt):
        """测试图生图功能"""
        # 模拟响应
        mock_queue_prompt.return_value = 'test_prompt_id'
        mock_wait_for_image.return_value = 'test_output_image.png'
        mock_save_work.return_value = {'id': 'test_work_id'}
        
        # 设置输入
        self.app.img2img_input_path.set(self.test_image_path)
        
        self.app.img2img_prompt.delete(1.0, tk.END)
        self.app.img2img_prompt.insert(tk.END, 'test prompt')
        
        self.app.img2img_negative_prompt.delete(1.0, tk.END)
        self.app.img2img_negative_prompt.insert(tk.END, 'test negative prompt')
        
        # 调用生成方法
        self.app.generate_img2img()
        
        # 验证结果
        mock_queue_prompt.assert_called_once()
        mock_wait_for_image.assert_called_once_with('test_prompt_id')
        mock_save_work.assert_called_once()
        
        # 验证工作流参数
        workflow = mock_queue_prompt.call_args[0][0]
        self.assertEqual(workflow['3']['inputs']['text'], 'test prompt')
        self.assertEqual(workflow['5']['inputs']['text'], 'test negative prompt')
        self.assertEqual(workflow['10']['inputs']['image'], self.test_image_path)

if __name__ == '__main__':
    unittest.main()
```

#### 预期效果

- 图生图功能能够成功生成图像
- 输入图像、提示词和反向提示词正确传递到ComfyUI
- 生成的图像保存到作品库
- 测试通过

### 6. 作品库基础功能

最后，我们需要实现作品库的基础功能。

#### 测试代码

```python
# tests/test_gallery.py
import unittest
import os
import json
import shutil
from unittest.mock import patch, MagicMock
from app.ui.app import AIGCApp
from app.services.work_service import WorkService
import tkinter as tk
from PIL import Image
import io

class TestGallery(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = AIGCApp(self.root)
        
        # 创建测试作品
        self.gallery_dir = 'gallery'
        os.makedirs(self.gallery_dir, exist_ok=True)
        
        # 创建测试图像
        self.test_image = Image.new('RGB', (100, 100), color='blue')
        self.test_image_path = os.path.join(self.gallery_dir, 'test_work.png')
        self.test_image.save(self.test_image_path)
        
        # 创建测试作品信息
        self.works_file = os.path.join(self.gallery_dir, 'works.json')
        self.test_work = {
            'id': 'test_work_id',
            'prompt': 'test prompt',
            'negative_prompt': 'test negative prompt',
            'image_path': self.test_image_path,
            'is_variation': False,
            'created_at': '2023-01-01T00:00:00'
        }
        
        with open(self.works_file, 'w') as f:
            json.dump([self.test_work], f)
    
    def tearDown(self):
        self.root.destroy()
        if os.path.exists(self.gallery_dir):
            shutil.rmtree(self.gallery_dir)
    
    def test_load_works(self):
        """测试加载作品列表"""
        # 调用加载方法
        self.app.load_works_list()
        
        # 验证作品列表
        self.assertEqual(self.app.works_listbox.size(), 1, "作品列表应该包含1个作品")
        
        # 验证作品信息
        work_text = self.app.works_listbox.get(0)
        self.assertIn('test_work_id', work_text, "作品列表应该包含作品ID")
        self.assertIn('test prompt', work_text, "作品列表应该包含提示词")
    
    def test_select_work(self):
        """测试选择作品"""
        # 加载作品列表
        self.app.load_works_list()
        
        # 选择作品
        self.app.works_listbox.select_set(0)
        self.app.on_work_selected(None)
        
        # 验证作品详情
        self.assertEqual(self.app.gallery_prompt.get(1.0, tk.END).strip(), 'test prompt', "提示词应该正确显示")
        self.assertEqual(self.app.gallery_negative_prompt.get(1.0, tk.END).strip(), 'test negative prompt', "反向提示词应该正确显示")

if __name__ == '__main__':
    unittest.main()
```

#### 预期效果

- 作品库能够正确加载作品列表
- 能够选择并查看作品详情
- 作品信息正确显示
- 测试通过

## 第二阶段开发计划

### 7. 模板系统

接下来，我们将实现模板系统。

#### 测试代码

```python
# tests/test_templates.py
import unittest
import os
import json
from unittest.mock import patch, MagicMock
from app.ui.app import AIGCApp
from app.services.template_service import TemplateService
import tkinter as tk

class TestTemplates(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = AIGCApp(self.root)
        
        # 创建测试模板
        self.templates_dir = 'templates'
        os.makedirs(self.templates_dir, exist_ok=True)
        
        # 创建测试模板文件
        self.test_template = {
            'id': 'test_template_id',
            'name': '测试模板',
            'category': '人物',
            'style': '写实',
            'prompt_template': 'test {gender} person, {age} years old',
            'negative_prompt_template': 'test negative prompt',
            'parameters': {
                'steps': 20,
                'cfg': 7,
                'width': 512,
                'height': 512
            }
        }
        
        self.template_file = os.path.join(self.templates_dir, 'test_template.json')
        with open(self.template_file, 'w') as f:
            json.dump(self.test_template, f)
    
    def tearDown(self):
        self.root.destroy()
        if os.path.exists(self.templates_dir):
            import shutil
            shutil.rmtree(self.templates_dir)
    
    def test_load_templates(self):
        """测试加载模板列表"""
        # 调用加载方法
        self.app.load_templates()
        
        # 验证模板列表
        self.assertEqual(len(self.app.templates), 1, "模板列表应该包含1个模板")
        
        # 验证模板信息
        template = self.app.templates[0]
        self.assertEqual(template['id'], 'test_template_id', "模板ID应该正确")
        self.assertEqual(template['name'], '测试模板', "模板名称应该正确")
    
    def test_apply_template(self):
        """测试应用模板"""
        # 加载模板
        self.app.load_templates()
        
        # 选择模板
        self.app.txt2img_template_var.set('test_template_id')
        
        # 应用模板
        self.app.apply_template()
        
        # 验证提示词
        self.assertEqual(self.app.txt2img_prompt.get(1.0, tk.END).strip(), 'test {gender} person, {age} years old', "提示词应该正确应用")
        self.assertEqual(self.app.txt2img_negative_prompt.get(1.0, tk.END).strip(), 'test negative prompt', "反向提示词应该正确应用")
        
        # 验证参数
        self.assertEqual(self.app.txt2img_steps.get(), 20, "步数应该正确应用")
        self.assertEqual(self.app.txt2img_cfg.get(), 7, "CFG应该正确应用")
        self.assertEqual(self.app.txt2img_width.get(), 512, "宽度应该正确应用")
        self.assertEqual(self.app.txt2img_height.get(), 512, "高度应该正确应用")

if __name__ == '__main__':
    unittest.main()
```

#### 预期效果

- 模板系统能够正确加载模板列表
- 能够选择并应用模板
- 模板参数正确应用到文生图或图生图功能
- 测试通过

### 8. 提示词优化功能

接下来，我们将实现提示词优化功能。

#### 测试代码

```python
# tests/test_prompt_optimization.py
import unittest
from unittest.mock import patch, MagicMock
from app.ui.app import AIGCApp
from app.services.prompt_service import PromptService
import tkinter as tk

class TestPromptOptimization(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = AIGCApp(self.root)
    
    def tearDown(self):
        self.root.destroy()
    
    @patch('app.services.prompt_service.PromptService.optimize_prompt')
    def test_optimize_prompt(self, mock_optimize):
        """测试提示词优化功能"""
        # 模拟响应
        mock_optimize.return_value = {
            'optimized_prompt': 'optimized test prompt',
            'explanation': '优化说明'
        }
        
        # 设置输入
        self.app.original_prompt.delete(1.0, tk.END)
        self.app.original_prompt.insert(tk.END, 'test prompt')
        
        # 调用优化方法
        self.app.optimize_prompt()
        
        # 验证结果
        mock_optimize.assert_called_once_with('test prompt', 'default', 3, 'en')
        
        # 验证优化后的提示词
        self.assertEqual(self.app.optimized_prompt.get(1.0, tk.END).strip(), 'optimized test prompt', "优化后的提示词应该正确显示")
        
        # 验证优化说明
        self.assertEqual(self.app.optimization_explanation.get(1.0, tk.END).strip(), '优化说明', "优化说明应该正确显示")
    
    def test_use_optimized_prompt(self):
        """测试使用优化后的提示词"""
        # 设置优化后的提示词
        self.app.optimized_prompt.delete(1.0, tk.END)
        self.app.optimized_prompt.insert(tk.END, 'optimized test prompt')
        
        # 调用使用方法
        self.app.use_optimized_prompt()
        
        # 验证提示词已应用到文生图
        self.assertEqual(self.app.txt2img_prompt.get(1.0, tk.END).strip(), 'optimized test prompt', "优化后的提示词应该应用到文生图")
        
        # 验证已切换到文生图标签页
        current_tab = self.app.notebook.select()
        self.assertEqual(self.app.notebook.tab(current_tab)['text'], '文生图', "应该切换到文生图标签页")

if __name__ == '__main__':
    unittest.main()
```

#### 预期效果

- 提示词优化功能能够成功优化提示词
- 优化后的提示词和说明正确显示
- 能够将优化后的提示词应用到文生图或图生图功能
- 测试通过

### 9. AI引擎选择功能

接下来，我们将实现AI引擎选择功能。

#### 测试代码

```python
# tests/test_ai_engine_selection.py
import unittest
from unittest.mock import patch, MagicMock
from app.ui.app import AIGCApp
from app.services.ai_engine_service import AIEngineService
import tkinter as tk

class TestAIEngineSelection(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = AIGCApp(self.root)
    
    def tearDown(self):
        self.root.destroy()
    
    @patch('app.services.ai_engine_service.AIEngineService.recommend_engine')
    def test_recommend_engine(self, mock_recommend):
        """测试AI引擎推荐功能"""
        # 模拟响应
        mock_recommend.return_value = {
            'recommended_engine': 'comfyui',
            'engines': [
                {
                    'id': 'comfyui',
                    'name': 'ComfyUI',
                    'description': '高度可定制的工作流',
                    'strengths': ['可定制性高', '支持多种模型'],
                    'weaknesses': ['学习曲线陡峭'],
                    'best_for': ['精细控制', '自定义工作流']
                },
                {
                    'id': 'stable-diffusion',
                    'name': 'Stable Diffusion',
                    'description': '平衡的速度和质量',
                    'strengths': ['社区支持强', '速度较快'],
                    'weaknesses': ['可定制性较低'],
                    'best_for': ['一般用途', '快速生成']
                }
            ]
        }
        
        # 设置输入
        self.app.txt2img_prompt.delete(1.0, tk.END)
        self.app.txt2img_prompt.insert(tk.END, 'test prompt')
        
        # 调用推荐方法
        self.app.recommend_engine()
        
        # 验证结果
        mock_recommend.assert_called_once_with('test prompt', None)
        
        # 验证推荐的引擎
        self.assertEqual(self.app.txt2img_ai_engine_var.get(), 'comfyui', "推荐的引擎应该正确设置")
        
        # 验证引擎信息显示
        self.assertIn('ComfyUI', self.app.ai_engine_info.get(1.0, tk.END), "引擎信息应该包含ComfyUI")
        self.assertIn('Stable Diffusion', self.app.ai_engine_info.get(1.0, tk.END), "引擎信息应该包含Stable Diffusion")
    
    def test_select_engine(self):
        """测试选择AI引擎"""
        # 设置引擎列表
        self.app.ai_engines = [
            {
                'id': 'comfyui',
                'name': 'ComfyUI',
                'description': '高度可定制的工作流'
            },
            {
                'id': 'stable-diffusion',
                'name': 'Stable Diffusion',
                'description': '平衡的速度和质量'
            }
        ]
        
        # 选择引擎
        self.app.txt2img_ai_engine_var.set('stable-diffusion')
        self.app.on_engine_selected()
        
        # 验证引擎信息显示
        self.assertIn('Stable Diffusion', self.app.ai_engine_info.get(1.0, tk.END), "引擎信息应该包含Stable Diffusion")
        self.assertIn('平衡的速度和质量', self.app.ai_engine_info.get(1.0, tk.END), "引擎信息应该包含描述")

if __name__ == '__main__':
    unittest.main()
```

#### 预期效果

- AI引擎推荐功能能够成功推荐最适合的引擎
- 推荐的引擎和引擎信息正确显示
- 能够手动选择其他引擎
- 测试通过

### 10. 一键同款功能

接下来，我们将实现一键同款功能。

#### 测试代码

```python
# tests/test_similar_style.py
import unittest
import os
from unittest.mock import patch, MagicMock
from app.ui.app import AIGCApp
from app.services.similar_style_service import SimilarStyleService
import tkinter as tk
from PIL import Image
import io

class TestSimilarStyle(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = AIGCApp(self.root)
        
        # 创建测试图像
        self.test_image = Image.new('RGB', (100, 100), color='green')
        self.test_image_path = 'test_reference.png'
        self.test_image.save(self.test_image_path)
    
    def tearDown(self):
        self.root.destroy()
        if os.path.exists(self.test_image_path):
            os.remove(self.test_image_path)
    
    @patch('app.services.similar_style_service.SimilarStyleService.analyze_image')
    def test_analyze_image(self, mock_analyze):
        """测试图像分析功能"""
        # 模拟响应
        mock_analyze.return_value = {
            'style': 'realistic',
            'colors': ['red', 'blue'],
            'composition': 'portrait',
            'prompt': 'analyzed test prompt'
        }
        
        # 设置输入
        self.app.similar_style_input_path.set(self.test_image_path)
        
        # 调用分析方法
        self.app.analyze_reference_image()
        
        # 验证结果
        mock_analyze.assert_called_once_with(self.test_image_path)
        
        # 验证生成的提示词
        self.assertEqual(self.app.similar_style_prompt.get(1.0, tk.END).strip(), 'analyzed test prompt', "生成的提示词应该正确显示")
    
    @patch('app.services.similar_style_service.SimilarStyleService.analyze_image')
    @patch('app.services.comfyui_service.ComfyUIService.queue_prompt')
    @patch('app.services.comfyui_service.ComfyUIService.wait_for_image')
    @patch('app.services.work_service.WorkService.save_work')
    def test_generate_similar_style(self, mock_save_work, mock_wait_for_image, mock_queue_prompt, mock_analyze):
        """测试一键同款功能"""
        # 模拟响应
        mock_analyze.return_value = {
            'style': 'realistic',
            'colors': ['red', 'blue'],
            'composition': 'portrait',
            'prompt': 'analyzed test prompt'
        }
        mock_queue_prompt.return_value = 'test_prompt_id'
        mock_wait_for_image.return_value = 'test_output_image.png'
        mock_save_work.return_value = {'id': 'test_work_id'}
        
        # 设置输入
        self.app.similar_style_input_path.set(self.test_image_path)
        
        # 调用生成方法
        self.app.generate_similar_style()
        
        # 验证结果
        mock_analyze.assert_called_once_with(self.test_image_path)
        mock_queue_prompt.assert_called_once()
        mock_wait_for_image.assert_called_once_with('test_prompt_id')
        mock_save_work.assert_called_once()
        
        # 验证工作流参数
        workflow = mock_queue_prompt.call_args[0][0]
        self.assertEqual(workflow['3']['inputs']['text'], 'analyzed test prompt', "提示词应该正确传递")

if __name__ == '__main__':
    unittest.main()
```

#### 预期效果

- 一键同款功能能够成功分析参考图像
- 能够生成与参考图像风格相似的提示词
- 能够使用生成的提示词生成图像
- 生成的图像保存到作品库
- 测试通过

### 11. 主题扩写功能

最后，我们将实现主题扩写功能。

#### 测试代码

```python
# tests/test_theme_expansion.py
import unittest
from unittest.mock import patch, MagicMock
from app.ui.app import AIGCApp
from app.services.theme_service import ThemeService
import tkinter as tk

class TestThemeExpansion(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = AIGCApp(self.root)
    
    def tearDown(self):
        self.root.destroy()
    
    @patch('app.services.theme_service.ThemeService.expand_theme')
    def test_expand_theme(self, mock_expand):
        """测试主题扩写功能"""
        # 模拟响应
        mock_expand.return_value = {
            'expanded_prompt': 'expanded test theme prompt',
            'ai_engine': 'comfyui'
        }
        
        # 设置输入
        self.app.theme_input.delete(0, tk.END)
        self.app.theme_input.insert(0, 'test theme')
        
        # 调用扩写方法
        self.app.expand_theme()
        
        # 验证结果
        mock_expand.assert_called_once_with('test theme', 'default', 3, 'en')
        
        # 验证扩写后的提示词
        self.assertEqual(self.app.expanded_prompt.get(1.0, tk.END).strip(), 'expanded test theme prompt', "扩写后的提示词应该正确显示")
        
        # 验证推荐的引擎
        self.assertEqual(self.app.theme_ai_engine_var.get(), 'comfyui', "推荐的引擎应该正确设置")
    
    def test_use_expanded_prompt(self):
        """测试使用扩写后的提示词"""
        # 设置扩写后的提示词
        self.app.expanded_prompt.delete(1.0, tk.END)
        self.app.expanded_prompt.insert(tk.END, 'expanded test theme prompt')
        
        # 调用使用方法
        self.app.use_expanded_prompt()
        
        # 验证提示词已应用到文生图
        self.assertEqual(self.app.txt2img_prompt.get(1.0, tk.END).strip(), 'expanded test theme prompt', "扩写后的提示词应该应用到文生图")
        
        # 验证已切换到文生图标签页
        current_tab = self.app.notebook.select()
        self.assertEqual(self.app.notebook.tab(current_tab)['text'], '文生图', "应该切换到文生图标签页")

if __name__ == '__main__':
    unittest.main()
```

#### 预期效果

- 主题扩写功能能够成功扩写主题
- 扩写后的提示词和推荐的引擎正确显示
- 能够将扩写后的提示词应用到文生图或图生图功能
- 测试通过

## 第三阶段开发计划

### 12. 多AI引擎集成

接下来，我们将实现多AI引擎集成。

#### 测试代码

```python
# tests/test_multi_ai_engines.py
import unittest
from unittest.mock import patch, MagicMock
from app.ui.app import AIGCApp
from app.services.ai_engine_service import AIEngineService
import tkinter as tk

class TestMultiAIEngines(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = AIGCApp(self.root)
    
    def tearDown(self):
        self.root.destroy()
    
    @patch('app.services.comfyui_service.ComfyUIService.generate_image')
    def test_comfyui_generation(self, mock_generate):
        """测试ComfyUI图像生成"""
        # 模拟响应
        mock_generate.return_value = 'test_comfyui_image.png'
        
        # 设置输入
        self.app.txt2img_prompt.delete(1.0, tk.END)
        self.app.txt2img_prompt.insert(tk.END, 'test prompt')
        self.app.txt2img_ai_engine_var.set('comfyui')
        
        # 调用生成方法
        self.app.generate_txt2img()
        
        # 验证结果
        mock_generate.assert_called_once()
    
    @patch('app.services.stable_diffusion_service.StableDiffusionService.generate_image')
    def test_stable_diffusion_generation(self, mock_generate):
        """测试Stable Diffusion图像生成"""
        # 模拟响应
        mock_generate.return_value = 'test_sd_image.png'
        
        # 设置输入
        self.app.txt2img_prompt.delete(1.0, tk.END)
        self.app.txt2img_prompt.insert(tk.END, 'test prompt')
        self.app.txt2img_ai_engine_var.set('stable-diffusion')
        
        # 调用生成方法
        self.app.generate_txt2img()
        
        # 验证结果
        mock_generate.assert_called_once()
    
    @patch('app.services.dalle_service.DALLEService.generate_image')
    def test_dalle_generation(self, mock_generate):
        """测试DALL-E图像生成"""
        # 模拟响应
        mock_generate.return_value = 'test_dalle_image.png'
        
        # 设置输入
        self.app.txt2img_prompt.delete(1.0, tk.END)
        self.app.txt2img_prompt.insert(tk.END, 'test prompt')
        self.app.txt2img_ai_engine_var.set('dall-e')
        
        # 调用生成方法
        self.app.generate_txt2img()
        
        # 验证结果
        mock_generate.assert_called_once()
    
    @patch('app.services.midjourney_service.MidjourneyService.generate_image')
    def test_midjourney_generation(self, mock_generate):
        """测试Midjourney图像生成"""
        # 模拟响应
        mock_generate.return_value = 'test_midjourney_image.png'
        
        # 设置输入
        self.app.txt2img_prompt.delete(1.0, tk.END)
        self.app.txt2img_prompt.insert(tk.END, 'test prompt')
        self.app.txt2img_ai_engine_var.set('midjourney')
        
        # 调用生成方法
        self.app.generate_txt2img()
        
        # 验证结果
        mock_generate.assert_called_once()

if __name__ == '__main__':
    unittest.main()
```

#### 预期效果

- 多AI引擎集成功能能够成功集成ComfyUI、Stable Diffusion、DALL-E和Midjourney
- 能够使用不同的AI引擎生成图像
- 每个AI引擎的参数正确传递
- 测试通过

### 13. 性能优化

接下来，我们将进行性能优化。

#### 测试代码

```python
# tests/test_performance.py
import unittest
import time
from unittest.mock import patch, MagicMock
from app.ui.app import AIGCApp
import tkinter as tk

class TestPerformance(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = AIGCApp(self.root)
    
    def tearDown(self):
        self.root.destroy()
    
    def test_ui_responsiveness(self):
        """测试UI响应性"""
        # 记录开始时间
        start_time = time.time()
        
        # 执行UI操作
        self.app.notebook.select(0)  # 切换到文生图标签页
        self.app.txt2img_prompt.delete(1.0, tk.END)
        self.app.txt2img_prompt.insert(tk.END, 'test prompt')
        
        # 记录结束时间
        end_time = time.time()
        
        # 验证响应时间
        response_time = end_time - start_time
        self.assertLess(response_time, 0.1, "UI操作响应时间应该小于0.1秒")
    
    @patch('app.services.comfyui_service.ComfyUIService.queue_prompt')
    @patch('app.services.comfyui_service.ComfyUIService.wait_for_image')
    def test_generation_performance(self, mock_wait_for_image, mock_queue_prompt):
        """测试图像生成性能"""
        # 模拟响应
        mock_queue_prompt.return_value = 'test_prompt_id'
        mock_wait_for_image.return_value = 'test_image.png'
        
        # 设置输入
        self.app.txt2img_prompt.delete(1.0, tk.END)
        self.app.txt2img_prompt.insert(tk.END, 'test prompt')
        
        # 记录开始时间
        start_time = time.time()
        
        # 调用生成方法
        self.app.generate_txt2img()
        
        # 记录结束时间
        end_time = time.time()
        
        # 验证响应时间
        response_time = end_time - start_time
        self.assertLess(response_time, 0.5, "图像生成响应时间应该小于0.5秒")
    
    def test_template_loading_performance(self):
        """测试模板加载性能"""
        # 记录开始时间
        start_time = time.time()
        
        # 加载模板
        self.app.load_templates()
        
        # 记录结束时间
        end_time = time.time()
        
        # 验证响应时间
        response_time = end_time - start_time
        self.assertLess(response_time, 0.2, "模板加载响应时间应该小于0.2秒")
    
    def test_works_loading_performance(self):
        """测试作品加载性能"""
        # 记录开始时间
        start_time = time.time()
        
        # 加载作品
        self.app.load_works_list()
        
        # 记录结束时间
        end_time = time.time()
        
        # 验证响应时间
        response_time = end_time - start_time
        self.assertLess(response_time, 0.2, "作品加载响应时间应该小于0.2秒")

if __name__ == '__main__':
    unittest.main()
```

#### 预期效果

- UI操作响应时间小于0.1秒
- 图像生成响应时间小于0.5秒
- 模板加载响应时间小于0.2秒
- 作品加载响应时间小于0.2秒
- 测试通过

### 14. UI美化

接下来，我们将进行UI美化。

#### 测试代码

```python
# tests/test_ui_beautification.py
import unittest
from unittest.mock import patch, MagicMock
from app.ui.app import AIGCApp
import tkinter as tk

class TestUIBeautification(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = AIGCApp(self.root)
    
    def tearDown(self):
        self.root.destroy()
    
    def test_theme_application(self):
        """测试主题应用"""
        # 验证主题设置
        self.assertEqual(self.app.root['bg'], '#f0f0f0', "背景色应该正确设置")
        self.assertEqual(self.app.notebook['style'], 'Custom.TNotebook', "标签页样式应该正确设置")
    
    def test_widget_styles(self):
        """测试组件样式"""
        # 验证按钮样式
        self.assertEqual(self.app.txt2img_generate_btn['style'], 'Accent.TButton', "生成按钮样式应该正确设置")
        
        # 验证输入框样式
        self.assertEqual(self.app.txt2img_prompt['bg'], '#ffffff', "输入框背景色应该正确设置")
        self.assertEqual(self.app.txt2img_prompt['fg'], '#000000', "输入框前景色应该正确设置")
        
        # 验证标签样式
        self.assertEqual(self.app.txt2img_status['style'], 'Status.TLabel', "状态标签样式应该正确设置")
    
    def test_layout(self):
        """测试布局"""
        # 验证标签页布局
        self.assertEqual(self.app.notebook.winfo_width(), 800, "标签页宽度应该正确设置")
        self.assertEqual(self.app.notebook.winfo_height(), 600, "标签页高度应该正确设置")
        
        # 验证文生图标签页布局
        self.assertEqual(self.app.txt2img_frame.winfo_width(), 780, "文生图标签页宽度应该正确设置")
        self.assertEqual(self.app.txt2img_frame.winfo_height(), 580, "文生图标签页高度应该正确设置")
    
    def test_responsive_design(self):
        """测试响应式设计"""
        # 调整窗口大小
        self.root.geometry('1024x768')
        
        # 验证组件大小调整
        self.assertEqual(self.app.notebook.winfo_width(), 1004, "标签页宽度应该随窗口大小调整")
        self.assertEqual(self.app.notebook.winfo_height(), 768, "标签页高度应该随窗口大小调整")

if __name__ == '__main__':
    unittest.main()
```

#### 预期效果

- 主题正确应用
- 组件样式美观
- 布局合理
- 响应式设计正常工作
- 测试通过

### 15. 文档完善

最后，我们将完善文档。

#### 测试代码

```python
# tests/test_documentation.py
import unittest
import os
import re

class TestDocumentation(unittest.TestCase):
    def test_readme_exists(self):
        """测试README.md文件是否存在"""
        self.assertTrue(os.path.exists('README.md'), "README.md文件应该存在")
    
    def test_readme_content(self):
        """测试README.md内容是否完整"""
        with open('README.md', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 验证必要内容
        self.assertIn('# AIGC图像生成平台', content, "README.md应该包含项目标题")
        self.assertIn('## 功能特点', content, "README.md应该包含功能特点")
        self.assertIn('## 安装步骤', content, "README.md应该包含安装步骤")
        self.assertIn('## 使用方法', content, "README.md应该包含使用方法")
        self.assertIn('## 贡献指南', content, "README.md应该包含贡献指南")
    
    def test_api_documentation(self):
        """测试API文档是否完整"""
        self.assertTrue(os.path.exists('docs/api.md'), "API文档应该存在")
        
        with open('docs/api.md', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 验证必要内容
        self.assertIn('# API文档', content, "API文档应该包含标题")
        self.assertIn('## 文生图API', content, "API文档应该包含文生图API")
        self.assertIn('## 图生图API', content, "API文档应该包含图生图API")
        self.assertIn('## 作品库API', content, "API文档应该包含作品库API")
    
    def test_user_guide(self):
        """测试用户指南是否完整"""
        self.assertTrue(os.path.exists('docs/user_guide.md'), "用户指南应该存在")
        
        with open('docs/user_guide.md', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 验证必要内容
        self.assertIn('# 用户指南', content, "用户指南应该包含标题")
        self.assertIn('## 文生图功能', content, "用户指南应该包含文生图功能")
        self.assertIn('## 图生图功能', content, "用户指南应该包含图生图功能")
        self.assertIn('## 一键同款功能', content, "用户指南应该包含一键同款功能")
        self.assertIn('## 主题扩写功能', content, "用户指南应该包含主题扩写功能")
        self.assertIn('## 提示词优化功能', content, "用户指南应该包含提示词优化功能")
        self.assertIn('## 作品库功能', content, "用户指南应该包含作品库功能")

if __name__ == '__main__':
    unittest.main()
```

#### 预期效果

- README.md文件存在且内容完整
- API文档存在且内容完整
- 用户指南存在且内容完整
- 测试通过 