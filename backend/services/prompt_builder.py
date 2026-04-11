# --- START OF FILE prompt_builder.py (V5.1 Production-Ready Final & Complete) ---

import json
import re
from typing import Dict, List, Any, Optional

class PromptBuilderService:
    """
    Amazon Listing图片生成提示词构建器 - V5.1 生产级最终版

    核心哲学: 大道至简。为AI提供清晰的目标和拥有明确优先级的上下文，
              而不是用复杂的规则束缚其创造力。
    """
    
    def __init__(self):
        """
        V5.1 优化:
        - 'goal'描述中内置了对复杂用户指令（如拼贴图、尺码表）的智能引导。
        - 市场风格描述更具操作性，直接指导场景设计。
        - 包含了用于生成智能默认提示词的配置。
        """
        self.image_type_goals = {
            'main': 'a flawless, studio-quality hero image on a pure white background (RGB 255,255,255).',
            'lifestyle': 'a compelling, realistic lifestyle photo showing the product in an aspirational, real-world context.',
            'detail': 'a stunning macro close-up shot that showcases a specific, high-quality detail of the product.',
            'size': 'a clear, intuitive visual guide to the product\'s dimensions, using either dimension lines or a size chart if specified in the user\'s prompt.',
            'angle': 'a professional multi-angle view of the product, often presented as a clean grid or a single image composite, showing key perspectives.',
            'infographic': 'a visually engaging infographic that pairs the product with icons and minimal text to highlight its key benefits.',
            'packaging': 'an attractive shot of the product with its packaging, conveying a premium unboxing experience.',
            'comparison': 'a clear side-by-side comparison image that visually highlights the advantages of our product.',
            'instruction': 'a simple, step-by-step visual guide on how to use the product, often in a multi-panel layout.'
        }
        
        self.market_styles = {
            'US': 'The scene should feel bright, optimistic, and family-centric, set in a modern American home or outdoor space.',
            'UK': 'The scene should have an understated elegance, feel authentic and cozy, reflecting classic British quality.',
            'DE': 'The scene must be clean, minimalist, and functional, highlighting the product\'s engineering and precision.',
            'JP': 'The scene should be harmonious and simple, using natural materials with a serene, minimalist aesthetic.',
            'IN': 'The scene should be vibrant and colorful, focusing on family, community, and the product\'s versatility.'
        }
         # V5.2 新增: 市场与语言的强制映射
        self.market_languages = {
            'US': 'English',
            'UK': 'English',
            'DE': 'German (Deutsch)',
            'FR': 'French (Français)',
            'ES': 'Spanish (Español)',
            'IT': 'Italian (Italiano)',
            'JP': 'Japanese (日本語)',
            'IN': 'English' # 印度站点通常以英文为主
        }
    
    
    def _generate_default_creative_prompt(self, image_type: str, product_title: str, selling_points: List[str]) -> str:
        """
        当用户未提供任何创意指令时，智能生成一个默认指令。
        """
        sp_text = ", ".join(selling_points) if selling_points else "its key features"
        
        default_prompts = {
            'main': f"A clean, professional studio shot of the '{product_title}'. Focus on perfect lighting and a clear, appealing front-on or 3/4 angle.",
            'lifestyle': f"A realistic lifestyle scene showing a person happily using the '{product_title}'. The scene should subtly hint at its benefits, like '{sp_text}'.",
            'detail': f"A macro close-up shot focusing on the most impressive detail of the '{product_title}', such as its high-quality material, a specific button, or a unique design element. Highlight its craftsmanship.",
            'size': f"A clear, easy-to-understand image demonstrating the scale of the '{product_title}'. Place it next to a common object for reference or show it being held.",
            'angle': f"A multi-angle composite image of the '{product_title}', showing the front, side, and back views in a clean grid layout.",
            'infographic': f"A simple infographic for the '{product_title}'. Place the product on one side and use 3-4 minimalist icons on the other side to represent its main benefits: {sp_text}.",
            'packaging': f"An elegant shot of the '{product_title}' displayed with its packaging. The scene should feel like a premium unboxing experience.",
            'comparison': f"A side-by-side comparison showing the '{product_title}' next to a generic, older version, visually highlighting that our product is superior.",
            'instruction': f"A simple 3-step visual guide on how to use the '{product_title}'. Use clean graphics and directional arrows to show the process."
        }
        
        return default_prompts.get(image_type, f"A professional photograph showcasing the '{product_title}' and its main features.")

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
        allow_text_in_image: bool = False # V5.2: 恢复此参数的绝对控制权
    ) -> str:
        """
        构建提示词 V5.2。
        强制执行语言本地化和文本控制开关。
        """
        market = product_form.get('targetMarket', 'US')
        # 获取目标语言，默认为英语
        target_language = self.market_languages.get(market, 'English')
        
        prompt_parts = []

        # --- 1. 角色与任务定义 (强化 Amazon 身份) ---
        prompt_parts.append(f"### AMAZON LISTING IMAGE SPECIALIST: CREATIVE BRIEF ###")
        prompt_parts.append(f"**MISSION:** Generate a high-conversion image for the **{market} Amazon Marketplace**.")
        prompt_parts.append(f"**TARGET LANGUAGE:** {target_language}. (CRITICAL: Any generated text MUST be in this language).")

        # --- 2. 图像输入与角色 ---
        prompt_parts.append("\n### INPUTS & ROLES ###")
        #保证原产品图片细节
        prompt_parts.append("1. **PRODUCT IMAGES (The Fact):** Your non-negotiable source of truth for visual appearance. Replicate EXACTLY.")
        #但是可以改变其操作状态
        prompt_parts.append("\n- **Functional State Exception:** To demonstrate the product's primary function, you are permitted to change its operational state. For example, you can show a clasp being open and attached, a lid being unscrewed, or a light being turned on. The fundamental appearance (color, material, shape, logos) must remain 100% identical.")
        final_reference_images = type_specific_references if type_specific_references is not None else reference_images
        if final_reference_images:
            prompt_parts.append(f"2. **REFERENCE IMAGES ({len(final_reference_images)} provided for Style):** Use for artistic direction (composition, lighting, mood). DO NOT copy products shown in them.")
        else:
             prompt_parts.append("2. **REFERENCE IMAGES:** None. Use your expertise to create a top-tier Amazon listing image.")

        # --- 3. 核心执行指令 ---
        prompt_parts.append("\n### EXECUTION ORDER ###")
        goal_desc = self.image_type_goals.get(image_type, f'a professional {image_type} image.')
        core_task = f"Generate {goal_desc}"
        
        # 级联创意指令
        final_creative_prompt = main_prompt
        if type_specific_references:
            specific_prompts = [ref.get('description') for ref in type_specific_references if ref.get('description')]
            if specific_prompts:
                final_creative_prompt = " ".join(specific_prompts)

        # 智能默认值 (如果用户什么都没填)
        if not final_creative_prompt or final_creative_prompt.isspace():
             # 简单的默认引导，确保不留空
             final_creative_prompt = f"Showcase the product's key features in a way that appeals to {market} customers."

        core_task += f" Creative direction: **\"{final_creative_prompt}\"**."
        prompt_parts.append(core_task)
        
        # --- 4. 关键商业规则 (V5.2 核心修复) ---
        prompt_parts.append("\n### CRITICAL BUSINESS RULES ###")
        
        # 4.1 产品保真度
        prompt_parts.append("- **PRODUCT FIDELITY (TIER 1 PRIORITY):** The product in the output image MUST be 100% identical to the PRODUCT IMAGES input. No hallucinations, no redesigns.")
        
        # 4.2 市场风格适配
        market_style = self.market_styles.get(market)
        if market_style:
            prompt_parts.append(f"- **MARKET ADAPTATION:** Scene style should be: {market_style}")

        # 4.3 文本控制与语言本地化 (V5.2 重中之重)
        if allow_text_in_image:
            # 如果允许文字，必须强制本地化
            prompt_parts.append(f"- **TEXT CONTROL:** AUTHORIZED. You may add text if needed (e.g., for infographic callouts, size charts).")
            prompt_parts.append(f"- **LANGUAGE LOCK ({target_language}):** CRITICAL! All generated text MUST be in **{target_language}**.")
            prompt_parts.append(f"  - WARNING: The input data may contain Chinese or other languages. **DO NOT** use them directly in the image. TRANSLATE them to {target_language} if you need to use them.")
        else:
            # 如果禁止文字，必须严厉禁止
            prompt_parts.append("- **TEXT CONTROL:** STRICTLY PROHIBITED. Do NOT add any new text, captions, labels, or charts. The image must be purely visual.")
            prompt_parts.append("  - Exception: You MUST preserve original text that is physically printed ON the product itself in the input images.")

        # 4.4 技术规格
        prompt_parts.append(f"- **TECH SPECS:** {size} ({ratio}), Photorealistic, 8K, Amazon-ready commercial quality.")

        return "\n".join(prompt_parts)

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
        V5.2 重新生成逻辑，保持对 allow_text_in_image 的继承
        """
        try:
            # 从上下文中恢复所有必要参数
            product_form = context.get('product_form', {})
            image_type = context.get('image_type', 'main')
            original_main_prompt = context.get('main_prompt', '')
            # 确保在rework时也继承原始的文本控制设置
            allow_text = context.get('allow_text_in_image', False) 
            
            final_rework_references = reference_images if reference_images is not None else context.get('type_specific_references')

            rework_text = user_modifications.get('prompt_modifications', 'Improve quality.')
            new_main_prompt = f"Original idea: '{original_main_prompt}'. CRITICAL NEW FEEDBACK to apply: **\"{rework_text}\"**."
            
            rework_core = self.build_prompt(
                product_form=product_form,
                image_type=image_type,
                main_prompt=new_main_prompt,
                type_specific_references=final_rework_references,
                size=context.get('size', '1024x1024'),
                ratio=context.get('ratio', '1:1'),
                allow_text_in_image=allow_text # 传入继承的设置
            )
            
            header = "### REWORK REQUEST (Apply feedback while maintaining core rules) ###"
            if previous_image_url:
                 header += f"\nReference previous image for context: {previous_image_url}"

            return f"{header}\n\n{rework_core}"

        except Exception as e:
            print(f"Rework Error: {e}")
            return f"Rework image based on feedback: {user_modifications.get('prompt_modifications')}"

# --- END OF FILE prompt_builder.py (V5.2 Commercial Fix) ---