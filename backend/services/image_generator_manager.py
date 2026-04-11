import logging
from typing import List, Dict, Any, Optional
from .image_generator import ImageGeneratorService
from .chatgpt_image_generator import ChatGPTImageGeneratorService

logger = logging.getLogger(__name__)

class ImageGeneratorManager:
    """图片生成服务管理器，根据模型选择不同的服务"""
    
    def __init__(self):
        """初始化所有可用的图片生成服务"""
        self.services = {}
        self._initialize_services()
        
    def _initialize_services(self):
        """初始化所有图片生成服务"""
        try:
            self.services['qwen-plus'] = ImageGeneratorService()
            self.services['qwen-vl-plus'] = ImageGeneratorService()
            logger.info("✅ Qwen 图片生成服务初始化成功")
        except Exception as e:
            logger.error(f"❌ 图片生成服务初始化失败: {str(e)}")
            
    def get_service(self, model: str):
        if model in self.services:
            return self.services[model]
        
        # 默认回退
        return self.services.get('qwen-plus', ImageGeneratorService())
    
    def generate_image(
        self, 
        prompt: str, 
        input_images: List[str] = None, 
        model: str = "qwen-plus",
        size: str = "1024x1024",
        ratio: str = "1:1"
    ) -> bytes:
        try:
            service = self.get_service(model)
            
            logger.info(f"🚀 开始使用 {model} 模型生成图片")
            
            result = service.generate_image(
                prompt=prompt,
                input_images=input_images,
                model=model,
                size=size,
                ratio=ratio
            )
            
            logger.info(f"✅ 图片生成成功，使用模型: {model}")
            return result
            
        except Exception as e:
            logger.error(f"❌ 图片生成失败 (模型: {model}): {str(e)}")
            raise
    
    def get_available_models(self) -> List[str]:
        return ['qwen-plus', 'qwen-vl-plus']
    
    def get_model_info(self, model: str = None) -> Dict[str, Any]:
        if model:
            service = self.get_service(model)
            return service.get_model_info()
        return {}
    
    def validate_inputs(self, prompt: str, input_images: List[str] = None, model: str = "qwen-plus") -> bool:
        service = self.get_service(model)
        return service.validate_inputs(prompt, input_images)
    
    def estimate_cost(self, prompt: str, input_images: List[str] = None, model: str = "qwen-plus") -> float:
        service = self.get_service(model)
        return service.estimate_cost(prompt, input_images)