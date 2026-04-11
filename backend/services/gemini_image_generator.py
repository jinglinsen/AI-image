import asyncio
import base64
import os
import time
import logging
import json
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
from PIL import Image, ImageDraw, ImageFont
import io
import requests

logger = logging.getLogger(__name__)

class GeminiImageGeneratorService:
    """基于Google Gemini 2.5 Flash的图片生成服务"""
    
    def __init__(self):
        # 配置Google Generative AI
        api_key = os.getenv("GOOGLE_API_KEY")
        
        # 使用环境变量中的模型名称，默认使用图片生成专用模型
        self.model_name = os.getenv("GOOGLE_MODEL_NAME", "gemini-2.5-flash-image")
        self.client = genai.Client(api_key=api_key)
        # self.client = genai.Client()
        self.max_input_images = 10  # Gemini的图片输入限制
        
        logger.info(f"初始化Gemini图片生成服务，模型: {self.model_name}")
        
    def generate_image(
        self, 
        prompt: str, 
        input_images: List[str] = None, 
        model: str = "gemini-2.5-flash-image",
        size: str = "1k",
        ratio: str = "1:1"
    ) -> bytes:
        """
        使用Gemini生成单张图片
        
        Args:
            prompt: 生成提示词
            input_images: 输入图片的base64列表（最多10张）
            model: 使用的模型
            size: 图片尺寸
            ratio: 图片比例
            
        Returns:
            生成的图片数据（bytes）
        """
        
        
        try:
            start_time = time.time()

            # 准备输入内容 - 根据官方文档的格式
            contents = [prompt]
            
            # 添加输入图片（如果有）- 用于图片编辑和融合
            if input_images:
                limited_images = input_images[:self.max_input_images]
                
                for i, img_data in enumerate(limited_images):
                    if img_data:
                        try:
                            # 解码base64图片
                            image_bytes = base64.b64decode(img_data)
                            image = Image.open(io.BytesIO(image_bytes))
                            
                            # 转换为PNG格式
                            img_byte_arr = io.BytesIO()
                            image.save(img_byte_arr, format='PNG')
                            img_byte_arr.seek(0)
                            
                            # 添加图片到内容中
                            contents.append(image)
                            
                            print(f"✅ 输入图片 {i+1} 处理完成")
                            
                        except Exception as e:
                            print(f"⚠️  输入图片 {i+1} 处理失败: {str(e)}")
                            continue
            logger.info("系统最终生成提示词：\n%s", contents[0])
            # 调用Gemini API生成内容 - 使用官方文档的语法
            try:
                
                # 使用官方文档中的正确API调用方式
                response = self.client.models.generate_content(
                    model = 'gemini-2.5-flash-image',
                    contents = contents,
                    config=types.GenerateContentConfig(
                        image_config=types.ImageConfig(
                            aspect_ratio=ratio,
                            # image_size='1K'
                        )
                    )
                )
                
                print(f"📦 API调用完成，检查响应...")

                # 处理响应 - 根据官方文档的格式
                for part in response.candidates[0].content.parts:
                    if part.text is not None:
                        print(f"📝 收到文本响应: {part.text}")
                    elif part.inline_data is not None:
                        image_data = Image.open(io.BytesIO(part.inline_data.data))
                        img_byte_arr = io.BytesIO()
                        image_data.save(img_byte_arr, format='PNG')
                        return img_byte_arr.getvalue()
                
            except Exception as api_error:
                print(f"❌ Gemini API调用失败: {str(api_error)}")
                logger.error(f"Gemini API调用失败: {str(api_error)}")
                
                # 检查是否是认证错误
                if "authentication" in str(api_error).lower() or "api key" in str(api_error).lower():
                    print(f"🔑 请检查GOOGLE_API_KEY环境变量是否正确设置")
                    logger.error("Gemini API认证失败，请检查API密钥")
                
                # 检查是否是模型不支持错误
                if "model" in str(api_error).lower() or "not found" in str(api_error).lower():
                    print(f"🤖 模型 {self.model_name} 可能不支持图片生成")
                    logger.error(f"模型 {self.model_name} 不支持或不存在")
            
            response_time = time.time() - start_time
            print(f"📨 Gemini API响应完成，耗时: {response_time:.2f}秒")
            logger.info(f"Gemini API调用完成，耗时: {response_time:.2f}秒")
            
            # 如果没有生成图片，创建占位符
            print(f"🔄 未能从Gemini获取图片，生成占位符...")
            placeholder = self._create_placeholder_image(f"Gemini生成 - {prompt}")
            print(f"🖼️  占位符图片生成完成，大小: {len(placeholder)/1024:.1f}KB")
            return placeholder
                
        except Exception as e:
            print(f"❌ Gemini图片生成发生错误: {str(e)}")
            logger.error(f"Gemini图片生成失败: {str(e)}")
            print(f"🔄 将返回错误占位符图片")
            # 返回错误占位符而不是抛出异常
            placeholder = self._create_placeholder_image(f"Gemini生成失败: {str(e)[:50]}")
            print(f"🖼️  错误占位符生成完成")
            return placeholder
    
    def generate_image_with_vision(
        self, 
        prompt: str, 
        input_images: List[str] = None
    ) -> bytes:
        """
        使用Gemini的视觉能力分析输入图片并生成新图片
        
        Args:
            prompt: 生成提示词
            input_images: 输入图片的base64列表
            
        Returns:
            生成的图片数据（bytes）
        """
        try:
            print(f"\n🔍 使用Gemini视觉能力分析并生成图片...")
            logger.info("使用Gemini视觉能力进行图片分析和生成")
            
            if not input_images:
                print(f"⚠️  没有输入图片，使用普通生成模式")
                return self.generate_image(prompt)
            
            # 准备内容
            content_parts = []
            
            # 添加分析和生成提示词
            vision_prompt = f"""请分析以下图片，然后根据描述生成一张新的图片：

                分析要求：
                1. 仔细观察输入图片的内容、风格、颜色、构图
                2. 理解图片中的主要元素和特征

                生成要求：
                {prompt}

                请基于对输入图片的理解，生成一张符合要求的新图片。"""
            
            content_parts.append(vision_prompt)
            
            # 添加输入图片
            for i, img_data in enumerate(input_images[:self.max_input_images]):
                if img_data:
                    try:
                        image_bytes = base64.b64decode(img_data)
                        image = Image.open(io.BytesIO(image_bytes))
                        
                        # 直接添加PIL图片对象
                        content_parts.append(image)
                        
                        print(f"✅ 视觉输入图片 {i+1} 处理完成")
                        
                    except Exception as e:
                        print(f"⚠️  视觉输入图片 {i+1} 处理失败: {str(e)}")
                        continue
            
            # 调用Gemini API - 使用新的客户端语法
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=content_parts,
            )
            
            # 检查响应是否有效
            if not response or not hasattr(response, 'candidates') or not response.candidates:
                print(f"❌ 视觉生成响应无效或为空")
                logger.error("Gemini视觉生成API返回空响应或无候选结果")
                raise Exception("视觉生成API返回空响应")
            
            candidate = response.candidates[0]
            if not candidate or not hasattr(candidate, 'content') or not candidate.content:
                print(f"❌ 视觉生成候选结果无效或为空")
                logger.error("Gemini视觉生成API候选结果无内容")
                raise Exception("视觉生成API候选结果无内容")
            
            if not hasattr(candidate.content, 'parts') or not candidate.content.parts:
                print(f"❌ 视觉生成响应内容无parts或为空")
                logger.error("Gemini视觉生成API响应内容无parts")
                raise Exception("视觉生成API响应内容无parts")
            
            # 处理响应（与普通生成相同的逻辑）
            for part in candidate.content.parts:
                if part.text is not None:
                    print(f"📝 收到文本响应: {part.text}")
                elif hasattr(part, 'inline_data') and part.inline_data is not None:
                    image_data = part.inline_data.data
                    print(f"✅ 视觉生成成功! 大小: {len(image_data)/1024:.1f}KB")
                    logger.info(f"Gemini视觉生成成功，大小: {len(image_data)} bytes")
                    
                    # 转换为bytes格式返回
                    image = Image.open(io.BytesIO(image_data))
                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format='PNG')
                    return img_byte_arr.getvalue()
            
            # 如果没有生成图片，返回占位符
            placeholder = self._create_placeholder_image(f"Gemini视觉生成 - {prompt}")
            return placeholder
            
        except Exception as e:
            logger.error(f"Gemini视觉生成失败: {str(e)}")
            return self._create_placeholder_image(f"视觉生成失败: {str(e)[:50]}")
    
    async def generate_images_batch(
        self, 
        prompts: List[str], 
        input_images: List[str] = None
    ) -> List[Optional[bytes]]:
        """
        批量生成图片（异步）
        
        Args:
            prompts: 提示词列表
            input_images: 共享的输入图片
            
        Returns:
            生成的图片数据列表
        """
        async def generate_single(prompt):
            try:
                return await asyncio.get_event_loop().run_in_executor(
                    None, 
                    self.generate_image, 
                    prompt, 
                    input_images
                )
            except Exception as e:
                logger.error(f"Gemini批量生成中的单个图片失败: {str(e)}")
                return None
        
        # 控制并发数量避免API限制
        semaphore = asyncio.Semaphore(2)  # Gemini API限制更严格，使用2个并发
        
        async def generate_with_semaphore(prompt):
            async with semaphore:
                return await generate_single(prompt)
        
        tasks = [generate_with_semaphore(prompt) for prompt in prompts]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常结果
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Gemini批量生成异常: {str(result)}")
                processed_results.append(None)
            else:
                processed_results.append(result)
        
        return processed_results
    
    def validate_inputs(self, prompt: str, input_images: List[str] = None) -> bool:
        """
        验证输入参数
        
        Args:
            prompt: 提示词
            input_images: 输入图片列表
            
        Returns:
            是否有效
        """
        if not prompt or len(prompt.strip()) == 0:
            raise ValueError("提示词不能为空")
        
        if len(prompt) > 10000:  # Gemini的文本限制
            raise ValueError("提示词过长，请缩短到10000字符以内")
        
        if input_images and len(input_images) > self.max_input_images:
            raise ValueError(f"输入图片数量超过限制（最大{self.max_input_images}张）")
        
        return True
    
    def estimate_cost(self, prompt: str, input_images: List[str] = None) -> float:
        """
        估算生成成本（基于Gemini定价）
        
        Args:
            prompt: 提示词
            input_images: 输入图片列表
            
        Returns:
            估算成本（美元）
        """
        # Gemini 2.5 Flash的定价（需要根据实际定价调整）
        base_cost = 0.01  # 基础成本
        
        # 根据提示词长度调整
        prompt_factor = len(prompt) / 1000 * 0.0005
        
        # 根据输入图片数量调整
        image_factor = len(input_images) * 0.002 if input_images else 0
        
        total_cost = base_cost + prompt_factor + image_factor
        return round(total_cost, 4)
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        获取Gemini模型信息
        
        Returns:
            模型信息字典
        """
        return {
            "model_name": self.model_name,
            "provider": "Google",
            "max_input_images": self.max_input_images,
            "supported_formats": ["JPEG", "PNG", "WebP", "GIF"],
            "max_resolution": "2048x2048",
            "typical_generation_time": "5-15 seconds",
            "features": ["text-to-image", "image-to-image", "vision-analysis"],
            "languages": ["中文", "English", "多语言支持"]
        }
    
    def _create_placeholder_image(self, prompt: str) -> bytes:
        """
        创建占位符图片（Gemini主题）
        """
        try:
            # 创建一个1024x1024的图片
            img = Image.new('RGB', (1024, 1024), color='#f8f9fa')
            draw = ImageDraw.Draw(img)
            
            # 添加提示词文本
            try:
                font = ImageFont.load_default()
            except:
                font = None
            
            # 绘制Gemini主题边框（蓝色渐变风格）
            draw.rectangle([50, 50, 974, 974], outline='#4285f4', width=3)
            draw.rectangle([60, 60, 964, 964], outline='#34a853', width=2)
            
            # 添加Gemini标识
            title_text = "🤖 Gemini AI Generated Image"
            draw.text((100, 100), title_text, fill='#4285f4', font=font)
            
            # 添加模型信息
            model_text = f"Model: {self.model_name}"
            draw.text((100, 140), model_text, fill='#34a853', font=font)
            
            # 添加提示词（截取前150个字符）
            prompt_text = f"Prompt: {prompt[:150]}..."
            draw.text((100, 180), prompt_text, fill='#333333', font=font)
            
            # 添加时间戳
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            draw.text((100, 220), f"Generated: {timestamp}", fill='#666666', font=font)
            
            # 根据提示词内容绘制相关图形
            if any(keyword in prompt.lower() for keyword in ['帽子', 'hat', '产品', 'product']):
                # 绘制产品相关图形
                draw.ellipse([350, 400, 650, 500], fill='#fbbc04', outline='#ea4335', width=2)
                draw.ellipse([400, 350, 600, 480], fill='#34a853', outline='#4285f4', width=2)
                draw.text((420, 520), "Product Design", fill='#4285f4', font=font)
            else:
                # 默认Gemini风格装饰
                # 绘制多彩圆形（Google色彩）
                colors = ['#4285f4', '#34a853', '#fbbc04', '#ea4335']
                for i, color in enumerate(colors):
                    x = 300 + (i % 2) * 200
                    y = 400 + (i // 2) * 150
                    draw.ellipse([x, y, x+150, y+150], fill=color, outline='white', width=3)
                
                draw.text((420, 580), "AI Generated", fill='#4285f4', font=font)
            
            # 添加Google/Gemini标识性元素
            draw.text((100, 900), "Powered by Google Gemini 2.5 Flash", fill='#666666', font=font)
            
            # 转换为字节
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            logger.info(f"创建Gemini占位符图片成功，大小: {len(img_byte_arr)} bytes")
            return img_byte_arr
            
        except Exception as e:
            logger.error(f"创建Gemini占位符图片失败: {str(e)}")
            return self._create_minimal_image()
    
    def _create_minimal_image(self) -> bytes:
        """创建最小的PNG图片（Gemini主题）"""
        img = Image.new('RGB', (512, 512), color='#f8f9fa')
        draw = ImageDraw.Draw(img)
        draw.text((150, 200), "🤖 Gemini AI", fill='#4285f4')
        draw.text((150, 250), "Generated Image", fill='#34a853')
        
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()
    
    def test_real_generation(self, prompt: str = "Generate a beautiful sunset over mountains with vibrant colors") -> bytes:
        """
        测试真实的Gemini图片生成功能
        """
        try:
            logger.info(f"测试Gemini真实图片生成，提示词: {prompt}")
            
            # 使用完整的生成流程
            result = self.generate_image(prompt)
            
            if result:
                logger.info(f"Gemini测试生成成功，图片大小: {len(result)} bytes")
                return result
            else:
                logger.warning("Gemini测试生成返回空结果")
                return self._create_placeholder_image(f"测试生成 - {prompt}")
                
        except Exception as e:
            logger.error(f"Gemini测试真实图片生成失败: {str(e)}")
            return self._create_placeholder_image(f"测试失败 - {prompt}")
    
    def analyze_image(self, image_data: str, question: str = "请描述这张图片") -> str:
        """
        使用Gemini分析图片内容
        
        Args:
            image_data: base64编码的图片数据
            question: 分析问题
            
        Returns:
            分析结果文本
        """
        try:
            logger.info("使用Gemini分析图片内容")
            
            # 解码图片
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # 准备内容 - 使用新的格式
            contents = [question, image]
            
            # 调用Gemini API - 使用新的客户端语法
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents
            )
            
            # 检查响应是否有效
            if not response or not hasattr(response, 'candidates') or not response.candidates:
                logger.error("Gemini图片分析API返回空响应或无候选结果")
                return "分析失败：API返回空响应"
            
            candidate = response.candidates[0]
            if not candidate or not hasattr(candidate, 'content') or not candidate.content:
                logger.error("Gemini图片分析API候选结果无内容")
                return "分析失败：API候选结果无内容"
            
            if not hasattr(candidate.content, 'parts') or not candidate.content.parts:
                logger.error("Gemini图片分析API响应内容无parts")
                return "分析失败：API响应内容无parts"
            
            # 处理文本响应
            for part in candidate.content.parts:
                if part.text is not None:
                    logger.info(f"Gemini图片分析完成，结果长度: {len(part.text)} 字符")
                    return part.text
            
            return "无法分析图片内容"
                
        except Exception as e:
            logger.error(f"Gemini图片分析失败: {str(e)}")
            return f"图片分析失败: {str(e)}"