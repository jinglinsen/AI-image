import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime

class PromptBuilderService:
    """Amazon Listing图片生成提示词构建器 - 优化版
    
    核心原则：
    1. 产品外观100%还原（WHAT） - 颜色、材质、细节完全一致
    2. 展示方式自由创作（HOW） - 角度、构图、环境由AI选择
    """
    
    def __init__(self):
        # 精简的图片类型配置
        self.image_type_prompts = {
            'main': {
                'role': 'Amazon Main Image Photographer',
                'rule': 'Product appearance = input (100%). Choose best front angle.',
                'specs': 'White RGB(255,255,255) | 85% fill | Professional lighting'
            },
            'lifestyle': {
                'role': 'Amazon Lifestyle Photographer',
                'rule': 'Product appearance = input (100%). Choose natural usage angle.',
                'specs': 'Real-life scene | Emotional appeal | Product in context'
            },
            'detail': {
                'role': 'Amazon Macro Detail Photographer',
                'rule': 'Product details = input (100%). Choose best close-up angle.',
                'specs': 'Sharp macro | Highlight quality | Material texture focus'
            },
            'size': {
                'role': 'Amazon Size Demonstration Photographer & Technical Illustrator',
                'rule': 'Product appearance = input (100%). Analyze product shape, add accurate dimension lines.',
                'specs': 'Visual dimension lines (NO TEXT) | Scale objects | Professional technical drawing style'
            },
            'angle': {
                'role': 'Amazon Multi-Angle Photographer',
                'rule': 'Product appearance = input (100%). Show 360° views.',
                'specs': 'Multiple angles | Consistent lighting | Comprehensive views'
            },
            'infographic': {
                'role': 'Amazon Infographic Designer',
                'rule': 'Product appearance = input (100%). Add visual info graphics.',
                'specs': 'Icons/symbols | Feature highlights | Professional layout'
            },
            'packaging': {
                'role': 'Amazon Packaging Photographer',
                'rule': 'Product + packaging = input (100%). Show unboxing appeal.',
                'specs': 'Attractive presentation | Contents visible | Gift-worthy'
            },
            'comparison': {
                'role': 'Amazon Comparison Designer',
                'rule': 'Our product appearance = input (100%). Show advantages.',
                'specs': 'Side-by-side | Visual benefits | Fair but favorable'
            },
            'instruction': {
                'role': 'Amazon Instruction Visual Designer',
                'rule': 'Product appearance = input (100%). Show usage steps.',
                'specs': 'Step-by-step | Clear sequence | Easy to follow'
            }
        }
        
        # 市场风格配置
        self.market_styles = {
            'US': 'Bright optimistic | Family-focused | Spacious modern settings',
            'UK': 'Elegant classic | Sophisticated | Traditional quality',
            'DE': 'Clean minimal | Engineering quality | Functional precision',
            'JP': 'Harmonious simple | Detail-oriented | Natural minimal',
            'IN': 'Vibrant warm | Value-focused | Family versatile'
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
        """构建Amazon Listing图片生成提示词"""
        
        try:
            config = self.image_type_prompts.get(image_type, self.image_type_prompts['main'])
            market = product_form.get('targetMarket', 'US')
            product_name = product_form.get('title', 'Product')
            
            # 构建精简提示词
            prompt = f"""
╔════════════════════════════════════════════════════════════════════════════╗
║ AMAZON LISTING IMAGE GENERATION
║ Role: {config['role']}
║ Product: {product_name}
║ Target: {market} Market
╚════════════════════════════════════════════════════════════════════════════╝

▼ CORE RULE (MANDATORY)
{config['rule']}
Specifications: {config['specs']}

▼ TWO-PHASE APPROACH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE 1: PRODUCT REPLICATION (100% Accuracy Required)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Input images show the ACTUAL product. Replicate EXACTLY:
✓ Colors (every shade, finish, material property)
✓ Textures (surface quality, manufacturing details)
✓ Logos & Text (brand names, labels, packaging text)
✓ Shape & Form (proportions, silhouette, dimensions)
✓ Details (buttons, seams, patterns, wear marks)

✗ Do NOT change: Colors | Materials | Features | Design elements
✗ Do NOT add/remove: Components | Accessories | Product elements
✗ Do NOT "improve": Appearance | Style | Modernize | Upgrade

Rule: If it exists in input → Keep exactly | If not in input → Don't add

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE 2: CREATIVE PRESENTATION (Full Creative Freedom)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Freely adjust HOW to present the product:
✓ Camera angle (front, 45°, top, side, close-up - choose best)
✓ Product rotation (show different sides, find hero angle)
✓ Composition (rule of thirds, golden ratio, centering)
✓ Positioning (centered, offset, diagonal, dynamic)
✓ Environment (background, props, scene context)
✓ Lighting (direction, mood, shadows, highlights)

Mandate: DO NOT copy input angle → Choose optimal angle for {image_type}

▼ IMAGE CLASSIFICATION
Product Images (first): Your reference for WHAT product looks like
Reference Images (if provided): Inspiration for HOW to present (style/composition)

▼ CREATIVE DIRECTION (Environment & Presentation Only)
User request: "{main_prompt}"
Apply to: Backgrounds, lighting, angles, composition, mood
Protect: Product appearance remains identical to input

▼ MARKET ADAPTATION
{market}: {self.market_styles[market]}
Apply to: Environment styling, color schemes, scene settings
Protect: Product itself unchanged

▼ TECHNICAL SPECS
Resolution: {size} | Ratio: {ratio} | Quality: 8K, professional DSLR
Style: Photorealistic, commercial, Amazon-optimized"""

            # 添加文字控制
            if not allow_text_in_image:
                prompt += """

▼ TEXT CONTROL (CRITICAL - MUST FOLLOW)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ABSOLUTE PROHIBITION: NO ADDITIONAL TEXT IN THIS IMAGE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✗ STRICTLY FORBIDDEN - DO NOT ADD:
• NO captions, subtitles, titles, headlines, descriptions
• NO infographic text, annotations, explanatory labels, callouts
• NO measurements text, dimension numbers, size labels
• NO price tags, promotional text, marketing copy, slogans
• NO UI overlays, text bubbles, speech bubbles, banners
• NO watermarks, copyright text, brand overlays
• NO decorative text, artistic lettering, stylized fonts
• NO instructions text, warnings, informational overlays
• NO any readable text, characters, letters, numbers, symbols

✓ ONLY EXCEPTION - MUST PRESERVE (if present in input):
• Product's original logos, brand names, product labels
• Packaging's original text (product names, warnings, ingredients)
• Text that is PART OF PRODUCT DESIGN in input images

RULE: Text in input product → Keep exactly | No text in input → ZERO text added

FINAL CHECK: Before submitting, verify there is NO NEW TEXT anywhere in the image
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

            # 添加尺寸信息
            if image_type == 'size' and product_form.get('dimensions'):
                dims = product_form['dimensions']
                if dims.get('length') and dims.get('width') and dims.get('height'):
                    prompt += f"""

▼ DIMENSION MARKING INSTRUCTIONS (CRITICAL FOR SIZE IMAGES)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRODUCT DIMENSIONS: {dims['length']} × {dims['width']} × {dims['height']} {dims.get('unit', 'cm')}

STEP 1: ANALYZE PRODUCT SHAPE
• Carefully examine the product in input images
• Identify the longest dimension (usually length)
• Identify the widest dimension (usually width)  
• Identify the tallest dimension (usually height)
• For irregular shapes: measure at the MAXIMUM extent in each direction

STEP 2: ADD DIMENSION LINES (VISUAL ONLY - NO TEXT)
• Draw solid straight lines (━━━) for primary dimensions
• Draw dashed lines (- - -) for secondary/internal dimensions
• Add arrows (←→ ↕) or brackets (⟨ ⟩) at line endpoints
• Position lines OUTSIDE the product boundary when possible
• Make lines clear and unambiguous

STEP 3: VISUAL SCALE REFERENCE
• Add familiar reference objects (ruler, hand, coin, smartphone, etc.)
• Place reference object next to product for size comparison
• Ensure reference object is recognizable and standard-sized

STEP 4: LAYOUT
• Choose angle that clearly shows all three dimensions
• Use orthographic or isometric view for clarity
• Ensure dimension lines don't overlap or confuse
• White or light neutral background for maximum clarity

EXAMPLE LAYOUT:
        ←──────────────→ (length line)
    ↑   [  PRODUCT  ]
    |   [           ]
    ↓   [___________] (width line goes perpendicular)
    (height)

CRITICAL RULES:
• NO TEXT on dimension lines (numbers, labels, or measurements)
• ONLY visual indicators: lines, arrows, brackets
• Product appearance stays 100% identical to input
• Focus on making measurements VISUALLY obvious
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

            # 添加参考图指导
            ref_images = type_specific_references or reference_images
            if ref_images:
                prompt += """

▼ REFERENCE IMAGES USAGE
Purpose: Style/composition/lighting inspiration ONLY
Rule: DO NOT copy products from reference images
Apply: Their style/mood/layout to YOUR product (from input images)"""

            # 添加卖点
            if product_form.get('sellingPoints'):
                prompt += f"""

▼ SELLING POINTS TO HIGHLIGHT (via composition, not product changes)
{product_form['sellingPoints']}"""

            # 负面提示词
            negatives = ['blurry', 'low-res', 'pixelated', 'unrealistic', 'cartoon', 'oversaturated']
            if not allow_text_in_image:
                text_negatives = [
                    'text', 'words', 'letters', 'captions', 'subtitles', 'titles',
                    'labels', 'annotations', 'overlay text', 'UI text', 'infographic text',
                    'watermark text', 'promotional text', 'marketing text', 'decorative text',
                    'text banner', 'text overlay', 'floating text', 'readable characters',
                    'numbers overlay', 'dimension text', 'measurement text', 'price text'
                ]
                negatives.extend(text_negatives)
            
            prompt += f"""

▼ AVOID
{', '.join(negatives)}

═══════════════════════════════════════════════════════════════════════════════
SUMMARY: Product = Input (WHAT) | Presentation = Your Choice (HOW)
Think: Professional Amazon photographer preserving product, choosing best angle
═══════════════════════════════════════════════════════════════════════════════"""

            # 输出调试信息
            print("\n" + "="*80)
            print(f"Amazon Listing Image Prompt | Type: {image_type} | Market: {market}")
            print(f"Text: {'Allowed' if allow_text_in_image else 'Prohibited (except product text)'}")
            print(f"Length: {len(prompt)} chars")
            print("="*80)
            
            return prompt.strip()
            
        except Exception as e:
            print(f"Prompt build error: {e}")
            return self._build_fallback_prompt(product_form, image_type, main_prompt, allow_text_in_image)
    
    def _build_fallback_prompt(self, product_form, image_type, main_prompt, allow_text_in_image):
        """简化的后备提示词"""
        product_name = product_form.get('title', 'Product')
        text_rule = " | NO ADDITIONAL TEXT (preserve product text only)" if not allow_text_in_image else ""
        
        return f"""Amazon {image_type} image: {product_name}
Rule: Product appearance = input images (100% match) | Choose best angle
User direction (environment only): {main_prompt}
Quality: Professional, photorealistic, 8K{text_rule}"""
    
    def build_rework_prompt(
        self,
        original_prompt: str,
        user_modifications: Dict[str, Any],
        context: Dict[str, Any],
        reference_images: List[Dict] = None,
        original_image_info: Dict[str, Any] = None
    ) -> str:
        """构建重新生成提示词（简化版）"""
        
        user_feedback = user_modifications.get('prompt_modifications', 'Improve quality')
        image_type = original_image_info.get('type', 'main') if original_image_info else 'main'
        
        rework_prompt = f"""
╔════════════════════════════════════════════════════════════════════════════╗
║ AMAZON LISTING IMAGE REWORK
║ Improvement Request: {user_feedback}
╚════════════════════════════════════════════════════════════════════════════╝

▼ REWORK RULES
1. Product appearance MUST still match input images (100%)
2. Apply user feedback to: Angle, composition, lighting, environment
3. Do NOT change: Product colors, materials, features, details

▼ IMPROVEMENT FOCUS FOR {image_type.upper()}
{self._get_improvement_focus(image_type)}

▼ ORIGINAL CONTEXT (maintain successful elements)
{original_prompt}

▼ USER FEEDBACK APPLICATION
"{user_feedback}"
Apply to: Camera angle, composition, lighting, background, mood
Protect: Product appearance (colors, textures, materials, features)

═══════════════════════════════════════════════════════════════════════════════
Goal: Better presentation while maintaining product fidelity
═══════════════════════════════════════════════════════════════════════════════"""

        return rework_prompt.strip()
    
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

