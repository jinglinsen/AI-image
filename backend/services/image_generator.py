import asyncio
import base64
import os
import time
import logging
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont
import io
import requests

logger = logging.getLogger(__name__)

class ImageGeneratorService:
    """图片生成服务，处理与阿里云 DashScope API 的交互"""
    
    def __init__(self):
        self.api_key = os.getenv("API_KEY", "")
        self.base_url = os.getenv("API_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )
        self.model_name = os.getenv("FAST_MODEL_NAME", "qwen-plus")  
        self.vision_model_name = os.getenv("VISION_MODEL_NAME", "qwen-vl-plus")
        self.max_input_images = 10 
        
    def generate_image(
        self, 
        prompt: str, 
        input_images: List[str] = None, 
        model: str = "qwen-plus",
        size: str = "1024x1024",
        ratio: str = "1:1"
    ) -> bytes:
        """
        生成单张图片
        """
        try:
            start_time = time.time()
            
            # 使用前端选择的模型
            current_model = model if model else (self.vision_model_name if input_images else self.model_name)

            # 准备消息内容
            message_content = [
                {
                    "type": "text",
                    "text": prompt
                }
            ]
            
            # 添加输入图片（限制数量）
            if input_images:
                limited_images = input_images[:self.max_input_images]
                for img_data in limited_images:
                    if img_data:
                        message_content.append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_data}"
                            }
                        })
            
            print(f"\n" + "="*80)
            print(f"[Info] ImageGeneratorService.generate_image() starting")
            print(f"[Info] Prompt length: {len(prompt)}")
            print(f"[Info] Current model: {current_model}")
            print(f"="*80)
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.base_url}/images/generations"
            if "dall-e" in current_model or "image" in current_model:
                # DALL-E 3 supports specific sizes based on ratio
                mapped_size = size
                if current_model == "dall-e-3":
                    if ratio in ["4:3", "16:9"]:
                        mapped_size = "1792x1024"
                    elif ratio in ["3:4", "9:16"]:
                        mapped_size = "1024x1792"
                    else:
                        mapped_size = "1024x1024"

                payload = {
                    "model": current_model,
                    "prompt": prompt,
                    "n": 1,
                    "size": mapped_size
                }
                print(f"[Info] Sending request to {url} with model {current_model}")
                response = requests.post(url, headers=headers, json=payload, timeout=120)
                
                if response.status_code != 200:
                    print(f"[Error] API failed: {response.text}")
                    return self._create_placeholder_image(f"API Failed: {response.text}")
                
                try:
                    data = response.json()
                    if "data" in data and len(data["data"]) > 0:
                        image_url = data["data"][0].get("url")
                        if image_url:
                            print(f"[Success] Found image URL in data array: {image_url}")
                            img_response = requests.get(image_url)
                            if img_response.status_code == 200:
                                return img_response.content
                except Exception as e:
                    print(f"[Error] Failed to parse image response: {str(e)}")
                    
                return self._create_placeholder_image("Gen success but no valid URL in response")

            # 原有的基于 /chat/completions 的处理
            url = f"{self.base_url}/chat/completions"
            if isinstance(message_content, list) and len(message_content) == 1 and message_content[0].get("type") == "text":
                content = message_content[0]["text"]
            else:
                content = message_content
            
            payload = {
                "model": current_model,
                "messages": [
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                "stream": True 
            }
            
            print(f"[Info] Sending chat stream request to {url} with model {current_model}")
            response = requests.post(url, headers=headers, json=payload, timeout=60, stream=True)
            
            if response.status_code != 200:
                print(f"[Error] API failed: {response.text}")
                return self._create_placeholder_image(f"API Failed: {response.text}")
            
            full_text_response = ""
            generated_images = []
            import base64
            import re
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]
                        if data != '[DONE]':
                            try:
                                chunk = json.loads(data)
                                if chunk.get("choices"):
                                    delta = chunk["choices"][0].get("delta", {})
                                    
                                    if delta.get("images"):
                                        for image in delta["images"]:
                                            image_url = image.get("image_url", {}).get("url", "")
                                            if image_url.startswith('data:image'):
                                                base64_data = image_url.split(',')[1]
                                                image_bytes = base64.b64decode(base64_data)
                                                generated_images.append(image_bytes)
                                            elif image_url.startswith('http'):
                                                img_response = requests.get(image_url)
                                                if img_response.status_code == 200:
                                                    generated_images.append(img_response.content)
                                    
                                    if delta.get("content"):
                                        full_text_response += delta["content"]
                            except:
                                pass
            
            print(f"\n[Info] API call completed. Text returned: {full_text_response[:100]}")
            
            if generated_images:
                print(f"[Success] Found image in delta structure!")
                return generated_images[0]
                
            img_urls = re.findall(r'!\[.*?\]\((.*?)\)', full_text_response)
            if img_urls:
                img_url = img_urls[0]
                print(f"[Success] Found image URL in markdown: {img_url}")
                img_response = requests.get(img_url)
                if img_response.status_code == 200:
                    return img_response.content
                    
            return self._create_placeholder_image("Gen success but text only returned")
                
        except Exception as e:
            print(f"[Exception] Error in image generation: {str(e)}")
            placeholder = self._create_placeholder_image(f"Generation Failed: {str(e)[:50]}")
            return placeholder
    
    async def generate_images_batch(
        self, 
        prompts: List[str], 
        input_images: List[str] = None
    ) -> List[Optional[bytes]]:
        async def generate_single(prompt):
            try:
                return await asyncio.get_event_loop().run_in_executor(
                    None, 
                    self.generate_image, 
                    prompt, 
                    input_images
                )
            except Exception as e:
                logger.error(f"批量生成异常: {str(e)}")
                return None
        
        semaphore = asyncio.Semaphore(3)
        async def generate_with_semaphore(prompt):
            async with semaphore:
                return await generate_single(prompt)
        
        tasks = [generate_with_semaphore(prompt) for prompt in prompts]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append(None)
            else:
                processed_results.append(result)
        
        return processed_results
    
    def validate_inputs(self, prompt: str, input_images: List[str] = None) -> bool:
        if not prompt or len(prompt.strip()) == 0:
            raise ValueError("提示词不能为空")
        return True
    
    def estimate_cost(self, prompt: str, input_images: List[str] = None) -> float:
        return 0.01
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "max_input_images": self.max_input_images,
            "supported_formats": ["JPEG", "PNG", "WebP"],
            "max_resolution": "2048x2048"
        }
    
    def _create_placeholder_image(self, prompt: str) -> bytes:
        try:
            img = Image.new('RGB', (1024, 1024), color='white')
            draw = ImageDraw.Draw(img)
            try:
                font = ImageFont.load_default()
            except:
                font = None
            
            draw.rectangle([50, 50, 974, 974], outline='black', width=2)
            draw.text((100, 100), "DashScope Result", fill='black', font=font)
            draw.text((100, 150), prompt[:150], fill='gray', font=font)
            
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            return img_byte_arr.getvalue()
        except:
            return self._create_minimal_image()
    
    def _create_minimal_image(self) -> bytes:
        img = Image.new('RGB', (512, 512), color='lightblue')
        draw = ImageDraw.Draw(img)
        draw.text((200, 250), "DashScope Flow", fill='black')
        
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()
    
    def test_real_generation(self, prompt: str = "Generate a beautiful sunset over mountains") -> bytes:
        return self.generate_image(prompt)
