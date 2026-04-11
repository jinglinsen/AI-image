// 前端应用配置
console.log(process.env.NODE_ENV)
// development , production
const config = {
  // API配置
  api: {
    baseURL: process.env.NODE_ENV === 'development' 
      ? 'http://127.0.0.1:5000/api'   // 生产环境API地址
      : 'http://192.168.0.3:5000/api',     // 开发环境使用局域网后端地址
    timeout: 120000, // 2分钟超时
    // 图片服务基础URL（用于构建图片访问路径）
    imageBaseURL: process.env.NODE_ENV === 'development'
      ? 'http://127.0.0.1:5000'       // 生产环境图片基础地址
      : 'http://192.168.0.3:5000',         // 开发环境使用局域网图片服务
  },
  
  // 应用配置
  app: {
    name: 'Amazon AIGC助手',
    version: '1.0.0',
    description: '智能产品图片生成平台'
  },
  
  // 上传配置
  upload: {
    maxFileSize: 10 * 1024 * 1024, // 10MB
    allowedTypes: ['image/jpeg', 'image/png', 'image/webp', 'image/bmp'],
    maxFiles: 10
  },
  
  // 图片生成配置
  generation: {
    pollInterval: 2000, // 轮询间隔（毫秒）
    maxPollAttempts: 300, // 最大轮询次数（10分钟）
    supportedImageTypes: [
      { key: 'main', label: '产品主图', description: '纯白色背景，产品专业照片，清晰对焦占据85%以上区域，不含文字Logo水印' },
      { key: 'infographic', label: '信息图', description: '通过图形和少量文字直观展示产品核心功能、优点或规格，快速传达复杂信息' },
      { key: 'lifestyle', label: '生活方式图', description: '展示产品在真实生活场景中使用画面，帮助消费者建立情感连接' },
      { key: 'size', label: '尺寸图', description: '使用尺子、手或常见物品作参照物展示产品尺寸，减少因尺寸不符导致的退货' },
      { key: 'detail', label: '产品细节图', description: '特写镜头突出产品关键细节、材质、工艺或独特设计，展示产品高品质' },
      { key: 'angle', label: '多角度图', description: '从正面、背面、侧面、俯视等不同角度展示产品，让消费者全面了解外观' },
      { key: 'instruction', label: '使用说明图', description: '对需要组装或特定使用方法的产品，用图片分步骤展示操作方法' },
      { key: 'comparison', label: '对比图', description: '将产品与竞争对手或同系列不同型号产品进行比较，突出自身优势' },
      { key: 'packaging', label: '包装图', description: '展示产品包装，特别适合包装设计精美或适合送礼的产品，增加吸引力' }
    ],
    supportedMarkets: [
      { value: 'US', label: '🇺🇸 美国 (Amazon.com)', description: '北美最大市场，注重功能性和家庭场景' },
      { value: 'UK', label: '🇬🇧 英国 (Amazon.co.uk)', description: '欧洲重要市场，偏好经典优雅风格' },
      { value: 'DE', label: '🇩🇪 德国 (Amazon.de)', description: '注重品质和工艺，简约实用风格' },
      { value: 'JP', label: '🇯🇵 日本 (Amazon.co.jp)', description: '精致简约，温馨整洁的日式美学' },
      { value: 'IN', label: '🇮🇳 印度 (Amazon.in)', description: '新兴市场，重视性价比和实用性' }
    ],
    availableModels: [
      { value: 'dall-e-3', label: '🎨 DALL-E 3', description: 'OpenAI 图像生成模型' },
      { value: 'qwen-plus', label: '☁️ Qwen Plus', description: '通义千问大模型生成' },
      { value: 'qwen-vl-plus', label: '👁️ Qwen VL Plus', description: '通义千问视觉大模型' },
      { value: 'gpt5', label: '🤖 GPT-5', description: '最新模型，理解力强，创意丰富' }
    ]
  },
  
  // 用户体验配置
  ui: {
    theme: 'dark',
    primaryColor: '#FFD700', // 金色主题
    animationDuration: 300,
    toastDuration: 3000
  },
  
  // 调试配置
  debug: {
    enabled: process.env.NODE_ENV === 'production',
    logLevel: 'info', // 'debug', 'info', 'warn', 'error'
    showApiLogs: true
  }
}

export default config

