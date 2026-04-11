import os
import base64
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from PIL import Image, ImageOps
import io
import logging

logger = logging.getLogger(__name__)

class ImageProcessor:
    """图片处理工具类"""
    
    def __init__(self):
        self.supported_formats = ['JPEG', 'PNG', 'WebP', 'BMP']
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        self.max_dimensions = (4096, 4096)
        self.nano_banana_max_images = 10
        
        # 获取绝对路径
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # backend目录
        self.uploads_dir = os.path.join(self.base_dir, 'uploads')
        self.generated_images_dir = os.path.join(self.base_dir, 'generated_images')
        
        # 确保目录存在
        os.makedirs(self.uploads_dir, exist_ok=True)
        os.makedirs(self.generated_images_dir, exist_ok=True)
        
        logger.info(f"初始化图片处理器，上传目录: {self.uploads_dir}")
        logger.info(f"初始化图片处理器，生成目录: {self.generated_images_dir}")
    
    def save_uploaded_image(self, file, oss_uploader=None) -> Dict[str, Any]:
        """
        保存上传的图片文件，支持OSS和本地存储
        
        Args:
            file: Flask上传的文件对象
            oss_uploader: OSS上传器实例（可选）
            
        Returns:
            Dict包含保存结果信息，包括文件名、URL和存储位置
        """
        try:
            # 验证文件
            self._validate_upload_file(file)
            
            # 生成唯一文件名
            file_ext = self._get_file_extension(file.filename)
            filename = f"upload_{uuid.uuid4().hex}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_ext}"
            
            logger.info(f"准备保存上传图片: {file.filename}")
            
            # 处理图片
            file.stream.seek(0)  # 确保流位置在开头
            image = Image.open(file.stream)
            processed_image = self._process_uploaded_image(image)
            
            # 优先尝试上传到OSS
            if oss_uploader:
                try:
                    # 将处理后的图片转换为字节流
                    img_buffer = io.BytesIO()
                    processed_image.save(img_buffer, format='JPEG', optimize=True, quality=95)
                    image_bytes = img_buffer.getvalue()
                    
                    logger.info(f"尝试上传图片到OSS: {filename}, 大小: {len(image_bytes)} bytes")
                    
                    # 上传到OSS（带重试机制）
                    oss_result = oss_uploader.upload_image(file, folder="uploads")
                    
                    if oss_result.get('success'):
                        logger.info(f"成功上传图片到OSS: {oss_result['filename']}")
                        return {
                            'success': True,
                            'filename': oss_result['filename'],
                            'url': oss_result['url'],
                            'storage': 'oss',
                            'size': oss_result.get('size', len(image_bytes))
                        }
                    else:
                        logger.warning(f"OSS上传失败，回退到本地存储: {filename}")
                        
                except Exception as e:
                    logger.warning(f"OSS上传异常，回退到本地存储: {str(e)}")
            
            # 回退到本地存储
            filepath = os.path.join(self.uploads_dir, filename)
            logger.info(f"保存图片到本地: {filepath}")
            
            # 保存图片
            processed_image.save(filepath, optimize=True, quality=95)
            
            # 验证文件是否真的保存成功
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                logger.info(f"成功保存上传图片到本地: {filename}, 大小: {file_size} bytes")
                
                return {
                    'success': True,
                    'filename': filename,
                    'url': f'/api/upload/{filename}',
                    'storage': 'local',
                    'size': file_size
                }
            else:
                logger.error(f"文件保存失败，文件不存在: {filepath}")
                raise Exception(f"文件保存失败，保存后文件不存在")
            
        except Exception as e:
            logger.error(f"保存上传图片失败: {str(e)}")
            raise Exception(f"图片保存失败: {str(e)}")
    
    def save_generated_image(self, image_data: bytes, filename: str, oss_uploader=None) -> Dict[str, Any]:
        """
        保存生成的图片，优先上传到OSS，失败时保存到本地
        
        Args:
            image_data: 图片字节数据
            filename: 文件名（可能没有扩展名）
            oss_uploader: OSS上传器实例（可选）
            
        Returns:
            Dict包含保存结果信息，包括文件名、URL和存储位置
        """
        try:
            # 确保文件名有正确的扩展名
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                # 检测图片格式并添加正确的扩展名
                if isinstance(image_data, bytes):
                    # 检查字节数据的前几个字节来确定格式
                    if image_data[:8] == b'\x89PNG\r\n\x1a\n':
                        filename += '.png'
                    elif image_data[:3] == b'\xff\xd8\xff':
                        filename += '.jpg'
                    elif image_data[:4] == b'RIFF' and image_data[8:12] == b'WEBP':
                        filename += '.webp'
                    else:
                        # 默认使用PNG扩展名
                        filename += '.png'
                else:
                    # 如果是PIL Image对象，默认使用PNG
                    filename += '.png'
            
            # 优先尝试上传到OSS
            if oss_uploader:
                try:
                    logger.info(f"尝试上传生成图片到OSS: {filename}")
                    oss_result = oss_uploader.upload_generated_image(image_data, filename)
                    
                    if oss_result.get('success'):
                        logger.info(f"成功上传生成图片到OSS: {oss_result['filename']}")
                        return {
                            'success': True,
                            'filename': oss_result['filename'],
                            'url': oss_result['url'],
                            'storage': 'oss',
                            'size': oss_result.get('size', len(image_data))
                        }
                    else:
                        logger.warning(f"OSS上传失败，回退到本地存储: {filename}")
                        
                except Exception as e:
                    logger.warning(f"OSS上传异常，回退到本地存储: {str(e)}")
            
            # 回退到本地存储
            filepath = os.path.join(self.generated_images_dir, filename)
            logger.info(f"保存生成图片到本地: {filepath}")
            
            # 如果是字节数据，直接保存
            if isinstance(image_data, bytes):
                with open(filepath, 'wb') as f:
                    f.write(image_data)
            else:
                # 如果是PIL Image对象
                image_data.save(filepath, optimize=True, quality=95)
            
            # 验证文件是否真的保存成功
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                logger.info(f"成功保存生成图片到本地: {filename}, 大小: {file_size} bytes")
                
                return {
                    'success': True,
                    'filename': filename,
                    'url': f'/api/image/{filename}',
                    'storage': 'local',
                    'size': file_size
                }
            else:
                logger.error(f"生成图片保存失败，文件不存在: {filepath}")
                raise Exception(f"生成图片保存失败，保存后文件不存在")
            
        except Exception as e:
            logger.error(f"保存生成图片失败: {str(e)}")
            raise Exception(f"生成图片保存失败: {str(e)}")
    
    def prepare_input_images(
        self, 
        product_images: List[Dict], 
        reference_images: List[Dict] = None,
        max_images: int = None
    ) -> List[str]:
        """
        准备输入给Nano Banana的图片
        
        Args:
            product_images: 产品图片列表
            reference_images: 参考图片列表
            max_images: 最大图片数量限制
            
        Returns:
            base64编码的图片列表
        """
        try:
            if max_images is None:
                max_images = self.nano_banana_max_images
            
            all_images = []
            processed_count = 0
            
            # 处理产品图片（优先级高）
            for img_info in product_images:
                if processed_count >= max_images:
                    break
                
                base64_data = self._process_image_to_base64(img_info)
                if base64_data:
                    all_images.append(base64_data)
                    processed_count += 1
            
            # 处理参考图片
            if reference_images and processed_count < max_images:
                logger.info(f"🎨 开始处理参考图片，共 {len(reference_images)} 张")
                for idx, img_info in enumerate(reference_images):
                    if processed_count >= max_images:
                        logger.warning(f"⚠️  达到最大图片限制({max_images})，剩余参考图未处理")
                        break
                    
                    base64_data = self._process_image_to_base64(img_info)
                    if base64_data:
                        all_images.append(base64_data)
                        processed_count += 1
                        logger.info(f"  ✅ 参考图#{idx+1} 处理成功: {img_info.get('description', 'N/A')[:50]}")
                    else:
                        logger.error(f"  ❌ 参考图#{idx+1} 处理失败")
            elif reference_images:
                logger.warning(f"⚠️  已达到最大图片数({max_images})，无法添加参考图")
            
            logger.info(f"📊 准备输入图片完成 - 产品图: {len(product_images)}, 参考图: {len(reference_images) if reference_images else 0}, 总计: {len(all_images)} 张")
            return all_images
            
        except Exception as e:
            logger.error(f"准备输入图片失败: {str(e)}")
            return []
    
    def resize_image_for_api(self, image: Image.Image, max_size: tuple = (1024, 1024)) -> Image.Image:
        """
        调整图片尺寸以适应API要求
        
        Args:
            image: PIL Image对象
            max_size: 最大尺寸
            
        Returns:
            调整后的图片
        """
        try:
            # 保持宽高比缩放
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # 如果图片有透明通道，转换为RGB
            if image.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            return image
            
        except Exception as e:
            logger.error(f"调整图片尺寸失败: {str(e)}")
            return image
    
    def optimize_image_for_storage(self, image: Image.Image, quality: int = 85) -> Image.Image:
        """
        优化图片以减少存储空间
        
        Args:
            image: PIL Image对象
            quality: JPEG质量 (1-100)
            
        Returns:
            优化后的图片
        """
        try:
            # 如果图片过大，进行压缩
            if image.size[0] > 2048 or image.size[1] > 2048:
                image.thumbnail((2048, 2048), Image.Resampling.LANCZOS)
            
            # 转换为RGB模式以支持JPEG
            if image.mode != 'RGB':
                if image.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                    image = background
                else:
                    image = image.convert('RGB')
            
            return image
            
        except Exception as e:
            logger.error(f"优化图片失败: {str(e)}")
            return image
    
    def extract_image_metadata(self, image: Image.Image) -> Dict[str, Any]:
        """
        提取图片元数据
        
        Args:
            image: PIL Image对象
            
        Returns:
            元数据字典
        """
        try:
            metadata = {
                'size': image.size,
                'mode': image.mode,
                'format': image.format,
                'has_transparency': image.mode in ('RGBA', 'LA') or 'transparency' in image.info
            }
            
            # 提取EXIF信息（如果存在）
            if hasattr(image, '_getexif') and image._getexif():
                exif = image._getexif()
                if exif:
                    metadata['exif'] = {
                        key: value for key, value in exif.items() 
                        if isinstance(key, int) and key < 65536
                    }
            
            return metadata
            
        except Exception as e:
            logger.error(f"提取图片元数据失败: {str(e)}")
            return {'size': image.size, 'mode': image.mode}
    
    def _validate_upload_file(self, file) -> None:
        """验证上传文件"""
        if not file or not file.filename:
            raise ValueError("没有选择文件")
        
        # 检查文件扩展名
        ext = self._get_file_extension(file.filename).lower()
        if ext not in ['.jpg', '.jpeg', '.png', '.webp', '.bmp']:
            raise ValueError(f"不支持的文件格式: {ext}")
        
        # 检查文件大小
        file.seek(0, 2)  # 移动到文件末尾
        file_size = file.tell()
        file.seek(0)     # 重置到文件开头
        
        if file_size > self.max_file_size:
            raise ValueError(f"文件大小超过限制 ({self.max_file_size // (1024*1024)}MB)")
    
    def _get_file_extension(self, filename: str) -> str:
        """获取文件扩展名"""
        return os.path.splitext(filename)[1].lower()
    
    def _process_uploaded_image(self, image: Image.Image) -> Image.Image:
        """处理上传的图片"""
        try:
            # 自动旋转（基于EXIF）
            image = ImageOps.exif_transpose(image)
            
            # 调整尺寸
            if image.size[0] > self.max_dimensions[0] or image.size[1] > self.max_dimensions[1]:
                image.thumbnail(self.max_dimensions, Image.Resampling.LANCZOS)
            
            # 优化存储
            image = self.optimize_image_for_storage(image)
            
            return image
            
        except Exception as e:
            logger.error(f"处理上传图片失败: {str(e)}")
            return image
    
    def _process_image_to_base64(self, img_info: Dict) -> Optional[str]:
        """将图片信息转换为base64"""
        try:
            # 从不同来源加载图片
            image = None
            
            logger.info(f"尝试加载图片，信息: {img_info}")
            
            # 智能判断存储类型
            storage_type = img_info.get('storage', None)
            
            # 如果没有明确的storage字段，根据URL判断
            if storage_type is None:
                if 'url' in img_info and img_info['url'] and img_info['url'].startswith('http'):
                    storage_type = 'oss'
                elif 'filename' in img_info and img_info['filename']:
                    storage_type = 'local'
                else:
                    storage_type = 'local'  # 默认
            
            logger.info(f"图片存储类型: {storage_type}")
            
            # 处理OSS存储的图片
            if storage_type == 'oss':
                if 'url' in img_info and img_info['url']:
                    try:
                        import requests
                        # 如果是相对URL，需要构建完整的OSS URL
                        url = img_info['url']
                        if not url.startswith('http'):
                            # 这里可能需要根据实际OSS配置构建完整URL
                            # 暂时直接使用相对URL，如果失败会回退到其他方法
                            pass
                        
                        response = requests.get(url, timeout=10)
                        if response.status_code == 200:
                            image = Image.open(io.BytesIO(response.content))
                            logger.info(f"成功从OSS URL加载图片: {url}")
                        else:
                            logger.error(f"OSS URL请求失败: {response.status_code}")
                    except Exception as e:
                        logger.error(f"从OSS URL加载图片失败: {str(e)}")
                        
            # 处理本地存储的图片
            elif storage_type == 'local':
                # 优先使用filename字段
                if 'filename' in img_info and img_info['filename']:
                    filepath = os.path.join(self.uploads_dir, img_info['filename'])
                    if os.path.exists(filepath):
                        image = Image.open(filepath)
                        logger.info(f"成功从本地存储加载图片: {img_info['filename']}")
                    else:
                        logger.error(f"本地文件不存在: {filepath}")
                        
                 # 处理直接的文件对象（通常是拖拽或点击上传）
                elif 'raw' in img_info and img_info['raw'] and hasattr(img_info['raw'], 'read'):
                    try:
                        if hasattr(img_info['raw'], 'seek'):
                            img_info['raw'].seek(0)  # 重置文件指针
                        image = Image.open(img_info['raw'])
                        logger.info("成功从原始文件对象加载图片")
                    except Exception as e:
                        logger.error(f"从原始文件对象加载图片失败: {str(e)}")
            
            if image is None:
                logger.warning(f"无法加载图片: {img_info}")
                return None
            
            # 调整图片以适应API
            processed_image = self.resize_image_for_api(image)
            
            # 转换为base64
            buffer = io.BytesIO()
            processed_image.save(buffer, format='JPEG', quality=85)
            image_bytes = buffer.getvalue()
            base64_string = base64.b64encode(image_bytes).decode('utf-8')
            
            return base64_string
            
        except Exception as e:
            logger.error(f"图片转base64失败: {str(e)}")
            return None
    
    def cleanup_old_files(self, days_old: int = 7) -> int:
        """
        清理旧文件
        
        Args:
            days_old: 清理多少天前的文件
            
        Returns:
            清理的文件数量
        """
        try:
            from datetime import timedelta
            import time
            
            cutoff_time = time.time() - (days_old * 24 * 60 * 60)
            deleted_count = 0
            
            # 清理上传文件
            for filename in os.listdir(self.uploads_dir):
                filepath = os.path.join(self.uploads_dir, filename)
                if os.path.isfile(filepath) and os.path.getmtime(filepath) < cutoff_time:
                    try:
                        os.remove(filepath)
                        deleted_count += 1
                    except OSError:
                        pass
            
            # 清理生成的图片（可能需要检查数据库引用）
            # 这里暂时不自动清理生成的图片，因为它们可能在数据库中被引用
            
            logger.info(f"清理了 {deleted_count} 个旧文件")
            return deleted_count
            
        except Exception as e:
            logger.error(f"清理旧文件失败: {str(e)}")
            return 0
