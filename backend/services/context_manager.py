import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from models.database import GenerationContext, GeneratedImage, UserFeedback, db
import logging

logger = logging.getLogger(__name__)

class ContextManagerService:
    """上下文记忆管理服务，用于优化重新生成的效果"""
    
    def __init__(self):
        self.context_types = {
            'product_info': {
                'weight': 1.0,
                'description': '产品基础信息和特性'
            },
            'style_preference': {
                'weight': 0.8,
                'description': '用户风格偏好学习'
            },
            'feedback_history': {
                'weight': 0.6,
                'description': '用户反馈历史记录'
            },
            'successful_elements': {
                'weight': 0.9,
                'description': '成功的生成元素'
            },
            'failed_attempts': {
                'weight': 0.4,
                'description': '失败尝试的避免指导'
            },
            'market_adaptation': {
                'weight': 0.7,
                'description': '市场适应性优化'
            }
        }
    
    def initialize_context(self, task_id: str, product_form: Dict[str, Any]) -> None:
        """
        初始化生成上下文
        
        Args:
            task_id: 任务ID
            product_form: 产品表单信息
        """
        try:
            # 保存产品基础信息
            product_context = GenerationContext(
                task_id=task_id,
                context_type='product_info',
                context_data=json.dumps({
                    'title': product_form.get('title', ''),
                    'target_market': product_form.get('targetMarket', 'US'),
                    'selling_points': product_form.get('sellingPoints', ''),
                    'dimensions': product_form.get('dimensions', {}),
                    'created_at': datetime.utcnow().isoformat()
                }),
                weight=self.context_types['product_info']['weight']
            )
            
            db.session.add(product_context)
            db.session.commit()
            
            logger.info(f"初始化任务 {task_id} 的上下文")
            
        except Exception as e:
            logger.error(f"初始化上下文失败: {str(e)}")
            db.session.rollback()
    
    def update_context(
        self, 
        task_id: str, 
        original_image: GeneratedImage, 
        new_image: GeneratedImage, 
        new_prompt: str
    ) -> None:
        """
        更新生成上下文，基于重新生成的结果
        
        Args:
            task_id: 任务ID
            original_image: 原始图片
            new_image: 新生成的图片
            new_prompt: 新使用的提示词
        """
        try:
            # 分析提示词变化
            prompt_analysis = self._analyze_prompt_changes(
                original_image.prompt_used, 
                new_prompt
            )
            
            # 更新风格偏好上下文
            style_context_data = {
                'prompt_evolution': prompt_analysis,
                'original_prompt': original_image.prompt_used,
                'improved_prompt': new_prompt,
                'image_type': new_image.image_type,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            self._update_or_create_context(
                task_id, 
                'style_preference', 
                style_context_data
            )
            
            logger.info(f"更新任务 {task_id} 的风格偏好上下文")
            
        except Exception as e:
            logger.error(f"更新上下文失败: {str(e)}")
    
    def record_user_feedback(
        self, 
        image_id: int, 
        feedback_type: str, 
        feedback_data: Dict[str, Any] = None
    ) -> None:
        """
        记录用户反馈
        
        Args:
            image_id: 图片ID
            feedback_type: 反馈类型 (like, dislike, regenerate, download)
            feedback_data: 详细反馈数据
        """
        try:
            image = GeneratedImage.query.get(image_id)
            if not image:
                raise ValueError(f"图片 {image_id} 不存在")
            
            # 记录反馈
            feedback = UserFeedback(
                image_id=image_id,
                feedback_type=feedback_type,
                feedback_data=json.dumps(feedback_data or {}),
                created_at=datetime.utcnow()
            )
            
            db.session.add(feedback)
            
            # 更新反馈历史上下文
            feedback_context_data = {
                'feedback_type': feedback_type,
                'image_type': image.image_type,
                'model_used': image.model_used,
                'feedback_details': feedback_data,
                'recorded_at': datetime.utcnow().isoformat()
            }
            
            self._update_or_create_context(
                image.task_id,
                'feedback_history',
                feedback_context_data,
                append=True
            )
            
            # 如果是正面反馈，更新成功元素
            if feedback_type in ['like', 'download']:
                self._record_successful_elements(image, feedback_data)
            
            # 如果是负面反馈，记录失败尝试
            elif feedback_type == 'dislike':
                self._record_failed_attempt(image, feedback_data)
            
            db.session.commit()
            logger.info(f"记录图片 {image_id} 的用户反馈: {feedback_type}")
            
        except Exception as e:
            logger.error(f"记录用户反馈失败: {str(e)}")
            db.session.rollback()
    
    def get_generation_context(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务的完整生成上下文
        
        Args:
            task_id: 任务ID
            
        Returns:
            整合的上下文信息
        """
        try:
            contexts = GenerationContext.query.filter_by(task_id=task_id).all()
            
            integrated_context = {
                'task_id': task_id,
                'contexts': {},
                'recommendations': [],
                'confidence_score': 0.0
            }
            
            total_weight = 0
            weighted_score = 0
            
            for context in contexts:
                context_data = json.loads(context.context_data)
                context_type = context.context_type
                
                integrated_context['contexts'][context_type] = {
                    'data': context_data,
                    'weight': context.weight,
                    'updated_at': context.updated_at.isoformat() if context.updated_at else None
                }
                
                # 计算置信度分数
                total_weight += context.weight
                weighted_score += context.weight * self._calculate_context_quality(context_data)
            
            # 生成推荐
            integrated_context['recommendations'] = self._generate_recommendations(integrated_context['contexts'])
            
            # 计算最终置信度
            if total_weight > 0:
                integrated_context['confidence_score'] = weighted_score / total_weight
            
            return integrated_context
            
        except Exception as e:
            logger.error(f"获取生成上下文失败: {str(e)}")
            return {'task_id': task_id, 'contexts': {}, 'recommendations': [], 'confidence_score': 0.0}
    
    def clean_old_contexts(self, days_old: int = 30) -> int:
        """
        清理旧的上下文数据
        
        Args:
            days_old: 清理多少天前的数据
            
        Returns:
            清理的记录数量
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            old_contexts = GenerationContext.query.filter(
                GenerationContext.created_at < cutoff_date
            ).all()
            
            count = len(old_contexts)
            
            for context in old_contexts:
                db.session.delete(context)
            
            db.session.commit()
            logger.info(f"清理了 {count} 条旧上下文记录")
            
            return count
            
        except Exception as e:
            logger.error(f"清理旧上下文失败: {str(e)}")
            db.session.rollback()
            return 0
    
    def _update_or_create_context(
        self, 
        task_id: str, 
        context_type: str, 
        data: Dict[str, Any], 
        append: bool = False
    ) -> None:
        """更新或创建上下文"""
        existing_context = GenerationContext.query.filter_by(
            task_id=task_id, 
            context_type=context_type
        ).first()
        
        if existing_context and append:
            # 追加数据
            existing_data = json.loads(existing_context.context_data)
            if isinstance(existing_data, list):
                existing_data.append(data)
            else:
                existing_data = [existing_data, data]
            
            existing_context.context_data = json.dumps(existing_data)
            existing_context.updated_at = datetime.utcnow()
        elif existing_context:
            # 更新数据
            existing_context.context_data = json.dumps(data)
            existing_context.updated_at = datetime.utcnow()
        else:
            # 创建新上下文
            new_context = GenerationContext(
                task_id=task_id,
                context_type=context_type,
                context_data=json.dumps(data),
                weight=self.context_types.get(context_type, {}).get('weight', 1.0)
            )
            db.session.add(new_context)
    
    def _record_successful_elements(self, image: GeneratedImage, feedback_data: Dict[str, Any]) -> None:
        """记录成功的生成元素"""
        successful_data = {
            'image_type': image.image_type,
            'model_used': image.model_used,
            'prompt_elements': self._extract_prompt_elements(image.prompt_used),
            'feedback_details': feedback_data,
            'success_recorded_at': datetime.utcnow().isoformat()
        }
        
        self._update_or_create_context(
            image.task_id,
            'successful_elements',
            successful_data,
            append=True
        )
    
    def _record_failed_attempt(self, image: GeneratedImage, feedback_data: Dict[str, Any]) -> None:
        """记录失败的尝试"""
        failed_data = {
            'image_type': image.image_type,
            'model_used': image.model_used,
            'prompt_elements': self._extract_prompt_elements(image.prompt_used),
            'failure_reasons': feedback_data.get('reasons', []),
            'failure_recorded_at': datetime.utcnow().isoformat()
        }
        
        self._update_or_create_context(
            image.task_id,
            'failed_attempts',
            failed_data,
            append=True
        )
    
    def _analyze_prompt_changes(self, original_prompt: str, new_prompt: str) -> Dict[str, Any]:
        """分析提示词变化"""
        return {
            'original_length': len(original_prompt),
            'new_length': len(new_prompt),
            'length_change': len(new_prompt) - len(original_prompt),
            'change_ratio': len(new_prompt) / len(original_prompt) if original_prompt else 1.0,
            'analysis_date': datetime.utcnow().isoformat()
        }
    
    def _extract_prompt_elements(self, prompt: str) -> List[str]:
        """提取提示词关键元素"""
        # 简单的关键词提取
        key_elements = []
        keywords = [
            'photorealistic', 'professional', 'high resolution', 'clean background',
            'natural lighting', 'commercial photography', 'product focus',
            'white background', 'detailed', 'sharp focus'
        ]
        
        prompt_lower = prompt.lower()
        for keyword in keywords:
            if keyword in prompt_lower:
                key_elements.append(keyword)
        
        return key_elements
    
    def _calculate_context_quality(self, context_data: Dict[str, Any]) -> float:
        """计算上下文数据质量分数"""
        score = 0.5  # 基础分数
        
        # 检查数据完整性
        if isinstance(context_data, dict):
            if context_data.get('created_at') or context_data.get('updated_at'):
                score += 0.2
            
            if len(context_data) > 3:  # 有足够的字段
                score += 0.2
            
            # 检查时效性
            if context_data.get('updated_at'):
                try:
                    updated_time = datetime.fromisoformat(context_data['updated_at'].replace('Z', '+00:00'))
                    age_hours = (datetime.utcnow() - updated_time).total_seconds() / 3600
                    if age_hours < 24:  # 24小时内
                        score += 0.1
                except:
                    pass
        
        return min(1.0, score)
    
    def _generate_recommendations(self, contexts: Dict[str, Any]) -> List[str]:
        """基于上下文生成推荐"""
        recommendations = []
        
        # 基于成功元素的推荐
        if 'successful_elements' in contexts:
            recommendations.append("继续使用之前成功的视觉元素和风格")
        
        # 基于反馈历史的推荐
        if 'feedback_history' in contexts:
            feedback_data = contexts['feedback_history']['data']
            if isinstance(feedback_data, list) and len(feedback_data) > 0:
                recent_feedback = feedback_data[-3:]  # 最近3条反馈
                positive_count = sum(1 for f in recent_feedback if f.get('feedback_type') in ['like', 'download'])
                if positive_count >= 2:
                    recommendations.append("用户对当前风格满意，可继续优化细节")
                else:
                    recommendations.append("考虑调整生成风格以提高用户满意度")
        
        # 基于失败尝试的推荐
        if 'failed_attempts' in contexts:
            recommendations.append("避免使用之前导致不满意结果的元素")
        
        return recommendations
