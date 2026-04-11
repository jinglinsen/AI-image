import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime

class PromptBuilderService:
    """提示词构建服务，基于模板动态生成高质量提示词"""
    
    def __init__(self):
        self.image_type_prompts = {
            'main': {
                'system_prompt': 'You are a professional Amazon product photographer specializing in main product images. Create a photo-realistic main product image with pure white background (RGB 255,255,255). The product should occupy 85% of the frame, be sharply focused, and have professional commercial lighting with soft shadows. CRITICAL: Maintain exact product appearance - preserve all colors, details, textures, and features from the input images without any modifications.',
                'requirements': [
                    'Pure white background (RGB 255,255,255)',
                    'Product occupies 85% of frame',
                    'Sharp focus on product',
                    'Professional commercial lighting',
                    'Soft natural shadows',
                    'Preserve exact product colors and details',
                    'Maintain all original product features',
                    'No text, logos, or watermarks on background',
                    'Ultra-high resolution and detail'
                ]
            },
            'infographic': {
                'system_prompt': 'You are a professional infographic designer for Amazon listings. Create a clean, informative infographic that showcases key product features and benefits through visual elements and minimal text.',
                'requirements': [
                    'Clean professional layout',
                    'Highlight key features visually',
                    'Minimal but effective text',
                    'Easy to understand at a glance',
                    'Brand-consistent colors',
                    'High contrast for readability'
                ]
            },
            'lifestyle': {
                'system_prompt': 'You are a lifestyle photographer for Amazon products. Create an emotional, aspirational scene showing the product in real-life use, helping customers envision the product in their daily lives. IMPORTANT: Keep the product exactly as it appears in the input images - preserve all colors, features, and details while placing it in the lifestyle context.',
                'requirements': [
                    'Natural real-life setting',
                    'Emotional connection',
                    'Product naturally integrated but unchanged',
                    'Preserve original product appearance',
                    'Aspirational but relatable',
                    'Warm inviting lighting',
                    'Space for text overlay'
                ]
            },
            'size': {
                'system_prompt': 'You are a technical photographer specializing in size demonstration images. Create a clear image showing product dimensions.',
                'requirements': [
                    'Clear size reference objects,if available',
                    'Accurate scale representation',
                    'Mark the product dimensions with solid or dotted lines',
                    'Clean uncluttered composition',
                    'Good lighting for clarity',
                    'Multiple angle views if helpful'
                ]
            },
            'detail': {
                'system_prompt': 'You are a macro photographer specializing in product detail shots. Create close-up images that showcase important product features, materials, craftsmanship, or functional elements. ESSENTIAL: Maintain absolute accuracy to the original product - every texture, color, finish, and detail must be precisely preserved.',
                'requirements': [
                    'Sharp macro detail focus',
                    'Highlight key features with precision',
                    'Preserve exact materials and textures',
                    'Show material quality',
                    'Excellent lighting for texture',
                    'Clean background'
                ]
            },
            'angle': {
                'system_prompt': 'You are a product photographer creating multi-angle views. Show the product from different perspectives to give customers a comprehensive understanding of its design and features.',
                'requirements': [
                    'Multiple distinct angles',
                    'Consistent lighting across views',
                    'Professional composition',
                    'Clear view of all sides',
                    'Organized layout'
                ]
            },
            'instruction': {
                'system_prompt': 'You are an instructional photographer creating step-by-step visual guides. Show clear, easy-to-follow instructions for product assembly, setup, or usage.',
                'requirements': [
                    'Clear step-by-step progression',
                    'Easy to follow visually',
                    'Hands demonstrating if needed',
                    'Good lighting for clarity',
                    'Logical sequence flow'
                ]
            },
            'comparison': {
                'system_prompt': 'You are a comparison photographer for Amazon listings. Create side-by-side comparisons highlighting the advantages and unique selling points of the product versus alternatives.',
                'requirements': [
                    'Clear side-by-side layout',
                    'Highlight key differences',
                    'Fair but favorable comparison',
                    'Professional presentation',
                    'Easy to understand benefits'
                ]
            },
            'packaging': {
                'system_prompt': 'You are a packaging photographer for Amazon listings. Create appealing images of product packaging that convey quality, giftability, and what customers will receive.',
                'requirements': [
                    'Attractive package presentation',
                    'Show contents relationship',
                    'Gift-worthy appearance',
                    'Professional unboxing feel',
                    'Brand quality impression'
                ]
            }
        }
        
        self.market_styles = {
            'US': {
                'style_description': 'American market preferences: spacious, family-oriented scenes with bright, optimistic lighting. Emphasize functionality, durability, and family lifestyle.',
                'color_palette': 'Bright, vibrant colors with good contrast',
                'setting_preferences': 'Modern American homes, outdoor spaces, family gatherings'
            },
            'UK': {
                'style_description': 'British market preferences: elegant, classic styling with sophisticated color schemes. Emphasize tradition, quality craftsmanship, and understated luxury.',
                'color_palette': 'Muted, sophisticated colors with classic appeal',
                'setting_preferences': 'Traditional British homes, countryside, elegant interiors'
            },
            'DE': {
                'style_description': 'German market preferences: clean, minimalist design emphasizing engineering quality and functionality. Focus on precision, durability, and efficient design.',
                'color_palette': 'Clean, minimal color schemes with focus on functionality',
                'setting_preferences': 'Modern minimalist interiors, organized spaces, technical environments'
            },
            'JP': {
                'style_description': 'Japanese market preferences: clean, minimalist aesthetics with attention to detail and harmony. Emphasize simplicity, quality, and thoughtful design.',
                'color_palette': 'Soft, harmonious colors with natural elements',
                'setting_preferences': 'Japanese-style interiors, natural settings, organized minimal spaces'
            },
            'IN': {
                'style_description': 'Indian market preferences: vibrant, value-focused presentation emphasizing practicality and family use. Show versatility and cost-effectiveness.',
                'color_palette': 'Vibrant, warm colors that feel welcoming',
                'setting_preferences': 'Indian family homes, practical everyday settings, multi-generational use'
            }
        }
    
    def build_prompt(
        self,
        product_form: Dict[str, Any],
        image_type: str,
        main_prompt: str,
        reference_images: List[Dict] = None,
        competitors: List[Dict] = None,
        type_specific_references: List[Dict] = None,
        size: str = "1024x1024",
        ratio: str = "1:1",
        allow_text_in_image: bool = False
    ) -> str:
        """
        构建完整的生成提示词
        
        Args:
            product_form: 产品信息表单
            image_type: 图片类型
            main_prompt: 用户主要提示词
            reference_images: 参考图片信息
            competitors: 竞品信息
            
        Returns:
            构建好的完整提示词
        """
        try:
            # 获取目标市场
            target_market = product_form.get('targetMarket', 'US')
            
            # 获取图片类型的系统提示词
            image_config = self.image_type_prompts.get(image_type, self.image_type_prompts['main'])
            
            # 如果是文字密集型图片类型但要求无文字，需要特殊处理
            text_heavy_types = ['infographic', 'instruction', 'comparison', 'size']
            if not allow_text_in_image and image_type in text_heavy_types:
                # 修改系统提示词以适应无文字要求
                if image_type == 'infographic':
                    image_config = {
                        'system_prompt': 'You are a visual designer creating a purely visual infographic without any text. Use icons, symbols, visual metaphors, color coding, and graphic elements to convey information. NO text, letters, or numbers allowed.',
                        'requirements': [
                            'Pure visual communication through icons and symbols',
                            'Color coding to represent different features',
                            'Visual metaphors and graphic elements',
                            'Clean professional layout without text',
                            'High contrast visual hierarchy',
                            'Intuitive visual flow and organization'
                        ]
                    }
                elif image_type == 'size':
                    image_config = {
                        'system_prompt': 'You are a photographer creating size demonstration images using only visual comparison objects. Show scale through familiar reference objects without any text, measurements, or dimensional markings.',
                        'requirements': [
                            'Visual size comparison with familiar objects',
                            'Multiple reference objects for scale',
                            'Clear proportional relationships',
                            'Clean composition without text or measurements',
                            'Professional lighting for size clarity',
                            'Intuitive size understanding through visuals only'
                        ]
                    }
                elif image_type == 'instruction':
                    image_config = {
                        'system_prompt': 'You are creating visual step-by-step instructions using only imagery. Show the process through clear visual sequences, hand gestures, arrows, and visual cues without any text or labels.',
                        'requirements': [
                            'Clear visual step progression',
                            'Hand demonstrations and gestures',
                            'Visual arrows and flow indicators',
                            'Intuitive sequence understanding',
                            'No text labels or written instructions',
                            'Pure visual communication of process'
                        ]
                    }
                elif image_type == 'comparison':
                    image_config = {
                        'system_prompt': 'You are creating visual product comparisons using only imagery. Show differences through visual elements, color coding, checkmarks, crosses, and graphic indicators without any text.',
                        'requirements': [
                            'Visual comparison through graphic elements',
                            'Color coding for advantages/disadvantages',
                            'Visual checkmarks and crosses',
                            'Side-by-side visual presentation',
                            'No text labels or written comparisons',
                            'Intuitive visual advantage communication'
                        ]
                    }
            
            # 构建完整提示词
            prompt_parts = []
            
            # 0. 文字禁止前置声明（如果需要）
            if not allow_text_in_image:
                prompt_parts.append("TEXTLESS IMAGE MANDATE")
                prompt_parts.append("CRITICAL: This image must contain ZERO text, letters, numbers, or any readable content.")
                prompt_parts.append("=" * 80)
            
            # 1. 核心指令
            prompt_parts.append("### CORE DIRECTIVE ###")
            prompt_parts.append(image_config['system_prompt'])
            prompt_parts.append(f"Target market: {target_market} - {self.market_styles[target_market]['style_description']}")
            
            # 添加明确的尺寸和比例要求
            aspect_ratio_instructions = self._get_aspect_ratio_instructions(ratio, size)
            prompt_parts.append(f"### IMAGE SPECIFICATIONS ###")
            prompt_parts.append(f"Image dimensions: {size}")
            prompt_parts.append(f"Aspect ratio: {ratio}")
            prompt_parts.append(aspect_ratio_instructions)
            
            # 2. 产品定义
            prompt_parts.append("\n### PRODUCT DEFINITION ###")
            prompt_parts.append(f"Product: {product_form.get('title', 'Product')}")
            
            if product_form.get('sellingPoints'):
                prompt_parts.append(f"Key selling points: {product_form['sellingPoints']}")
            
            if product_form.get('dimensions'):
                dims = product_form['dimensions']
                if dims.get('length') and dims.get('width') and dims.get('height'):
                    prompt_parts.append(f"Dimensions: {dims['length']}×{dims['width']}×{dims['height']} {dims.get('unit', 'cm')}")
            
            # 3. 市场与文化背景
            prompt_parts.append("\n### MARKET & CULTURAL CONTEXT ###")
            market_info = self.market_styles[target_market]
            prompt_parts.append(f"Style adaptation: {market_info['style_description']}")
            prompt_parts.append(f"Color preferences: {market_info['color_palette']}")
            prompt_parts.append(f"Setting preferences: {market_info['setting_preferences']}")
            
            # 4. 竞品分析（如果提供）
            if competitors and len(competitors) > 0:
                prompt_parts.append("\n### COMPETITIVE ANALYSIS ###")
                competitor_insights = self._analyze_competitors(competitors)
                prompt_parts.append(competitor_insights)
            
            # 5. 产品保真度要求
            prompt_parts.append("\n### PRODUCT FIDELITY REQUIREMENTS ###")
            product_fidelity_instructions = self._build_product_fidelity_instructions(main_prompt)
            prompt_parts.append(product_fidelity_instructions)
            
            # 调试输出产品保真度模式
            fidelity_mode = "设计自由" if "ignore original" in product_fidelity_instructions.lower() else "产品保真"
            print(f"产品保真度模式: {fidelity_mode}模式")
            if fidelity_mode == "设计自由":
                print("   ↳ 用户明确要求修改产品设计")
            else:
                print("   ↳ 保持原产品所有细节和颜色不变")
            
            # 调试输出文字生成设置
            text_mode = "允许文字" if allow_text_in_image else "禁止文字"
            print(f"📝 文字生成模式: {text_mode}")
            if not allow_text_in_image:
                print("   ↳ 强制禁止任何文字、字符、Logo等文本元素")
            
            # 6. 创意执行
            prompt_parts.append("\n### CREATIVE EXECUTION ###")
            prompt_parts.append(f"User creative direction: {main_prompt}")
            
            # 6.1 文本元素约束（当不允许图文时，强制禁止任何文字/字符）
            if not allow_text_in_image:
                prompt_parts.append("\n### CRITICAL: ABSOLUTELY NO TEXT ALLOWED ###")
                prompt_parts.append(
                    "MANDATORY TEXTLESS REQUIREMENT\n"
                    "This is a CRITICAL requirement that MUST be followed:\n"
                    "- ZERO text, letters, numbers, characters, or symbols of any kind\n"
                    "- NO logos, watermarks, brand names, or typographic elements\n"
                    "- NO captions, subtitles, labels, or UI overlays\n"
                    "- NO infographic text, measurements, or dimensional markings\n"
                    "- NO price tags, product codes, or any written information\n"
                    "- NO artistic text, decorative lettering, or stylized fonts\n"
                    "- The image must be PURELY VISUAL with NO readable content whatsoever\n"
                    "\n"
                    "IMPORTANT: If you feel compelled to add text for any reason, DO NOT DO IT.\n"
                    "Express all information through visual composition, lighting, colors, and product positioning only.\n"
                    "This is a STRICT requirement - any text will result in generation failure."
                )

            # 7. 参考图片指导（优先使用类型特定的参考图）
            ref_images_to_use = type_specific_references if type_specific_references else reference_images
            if ref_images_to_use:
                prompt_parts.append("\n### VISUAL REFERENCE GUIDANCE ###")
                ref_instructions = self._build_reference_instructions(ref_images_to_use)
                prompt_parts.append(ref_instructions)
            
            # 7. 技术规格和要求
            prompt_parts.append("\n### TECHNICAL SPECIFICATIONS ###")
            prompt_parts.extend([
                "Style: Photorealistic, ultra-high detail, clean, professional",
                "Technical specs: 8K resolution, professional DSLR quality, 50mm lens equivalent",
                f"Specific requirements for {image_type}:"
            ])
            
            for req in image_config['requirements']:
                prompt_parts.append(f"- {req}")
            
            # 8. 负面提示词
            prompt_parts.append("\n### NEGATIVE PROMPTS ###")
            negative_prompts = [
                "blurry", "low resolution", "pixelated", "watermark", "text overlay",
                "logo", "brand name", "unrealistic shadows", "cartoon style", 
                "oversaturated", "poor lighting", "cluttered background"
            ]
            if not allow_text_in_image:
                # 大幅扩展文字相关的负面提示词
                text_negative_prompts = [
                    "text", "letters", "characters", "typography", "captions", "subtitles", 
                    "labels", "UI overlay", "infographic text", "words", "writing", "script",
                    "font", "alphabet", "numbers", "digits", "symbols", "signs", "signage",
                    "price tag", "product code", "barcode", "QR code", "measurements",
                    "dimensions", "size indicators", "brand text", "logo text", "watermark text",
                    "copyright text", "trademark", "product name text", "model number",
                    "instructions text", "warning text", "description text", "title text",
                    "heading", "banner text", "promotional text", "advertising text",
                    "decorative text", "artistic lettering", "calligraphy", "handwriting",
                    "printed text", "embossed text", "engraved text", "sticker text",
                    "label sticker", "name tag", "price sticker", "information panel",
                    "text bubble", "speech bubble", "annotation", "callout", "pointer text",
                    "readable content", "legible text", "visible text", "any textual element"
                ]
                negative_prompts.extend(text_negative_prompts)
                
                # 添加额外的强调
                prompt_parts.append("CRITICAL NEGATIVE PROMPTS FOR TEXTLESS IMAGE:")
                prompt_parts.append(f"ABSOLUTELY AVOID: {', '.join(text_negative_prompts)}")
                prompt_parts.append(f"\nGeneral negative prompts: {', '.join(negative_prompts[:7])}")
            else:
                prompt_parts.append(f"Avoid: {', '.join(negative_prompts)}")
            
            # 9. 最终文字禁止强调（如果需要）
            if not allow_text_in_image:
                prompt_parts.append("\n" + "=" * 80)
                prompt_parts.append("FINAL REMINDER: ABSOLUTELY NO TEXT IN THIS IMAGE")
                prompt_parts.append("Before generating, double-check: Does this image contain ANY text, letters, numbers, or symbols?")
                prompt_parts.append("If YES, modify the image to remove ALL textual elements.")
                prompt_parts.append("This is a MANDATORY requirement - the image must be purely visual.")
                prompt_parts.append("=" * 80)
            
            # 组合所有部分
            final_prompt = "\n".join(prompt_parts)
            
            # 在控制台输出最终提示词
            print("\n" + "="*80)
            print("完整生成提示词 (Complete Generation Prompt)")
            print("="*80)
            print(f"图片类型: {image_type}")
            print(f"目标市场: {target_market}")
            print(f"提示词长度: {len(final_prompt)} 字符")
            print("-"*80)
            print(final_prompt)
            print("-"*80)
            print("准备发送到AI模型...")
            print("="*80)
            
            return final_prompt
            
        except Exception as e:
            print(f"提示词构建失败: {e}")
            # 如果构建失败，返回基础提示词
            fallback_prompt = f"Create a professional, high-quality {image_type} image of: {product_form.get('title', 'Product')}\nUser direction: {main_prompt}"
            
            if not allow_text_in_image:
                fallback_prompt += "\n\nCRITICAL: This image must contain ZERO text, letters, numbers, or any readable content. The image must be purely visual."
            
            return fallback_prompt
    
    def _get_aspect_ratio_instructions(self, ratio: str, size: str) -> str:
        """
        根据比例生成详细的构图指令
        
        Args:
            ratio: 图片比例 (如 1:1, 3:4, 4:3, 16:9)
            size: 图片尺寸 (如 1024x1024)
            
        Returns:
            详细的构图指令
        """
        ratio_instructions = {
            '1:1': "SQUARE FORMAT (1:1): Create a perfectly square composition. Center the subject symmetrically. Use balanced visual weight on all sides. Ideal for profile pictures and balanced product shots.",
            '3:4': "PORTRAIT FORMAT (3:4): Vertical orientation with emphasis on height. Center the subject with slight upward focus. Great for showing full product height or lifestyle scenes with people.",
            '4:3': "LANDSCAPE FORMAT (4:3): Horizontal orientation with width emphasis. Use rule of thirds for subject placement. Perfect for environmental product shots and wider scenes.",
            '16:9': "WIDESCREEN FORMAT (16:9): Ultra-wide cinematic composition. Strong horizontal emphasis. Use leading lines and panoramic views. Ideal for lifestyle and environmental contexts."
        }
        
        base_instruction = ratio_instructions.get(ratio, ratio_instructions['1:1'])
        
        # 添加尺寸特定的指令
        if size == "1024x1024":
            base_instruction += " High resolution 1024x1024 pixels ensures sharp detail and print quality."
        elif "1024" in size:
            base_instruction += f" High resolution {size} pixels for professional quality output."
        
        # 强调比例的重要性
        base_instruction += f" CRITICAL: The final image MUST strictly maintain the {ratio} aspect ratio. Do not crop or alter the proportions."
        
        return base_instruction
    
    def _build_product_fidelity_instructions(self, main_prompt: str) -> str:
        """
        构建产品保真度指令，确保保持原产品细节和颜色
        
        Args:
            main_prompt: 用户主要提示词
            
        Returns:
            产品保真度指令
        """
        # 检查用户提示词中是否明确要求改变产品细节
        ignore_original_keywords = [
            # 中文关键词
            "不要保持", "无需保持", "改变颜色", "修改颜色", "换个颜色", "不同颜色", "改变外观",
            "新设计", "重新设计", "不要原样", "完全不同", "改变样式", "修改设计",
            # 英文关键词
            "ignore original", "change color", "different color", "modify appearance",
            "alter design", "redesign", "completely different", "new design", "don't keep",
            "change style", "modify design", "different style", "new appearance"
        ]
        
        # 更智能的检测：检查是否有明确的改变指令
        main_prompt_lower = main_prompt.lower()
        should_ignore_original = any(keyword.lower() in main_prompt_lower for keyword in ignore_original_keywords)
        
        # 额外检测：如果提示词包含强烈的风格改变指令
        style_change_patterns = [
            "make it", "turn it", "transform", "convert", "变成", "做成", "转换成"
        ]
        strong_change_indicators = any(pattern in main_prompt_lower for pattern in style_change_patterns)
        
        if strong_change_indicators:
            # 但如果同时提到了"保持"或"keep"，则优先保持原样
            preserve_keywords = ["保持", "keep", "maintain", "preserve", "原样", "不变"]
            has_preserve_instruction = any(keyword in main_prompt_lower for keyword in preserve_keywords)
            if not has_preserve_instruction:
                should_ignore_original = True
        
        if should_ignore_original:
            return """DESIGN FREEDOM MODE: User has explicitly requested changes to the original product design.
You may creatively interpret and modify colors, details, and design elements as directed by the user's prompt.
Focus on the creative direction provided while maintaining product functionality and category."""
        
        else:
            return """PRODUCT FIDELITY MODE: CRITICAL - Maintain absolute fidelity to the original product's visual characteristics:

COLOR PRESERVATION:
- Preserve exact colors, finishes, and materials from the input product images
- Match color temperature, saturation, and hue precisely
- Maintain material properties (metallic, matte, glossy, textured surfaces)
- Do NOT alter or "improve" the original color scheme unless specifically requested

DETAIL PRESERVATION:
- Keep all product features, buttons, logos, text, patterns exactly as shown
- Preserve structural elements, proportions, and design details
- Maintain surface textures, manufacturing details, and wear patterns
- If original images are blurry or low quality, enhance clarity while keeping ALL details identical

SHAPE & FORM FIDELITY:
- Exact product dimensions and proportions must be maintained
- Keep all functional elements in their original positions
- Preserve product silhouette and distinctive design elements
- Do NOT "stylize" or "improve" the product design

ENHANCEMENT GUIDELINES:
- ONLY improve image quality, lighting, and clarity
- Remove blur, noise, or image artifacts while preserving every detail
- Enhance sharpness and definition without changing any product characteristics
- Upgrade resolution while maintaining pixel-perfect detail accuracy

STRICT PROHIBITIONS:
- Do NOT change any colors whatsoever
- Do NOT add, remove, or modify any product features
- Do NOT "upgrade" or "modernize" the product design
- Do NOT apply artistic interpretation to product elements

This is a PRODUCT PHOTOGRAPHY task - treat the input as the definitive reference for all visual elements."""
    
    def build_rework_prompt(
        self,
        original_prompt: str,
        user_modifications: Dict[str, Any],
        context: Dict[str, Any],
        reference_images: List[Dict] = None,
        original_image_info: Dict[str, Any] = None
    ) -> str:
        """
        构建重新生成的提示词，基于原始提示词和用户修改
        
        Args:
            original_prompt: 原始提示词
            user_modifications: 用户修改内容
            context: 生成上下文
            reference_images: 新的参考图片
            
        Returns:
            优化后的提示词
        """
        try:
            prompt_parts = []
            
            # 基于原始提示词
            prompt_parts.append("### REWORK BASED ON FEEDBACK ###")
            prompt_parts.append("Previous generation context maintained with the following improvements:")
            
            # 添加改进方向指导（如果提供了原图片信息）
            if original_image_info:
                prompt_parts.append("\n### IMPROVEMENT DIRECTION ###")
                prompt_parts.append("Based on the previous generation context, focus on these improvement areas:")
                
                # 根据图片类型提供具体的改进建议
                image_type = original_image_info.get('type', 'main')
                improvement_suggestions = self._get_rework_improvement_suggestions(image_type)
                prompt_parts.append(improvement_suggestions)
                
                # 添加质量提升指导（不强制参考上一张图）
                prompt_parts.append("\nQUALITY ENHANCEMENT FOCUS:")
                prompt_parts.append("- Create a higher quality version addressing any previous limitations")
                prompt_parts.append("- Improve visual appeal and professional presentation")
                prompt_parts.append("- Maintain product accuracy while enhancing overall impact")
                prompt_parts.append("- Consider better composition, lighting, or detail clarity")
            
            # 添加产品保真度要求（对于重新生成同样重要）
            if user_modifications.get('prompt_modifications'):
                product_fidelity_instructions = self._build_product_fidelity_instructions(user_modifications['prompt_modifications'])
                prompt_parts.append(f"\n### PRODUCT FIDELITY FOR REWORK ###")
                prompt_parts.append(product_fidelity_instructions)
                prompt_parts.append(f"\nUser feedback and modifications: {user_modifications['prompt_modifications']}")
            else:
                # 默认保持产品保真度
                prompt_parts.append(f"\n### PRODUCT FIDELITY FOR REWORK ###")
                prompt_parts.append(self._build_product_fidelity_instructions(""))
            
            # 添加上下文学习
            if context.get('style_preferences'):
                prompt_parts.append(f"\nLearned style preferences: {context['style_preferences']}")
            
            if context.get('successful_elements'):
                prompt_parts.append(f"\nMaintain successful elements: {context['successful_elements']}")
            
            # 添加新的参考图片
            if reference_images:
                prompt_parts.append("\n### NEW REFERENCE GUIDANCE ###")
                ref_instructions = self._build_reference_instructions(reference_images)
                prompt_parts.append(ref_instructions)
            
            # 保持原始提示词的核心部分
            prompt_parts.append(f"\n### ORIGINAL FOUNDATION ###")
            prompt_parts.append(original_prompt)
            
            # 强调改进方向
            prompt_parts.append("\n### IMPROVEMENT FOCUS ###")
            prompt_parts.append("Focus on addressing user feedback while maintaining the quality and style of successful elements.")
            
            return "\n".join(prompt_parts)
            
        except Exception as e:
            # 降级处理
            return f"{original_prompt}\n\nUser modifications: {user_modifications.get('prompt_modifications', 'General improvement requested')}"
    
    def _analyze_competitors(self, competitors: List[Dict]) -> str:
        """分析竞品信息"""
        analysis_parts = []
        valid_competitors = [comp for comp in competitors if comp.get('title') or comp.get('description')]
        
        if not valid_competitors:
            return "No competitor analysis available."
        
        # 构建竞品信息摘要
        for i, competitor in enumerate(valid_competitors[:3], 1):  # 最多分析3个竞品
            comp_line = f"Competitor {i}:"
            if competitor.get('title'):
                comp_line += f" '{competitor['title']}'"
            if competitor.get('description'):
                comp_line += f" - {competitor['description'][:100]}..."  # 限制长度
            analysis_parts.append(comp_line)
        
        # 添加分析策略
        analysis_parts.append("\nStrategy: Create imagery that differentiates this product while maintaining commercial appeal and incorporating successful market elements.")
        
        return "Learn from successful competitor approaches:\n" + "\n".join(analysis_parts)
    
    def _build_reference_instructions(self, reference_images: List[Dict]) -> str:
        """构建参考图片指导"""
        instructions = []
        
        for i, ref_img in enumerate(reference_images, 1):
            if ref_img.get('description'):
                instructions.append(f"Reference {i}: {ref_img['description']}")
            
            if ref_img.get('purpose'):
                purpose_map = {
                    'style': 'Use this image as style and aesthetic reference',
                    'composition': 'Follow the composition and layout of this image',
                    'lighting': 'Replicate the lighting mood and setup',
                    'color': 'Match the color palette and tone',
                    'scene': 'Use similar scene and environment setup'
                }
                purpose_text = purpose_map.get(ref_img['purpose'], 'Use as general reference')
                instructions.append(f"Purpose: {purpose_text}")
        
        if instructions:
            return "\n".join(instructions)
        else:
            return "Use reference images for general guidance on style and composition."
    
    def _extract_key_features(self, description: str) -> str:
        """从竞品描述中提取关键特性"""
        # 简单的关键词提取逻辑
        keywords = []
        common_features = [
            'durable', 'waterproof', 'easy to clean', 'microwave safe',
            'dishwasher safe', 'BPA free', 'non-toxic', 'eco-friendly',
            'portable', 'lightweight', 'compact', 'versatile'
        ]
        
        description_lower = description.lower()
        for feature in common_features:
            if feature in description_lower:
                keywords.append(feature)
        
        return ', '.join(keywords) if keywords else 'general quality features'
    
    def validate_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        验证提示词质量
        
        Returns:
            验证结果和建议
        """
        result = {
            'is_valid': True,
            'warnings': [],
            'suggestions': [],
            'score': 0
        }
        
        # 长度检查
        if len(prompt) < 50:
            result['warnings'].append('提示词过短，可能缺少重要细节')
            result['score'] -= 20
        elif len(prompt) > 8000:
            result['warnings'].append('提示词过长，可能影响生成效果')
            result['score'] -= 10
        
        # 关键元素检查
        essential_elements = ['product', 'style', 'quality', 'lighting']
        for element in essential_elements:
            if element.lower() in prompt.lower():
                result['score'] += 15
        
        # 技术规格检查
        if any(term in prompt.lower() for term in ['8k', 'resolution', 'professional', 'photorealistic']):
            result['score'] += 10
        
        # 负面提示词检查
        if 'avoid' in prompt.lower() or 'negative' in prompt.lower():
            result['score'] += 5
        
        # 最终评分
        result['score'] = max(0, min(100, result['score']))
        
        if result['score'] < 60:
            result['is_valid'] = False
            result['suggestions'].append('建议增加更多产品细节和技术要求')
        
        return result
    
    def _get_rework_improvement_suggestions(self, image_type: str) -> str:
        """
        根据图片类型获取重新生成的改进建议
        
        Args:
            image_type: 图片类型
            
        Returns:
            改进建议文本
        """
        suggestions = {
            'main': """
- Lighting: Ensure even, professional lighting without harsh shadows
- Background: Perfect pure white background (RGB 255,255,255) with no color cast
- Product positioning: Optimal centering and size (85% of frame)
- Focus: Tack-sharp focus on all product details
- Color accuracy: Precise color reproduction matching the actual product
- Shadows: Subtle, natural shadows that enhance dimensionality
""",
            'lifestyle': """
- Scene authenticity: More natural, lived-in environment
- Emotional connection: Stronger aspirational appeal
- Product integration: More seamless product placement in the scene
- Lighting: Warmer, more inviting natural lighting
- Composition: Better balance between product and lifestyle elements
- Storytelling: Clearer narrative about product use and benefits
""",
            'detail': """
- Macro sharpness: Ultra-sharp focus on key details and textures
- Material representation: More accurate texture and finish rendering
- Feature highlighting: Better emphasis on important product features
- Lighting angle: Optimal lighting to show material quality
- Depth of field: Appropriate focus to isolate important details
- Color accuracy: Precise representation of materials and finishes
""",
            'infographic': """
- Information clarity: Clearer, more readable text and graphics
- Visual hierarchy: Better organization of information flow
- Color contrast: Improved readability and visual impact
- Layout balance: More professional and organized composition
- Feature highlighting: Better emphasis on key selling points
- Brand consistency: Stronger alignment with brand visual identity
""",
            'size': """
- Clear size reference objects,if available
- Measurement accuracy: More precise dimensional representation
-Mark the product dimensions with solid or dotted lines
- Multiple angles: Additional views to show size comprehensively
- Clarity: Better lighting and focus for size understanding
- Context: More relatable size reference objects
- Professional presentation: Cleaner, more organized layout
""",
            'angle': """
- View diversity: More comprehensive angle coverage
- Consistency: Better lighting and style consistency across views
- Product orientation: Optimal angles to show key features
- Layout organization: Cleaner arrangement of multiple views
- Detail visibility: Better angles to show important features
- Professional composition: More polished multi-angle presentation
""",
            'packaging': """
- Unboxing appeal: More attractive packaging presentation
- Quality perception: Better representation of packaging quality
- Information visibility: Clearer view of package information
- Lighting: More appealing lighting to enhance package appeal
- Context: Better setting to show packaging in use
- Professional styling: More polished packaging photography
""",
            'comparison': """
- Clarity of differences: More obvious competitive advantages
- Fair representation: Balanced but favorable comparison
- Visual impact: Stronger visual communication of benefits
- Layout improvement: Better organization of comparison elements
- Highlight advantages: Clearer emphasis on product superiority
- Professional presentation: More polished comparison layout
"""
        }
        
        return suggestions.get(image_type, suggestions['main'])
