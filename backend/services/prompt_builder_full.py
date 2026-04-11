import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime

class PromptBuilderService:
    """提示词构建服务，基于模板动态生成高质量提示词"""
    
    def __init__(self):
        self.image_type_prompts = {
            'main': {
                'system_prompt': 'Amazon Main Image Photographer | RULE: Product appearance 100% identical to input, choose optimal angle freely | Pure white background (RGB 255,255,255) | Product fills 85% frame | Sharp professional lighting',
                'requirements': [
                    'Product appearance = input images (100% match)',
                    'Choose best angle freely',
                    'Pure white RGB 255,255,255',
                    '85% frame fill',
                    'Professional lighting'
                ]
            },
            'infographic': {
                'system_prompt': 'Amazon Infographic Designer | RULE: Product appearance 100% identical to input, choose best angle | Add graphics/icons around product | Highlight key features visually',
                'requirements': [
                    'PRESERVE APPEARANCE: Product colors, materials, textures, details must be 100% identical',
                    'FLEXIBLE COMPOSITION: Choose optimal product angle and positioning for infographic',
                    'ZERO modifications to product appearance (colors, textures, features, logos)',
                    'Clean professional layout showcasing product effectively',
                    'Highlight key features with graphic elements (not product changes)',
                    'Input images define product appearance, you control the angle and layout',
                    'Minimal but effective text (if allowed)',
                    'Easy to understand at a glance',
                    'High contrast for readability'
                ]
            },
            'lifestyle': {
                'system_prompt': 'CRITICAL PRODUCT APPEARANCE FIDELITY: Preserve the EXACT APPEARANCE of the product (colors, materials, textures, details) from input images - 100% identical visual features required. You are a lifestyle photographer for Amazon products creating emotional, aspirational scenes. You may choose creative angles, positioning, and product placement in the scene, but the product appearance must remain unchanged. Focus on creating compelling environment and context.',
                'requirements': [
                    'PRESERVE APPEARANCE: Product colors, materials, textures, details must be 100% identical',
                    'CREATIVE FREEDOM: Choose best camera angles, product positioning, and scene composition',
                    'ZERO modifications to product appearance (colors, textures, features, logos)',
                    'Natural real-life setting showcasing product effectively',
                    'Emotional connection through environment, angle, and composition',
                    'Product naturally integrated with flexible positioning',
                    'Input images define product appearance, you control the scene and angle',
                    'Aspirational but relatable environment',
                    'Warm inviting lighting enhancing product appeal',
                    'Space for text overlay if needed'
                ]
            },
            'size': {
                'system_prompt': 'CRITICAL PRODUCT APPEARANCE FIDELITY: Preserve the EXACT APPEARANCE of the product (colors, materials, textures, details) from input images - 100% identical visual features required. You are a technical photographer and dimensional analyst. You may choose the best angle to clearly show product dimensions, but the product appearance must remain unchanged. Your task is to accurately measure and mark dimensions with precision indicators.',
                'requirements': [
                    'PRESERVE APPEARANCE: Product colors, materials, textures, details must be 100% identical',
                    'FLEXIBLE ANGLES: Choose the best angle to show dimensions clearly',
                    'ZERO modifications to product appearance (colors, textures, features, logos)',
                    'INTELLIGENT DIMENSION ANALYSIS: Understand product shape and measure correctly',
                    'For irregular shapes: measure at the widest/longest/tallest points',
                    'For complex products: show multiple key dimensions (length, width, height, diameter)',
                    'Use solid lines for primary dimensions, dashed lines for secondary measurements',
                    'Add measurement arrows or brackets at line endpoints',
                    'Place dimension lines outside the product boundary when possible',
                    'Include clear size reference objects (common objects) if helpful',
                    'Use provided dimension data from product form to mark accurate measurements',
                    'Reference uploaded size reference images for measurement style and format',
                    'For hollow/curved products: show both inner and outer dimensions if relevant',
                    'Maintain clean uncluttered composition while showing all key measurements',
                    'Good lighting for clarity on product and measurement indicators',
                    'Professional technical drawing style for dimension lines and markers'
                ]
            },
            'detail': {
                'system_prompt': 'CRITICAL PRODUCT APPEARANCE FIDELITY: Preserve the EXACT APPEARANCE of product details (colors, materials, textures, finishes, micro-features) from input images - 100% identical visual features required. You are a macro photographer creating close-up detail shots. You have creative freedom to choose the best angle, framing, and focus point, but the product appearance must remain unchanged. Showcase product quality through optimal angles and lighting.',
                'requirements': [
                    'PRESERVE APPEARANCE: Product details, colors, textures, finishes must be 100% identical',
                    'CREATIVE MACRO: Choose optimal close-up angle, framing, and focus point',
                    'ZERO modifications to product appearance (colors, textures, features, materials)',
                    'Sharp macro detail focus showcasing product quality',
                    'Highlight key features with angle and lighting choices',
                    'Input images define product appearance, you control the macro perspective',
                    'Preserve exact materials and textures as shown in input',
                    'Show material quality through excellent lighting',
                    'Excellent lighting for texture revelation (not modification)',
                    'Clean background emphasizing product details'
                ]
            },
            'angle': {
                'system_prompt': 'CRITICAL PRODUCT APPEARANCE FIDELITY: Preserve the EXACT APPEARANCE of the product (colors, materials, textures, details) from input images - 100% identical visual features required. You are a product photographer creating multi-angle views. This is your specialty - show the product from multiple creative angles and perspectives. The product appearance must remain unchanged, but you have full freedom to choose the most informative and appealing angles.',
                'requirements': [
                    'PRESERVE APPEARANCE: Product colors, materials, textures, details must be 100% identical',
                    'ANGLE FREEDOM: Full creative freedom to choose the best multiple camera angles',
                    'ZERO modifications to product appearance (colors, textures, features, logos)',
                    'Multiple distinct camera angles showcasing product comprehensively',
                    'Consistent lighting across views highlighting product features',
                    'Input images define product appearance, you choose all angles freely',
                    'Professional composition maximizing product understanding',
                    'Clear view of all important sides and features',
                    'Organized layout showing product from most informative angles'
                ]
            },
            'instruction': {
                'system_prompt': 'CRITICAL PRODUCT APPEARANCE FIDELITY: Preserve the EXACT APPEARANCE of the product (colors, materials, textures, details) from input images - 100% identical visual features required. You are an instructional photographer creating step-by-step visual guides. You may choose the best angles and positioning for each instruction step, but the product appearance must remain unchanged. Add hands, arrows, indicators, or step sequences as needed.',
                'requirements': [
                    'PRESERVE APPEARANCE: Product colors, materials, textures, details must be 100% identical',
                    'FLEXIBLE INSTRUCTION: Choose best angles and positioning for each step',
                    'ZERO modifications to product appearance (colors, textures, features, logos)',
                    'Clear step-by-step progression with effective angles',
                    'Easy to follow visually with optimal camera positions',
                    'Input images define product appearance, you control instruction angles',
                    'Hands demonstrating with appropriate product positioning if needed',
                    'Good lighting for clarity in each instruction step',
                    'Logical sequence flow with best angles for understanding'
                ]
            },
            'comparison': {
                'system_prompt': 'CRITICAL PRODUCT APPEARANCE FIDELITY: Preserve the EXACT APPEARANCE of the main product (colors, materials, textures, details) from input images - 100% identical visual features required. You are a comparison photographer creating side-by-side comparisons. You may choose the best angle and positioning for effective comparison, but the main product appearance must remain unchanged. Add comparison elements, alternative products, or graphic indicators as needed.',
                'requirements': [
                    'PRESERVE APPEARANCE: Main product colors, materials, textures, details must be 100% identical',
                    'FLEXIBLE COMPARISON: Choose optimal angle and positioning for effective comparison',
                    'ZERO modifications to main product appearance (colors, textures, features, logos)',
                    'Clear side-by-side layout with effective angles',
                    'Highlight key differences through layout, angle, and presentation',
                    'Input images define main product appearance, you control comparison angle',
                    'Fair but favorable comparison with professional positioning',
                    'Professional presentation maximizing comparison clarity',
                    'Easy to understand benefits through optimal angles and layout'
                ]
            },
            'packaging': {
                'system_prompt': 'CRITICAL PRODUCT APPEARANCE FIDELITY: Preserve the EXACT APPEARANCE of the product and packaging (colors, materials, textures, details) from input images - 100% identical visual features required. You are a packaging photographer creating appealing packaging images. You may choose the best angle, arrangement, and presentation style, but the product and packaging appearance must remain unchanged. Create attractive unboxing or display compositions.',
                'requirements': [
                    'PRESERVE APPEARANCE: Product and packaging colors, materials, textures, details must be 100% identical',
                    'CREATIVE PRESENTATION: Choose optimal angle, arrangement, and display style',
                    'ZERO modifications to product or packaging appearance (colors, textures, features, logos)',
                    'Attractive presentation with flexible positioning',
                    'Show contents relationship with creative angles',
                    'Input images define appearance, you control presentation angle and style',
                    'Gift-worthy appearance through lighting and composition choices',
                    'Professional unboxing feel with optimal camera angles',
                    'Brand quality impression through excellent presentation'
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
                        'system_prompt': 'CRITICAL PRODUCT APPEARANCE FIDELITY: Preserve the EXACT APPEARANCE of the product from input images. You are a technical photographer creating size demonstration images using visual measurement indicators WITHOUT text. Choose the best angle to show dimensions clearly. Use solid/dashed lines, arrows, brackets, and measurement markers. Include familiar reference objects for scale. NO text or numbers, but dimension lines and visual markers are REQUIRED.',
                        'requirements': [
                            'PRESERVE APPEARANCE: Product colors, materials, textures, details must be 100% identical',
                            'FLEXIBLE ANGLES: Choose the optimal angle to show product dimensions',
                            'Dimension lines: Use solid lines for primary dimensions, dashed for secondary',
                            'Measurement arrows/brackets at line endpoints (no text labels)',
                            'Visual scale comparison with familiar reference objects',
                            'Multiple dimension indicators showing length, width, height',
                            'For irregular shapes: measure at widest/longest/tallest points',
                            'Place dimension lines outside product boundary when possible',
                            'Clean professional technical drawing style',
                            'Reference uploaded size images for measurement line style',
                            'Use provided dimension data to position lines accurately',
                            'Professional lighting for size clarity',
                            'NO text or numbers - only visual dimension indicators'
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
            
            # 0. 输入图片分类声明（最高优先级）
            prompt_parts.append("=" * 80)
            prompt_parts.append("INPUT IMAGES CLASSIFICATION AND USAGE")
            prompt_parts.append("=" * 80)
            prompt_parts.append("You will receive MULTIPLE input images with DIFFERENT purposes:")
            prompt_parts.append("")
            prompt_parts.append("1. PRODUCT IMAGES (Primary - First images):")
            prompt_parts.append("   - These show the ACTUAL PRODUCT you must preserve")
            prompt_parts.append("   - CRITICAL: Preserve EXACT APPEARANCE (colors, materials, textures, details) 100% identical")
            prompt_parts.append("   - These are the ABSOLUTE AUTHORITY for product appearance")
            prompt_parts.append("   - You may choose different angles, but appearance MUST match these images exactly")
            prompt_parts.append("")
            prompt_parts.append("2. REFERENCE IMAGES (Secondary - Later images, if provided):")
            prompt_parts.append("   - These show STYLE, COMPOSITION, LIGHTING, or SCENE examples")
            prompt_parts.append("   - Use these for INSPIRATION ONLY - do NOT copy the products shown in them")
            prompt_parts.append("   - Apply their style/composition/lighting to YOUR product (from product images)")
            prompt_parts.append("   - NEVER confuse reference image products with YOUR actual product")
            prompt_parts.append("")
            prompt_parts.append("CRITICAL RULE: Product appearance comes from PRODUCT IMAGES, style/composition from REFERENCE IMAGES.")
            prompt_parts.append("=" * 80)
            
            # 0.1 文字禁止前置声明（如果需要）
            if not allow_text_in_image:
                prompt_parts.append("NO ADDITIONAL TEXT MANDATE")
                prompt_parts.append("CRITICAL: Do not add any new text, but preserve all text originally on the product/packaging.")
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
            
            # 2. 产品保真度要求（提升到最高优先级）
            prompt_parts.append("\n### PRODUCT FIDELITY REQUIREMENTS - HIGHEST PRIORITY ###")
            product_fidelity_instructions = self._build_product_fidelity_instructions(main_prompt)
            prompt_parts.append(product_fidelity_instructions)
            
            # 3. 产品定义
            prompt_parts.append("\n### PRODUCT DEFINITION ###")
            prompt_parts.append(f"Product: {product_form.get('title', 'Product')}")
            prompt_parts.append("REMINDER: The above product must appear EXACTLY as shown in the input images.")
            
            if product_form.get('sellingPoints'):
                prompt_parts.append(f"Key selling points: {product_form['sellingPoints']}")
                prompt_parts.append("NOTE: Highlight these selling points through composition and environment, NOT by changing the product.")
            
            if product_form.get('dimensions'):
                dims = product_form['dimensions']
                if dims.get('length') and dims.get('width') and dims.get('height'):
                    prompt_parts.append(f"Dimensions: {dims['length']}×{dims['width']}×{dims['height']} {dims.get('unit', 'cm')}")
                    prompt_parts.append("IMPORTANT: These dimensions refer to the product as shown in input images - do not modify the product to match these dimensions.")
                    
                    # 如果是尺寸图类型，添加详细的尺寸标注指导
                    if image_type == 'size':
                        prompt_parts.append("\n### SIZE MARKING INSTRUCTIONS - CRITICAL FOR SIZE IMAGES ###")
                        prompt_parts.append(f"ACCURATE DIMENSION MARKING REQUIRED:")
                        prompt_parts.append(f"- Length: {dims['length']} {dims.get('unit', 'cm')} - Mark this dimension with a horizontal line")
                        prompt_parts.append(f"- Width: {dims['width']} {dims.get('unit', 'cm')} - Mark this dimension with a perpendicular line")
                        prompt_parts.append(f"- Height: {dims['height']} {dims.get('unit', 'cm')} - Mark this dimension with a vertical line")
                        prompt_parts.append("\nMEASUREMENT LINE GUIDELINES:")
                        prompt_parts.append("1. Analyze the product shape carefully - identify widest/longest/tallest points")
                        prompt_parts.append("2. For irregular shapes: measure across the maximum extent in each direction")
                        prompt_parts.append("3. Use solid lines (━━━) for primary dimensions, dashed lines (- - -) for secondary")
                        prompt_parts.append("4. Add arrows (←→ ↕) or brackets at line endpoints to indicate measurement direction")
                        prompt_parts.append("5. Place dimension lines OUTSIDE the product boundary when possible")
                        prompt_parts.append("6. For complex shapes: show multiple key dimensions")
                        prompt_parts.append("7. Reference any uploaded size reference images for measurement line style")
                        prompt_parts.append("8. Ensure dimension lines correspond to the actual provided measurements")
            
            # 3.1 尺寸图的额外指导（即使没有提供尺寸数据）
            if image_type == 'size' and not (product_form.get('dimensions') and product_form['dimensions'].get('length')):
                prompt_parts.append("\n### SIZE DEMONSTRATION GUIDELINES ###")
                prompt_parts.append("No specific dimensions provided, but you must still create professional size indicators:")
                prompt_parts.append("- Analyze the product shape and identify key measurement points")
                prompt_parts.append("- Show length, width, and height with appropriate dimension lines")
                prompt_parts.append("- Use visual scale references (ruler, hand, common objects) to convey size")
                prompt_parts.append("- Apply professional technical drawing conventions")
                prompt_parts.append("- Reference any uploaded size reference images for style guidance")
            
            # 4. 市场与文化背景
            prompt_parts.append("\n### MARKET & CULTURAL CONTEXT ###")
            market_info = self.market_styles[target_market]
            prompt_parts.append(f"Style adaptation: {market_info['style_description']}")
            prompt_parts.append(f"Color preferences: {market_info['color_palette']}")
            prompt_parts.append(f"Setting preferences: {market_info['setting_preferences']}")
            prompt_parts.append("CONSTRAINT: Apply these preferences to ENVIRONMENT and COMPOSITION only, never to the product itself.")
            
            # 5. 竞品分析（如果提供）
            if competitors and len(competitors) > 0:
                prompt_parts.append("\n### COMPETITIVE ANALYSIS ###")
                competitor_insights = self._analyze_competitors(competitors)
                prompt_parts.append(competitor_insights)
                prompt_parts.append("LIMITATION: Use competitive insights for positioning and environment, never modify the actual product.")
            
            # 调试输出产品保真度模式
            fidelity_mode = "设计自由" if "ignore original" in product_fidelity_instructions.lower() else "产品保真"
            print(f"产品保真度模式: {fidelity_mode}模式")
            if fidelity_mode == "设计自由":
                print("   -> 用户明确要求修改产品设计")
            else:
                print("   -> 保持原产品所有细节和颜色不变")
            
            # 调试输出文字生成设置
            text_mode = "允许文字" if allow_text_in_image else "禁止文字"
            print(f"文字生成模式: {text_mode}")
            if not allow_text_in_image:
                print("   -> 强制禁止任何文字、字符、Logo等文本元素")
            
            # 6. 创意执行（限制范围）
            prompt_parts.append("\n### CREATIVE EXECUTION - ENVIRONMENT ONLY ###")
            prompt_parts.append("CRITICAL CONSTRAINT: User creative direction applies to environment, composition, lighting, angles, and positioning.")
            prompt_parts.append("PRODUCT PROTECTION: Product APPEARANCE must remain 100% identical to input images regardless of user instructions.")
            prompt_parts.append(f"User creative direction (for environment only): {main_prompt}")
            prompt_parts.append("INTERPRETATION RULE: Apply the above creative direction to:")
            prompt_parts.append("- Background and environment settings")
            prompt_parts.append("- Lighting mood and atmosphere")
            prompt_parts.append("- Camera angles and composition")
            prompt_parts.append("- Scene context and props")
            prompt_parts.append("- Overall visual style and mood")
            prompt_parts.append("STRICT PROHIBITION: Do NOT apply creative direction to:")
            prompt_parts.append("- Product colors, materials, or textures")
            prompt_parts.append("- Product shape, size, or proportions")
            prompt_parts.append("- Product features, details, or components")
            prompt_parts.append("- Product condition or appearance")
            prompt_parts.append("- Any aspect of the product itself")
            
            # 6.1 文本元素约束（当不允许图文时，禁止新增文字但保留产品原有文字）
            if not allow_text_in_image:
                prompt_parts.append("\n### CRITICAL: NO ADDITIONAL TEXT ALLOWED ###")
                prompt_parts.append(
                    "MANDATORY NO ADDITIONAL TEXT REQUIREMENT\n"
                    "This is a CRITICAL requirement that MUST be followed:\n"
                    "\n"
                    "PROHIBITED - DO NOT ADD:\n"
                    "- NO captions, subtitles, titles, or descriptive text\n"
                    "- NO infographic text, annotations, or explanatory labels\n"
                    "- NO measurements, dimensions, or size indicators (unless it's a size image type)\n"
                    "- NO price tags, promotional text, or marketing copy\n"
                    "- NO UI overlays, text bubbles, or callouts\n"
                    "- NO watermarks, copyright text, or brand overlays\n"
                    "- NO decorative text, artistic lettering, or stylized fonts\n"
                    "- NO instructions, warnings, or informational text\n"
                    "\n"
                    "EXCEPTION - MUST PRESERVE:\n"
                    "- KEEP all text that is ORIGINALLY on the product itself (logos, brand names, product labels)\n"
                    "- KEEP all text that is ORIGINALLY on the packaging (product names, warnings, ingredients)\n"
                    "- KEEP all text that is part of the PRODUCT DESIGN shown in input images\n"
                    "- These are PRODUCT FEATURES that must be preserved exactly as they appear in input images\n"
                    "\n"
                    "RULE: If text exists in the input product images, it's a PRODUCT FEATURE - preserve it exactly.\n"
                    "RULE: If text does not exist in input images, DO NOT ADD IT.\n"
                    "\n"
                    "IMPORTANT: Express marketing information through visual composition, lighting, colors, and product positioning only.\n"
                    "Do not add any NEW text elements - only preserve text that's already part of the product."
                )

            # 7. 参考图片指导（优先使用类型特定的参考图）
            ref_images_to_use = type_specific_references if type_specific_references else reference_images
            if ref_images_to_use:
                prompt_parts.append("\n### REFERENCE IMAGES GUIDANCE ###")
                prompt_parts.append("IMPORTANT: The following reference images are for STYLE/COMPOSITION/LIGHTING inspiration ONLY.")
                prompt_parts.append("DO NOT copy the products shown in these reference images.")
                prompt_parts.append("Apply their style to YOUR product (from the first product images).")
                prompt_parts.append("")
                ref_instructions = self._build_reference_instructions(ref_images_to_use)
                prompt_parts.append(ref_instructions)
                prompt_parts.append("")
                prompt_parts.append("REMINDER: Use reference images for environment/style, but product appearance comes from product images.")
            
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
                # 扩展文字相关的负面提示词 - 只针对新增文字，不包括产品原有文字
                text_negative_prompts = [
                    "added text", "overlay text", "captions", "subtitles", "titles",
                    "UI overlay", "infographic text", "annotations", "explanatory labels",
                    "promotional text", "advertising text", "marketing copy",
                    "decorative text", "artistic lettering", "callout text",
                    "text bubble", "speech bubble", "annotation arrows",
                    "measurement text", "dimension labels", "size text",
                    "price tag", "price overlay", "discount badge",
                    "watermark", "copyright overlay", "brand overlay",
                    "instructions overlay", "warning overlay", "description overlay",
                    "text banner", "text header", "text footer",
                    "floating text", "suspended text", "3D text overlay"
                ]
                negative_prompts.extend(text_negative_prompts)
                
                # 添加额外的强调 - 明确区分
                prompt_parts.append("CRITICAL NEGATIVE PROMPTS - NO ADDITIONAL TEXT:")
                prompt_parts.append(f"AVOID ADDING: {', '.join(text_negative_prompts)}")
                prompt_parts.append("NOTE: Product's original text (logos, labels, packaging text) must be preserved.")
                prompt_parts.append(f"\nGeneral negative prompts: {', '.join(negative_prompts[:7])}")
            else:
                prompt_parts.append(f"Avoid: {', '.join(negative_prompts)}")
            
            # 9. 最终文字禁止强调（如果需要）
            if not allow_text_in_image:
                prompt_parts.append("\n" + "=" * 80)
                prompt_parts.append("FINAL REMINDER: NO ADDITIONAL TEXT - PRESERVE PRODUCT TEXT")
                prompt_parts.append("Before generating, double-check:")
                prompt_parts.append("1. Have I added ANY new text (captions, labels, annotations)? If YES, REMOVE IT.")
                prompt_parts.append("2. Have I preserved ALL text that was originally on the product/packaging? If NO, RESTORE IT.")
                prompt_parts.append("3. Is all visible text part of the original product shown in input images? It should be.")
                prompt_parts.append("\nThis is a MANDATORY requirement - no additional text, but preserve product's original text.")
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
Focus on the creative direction provided while maintaining product functionality and category.
WARNING: This mode allows product modifications - use only when explicitly requested."""
        
        else:
            return """PRODUCT FIDELITY GUIDELINES - TWO CRITICAL RULES:

═══════════════════════════════════════════════════════════════════════════
RULE 1: PRESERVE PRODUCT APPEARANCE (WHAT THE PRODUCT LOOKS LIKE)
═══════════════════════════════════════════════════════════════════════════
Input product images are the ABSOLUTE AUTHORITY for product appearance.
You MUST preserve these visual characteristics EXACTLY:

APPEARANCE PRESERVATION REQUIREMENTS (100% MANDATORY):

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

STRICT PROHIBITIONS FOR APPEARANCE:
- Do NOT change any colors whatsoever
- Do NOT add, remove, or modify any product features
- Do NOT "upgrade" or "modernize" the product design
- Do NOT apply artistic interpretation to product elements
- Do NOT "improve" or "enhance" the product appearance
- Do NOT change materials, textures, or finishes
- Do NOT alter proportions, dimensions, or shapes
- Do NOT modify logos, text, or branding on the product
- Do NOT change the product's condition (new/used/worn)
- Do NOT add or remove product components or accessories

═══════════════════════════════════════════════════════════════════════════
RULE 2: FREELY ADJUST ANGLES & COMPOSITION (HOW TO PRESENT THE PRODUCT)
═══════════════════════════════════════════════════════════════════════════
You have COMPLETE CREATIVE FREEDOM to adjust how the product is presented:

ENCOURAGED CREATIVE ADJUSTMENTS:
✓ Change camera angles (top view, side view, 45-degree angle, close-up, etc.)
✓ Rotate the product to show different sides or the best angle
✓ Reposition the product within the frame for better composition
✓ Adjust product placement and arrangement (centered, offset, diagonal, etc.)
✓ Choose different perspectives and viewpoints than the input images
✓ Tilt or orient the product differently for visual appeal
✓ Arrange multiple products in creative layouts (if combo product)
✓ Select the most photogenic and informative angle for the image type
✓ Apply rule of thirds, golden ratio, or other composition principles

IMPORTANT: DO NOT copy the exact angle/position from input images.
Instead, analyze the product and ACTIVELY CHOOSE the best angle for:
- Main image: Front-facing, hero angle that shows product clearly
- Lifestyle: Natural usage angle that tells a story
- Detail: Close-up angle that highlights specific features
- Size: Angle that clearly shows dimensions
- Variety: Different angles showing color/style variations

═══════════════════════════════════════════════════════════════════════════
SUMMARY: PRESERVE WHAT IT LOOKS LIKE, CHANGE HOW IT'S SHOWN
═══════════════════════════════════════════════════════════════════════════
✓ Keep: Colors, textures, materials, details, features (WHAT)
✓ Change: Angles, positions, viewpoints, composition (HOW)

Think of it like a professional product photographer:
- The product itself (WHAT) must look exactly like the reference
- But you (the photographer) decide the best angle (HOW) to shoot it"""
    
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
        
        instructions.append("REFERENCE IMAGE DETAILS:")
        instructions.append("")
        
        for i, ref_img in enumerate(reference_images, 1):
            instructions.append(f"Reference Image #{i}:")
            
            if ref_img.get('description'):
                instructions.append(f"  Description: {ref_img['description']}")
            
            if ref_img.get('purpose'):
                purpose_map = {
                    'style': 'Learn the STYLE and aesthetic from this image (lighting mood, color grading, overall feel)',
                    'composition': 'Learn the COMPOSITION and layout from this image (product placement, framing, balance)',
                    'lighting': 'Learn the LIGHTING setup from this image (light direction, shadows, highlights)',
                    'color': 'Learn the COLOR PALETTE from this image (background colors, environment tones)',
                    'texture': 'Learn the TEXTURE and material feel from this image (surface quality presentation)',
                    'scene': 'Learn the SCENE and environment from this image (setting, props, context)'
                }
                purpose_text = purpose_map.get(ref_img['purpose'], 'Use as general inspiration for style and composition')
                instructions.append(f"  Purpose: {purpose_text}")
            else:
                instructions.append(f"  Purpose: General style and composition inspiration")
            
            instructions.append(f"  CRITICAL: Do NOT copy the product shown in this reference image!")
            instructions.append(f"  APPLY: Only the style/composition/lighting to YOUR product from product images.")
            instructions.append("")
        
        if not reference_images:
            return "No specific reference images provided."
        
        return "\n".join(instructions)
    
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
