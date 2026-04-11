import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
logger = logging.getLogger(__name__)

class PromptBuilderService:
    """
    Amazon Listing图片生成提示词构建器 - V3.0 创意赋能与兼容并蓄版

    核心哲学:
    1.  **产品是事实 (Product is Fact):** 100%忠于输入的产品外观。
    2.  **呈现是艺术 (Presentation is Art):** 用户的创意指令拥有最高优先级。
    """
    
    def __init__(self):
        """
        V3.0 优化:
        - 'role'全面升级，更具专业性和启发性。
        - 'goal'取代'rule'和'specs'，用目标导向的语言描述最终画面和创意方向。
        - 关键图片类型的'goal'中内置了对复杂用户指令（如拼贴图、尺码表）的“许可”和“引导”，使其能智能响应。
        """
        self.image_type_prompts = {
            'main': {
                'role': 'Elite Amazon Main Image Photographer & Retoucher',
                'goal': 'Create a flawless, studio-quality hero image with the product as the sole focus, filling ~85% of the frame with perfect, flattering lighting. **Background:** Default to pure white (RGB 255,255,255) for most products, but if the user\'s prompt explicitly requests a different background (e.g., lifestyle scene, gradient, textured surface) or if the product category benefits from it (e.g., jewelry on black, apparel on model), intelligently adapt the background while maintaining professional Amazon standards. This is the customer\'s first impression—make it perfect.'
            },
            'lifestyle': {
                'role': 'Evocative Lifestyle & Brand Storyteller',
                'goal': 'Create a compelling visual narrative showing the product in a realistic, aspirational context. **If the user\'s prompt describes multiple scenes, create a clean collage or multi-panel layout to showcase them.** Focus on the emotion and tangible benefit of using the product.'
            },
            'detail': {
                'role': 'Forensic Macro Photographer for High-End Products',
                'goal': 'Capture an extreme close-up that highlights the product\'s superior quality, craftsmanship, and material texture. **If reference images are provided, they are your PRIMARY GUIDE for composition, angle, framing, and focus area.** Study them carefully to understand exactly which detail to showcase and from what perspective. Make the details tangible, proving the product\'s value beyond words.'
            },
            'size': {
                'role': 'Technical Illustrator & Product Scale Expert',
                'goal': 'Create a visually intuitive guide to the product\'s dimensions. **For simple objects, use clean dimension lines (without text). For apparel or complex items where the user prompt provides size chart data, create a professional, minimalist size chart.** Clarity and preventing size-related returns is the mission.'
            },
            'angle': {
                'role': '360° Product Visualization Specialist',
                'goal': 'Generate a set of images showing the product from multiple key angles (e.g., front, back, side, 45-degree, top-down) with consistent studio lighting to provide a complete and comprehensive understanding of its form.'
            },
            'infographic': {
                'role': 'Visual Information & Marketing Designer',
                'goal': 'Create a visually engaging infographic that integrates the product image with minimalist icons and graphics to highlight key features. **If the user prompt provides text for callouts, incorporate it cleanly.** The layout must be professional and enhance understanding, not clutter.'
            },
            'packaging': {
                'role': 'Premium Unboxing & Product Presentation Photographer',
                'goal': 'Showcase the product with its packaging in an attractive, gift-worthy presentation. Convey a premium unboxing experience and the full value of the purchase from the moment it arrives.'
            },
            'comparison': {
                'role': 'Strategic Marketing & Competitive Analyst Designer',
                'goal': 'Create a clear, fair, but favorable side-by-side comparison as directed by the user. Visually emphasize our product\'s key advantages to make the customer\'s choice obvious.'
            },
            'instruction': {
                'role': 'User Experience & Instructional Designer',
                'goal': 'Create a simple, step-by-step visual guide showing how to use the product. Each step, as described by the user, should be clear, intuitive, and easy to follow, eliminating any potential customer confusion.'
            }
        }
        
        self.market_styles = {
            'US': 'Bright, optimistic, family-centric, diverse representation, modern and spacious settings.',
            'UK': 'Understated elegance, classic, sophisticated, authentic and cozy, quality craftsmanship.',
            'DE': 'Functionality, precision, high-quality engineering, clean, minimalist, Bauhaus influence.',
            'JP': 'Harmony, simplicity, detail-oriented, natural materials, serene and minimalist (wabi-sabi).',
            'IN': 'Vibrant, colorful, family and community-focused, celebratory, value and versatility.'
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
        allow_text_in_image: bool = False  # 参数保留，但逻辑由内部智能判断
    ) -> str:
        """构建赋能用户创意的Amazon Listing图片生成提示词"""
        
        try:
            config = self.image_type_prompts.get(image_type, self.image_type_prompts['main'])
            market = product_form.get('targetMarket', 'US')
            product_name = product_form.get('title', 'Product')
            
            # 内部智能判断是否应允许文本
            # 如果用户请求的是可能需要文本的类型，并且主提示词中包含了可能的文本数据（如尺码、列表等），则智能地允许文本
            should_allow_text = allow_text_in_image or \
                (image_type in ['size', 'infographic', 'comparison', 'instruction'] and \
                 re.search(r'[:：]|cm|inch|mm|[SsMmLlXx]{1,3}L', main_prompt))

            prompt = f"""
╔════════════════════════════════════════════════════════════════════════════╗
║ **CREATIVE BRIEF: Amazon Listing Image Generation**
║
║ **Mission Command:** You are an AI creative suite reporting directly to a Senior Amazon Operations Expert. 
║ Your ultimate objective for this task is to generate an image that MAXIMIZES customer engagement and conversion.
║
║ **Product:** {product_name}
║ **Image Type:** {image_type.upper()}
║ **Target Market:** {market}
╚════════════════════════════════════════════════════════════════════════════╝

**Your Specific Role for this Task:** As a `{config['role']}`, your mission is to achieve the following creative goal:
> **Creative Goal:** {config['goal']}
---
**CORE PHILOSOPHY: "The Product is Fact, The Presentation is Art."**
---

**1. THE PRODUCT (The Fact - Non-Negotiable Foundation)**
Your absolute priority is to replicate the product shown in the **input images** with 100% fidelity. This is the ground truth.

**PRODUCT ANALYSIS (Analyze before generating):**
- **Single Item:** If input shows one product → Replicate that one product exactly
- **Multi-Pack (Same Color/Design):** If input shows multiple identical items (e.g., "2-pack," "3-pack") → Show the SAME quantity with IDENTICAL appearance for each item
- **Variety Pack (Different Variants):** If input shows multiple products with different colors/patterns → Replicate ALL variants with their EXACT individual appearances
- **Combo/Bundle:** If input shows different products together (e.g., "set of 3 different items") → Show ALL products with their EXACT individual appearances

**REPLICATION RULES:**
- **REPLICATE EXACTLY:** All colors, textures, materials, logos, onboard text, shapes, proportions, and specific details
- **QUANTITY MATTERS:** If input shows 3 items, generate 3 items; if 5, generate 5
- **VARIETY MATTERS:** If input shows red + blue + green variants, show red + blue + green (not red + red + red)
- **DO NOT ALTER:** Do not "improve," modernize, or change any aspect of the product's design. What you see in the input is what you must create

**2. THE PRESENTATION (The Art - User's Creative Direction is KING)**
This is where you apply your creative expertise, guided primarily by the **user's prompts and reference images**.
- **USER'S MAIN PROMPT:** "{main_prompt}"
  - This is your **primary creative instruction**. Interpret it generously to shape the entire presentation—scene, mood, composition, and lighting. If the user asks for a collage, **your task is to create that collage**. If the user provides size chart data, **your task is to create that size chart**.
- **USER'S REFERENCE IMAGES (If provided):**
  - These are powerful visual commands. Analyze them for style, composition, color grading, lighting, and mood, as specified by the user's notes, and apply that aesthetic to **our product**.
- **YOUR CREATIVE FREEDOM:** Within the user's direction, you choose the best camera angles, and compositions to make the product look incredible. **Do not just copy the angle from the input images; find a superior, more dynamic one.**

---
**CONTEXTUAL MODIFIERS (Apply these to the Presentation)**
---

**Market Adaptation:**
The overall aesthetic should resonate with the **{market} market**: `{self.market_styles.get(market, '')}`. Apply this to the choice of environment, models, and color palette.
"""
            ref_images = type_specific_references or reference_images
            if ref_images and len(ref_images) > 0:
                prompt += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  **CRITICAL: REFERENCE IMAGES PROVIDED ({len(ref_images)} total)** ⚠️
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**THESE ARE YOUR PRIMARY CREATIVE INSTRUCTIONS!**
"""
                for idx, ref_img in enumerate(ref_images, 1):
                    ref_desc = ref_img.get('description', 'No specific instruction')
                    ref_purpose = ref_img.get('purpose', 'general')
                    prompt += f"""
📸 **Reference Image #{idx}:**
   ▸ User's Instruction: "{ref_desc}"
   ▸ Focus Area: {self._get_reference_purpose_description(ref_purpose)}
   ▸ **PRIORITY: HIGH** - Study this image carefully!
"""
                
                # 针对细节图类型特别强调
                if image_type == 'detail':
                    prompt += """
**🔍 SPECIAL INSTRUCTIONS FOR DETAIL IMAGES:**
You MUST carefully study the reference images to understand:
1. **EXACT ANGLE & PERSPECTIVE:** Match the camera angle, distance, and viewpoint
2. **FOCUS AREA:** Identify which specific part/detail is being highlighted
3. **FRAMING & COMPOSITION:** How the detail fills the frame
4. **LIGHTING DIRECTION:** Where the light comes from to reveal texture
5. **DEPTH OF FIELD:** How much blur vs sharpness in background

**YOUR TASK:** Recreate the SAME type of detail shot, but showing OUR product (from input images) instead of the product in the reference.
"""
                else:
                    prompt += """
**HOW TO USE REFERENCE IMAGES:**
1. **ANALYZE:** Study composition, lighting setup, color grading, mood, and styling
2. **ADAPT:** Apply their visual language and presentation style to OUR product
3. **DO NOT COPY:** The products shown in references - only their artistic approach
"""
                
                prompt += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            if product_form.get('sellingPoints'):
                prompt += f"""
**Feature Emphasis:**
- Visually hint at these key selling points through the scene and composition: `{product_form['sellingPoints']}`.
"""
            if not should_allow_text:
                prompt += """
**Text in Image Generation (Default Behavior):**
- **Strictly Prohibited:** Do not add any new text (captions, dimensions, etc.) to the image.
- **Exception:** Only preserve text that is part of the product's original design in the input images.
"""
            else:
                 prompt += """
**Text in Image Generation (User Override Active):**
- **Permitted:** The user's prompt appears to request text (e.g., a size chart or infographic). You are authorized to generate clean, professional, and accurate text as required to fulfill the request.
"""
            prompt += f"""---
**FINAL EXECUTION SPECS**
---
- **Style:** Photorealistic, professional commercial quality, high-end digital photography.
- **Quality:** 8K, UHD, tack-sharp focus.
- **Resolution & Ratio:** {size} ({ratio}).
- **Avoid:** Blurry, low-resolution, grainy, cartoonish, unrealistic lighting or shadows. Most importantly, avoid any deviation from the product's factual appearance in the input images.
- **Final Check:** Does the image fulfill the Creative Goal, perfectly execute the user's prompt, and maintain 100% product accuracy?
"""
            logger.info(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            logger.info(f"📋 生成图片提示词 - 图片类型: {image_type}")
            logger.info(f"📸 参考图数量: {len(ref_images) if ref_images else 0}")
            logger.info(f"📦 type_specific_references: {len(type_specific_references) if type_specific_references else 0}")
            logger.info(f"📦 reference_images: {len(reference_images) if reference_images else 0}")
            if ref_images:
                for idx, ref in enumerate(ref_images, 1):
                    logger.info(f"  🖼️  参考图#{idx}: description='{ref.get('description', 'N/A')}', purpose='{ref.get('purpose', 'N/A')}'")
            else:
                logger.warning(f"⚠️  警告: {image_type}类型没有收到任何参考图！")
            logger.info(f"📝 最终提示词长度: {len(prompt)} 字符")
            logger.info(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            return prompt.strip()
            
        except Exception as e:
            print(f"Prompt build error: {e}")
            return self._build_fallback_prompt(product_form, image_type, main_prompt, allow_text_in_image)

    def _build_fallback_prompt(self, product_form, image_type, main_prompt, allow_text_in_image):
        """优化的后备提示词"""
        product_name = product_form.get('title', 'Product')
        text_rule = "Do not add any text." if not allow_text_in_image else "Text generation is permitted as requested."
        return f"Create an Amazon {image_type} image for a product named '{product_name}'. User's main creative direction is: '{main_prompt}'. IMPORTANT RULE: The product in the image must look EXACTLY like the provided input images in every detail. The presentation (scene, style, angle) should creatively follow the user's direction. {text_rule} The final image must be professional, photorealistic, and high-resolution."
    
    def build_rework_prompt(
        self,
        original_prompt: str,
        user_modifications: Dict[str, Any],
        context: Dict[str, Any],
        reference_images: List[Dict] = None,
        original_image_info: Dict[str, Any] = None,
        previous_image_url: str = None
    ) -> str:
        """
        V3.1 优化的重新生成提示词:
        - 明确区分产品原图、参考图、上一次生成的图片
        - 完整传递用户的参考图提示词
        - 引入"Reflection"步骤，引导AI思考如何具体改进
        """
        user_feedback = user_modifications.get('prompt_modifications', 'Improve the overall quality and composition.')
        image_type = original_image_info.get('type', 'main') if original_image_info else 'main'
        product_name = context.get('product_form', {}).get('title', 'product')
        
        rework_prompt = f"""
╔════════════════════════════════════════════════════════════════════════════╗
║ **IMAGE REWORK REQUEST (ITERATION 2.0)**
║ Product: {product_name} | Type: {image_type.upper()}
╚════════════════════════════════════════════════════════════════════════════╝

**CRITICAL: IMAGE CLASSIFICATION & USAGE**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You will receive multiple images. Here's how to use each type:

**1. PRODUCT ORIGINAL IMAGES (First batch - Product Appearance Authority)**
   - Purpose: These show the ACTUAL product appearance
   - Usage: 100% REPLICATE the product's colors, textures, materials, logos, text, shape, details
   - Rule: This is your absolute reference for WHAT the product looks like
   - DO NOT ALTER: Any visual aspect of the product shown in these images

**2. REFERENCE IMAGES (If provided - Style & Composition Inspiration)**
   - Purpose: User-provided examples of desired presentation style
   - Usage: Study their composition, lighting, color grading, mood, layout
   - Rule: APPLY their artistic style to OUR product (from original images)
   - DO NOT: Copy the products shown in these reference images"""
        
        # 添加参考图的详细说明
        if reference_images and len(reference_images) > 0:
            rework_prompt += f"""
   
   **USER'S REFERENCE IMAGES GUIDANCE ({len(reference_images)} provided):**"""
            for idx, ref_img in enumerate(reference_images, 1):
                ref_desc = ref_img.get('description', 'No description')
                ref_purpose = ref_img.get('purpose', 'general')
                rework_prompt += f"""
   - Reference #{idx}: {ref_desc}
     Focus: {self._get_reference_purpose_description(ref_purpose)}"""
        
        # 添加上一次生成图片的说明
        if previous_image_url:
            rework_prompt += """

**3. PREVIOUS GENERATED IMAGE (Optional context)**
   - Purpose: The image you generated in the last iteration
   - Usage: Understand what was tried before, identify what needs improvement
   - Rule: This is for CONTEXT ONLY - not a strict reference
   - DO NOT: Simply copy this image; instead, IMPROVE based on user feedback"""
        
        rework_prompt += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**USER FEEDBACK FOR THIS ITERATION:**
> **"{user_feedback}"**

**YOUR TASK: Intelligent Iteration & Refinement**

1. **Maintain Core Requirements:**
   - Product appearance: 100% identical to PRODUCT ORIGINAL IMAGES
   - Market adaptation: Continue reflecting the target market aesthetic
   - Image type: Fulfill the specific goals of a `{image_type}` image

2. **Apply User Feedback:**
   - Analyze: What specific improvement is requested?
   - Plan: How to adjust presentation (angle, composition, lighting, background, mood)?
   - Execute: Implement changes while preserving product fidelity

3. **Leverage Reference Images (if provided):**
   - Study their visual language
   - Apply their presentation style to OUR product
   - Create a harmonious blend of user's vision and product reality

**REFLECTION BEFORE GENERATION:**
- What was the user dissatisfied with in the previous image?
- How can I adjust the presentation to address this specifically?
- Am I maintaining 100% product fidelity while making the requested changes?

**Execute the rework now with precision and creativity.**
"""
        logger.info(f"重新生图提示词 (含{len(reference_images) if reference_images else 0}张参考图): {rework_prompt[:200]}...")
        return rework_prompt.strip()

    
    def _get_reference_purpose_description(self, purpose: str) -> str:
        """获取参考图用途的详细描述"""
        purposes = {
            'composition': 'Learn from composition and framing techniques',
            'lighting': 'Study lighting setup, direction, and quality',
            'style': 'Adopt overall aesthetic and visual style',
            'color': 'Reference color grading and palette',
            'mood': 'Capture emotional tone and atmosphere',
            'props': 'Understand prop selection and placement',
            'general': 'Overall presentation inspiration'
        }
        return purposes.get(purpose, 'General reference for overall presentation')
    
    def _get_improvement_focus(self, image_type: str) -> str:
        """获取图片类型的改进重点"""
        focuses = {
            'main': '• Better angle | Perfect white background | Optimal lighting | Sharp focus',
            'lifestyle': '• More natural scene | Better emotional appeal | Stronger storytelling',
            'detail': '• Sharper macro | Better texture reveal | Optimal detail angle',
            'size': '• Clearer dimensions | Better measurement lines | Obvious scale',
            'angle': '• More comprehensive views | Better angle diversity | Consistent quality',
            'infographic': '• Clearer info hierarchy | Better visual balance | Stronger impact',
            'packaging': '• More appealing | Better unboxing feel | Quality perception',
            'comparison': '• Clearer advantages | Better visual contrast | Professional layout',
            'instruction': '• Clearer steps | Better visual flow | Easier to understand'
        }
        return focuses.get(image_type, focuses['main'])

