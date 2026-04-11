<template>
  <div class="task-creation">
    <div class="page-header">
      <h1 class="page-title">
        <el-icon><Plus /></el-icon>
        创建新的图片生成任务
      </h1>
      <p class="page-description">输入产品信息，让AI为您生成专业的亚马逊Listing图片</p>
    </div>

    <el-form 
      ref="taskForm" 
      :model="formData" 
      :rules="rules" 
      label-width="140px"
      class="task-form"
    >
      <!-- 第一部分：产品基础信息 -->
      <el-card class="form-section">
        <div class="section-title">
          <el-icon><Box /></el-icon>
          产品基础信息
        </div>
        
        <el-form-item label="产品名称" prop="productTitle" required>
          <el-input 
            v-model="formData.productTitle"
            placeholder="例如：宠物狗狗磨牙玩具套装"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="核心卖点" prop="keySellingPoints">
          <div class="tags-input">
            <el-tag
              v-for="tag in formData.keySellingPoints"
              :key="tag"
              closable
              @close="removeTag(tag)"
              class="selling-point-tag"
            >
              {{ tag }}
            </el-tag>
            <el-input
              v-if="tagInputVisible"
              ref="tagInput"
              v-model="newTag"
              size="small"
              @keyup.enter="addTag"
              @blur="addTag"
              class="tag-input"
            />
            <el-button 
              v-else 
              size="small" 
              @click="showTagInput"
              class="add-tag-btn"
            >
              <el-icon><Plus /></el-icon>
              添加卖点
            </el-button>
          </div>
          <div class="form-tip">
            添加产品的核心卖点，如"耐咬"、"天然橡胶"、"食品级安全"等
          </div>
        </el-form-item>

        <el-form-item label="目标市场" prop="targetMarket" required>
          <el-select 
            v-model="formData.targetMarket" 
            placeholder="选择目标市场"
            style="width: 100%"
          >
            <el-option label="美国" value="US" />
            <el-option label="英国" value="UK" />
            <el-option label="德国" value="DE" />
            <el-option label="日本" value="JP" />
            <el-option label="印度" value="IN" />
          </el-select>
        </el-form-item>
      </el-card>

      <!-- 第二部分：产品图片上传 -->
      <el-card class="form-section">
        <div class="section-title">
          <el-icon><Picture /></el-icon>
          原始产品图片
        </div>

        <el-form-item label="上传模式">
          <el-radio-group v-model="formData.uploadMode">
            <el-radio label="single">单张组合图</el-radio>
            <el-radio label="multiple">多张独立图（推荐）</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 单张组合图模式 -->
        <div v-if="formData.uploadMode === 'single'">
          <el-form-item label="组合产品图">
            <el-upload
              :file-list="formData.singleImage"
              :before-upload="beforeImageUpload"
              list-type="picture-card"
              :limit="1"
              accept="image/*"
              class="image-uploader"
              :auto-upload="false"
            >
              <el-icon><Plus /></el-icon>
            </el-upload>
          </el-form-item>
          
          <el-form-item label="图片说明">
            <el-input
              v-model="formData.singleImageDescription"
              type="textarea"
              :rows="3"
              placeholder="描述这张图片中包含的产品，例如：这是一套宠物玩具，包含一个蓝色骨头，一个黄色球和一个红色飞盘。"
            />
          </el-form-item>
        </div>

        <!-- 多张独立图模式 -->
        <div v-if="formData.uploadMode === 'multiple'">
          <el-form-item label="产品图片">
            <div class="multiple-images">
              <div 
                v-for="(image, index) in formData.multipleImages" 
                :key="index"
                class="image-item"
              >
                <el-upload
                  :file-list="image.file ? [image.file] : []"
                  :before-upload="(file) => handleFileSelect(file, index)"
                  list-type="picture-card"
                  :limit="1"
                  accept="image/*"
                  class="image-uploader"
                  :auto-upload="false"
                >
                  <el-icon><Plus /></el-icon>
                </el-upload>
                <el-input
                  v-model="image.description"
                  placeholder="描述这个产品"
                  class="image-description"
                />
                <el-button 
                  type="danger" 
                  size="small" 
                  @click="removeImage(index)"
                  class="remove-image-btn"
                >
                  删除
                </el-button>
              </div>
              <el-button 
                type="dashed" 
                @click="addImageSlot"
                class="add-image-btn"
              >
                <el-icon><Plus /></el-icon>
                添加产品图片
              </el-button>
            </div>
          </el-form-item>
        </div>
      </el-card>

      <!-- 第三部分：竞品信息（可选） -->
      <el-card class="form-section">
        <div class="section-title">
          <el-icon><Search /></el-icon>
          竞品信息分析（可选但推荐）
        </div>
        
        <el-form-item label="竞品链接">
          <div class="competitor-links">
            <div 
              v-for="(link, index) in formData.competitorLinks" 
              :key="index"
              class="link-item"
            >
              <el-input
                v-model="link.url"
                placeholder="粘贴亚马逊竞品链接"
                class="link-input"
              />
              <el-button 
                type="primary" 
                @click="analyzeCompetitor(index)"
                :loading="link.analyzing"
                class="analyze-btn"
              >
                分析
              </el-button>
              <el-button 
                type="danger" 
                @click="removeCompetitorLink(index)"
                class="remove-btn"
              >
                删除
              </el-button>
            </div>
            <el-button 
              v-if="formData.competitorLinks.length < 3"
              type="dashed" 
              @click="addCompetitorLink"
              class="add-link-btn"
            >
              <el-icon><Plus /></el-icon>
              添加竞品链接
            </el-button>
          </div>
        </el-form-item>

        <!-- 竞品分析结果展示 -->
        <div v-if="competitorAnalysis.length > 0" class="competitor-analysis">
          <div class="analysis-title">竞品分析结果</div>
          <div 
            v-for="(analysis, index) in competitorAnalysis" 
            :key="index"
            class="analysis-item"
          >
            <h4>{{ analysis.title }}</h4>
            <div class="analysis-content">
              <div class="analysis-images">
                <img 
                  v-for="(img, imgIndex) in analysis.images" 
                  :key="imgIndex"
                  :src="img" 
                  class="competitor-image"
                  @click="previewImage(img)"
                />
              </div>
              <div class="analysis-text">
                <p><strong>五点描述：</strong></p>
                <ul>
                  <li v-for="(point, pointIndex) in analysis.bulletPoints" :key="pointIndex">
                    {{ point }}
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 表单操作按钮 -->
      <div class="form-actions">
        <el-button @click="saveDraft" :loading="saving">
          <el-icon><Document /></el-icon>
          保存草稿
        </el-button>
        <el-button 
          type="primary" 
          @click="startGeneration" 
          :loading="submitting"
          size="large"
        >
          <el-icon><Magic /></el-icon>
          开始生成图片
        </el-button>
      </div>
    </el-form>

    <!-- 图片预览对话框 -->
    <el-dialog v-model="imagePreviewVisible" width="600px" title="图片预览">
      <img :src="previewImageUrl" style="width: 100%" />
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'TaskCreation',
  data() {
    return {
      formData: {
        productTitle: '',
        keySellingPoints: [],
        targetMarket: '',
        uploadMode: 'multiple',
        singleImage: [],
        singleImageDescription: '',
        multipleImages: [
          { file: null, description: '' }
        ],
        competitorLinks: [
          { url: '', analyzing: false }
        ]
      },
      rules: {
        productTitle: [
          { required: true, message: '请输入产品名称', trigger: 'blur' }
        ],
        targetMarket: [
          { required: true, message: '请选择目标市场', trigger: 'change' }
        ]
      },
      tagInputVisible: false,
      newTag: '',
      competitorAnalysis: [],
      imagePreviewVisible: false,
      previewImageUrl: '',
      saving: false,
      submitting: false
    }
  },
  methods: {
    // 标签管理
    showTagInput() {
      this.tagInputVisible = true
      this.$nextTick(() => {
        if (this.$refs.tagInput && this.$refs.tagInput.$refs.input) {
          this.$refs.tagInput.$refs.input.focus()
        }
      })
    },
    addTag() {
      if (this.newTag && this.newTag.trim() && !this.formData.keySellingPoints.includes(this.newTag.trim())) {
        this.formData.keySellingPoints.push(this.newTag.trim())
      }
      this.tagInputVisible = false
      this.newTag = ''
    },
    removeTag(tag) {
      const index = this.formData.keySellingPoints.indexOf(tag)
      if (index > -1) {
        this.formData.keySellingPoints.splice(index, 1)
      }
    },

    // 图片上传
    beforeImageUpload(file) {
      const isImage = file.type.startsWith('image/')
      const isLt10M = file.size / 1024 / 1024 < 10

      if (!isImage) {
        this.$message.error('只能上传图片文件!')
        return false
      }
      if (!isLt10M) {
        this.$message.error('图片大小不能超过 10MB!')
        return false
      }
      return false // 阻止自动上传
    },
    handleFileSelect(file, index) {
      const isImage = file.type.startsWith('image/')
      const isLt10M = file.size / 1024 / 1024 < 10

      if (!isImage) {
        this.$message.error('只能上传图片文件!')
        return false
      }
      if (!isLt10M) {
        this.$message.error('图片大小不能超过 10MB!')
        return false
      }
      
      this.formData.multipleImages[index].file = {
        name: file.name,
        url: URL.createObjectURL(file),
        raw: file
      }
      return false
    },
    addImageSlot() {
      this.formData.multipleImages.push({ file: null, description: '' })
    },
    removeImage(index) {
      this.formData.multipleImages.splice(index, 1)
    },

    // 竞品分析
    addCompetitorLink() {
      this.formData.competitorLinks.push({ url: '', analyzing: false })
    },
    removeCompetitorLink(index) {
      this.formData.competitorLinks.splice(index, 1)
    },
    async analyzeCompetitor(index) {
      const link = this.formData.competitorLinks[index]
      if (!link.url) {
        this.$message.warning('请先输入竞品链接')
        return
      }

      link.analyzing = true
      
      // 模拟API调用
      try {
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        // 模拟分析结果
        const mockAnalysis = {
          title: '宠物智能玩具球 - 竞品A',
          images: [
            'https://via.placeholder.com/200x200/FF6B6B/FFFFFF?text=Main',
            'https://via.placeholder.com/200x200/4ECDC4/FFFFFF?text=Detail',
            'https://via.placeholder.com/200x200/45B7D1/FFFFFF?text=Scene'
          ],
          bulletPoints: [
            '智能感应，自动滚动吸引宠物注意',
            '食品级硅胶材质，安全无毒可啃咬',
            'USB充电设计，续航时间长达8小时',
            '多种模式切换，满足不同游戏需求',
            '防水设计，室内外都可使用'
          ]
        }
        
        this.competitorAnalysis.push(mockAnalysis)
        this.$message.success('竞品分析完成')
      } catch (error) {
        this.$message.error('分析失败，请稍后重试')
      } finally {
        link.analyzing = false
      }
    },

    // 图片预览
    previewImage(url) {
      this.previewImageUrl = url
      this.imagePreviewVisible = true
    },

    // 表单操作
    async saveDraft() {
      this.saving = true
      try {
        await new Promise(resolve => setTimeout(resolve, 1000))
        this.$message.success('草稿已保存')
      } catch (error) {
        this.$message.error('保存失败')
      } finally {
        this.saving = false
      }
    },
    async startGeneration() {
      this.$refs.taskForm.validate(async (valid) => {
        if (valid) {
          this.submitting = true
          try {
            await new Promise(resolve => setTimeout(resolve, 1500))
            
            // 生成任务ID并跳转到工作台
            const taskId = 'T' + Date.now().toString().slice(-6)
            this.$message.success('任务创建成功，正在跳转到生成工作台...')
            
            setTimeout(() => {
              this.$router.push(`/workbench/${taskId}`)
            }, 1000)
          } catch (error) {
            this.$message.error('创建任务失败')
          } finally {
            this.submitting = false
          }
        } else {
          this.$message.error('请完善必填信息')
        }
      })
    }
  }
}
</script>

<style scoped>
.task-creation {
  max-width: 800px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.page-title .el-icon {
  margin-right: 12px;
  color: #409eff;
}

.page-description {
  color: #606266;
  font-size: 14px;
}

.form-section {
  margin-bottom: 24px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

/* 标签输入样式 */
.tags-input {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.selling-point-tag {
  background: linear-gradient(45deg, #667eea, #764ba2);
  color: white;
  border: none;
}

.tag-input {
  width: 120px;
}

.add-tag-btn {
  border-style: dashed;
}

/* 图片上传样式 */
.multiple-images {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.image-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
  border: 1px dashed #dcdfe6;
  border-radius: 8px;
}

.image-description {
  flex: 1;
}

.remove-image-btn {
  margin-top: 4px;
}

.add-image-btn {
  width: 100%;
  height: 60px;
  border-style: dashed;
}

/* 竞品分析样式 */
.competitor-links {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.link-item {
  display: flex;
  gap: 12px;
  align-items: center;
}

.link-input {
  flex: 1;
}

.add-link-btn {
  width: 100%;
  height: 40px;
  border-style: dashed;
}

.competitor-analysis {
  margin-top: 24px;
}

.analysis-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
}

.analysis-item {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.analysis-item h4 {
  color: #409eff;
  margin-bottom: 12px;
}

.analysis-content {
  display: flex;
  gap: 20px;
}

.analysis-images {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.competitor-image {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 4px;
  cursor: pointer;
  transition: transform 0.2s;
}

.competitor-image:hover {
  transform: scale(1.05);
}

.analysis-text {
  flex: 1;
}

.analysis-text ul {
  padding-left: 20px;
  margin-top: 8px;
}

.analysis-text li {
  margin-bottom: 4px;
  line-height: 1.5;
}

/* 表单操作按钮 */
.form-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 32px;
  padding: 24px;
  background: #fafafa;
  border-radius: 8px;
}
</style>
