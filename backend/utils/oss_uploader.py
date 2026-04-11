import os
import uuid
import logging
import time
from datetime import datetime
from typing import Optional, Dict, Any
import oss2
from oss2.exceptions import OssError, RequestError
from PIL import Image
import io

logger = logging.getLogger(__name__)

class OSSUploader:
    """阿里云OSS上传工具类"""
    
    def __init__(self, access_id: str, access_key: str, endpoint: str, bucket_name: str):
        """
        初始化OSS上传器
        
        Args:
            access_id: 阿里云AccessKey ID
            access_key: 阿里云AccessKey Secret
            endpoint: OSS endpoint
            bucket_name: OSS bucket名称
        """
        self.access_id = access_id
        self.access_key = access_key
        self.endpoint = endpoint
        self.bucket_name = bucket_name
        
        # 创建OSS认证对象
        self.auth = oss2.Auth(access_id, access_key)
        
        # 创建Bucket对象
        # 注意：oss2的超时设置通过put_object等方法的参数设置，而不是在Bucket构造时设置
        self.bucket = oss2.Bucket(self.auth, endpoint, bucket_name)
        
        # 默认超时配置（应用于所有操作）
        self.connect_timeout = 60  # 连接超时30秒
        self.operation_timeout = 300  # 操作超时300秒（5分钟）
        
        # 支持的图片格式
        self.supported_formats = ['JPEG', 'PNG', 'WebP', 'BMP']
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        
        # 重试配置
        self.max_retries = 3
        self.retry_delay = 1  # 初始重试延迟（秒）
        
        logger.info(f"初始化OSS上传器，bucket: {bucket_name}, endpoint: {endpoint}")
    
    def upload_image(self, file_obj, folder: str = "images") -> Dict[str, Any]:
        """
        上传图片到OSS（带重试机制）
        
        Args:
            file_obj: 文件对象（Flask上传的文件或PIL Image对象）
            folder: OSS中的文件夹路径
            
        Returns:
            Dict包含上传结果信息
        """
        # 生成唯一的文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = uuid.uuid4().hex[:8]
        
        try:
            # 处理不同类型的输入
            if hasattr(file_obj, 'filename') and hasattr(file_obj, 'stream'):
                # Flask上传的文件对象
                original_filename = file_obj.filename
                file_ext = self._get_file_extension(original_filename)
                
                # 读取文件内容
                file_obj.stream.seek(0)
                file_content = file_obj.stream.read()
                file_obj.stream.seek(0)  # 重置流位置以便重试
                
            elif isinstance(file_obj, Image.Image):
                # PIL Image对象
                file_ext = '.png'  # 默认保存为PNG
                original_filename = f"generated_image{file_ext}"
                
                # 将PIL Image转换为字节流
                img_buffer = io.BytesIO()
                file_obj.save(img_buffer, format='PNG', optimize=True, quality=95)
                file_content = img_buffer.getvalue()
                
            elif hasattr(file_obj, 'read'):
                # 文件流对象
                if hasattr(file_obj, 'seek'):
                    file_obj.seek(0)
                file_content = file_obj.read()
                if hasattr(file_obj, 'seek'):
                    file_obj.seek(0)  # 重置流位置以便重试
                file_ext = '.png'  # 默认扩展名
                original_filename = f"uploaded_image{file_ext}"
                
            else:
                raise ValueError("不支持的文件对象类型")
            
            # 验证文件大小
            if len(file_content) > self.max_file_size:
                raise ValueError(f"文件大小超过限制 ({self.max_file_size // (1024*1024)}MB)")
            
            logger.info(f"准备上传图片到OSS，大小: {len(file_content)} bytes, 原始文件名: {original_filename}")
            
            # 构建OSS对象键名
            filename = f"{folder}/{timestamp}_{unique_id}{file_ext}"
            
            # 使用重试机制上传到OSS
            result = self._upload_with_retry(filename, file_content)
            
            # 构建访问URL
            file_url = f"https://{self.bucket_name}.{self.endpoint}/{filename}"
            
            logger.info(f"成功上传图片到OSS: {filename}, URL: {file_url}, ETag: {result.etag}")
            
            return {
                'success': True,
                'filename': filename,
                'url': file_url,
                'original_filename': original_filename,
                'size': len(file_content),
                'etag': result.etag
            }
            
        except Exception as e:
            logger.error(f"OSS上传失败（所有重试均失败）: {str(e)}", exc_info=True)
            raise Exception(f"OSS上传失败: {str(e)}")
    
    def upload_generated_image(self, image_data: bytes, filename: str = None) -> Dict[str, Any]:
        """
        上传生成的图片到OSS（带重试机制）
        
        Args:
            image_data: 图片字节数据
            filename: 可选的文件名
            
        Returns:
            Dict包含上传结果信息
        """
        try:
            # 生成文件名
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                unique_id = uuid.uuid4().hex[:8]
                filename = f"generated/{timestamp}_{unique_id}.png"
            elif not filename.startswith('generated/'):
                filename = f"generated/{filename}"
            
            # 确保有正确的扩展名
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                filename += '.png'
            
            # 验证文件大小
            if len(image_data) > self.max_file_size:
                raise ValueError(f"文件大小超过限制 ({self.max_file_size // (1024*1024)}MB)")
            
            logger.info(f"准备上传生成图片到OSS，大小: {len(image_data)} bytes, 文件名: {filename}")
            
            # 使用重试机制上传到OSS
            result = self._upload_with_retry(filename, image_data)
            
            # 构建访问URL
            file_url = f"https://{self.bucket_name}.{self.endpoint}/{filename}"
            
            logger.info(f"成功上传生成图片到OSS: {filename}, URL: {file_url}, ETag: {result.etag}")
            
            return {
                'success': True,
                'filename': filename,
                'url': file_url,
                'size': len(image_data),
                'etag': result.etag
            }
            
        except Exception as e:
            logger.error(f"OSS上传生成图片失败（所有重试均失败）: {str(e)}", exc_info=True)
            raise Exception(f"OSS上传生成图片失败: {str(e)}")
    
    def delete_file(self, filename: str) -> bool:
        """
        删除OSS中的文件
        
        Args:
            filename: 要删除的文件名
            
        Returns:
            删除是否成功
        """
        try:
            self.bucket.delete_object(filename)
            logger.info(f"成功删除OSS文件: {filename}")
            return True
        except Exception as e:
            logger.error(f"删除OSS文件失败: {filename}, 错误: {str(e)}")
            return False
    
    def file_exists(self, filename: str) -> bool:
        """
        检查文件是否存在于OSS中
        
        Args:
            filename: 文件名
            
        Returns:
            文件是否存在
        """
        try:
            return self.bucket.object_exists(filename)
        except Exception as e:
            logger.error(f"检查OSS文件存在性失败: {filename}, 错误: {str(e)}")
            return False
    
    def get_file_url(self, filename: str) -> str:
        """
        获取文件的访问URL
        
        Args:
            filename: 文件名
            
        Returns:
            文件访问URL
        """
        return f"https://{self.bucket_name}.{self.endpoint}/{filename}"
    
    def _get_file_extension(self, filename: str) -> str:
        """获取文件扩展名"""
        return os.path.splitext(filename)[1].lower()
    
    def _upload_with_retry(self, filename: str, file_content: bytes):
        """
        带重试机制的上传方法
        
        Args:
            filename: OSS对象键名
            file_content: 文件内容（字节数据）
            
        Returns:
            OSS上传结果对象
            
        Raises:
            Exception: 所有重试失败后抛出异常
        """
        last_exception = None
        
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"OSS上传尝试 {attempt}/{self.max_retries}: {filename}")
                
                # 执行上传
                result = self.bucket.put_object(filename, file_content)
                
                # 验证上传是否成功
                if result.status == 200:
                    logger.info(f"OSS上传成功（第{attempt}次尝试）: {filename}, HTTP状态: {result.status}")
                    return result
                else:
                    logger.warning(f"OSS上传返回非200状态码: {result.status}")
                    raise Exception(f"OSS上传返回状态码: {result.status}")
                    
            except (RequestError, OssError) as e:
                last_exception = e
                error_msg = f"OSS上传失败（第{attempt}/{self.max_retries}次尝试）"
                
                # 记录详细的错误信息
                if isinstance(e, RequestError):
                    logger.warning(f"{error_msg} - 网络请求错误: {str(e)}")
                elif isinstance(e, OssError):
                    logger.warning(f"{error_msg} - OSS错误: 状态码={e.status}, 请求ID={e.request_id}, 错误码={e.code}, 消息={e.message}")
                else:
                    logger.warning(f"{error_msg} - 未知错误: {str(e)}")
                
                # 如果不是最后一次尝试，等待后重试
                if attempt < self.max_retries:
                    # 指数退避：第一次等1秒，第二次等2秒，第三次等4秒
                    delay = self.retry_delay * (2 ** (attempt - 1))
                    logger.info(f"等待 {delay} 秒后重试...")
                    time.sleep(delay)
                else:
                    logger.error(f"OSS上传失败，已达到最大重试次数 {self.max_retries}")
                    
            except Exception as e:
                last_exception = e
                logger.error(f"OSS上传发生意外错误（第{attempt}/{self.max_retries}次尝试）: {str(e)}", exc_info=True)
                
                # 对于意外错误，也尝试重试
                if attempt < self.max_retries:
                    delay = self.retry_delay * (2 ** (attempt - 1))
                    logger.info(f"等待 {delay} 秒后重试...")
                    time.sleep(delay)
                else:
                    logger.error(f"OSS上传失败，已达到最大重试次数 {self.max_retries}")
        
        # 所有重试都失败了
        if last_exception:
            raise last_exception
        else:
            raise Exception("OSS上传失败，原因未知")
    
    def test_connection(self) -> bool:
        """
        测试OSS连接
        
        Returns:
            连接是否成功
        """
        try:
            # 尝试列出bucket信息
            bucket_info = self.bucket.get_bucket_info()
            logger.info(f"OSS连接测试成功，bucket创建时间: {bucket_info.creation_date}")
            return True
        except Exception as e:
            logger.error(f"OSS连接测试失败: {str(e)}")
            return False