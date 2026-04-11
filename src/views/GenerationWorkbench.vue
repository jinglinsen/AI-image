<template>
  <div class="generation-workbench">
    <!-- 页面标题和任务信息 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">
          <el-icon><Magic /></el-icon>
          AI图片生成工作台
        </h1>
        <p class="task-info">任务ID: {{ taskId }} | 产品: {{ taskInfo.productName }}</p>
      </div>
      <div class="header-right">
        <el-button @click="$router.push('/')">
          <el-icon><Back /></el-icon>
          返回仪表盘
        </el-button>
      </div>
    </div>

    <!-- 主要工作区域 -->
    <el-container class="workbench-container">
      <!-- 左侧：图片类型导航 -->
      <el-aside class="sidebar" width="280px">
        <div class="sidebar-title">图片类型选择</div>
        <el-menu 
          :default-active="activeImageType"
          @select="selectImageType"
          class="image-type-menu"
        >
          <el-menu-item 
            v-for="type in imageTypes" 
            :key="type.id"
            :index="type.id"
            class="menu-item"
          >
            <el-icon>
              <component :is="type.icon" />
            </el-icon>
            <div class="menu-item-content">
              <span class="menu-title">{{ type.name }}</span>
              <span class="menu-description">{{ type.description }}</span>
              <el-badge 
                v-if="type.generatedCount > 0"
                :value="type.generatedCount" 
                class="generated-badge"
              />
            </div>
          </el-menu-item>
        </el-menu>

        <!-- 任务进度 -->
        <div class="progress-section">
          <div class="progress-title">完成进度</div>
          <el-progress 
            :percentage="overallProgress" 
            :stroke-width="8"
            :color="progressColor"
          />
          <p class="progress-text">
            已完成 {{ completedTypes }}/{{ imageTypes.length }} 种图片类型
          </p>
        </div>
      </el-aside>

      <!-- 右侧：配置和生成区域 -->
      <el-main class="main-area">
        <div v-if="currentImageType" class="generation-panel">
          <!-- 当前图片类型标题 -->
          <div class="panel-header">
            <h2 class="panel-title">
              <el-icon>
                <component :is="currentImageType.icon" />
              </el-icon>
              {{ currentImageType.name }}
            </h2>
            <p class="panel-description">{{ currentImageType.fullDescription }}</p>
          </div>

          <!-- 配置表单 -->
          <el-form 
            :model="generationConfig" 
            label-width="120px"
            class="config-form"
          >
            <!-- 基础配置 -->
            <el-card class="config-section">
              <div class="section-title">基础配置</div>
              
              <!-- 产品选择（如果有多个产品） -->
              <el-form-item v-if="taskInfo.products && taskInfo.products.length > 1" label="选择产品">
                <el-select v-model="generationConfig.selectedProduct" style="width: 100%">
                  <el-option 
                    v-for="product in taskInfo.products" 
                    :key="product.id"
                    :label="product.name"
                    :value="product.id"
                  />
                </el-select>
              </el-form-item>

              <!-- 动态配置项（根据图片类型变化） -->
              <component 
                v-if="currentImageType && currentImageType.configComponent"
                :is="currentImageType.configComponent" 
                v-model="generationConfig"
                :task-info="taskInfo"
              />

              <!-- 通用风格选择 -->
              <el-form-item label="图片风格">
                <el-select v-model="generationConfig.style" style="width: 100%">
                  <el-option label="写实照片" value="photorealistic" />
                  <el-option label="高端商业摄影" value="commercial" />
                  <el-option label="明亮通风" value="bright-airy" />
                  <el-option label="温馨家居" value="cozy-home" />
                  <el-option label="现代简约" value="modern-minimal" />
                </el-select>
              </el-form-item>

              <!-- 高级选项 -->
              <el-collapse class="advanced-options">
                <el-collapse-item title="高级选项" name="advanced">
                  <el-form-item label="负向提示词">
                    <el-input
                      v-model="generationConfig.negativePrompt"
                      type="textarea"
                      :rows="2"
                      placeholder="输入不希望出现的元素，如：模糊、低像素、怪异的肢体、文字"
                    />
                  </el-form-item>
                  
                  <el-form-item label="生成数量">
                    <el-slider
                      v-model="generationConfig.imageCount"
                      :min="1"
                      :max="4"
                      show-stops
                      show-input
                    />
                  </el-form-item>

                  <el-form-item label="图片尺寸">
                    <el-select v-model="generationConfig.imageSize">
                      <el-option label="正方形 (1024x1024)" value="1024x1024" />
                      <el-option label="横版 (1024x768)" value="1024x768" />
                      <el-option label="竖版 (768x1024)" value="768x1024" />
                    </el-select>
                  </el-form-item>
                </el-collapse-item>
              </el-collapse>
            </el-card>

            <!-- 用户提示词编辑 -->
            <el-card class="config-section">
              <div class="section-title">自定义提示词</div>
              <el-form-item>
                <el-input
                  v-model="generationConfig.userPrompt"
                  type="textarea"
                  :rows="4"
                  :placeholder="currentImageType.promptPlaceholder"
                />
                <div class="prompt-tip">
                  您可以在这里详细描述想要的场景、风格和细节要求
                </div>
              </el-form-item>
            </el-card>

            <!-- 生成按钮 -->
            <div class="generation-actions">
              <div class="text-graphic-toggle">
                <label class="toggle-label">是否为图文：</label>
                <el-switch 
                  v-model="generationConfig.isTextGraphic"
                  :active-value="true"
                  :inactive-value="false"
                  active-color="#13ce66"
                  inactive-color="#ff4949"
                  active-text="是"
                  inactive-text="否"
                />
                <span class="debug-text">（当前：{{ generationConfig.isTextGraphic ? '允许文字' : '禁止文字' }}）</span>
              </div>
              <el-button 
                type="primary" 
                size="large"
                @click="generateImages"
                :loading="generating"
                class="generate-btn"
              >
                <el-icon><Magic /></el-icon>
                {{ generating ? '生成中...' : '生成图片' }}
              </el-button>
              <el-button @click="resetConfig">
                <el-icon><Refresh /></el-icon>
                重置配置
              </el-button>
            </div>
          </el-form>

          <!-- 生成结果展示 -->
          <div v-if="generatedImages.length > 0" class="results-section">
            <div class="section-title">生成结果</div>
            <div class="images-grid">
              <div 
                v-for="(image, index) in generatedImages" 
                :key="index"
                class="image-card"
              >
                <div class="image-container" @click="previewImage(image)">
                  <img :src="image.url" :alt="`Generated image ${index + 1}`" />
                  <div class="image-overlay" @click.stop>
                    <el-button-group>
                      <el-button size="small" @click="previewImage(image)">
                        <el-icon><ZoomIn /></el-icon>
                      </el-button>
                      <el-button size="small" @click="downloadImage(image)">
                        <el-icon><Download /></el-icon>
                      </el-button>
                      <el-button size="small" @click="regenerateFromImage(image)">
                        <el-icon><Refresh /></el-icon>
                      </el-button>
                    </el-button-group>
                  </div>
                </div>
                <div class="image-info">
                  <div class="image-quality">
                    <span>质量评分:</span>
                    <el-rate 
                      v-model="image.quality" 
                      :max="5" 
                      size="small"
                      show-score
                    />
                  </div>
                  <el-button 
                    v-if="!image.approved"
                    type="success" 
                    size="small"
                    @click="approveImage(image)"
                  >
                    采用这张
                  </el-button>
                  <el-tag v-else type="success" size="small">已采用</el-tag>
                </div>
              </div>
            </div>

            <!-- 批量操作 -->
            <div class="batch-actions">
              <el-button @click="regenerateAll">
                <el-icon><Refresh /></el-icon>
                重新生成全部
              </el-button>
              <el-button @click="downloadAll">
                <el-icon><Download /></el-icon>
                下载全部
              </el-button>
            </div>
          </div>

          <!-- 生成历史 -->
          <div v-if="generationHistory.length > 0" class="history-section">
            <el-collapse>
              <el-collapse-item title="生成历史" name="history">
                <div class="history-list">
                  <div 
                    v-for="(history, index) in generationHistory" 
                    :key="index"
                    class="history-item"
                  >
                    <div class="history-info">
                      <span class="history-time">{{ history.timestamp }}</span>
                      <span class="history-config">{{ history.configSummary }}</span>
                    </div>
                    <el-button size="small" @click="loadHistoryConfig(history)">
                      使用此配置
                    </el-button>
                  </div>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>
        </div>

        <!-- 未选择图片类型时的提示 -->
        <div v-else class="empty-panel">
          <el-icon class="empty-icon"><Picture /></el-icon>
          <h3>请选择图片类型</h3>
          <p>从左侧菜单选择要生成的图片类型，开始您的AI创作之旅</p>
        </div>
      </el-main>
    </el-container>

    <!-- 大图预览区域 -->
    <div v-if="previewImageData" class="image-large-preview">
      <div class="preview-header">
        <h3>
          <el-icon><Picture /></el-icon>
          图片预览 - {{ getImageTypeLabel(previewImageData.type) }}
        </h3>
        <div class="preview-actions">
          <el-button @click="downloadImage(previewImageData)">
            <el-icon><Download /></el-icon>
            下载
          </el-button>
          <el-button type="warning" @click="showRegenerateDialog(previewImageData)">
            <el-icon><Refresh /></el-icon>
            重新生成
          </el-button>
          <el-button @click="closePreview">
            <el-icon><Close /></el-icon>
            关闭
          </el-button>
        </div>
      </div>
      
      <div class="preview-content">
        <div class="large-image-container">
          <img 
            :src="previewImageData.url" 
            :alt="previewImageData.type || '预览图片'"
            class="large-preview-image"
          />
        </div>
        
        <div class="preview-info-panel">
          <div class="info-section">
            <h4>图片信息</h4>
            <div class="info-item">
              <span class="label">类型:</span>
              <span class="value">{{ getImageTypeLabel(previewImageData.type) }}</span>
            </div>
            <div class="info-item">
              <span class="label">模型:</span>
              <span class="value">{{ previewImageData.model || 'qwen-plus' }}</span>
            </div>
            <div class="info-item">
              <span class="label">创建时间:</span>
              <span class="value">{{ formatTime(previewImageData.created_at) }}</span>
            </div>
            <div class="info-item" v-if="previewImageData.size">
              <span class="label">尺寸:</span>
              <span class="value">{{ previewImageData.size }}</span>
            </div>
          </div>
          
          <div class="info-section" v-if="previewImageData.prompt_used">
            <h4>生成提示词</h4>
            <div class="prompt-content">
              {{ previewImageData.prompt_used }}
            </div>
          </div>
          
          <div class="info-section">
            <h4>操作</h4>
            <div class="action-buttons">
              <el-button type="primary" @click="downloadImage(previewImageData)" style="width: 100%; margin-bottom: 8px;">
                <el-icon><Download /></el-icon>
                下载图片
              </el-button>
              <el-button type="warning" @click="showRegenerateDialog(previewImageData)" style="width: 100%; margin-bottom: 8px;">
                <el-icon><Refresh /></el-icon>
                重新生成
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 重新生成对话框 -->
    <el-dialog 
      v-model="regenerateVisible" 
      title="重新生成图片" 
      width="600px"
      :close-on-click-modal="false"
    >
      <div class="regenerate-form" v-if="regenerateImageData">
        <div class="original-image">
          <h4>原始图片</h4>
          <img :src="regenerateImageData.url" class="original-preview" />
          <p class="image-details">
            <strong>类型:</strong> {{ getImageTypeLabel(regenerateImageData.type) }}<br>
            <strong>模型:</strong> {{ regenerateImageData.model || 'qwen-plus' }}
          </p>
        </div>
        
        <el-divider />
        
        <div class="regenerate-options">
          <h4>重新生成选项</h4>
          
          <el-form :model="regenerateForm" label-width="120px">
            <el-form-item label="提示词修改">
              <el-input
                v-model="regenerateForm.promptModifications"
                type="textarea"
                :rows="4"
                placeholder="输入对原提示词的修改意见，例如：'增加更多光影效果'、'改为蓝色背景'等"
              />
            </el-form-item>
            
            <el-form-item label="使用模型">
              <el-select v-model="regenerateForm.model" placeholder="选择生成模型">
                <el-option 
                  v-for="model in availableModels" 
                  :key="model.value" 
                  :label="model.label" 
                  :value="model.value"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="参考图片">
              <UnifiedImageUpload
                v-model="regenerateForm.referenceImages"
                :multiple="true"
                :show-description="false"
                :show-purpose="true"
                upload-id="regenerate-ref"
                style="margin-top: 10px;"
              />
            </el-form-item>
          </el-form>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="regenerateVisible = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="handleRegenerate"
          :loading="regenerating"
        >
          开始重新生成
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
// 引入图标
import { Download, Refresh, Picture, Close, ZoomIn } from '@element-plus/icons-vue'

// 引入配置组件
import ProductMainImageConfig from '../components/ProductMainImageConfig.vue'
import SizeImageConfig from '../components/SizeImageConfig.vue'
import DetailImageConfig from '../components/DetailImageConfig.vue'
import SceneImageConfig from '../components/SceneImageConfig.vue'
import AngleImageConfig from '../components/AngleImageConfig.vue'
import InteractiveImageConfig from '../components/InteractiveImageConfig.vue'
import VarietyImageConfig from '../components/VarietyImageConfig.vue'
import UnifiedImageUpload from '../components/UnifiedImageUpload.vue'
import AIGCService from '../services/aigcService.js'
import config from '../config/index.js'

export default {
  name: 'GenerationWorkbench',
  components: {
    ProductMainImageConfig,
    SizeImageConfig,
    DetailImageConfig,
    SceneImageConfig,
    AngleImageConfig,
    InteractiveImageConfig,
    VarietyImageConfig,
    UnifiedImageUpload,
    Download,
    Refresh,
    Picture,
    Close,
    ZoomIn
  },
  props: {
    taskId: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      activeImageType: 'main-image',
      generationConfig: {
        selectedProduct: '',
        style: 'photorealistic',
        negativePrompt: '模糊, 低像素, 怪异的肢体, 文字, 水印',
        imageCount: 2,
        imageSize: '1024x1024',
        userPrompt: '',
        isTextGraphic: false
      },
      generatedImages: [],
      generationHistory: [],
      generating: false,
      previewImageData: null,
      // 重新生成相关
      regenerateVisible: false,
      regenerateImageData: null,
      regenerating: false,
      regenerateForm: {
        promptModifications: '',
        model: 'qwen-plus',
        referenceImages: []
      },
      taskInfo: {
        productName: '宠物狗狗磨牙玩具套装',
        targetMarket: 'US',
        products: [
          { id: 'p1', name: '蓝色骨头玩具' },
          { id: 'p2', name: '黄色发声球' },
          { id: 'p3', name: '红色飞盘' }
        ]
      },
      imageTypes: [
        {
          id: 'main-image',
          name: 'A. 产品主图',
          description: '纯白背景产品图',
          fullDescription: '在简洁、干净的纯白色背景上，整齐摆放单个或多个产品。产品需要精修，重塑光影改变高光和阴影。',
          icon: 'Box',
          configComponent: 'ProductMainImageConfig',
          promptPlaceholder: '例如：在纯白色背景上展示蓝色骨头玩具，柔和的侧光照明，突出产品材质纹理...',
          generatedCount: 0
        },
        {
          id: 'size-image',
          name: 'B. 尺寸图',
          description: '展示产品尺寸',
          fullDescription: '展示产品的尺寸或适用范围，每个产品放置在一个清晰的参照物旁边以方便消费者理解其大小。',
          icon: 'Ruler',
          configComponent: 'SizeImageConfig',
          promptPlaceholder: '例如：展示产品长度为20cm，与iPhone进行大小对比...',
          generatedCount: 0
        },
        {
          id: 'detail-image',
          name: 'C. 产品功能细节图',
          description: '突出功能特性',
          fullDescription: '单独展示产品的具体功能部分，图像中包含一只宠物正在使用该产品，展示其功能和舒适性。',
          icon: 'View',
          configComponent: 'DetailImageConfig',
          promptPlaceholder: '例如：放大展示牵引绳的金属卡扣，一只狗正在佩戴，展示卡扣的光泽和坚固性...',
          generatedCount: 0
        },
        {
          id: 'scene-image',
          name: 'D. 使用场景图',
          description: '实际使用场景',
          fullDescription: '展示产品在实际使用中的场景，给人温馨舒适的感受，保留空间方便后期添加文案。',
          icon: 'Picture',
          configComponent: 'SceneImageConfig',
          promptPlaceholder: '例如：在阳光明媚的客厅里，金毛犬正在开心地玩着蓝色骨头玩具...',
          generatedCount: 3
        },
        {
          id: 'angle-image',
          name: 'E. 多角度展示图',
          description: '不同角度展示',
          fullDescription: '展示产品从不同角度的图片，确保消费者能看到全面的信息。',
          icon: 'Compass',
          configComponent: 'AngleImageConfig',
          promptPlaceholder: '例如：从正面、侧面、背面三个角度展示牵引绳...',
          generatedCount: 0
        },
        {
          id: 'interactive-image',
          name: 'F. 互动图',
          description: '人宠互动场景',
          fullDescription: '展示宠物产品与主人互动的场景，场景自然、充满温馨的家庭氛围。',
          icon: 'User',
          configComponent: 'InteractiveImageConfig',
          promptPlaceholder: '例如：年轻女主人和金毛犬在公园里一起玩飞盘，阳光洒在草地上...',
          generatedCount: 0
        },
        {
          id: 'variety-image',
          name: 'G. 产品多样性展示图',
          description: '多颜色多款式',
          fullDescription: '如果产品有不同颜色或款式，展示产品的多个选择，所有选项整齐排列。',
          icon: 'Grid',
          configComponent: 'VarietyImageConfig',
          promptPlaceholder: '例如：展示红色、蓝色、绿色三种颜色的牵引绳，整齐排列在白色背景上...',
          generatedCount: 0
        }
      ]
    }
  },
  computed: {
    currentImageType() {
      return this.imageTypes.find(type => type.id === this.activeImageType)
    },
    completedTypes() {
      return this.imageTypes.filter(type => type.generatedCount > 0).length
    },
    overallProgress() {
      return Math.round((this.completedTypes / this.imageTypes.length) * 100)
    },
    progressColor() {
      if (this.overallProgress < 30) return '#f56c6c'
      if (this.overallProgress < 70) return '#e6a23c'
      return '#67c23a'
    }
  },
  methods: {
    selectImageType(typeId) {
      this.activeImageType = typeId
      this.generatedImages = []
      this.resetConfig()
    },
    
    async generateImages() {
      this.generating = true
      
      try {
        // 准备生成参数
        const params = {
          productForm: {
            targetMarket: this.taskInfo.targetMarket || 'US',
            title: this.taskInfo.productName || 'Product',
            sellingPoints: this.taskInfo.sellingPoints || '',
            dimensions: this.taskInfo.dimensions || {}
          },
          selectedImageTypes: [this.activeImageType],
          mainPrompt: this.generationConfig.userPrompt,
          productImages: [],
          referenceImagesByType: {},
          competitors: [],
          selectedSize: this.generationConfig.imageSize,
          selectedRatio: this.generationConfig.imageSize === '1024x1024' ? '1:1' : '4:3',
          selectedModel: 'qwen-plus',
          allowTextInImage: this.generationConfig.isTextGraphic
        }

        console.log('🎨 开始生成图片，参数:', params)

        // 使用真实的API调用（如果后端可用）
        try {
          const result = await AIGCService.generateImages(params)
          console.log('✅ 生成结果:', result)
          this.$message.success('图片生成任务已启动，请查看任务状态')
        } catch (apiError) {
          console.warn('⚠️ API调用失败，使用模拟数据:', apiError)
          // 回退到模拟数据
          await new Promise(resolve => setTimeout(resolve, 3000))
          const mockImages = []
          for (let i = 0; i < this.generationConfig.imageCount; i++) {
            mockImages.push({
              id: Date.now() + i,
              url: `https://via.placeholder.com/400x400/4ECDC4/FFFFFF?text=Generated+${i + 1}`,
              quality: Math.floor(Math.random() * 2) + 4,
              approved: false,
              timestamp: new Date().toLocaleString(),
              type: this.activeImageType
            })
          }
          this.generatedImages = mockImages
          const typeIndex = this.imageTypes.findIndex(type => type.id === this.activeImageType)
          if (typeIndex > -1) this.imageTypes[typeIndex].generatedCount += mockImages.length
        }

        this.generationHistory.unshift({
          timestamp: new Date().toLocaleString(),
          configSummary: `${this.generationConfig.style} 风格，${this.generationConfig.imageCount} 张图片，${this.generationConfig.isTextGraphic ? '允许文字' : '禁止文字'}`,
          config: { ...this.generationConfig }
        })
        this.$message.success('图片生成完成！')
      } catch (error) {
        console.error('❌ 生成失败:', error)
        this.$message.error('生成失败，请稍后重试')
      } finally {
        this.generating = false
      }
    },
    
    resetConfig() {
      this.generationConfig = {
        selectedProduct: '',
        style: 'photorealistic',
        negativePrompt: '模糊, 低像素, 怪异的肢体, 文字, 水印',
        imageCount: 2,
        imageSize: '1024x1024',
        userPrompt: '',
        isTextGraphic: false
      }
    },
    
    previewImage(image) {
      this.previewImageData = image
      // 不再使用对话框，直接显示大图预览区域
    },
    
    closePreview() {
      this.previewImageData = null
    },
    
    downloadImage(image) {
      // 下载生成的图片
      if (image && image.url) {
        const link = document.createElement('a')
        link.href = image.url
        link.download = `${this.getImageTypeLabel(image.type)}_${image.id || Date.now()}.png`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        this.$message.success('图片下载完成')
      } else {
        this.$message.error('图片下载失败')
      }
    },
    
    approveImage(image) {
      image.approved = true
      this.$message.success('图片已标记为采用')
    },
    
    showRegenerateDialog(image) {
      this.regenerateImageData = image
      this.regenerateForm = {
        promptModifications: '',
        model: image.model || 'qwen-plus',
        referenceImages: [
          {
            id: image.id,
            name: image.filename || `prev-${image.id}`,
            url: image.url,
            serverUrl: image.url,
            purpose: 'style',
            description: 'Previous generation - optional reference (you may remove)'
          }
        ]
      }
      this.regenerateVisible = true
    },
    
    async handleRegenerate() {
      if (!this.regenerateImageData) {
        this.$message.error('没有选择要重新生成的图片')
        return
      }
      
      this.regenerating = true
      
      try {
        const params = {
          originalImageId: this.regenerateImageData.id,
          promptModifications: this.regenerateForm.promptModifications,
          referenceImages: this.regenerateForm.referenceImages,
          model: this.regenerateForm.model
        }
        
        const result = await AIGCService.regenerateImage(params)
        
        this.$message.success('重新生成任务已开始')
        this.regenerateVisible = false
        
        // 轮询任务状态
        this.pollRegenerateTask(result.task_id)
        
      } catch (error) {
        console.error('重新生成失败:', error)
        this.$message.error('重新生成失败: ' + error.message)
      } finally {
        this.regenerating = false
      }
    },
    
    async pollRegenerateTask(taskId) {
      try {
        const result = await AIGCService.pollTaskStatus(taskId, (status) => {
          // 进度回调
          if (status.progress !== undefined) {
            this.$message.info(`重新生成进度: ${status.progress}%`)
          }
        })
        
        if (result.status === 'completed' && result.images.length > 0) {
          // 添加新生成的图片到列表
          const newImage = result.images[0]
          this.generatedImages.unshift(newImage)
          this.$message.success('图片重新生成完成!')
        } else {
          this.$message.warning('重新生成完成，但没有生成新图片')
        }
      } catch (error) {
        console.error('轮询重新生成任务失败:', error)
        this.$message.error('重新生成任务失败: ' + error.message)
      }
    },
    
    regenerateFromImage(image) {
      this.showRegenerateDialog(image)
    },
    
    regenerateAll() {
      this.generateImages()
    },
    
    downloadAll() {
      this.generatedImages.forEach(image => {
        this.downloadImage(image)
      })
    },
    
    loadHistoryConfig(history) {
      this.generationConfig = { ...history.config }
      this.$message.success('配置已加载')
    },
    
    // 辅助方法
    getImageTypeLabel(type) {
      const imageTypeMap = {
        'main': '产品主图',
        'infographic': '信息图',
        'lifestyle': '生活方式图',
        'size': '尺寸图',
        'detail': '产品细节图',
        'angle': '多角度图',
        'instruction': '使用说明图',
        'comparison': '对比图',
        'packaging': '包装图'
      }
      return imageTypeMap[type] || type || '未知类型'
    },
    
    formatTime(timeString) {
      if (!timeString) return '未知时间'
      try {
        const date = new Date(timeString)
        return date.toLocaleString('zh-CN')
      } catch (error) {
        return timeString
      }
    }
  },
  
  computed: {
    availableModels() {
      return config.generation.availableModels || [
        { value: 'qwen-plus', label: '☁️ Qwen Plus' },
        { value: 'qwen-vl-plus', label: '👁️ Qwen VL Plus' },
        { value: 'seedream-4', label: '✨ SeeDream 4.0' },
        { value: 'flux-kontext', label: '🎨 Flux Kontext' }
      ]
    }
  }
}
</script>

<style scoped>
.generation-workbench {
  height: calc(100vh - 84px);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  margin: 0;
}

.page-title .el-icon {
  margin-right: 8px;
  color: #409eff;
}

.task-info {
  color: #606266;
  margin: 4px 0 0 0;
  font-size: 14px;
}

.workbench-container {
  height: calc(100% - 60px);
}

/* 左侧边栏样式 */
.sidebar {
  background: white;
  border-radius: 8px;
  margin-right: 16px;
  overflow: hidden;
}

.sidebar-title {
  padding: 20px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  border-bottom: 1px solid #ebeef5;
  background: #f8f9fa;
}

.image-type-menu {
  border: none;
}

.menu-item {
  height: auto !important;
  padding: 16px 20px !important;
  border-bottom: 1px solid #f0f0f0;
}

.menu-item-content {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  margin-left: 12px;
  position: relative;
}

.menu-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.menu-description {
  font-size: 12px;
  color: #909399;
}

.generated-badge {
  position: absolute;
  top: 0;
  right: -10px;
}

.progress-section {
  padding: 20px;
  border-top: 1px solid #ebeef5;
}

.progress-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 12px;
}

.progress-text {
  font-size: 12px;
  color: #606266;
  margin: 8px 0 0 0;
  text-align: center;
}

/* 主工作区样式 */
.main-area {
  background: white;
  border-radius: 8px;
  padding: 24px;
  overflow-y: auto;
}

.panel-header {
  margin-bottom: 24px;
}

.panel-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  margin: 0 0 8px 0;
}

.panel-title .el-icon {
  margin-right: 8px;
  color: #409eff;
}

.panel-description {
  color: #606266;
  line-height: 1.6;
  margin: 0;
}

.config-form {
  margin-bottom: 24px;
}

.config-section {
  margin-bottom: 20px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
}

.prompt-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.generation-actions {
  display: flex;
  gap: 16px;
  align-items: center;
  justify-content: center;
  margin: 24px 0;
}

.text-graphic-toggle {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.toggle-label {
  color: #ffffff;
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
}

.debug-text {
  color: #cccccc;
  font-size: 12px;
  white-space: nowrap;
}

/* 确保el-switch可见 */
:deep(.el-switch) {
  min-width: 60px;
}

:deep(.el-switch__label) {
  color: #ffffff !important;
}

.generate-btn {
  padding: 12px 32px;
  font-size: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

/* 结果展示样式 */
.results-section {
  margin-top: 32px;
}

.images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
  margin: 16px 0;
}

.image-card {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
}

.image-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.image-container {
  position: relative;
  aspect-ratio: 1;
  cursor: pointer;
}

.image-container img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
}

.image-container:hover .image-overlay {
  opacity: 1;
}

.image-info {
  padding: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.image-quality {
  display: flex;
  align-items: center;
  font-size: 12px;
}

.image-quality span {
  margin-right: 8px;
  color: #606266;
}

.batch-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 16px;
}

/* 历史记录样式 */
.history-section {
  margin-top: 24px;
}

.history-list {
  max-height: 200px;
  overflow-y: auto;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.history-info {
  display: flex;
  flex-direction: column;
}

.history-time {
  font-size: 12px;
  color: #909399;
}

.history-config {
  font-size: 14px;
  color: #303133;
  margin-top: 2px;
}

/* 空状态样式 */
.empty-panel {
  text-align: center;
  padding: 80px 20px;
  color: #909399;
}

.empty-icon {
  font-size: 80px;
  color: #dcdfe6;
  margin-bottom: 20px;
}

.empty-panel h3 {
  color: #606266;
  margin-bottom: 12px;
}

.empty-panel p {
  margin: 0;
}

/* 图片预览对话框样式 */
:deep(.image-preview-dialog) {
  .el-dialog {
    max-width: 95vw;
    max-height: 90vh;
    margin: 5vh auto;
    display: flex;
    flex-direction: column;
  }
  
  .el-dialog__body {
    padding: 20px;
    flex: 1;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }
  
  .el-dialog__header {
    padding: 20px 20px 10px;
    flex-shrink: 0;
  }
  
  .el-dialog__footer {
    padding: 10px 20px 20px;
    flex-shrink: 0;
  }
}

.image-preview-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  height: 100%;
  min-height: 500px;
}

.preview-image-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  flex: 1;
  min-height: 400px;
  max-height: calc(70vh - 150px);
  background: #f5f5f5;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.preview-image {
  max-width: 100%;
  max-height: 100%;
  width: auto;
  height: auto;
  object-fit: contain;
  display: block;
  margin: auto;
}

.image-info {
  background: var(--dark-bg-tertiary);
  padding: 15px;
  border-radius: 8px;
  min-width: 300px;
  text-align: left;
}

:deep(.light-theme) .image-info {
  background: var(--light-bg-secondary);
}

.image-info p {
  margin: 8px 0;
  color: var(--dark-text-primary);
}

:deep(.light-theme) .image-info p {
  color: var(--light-text-primary);
}

/* 重新生成对话框样式 */
.regenerate-form {
  max-height: 70vh;
  overflow-y: auto;
}

.original-image {
  text-align: center;
  margin-bottom: 20px;
}

.original-image h4 {
  margin-bottom: 15px;
  color: var(--dark-text-primary);
}

:deep(.light-theme) .original-image h4 {
  color: var(--light-text-primary);
}

.original-preview {
  max-width: 200px;
  max-height: 200px;
  object-fit: contain;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.image-details {
  margin-top: 10px;
  font-size: 14px;
  color: var(--dark-text-secondary);
  text-align: left;
}

:deep(.light-theme) .image-details {
  color: var(--light-text-secondary);
}

.regenerate-options h4 {
  margin-bottom: 20px;
  color: var(--dark-text-primary);
}

:deep(.light-theme) .regenerate-options h4 {
  color: var(--light-text-primary);
}

/* 大图预览样式 */
.image-large-preview {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--dark-bg-primary);
  z-index: 2000;
  display: flex;
  flex-direction: column;
}

:deep(.light-theme) .image-large-preview {
  background: var(--light-bg-primary);
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--dark-border);
  background: var(--dark-bg-secondary);
}

:deep(.light-theme) .preview-header {
  border-bottom-color: var(--light-border);
  background: var(--light-bg-secondary);
}

.preview-header h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  color: var(--dark-text-primary);
  font-size: 18px;
  font-weight: 500;
}

:deep(.light-theme) .preview-header h3 {
  color: var(--light-text-primary);
}

.preview-actions {
  display: flex;
  gap: 12px;
}

.preview-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.large-image-container {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 24px;
  background: var(--dark-bg-tertiary);
}

:deep(.light-theme) .large-image-container {
  background: var(--light-bg-tertiary);
}

.large-preview-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.preview-info-panel {
  width: 350px;
  background: var(--dark-bg-secondary);
  border-left: 1px solid var(--dark-border);
  padding: 24px;
  overflow-y: auto;
}

:deep(.light-theme) .preview-info-panel {
  background: var(--light-bg-secondary);
  border-left-color: var(--light-border);
}

.info-section {
  margin-bottom: 24px;
}

.info-section h4 {
  margin: 0 0 12px 0;
  color: var(--dark-text-primary);
  font-size: 14px;
  font-weight: 500;
}

:deep(.light-theme) .info-section h4 {
  color: var(--light-text-primary);
}

.info-item {
  display: flex;
  margin-bottom: 8px;
  align-items: flex-start;
}

.info-item .label {
  min-width: 80px;
  color: var(--dark-text-secondary);
  font-size: 13px;
}

:deep(.light-theme) .info-item .label {
  color: var(--light-text-secondary);
}

.info-item .value {
  color: var(--dark-text-primary);
  font-size: 13px;
  word-break: break-all;
}

:deep(.light-theme) .info-item .value {
  color: var(--light-text-primary);
}

.prompt-content {
  background: var(--dark-bg-tertiary);
  border: 1px solid var(--dark-border);
  border-radius: 6px;
  padding: 12px;
  color: var(--dark-text-primary);
  font-size: 12px;
  line-height: 1.4;
  max-height: 150px;
  overflow-y: auto;
}

:deep(.light-theme) .prompt-content {
  background: var(--light-bg-tertiary);
  border-color: var(--light-border);
  color: var(--light-text-primary);
}

.action-buttons {
  display: flex;
  flex-direction: column;
}
</style>
