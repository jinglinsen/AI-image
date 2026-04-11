import oss2
import logging
import sys
import os
from typing import List, Dict, Any

# 添加父目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

logger = logging.getLogger(__name__)

class OSSCORSManager:
    """OSS CORS配置管理器"""
    
    def __init__(self):
        """初始化CORS管理器"""
        self.auth = oss2.Auth(Config.OSS_ACCESS_ID, Config.OSS_ACCESS_KEY)
        self.bucket = oss2.Bucket(self.auth, Config.OSS_ENDPOINT, Config.OSS_BUCKET)
    
    def setup_cors_rules(self) -> bool:
        """
        设置OSS Bucket的CORS规则
        
        Returns:
            设置是否成功
        """
        try:
            # 定义CORS规则
            cors_rules = [
                oss2.models.CorsRule(
                    allowed_origins=['*'],  # 允许所有来源
                    allowed_methods=['GET', 'POST', 'PUT', 'DELETE', 'HEAD'],
                    allowed_headers=['*'],
                    expose_headers=['ETag', 'x-oss-request-id'],
                    max_age_seconds=3600
                ),
                oss2.models.CorsRule(
                    allowed_origins=['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:5173'],
                    allowed_methods=['GET', 'HEAD'],
                    allowed_headers=['*'],
                    expose_headers=['ETag', 'x-oss-request-id', 'Access-Control-Allow-Origin'],
                    max_age_seconds=86400  # 24小时
                )
            ]
            
            # 应用CORS规则
            self.bucket.put_bucket_cors(oss2.models.BucketCors(cors_rules))
            logger.info("OSS CORS规则设置成功")
            return True
            
        except Exception as e:
            logger.error(f"设置OSS CORS规则失败: {str(e)}")
            return False
    
    def get_cors_rules(self) -> List[Dict[str, Any]]:
        """
        获取当前的CORS规则
        
        Returns:
            CORS规则列表
        """
        try:
            cors_config = self.bucket.get_bucket_cors()
            rules = []
            
            for rule in cors_config.rules:
                rules.append({
                    'allowed_origins': rule.allowed_origins,
                    'allowed_methods': rule.allowed_methods,
                    'allowed_headers': rule.allowed_headers,
                    'expose_headers': rule.expose_headers,
                    'max_age_seconds': rule.max_age_seconds
                })
            
            return rules
            
        except Exception as e:
            logger.error(f"获取OSS CORS规则失败: {str(e)}")
            return []
    
    def delete_cors_rules(self) -> bool:
        """
        删除所有CORS规则
        
        Returns:
            删除是否成功
        """
        try:
            self.bucket.delete_bucket_cors()
            logger.info("OSS CORS规则删除成功")
            return True
            
        except Exception as e:
            logger.error(f"删除OSS CORS规则失败: {str(e)}")
            return False

def setup_oss_cors():
    """设置OSS CORS规则的便捷函数"""
    if not Config.OSS_ENABLED:
        logger.warning("OSS未启用，跳过CORS设置")
        return False
    
    cors_manager = OSSCORSManager()
    return cors_manager.setup_cors_rules()

if __name__ == '__main__':
    # 直接运行此脚本来设置CORS规则
    logging.basicConfig(level=logging.INFO)
    
    print("正在设置OSS CORS规则...")
    success = setup_oss_cors()
    
    if success:
        print("OK OSS CORS设置成功")
        
        # 显示当前规则
        cors_manager = OSSCORSManager()
        rules = cors_manager.get_cors_rules()
        print(f"当前CORS规则数量: {len(rules)}")
        for i, rule in enumerate(rules, 1):
            print(f"规则 {i}:")
            print(f"  允许的来源: {rule['allowed_origins']}")
            print(f"  允许的方法: {rule['allowed_methods']}")
            print(f"  允许的头部: {rule['allowed_headers']}")
            print(f"  暴露的头部: {rule['expose_headers']}")
            print(f"  最大缓存时间: {rule['max_age_seconds']}秒")
    else:
        print("ERROR OSS CORS设置失败")