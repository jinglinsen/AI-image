<template>
  <div class="history-panel">
    <div class="history-header">
      <h3>
        <el-icon><Clock /></el-icon>
        生成历史
      </h3>
      <div class="history-actions">
        <el-button size="small" @click="refreshHistory">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button size="small" @click="clearAllHistory" type="danger" plain>
          <el-icon><Delete /></el-icon>
          清空
        </el-button>
      </div>
    </div>

    <div class="history-filters">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索历史记录..."
        size="small"
        clearable
        @input="handleSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
    </div>

    <div class="history-content" v-loading="loading">
      <div v-if="historyList.length === 0 && !loading" class="empty-history">
        <el-icon class="empty-icon"><DocumentCopy /></el-icon>
        <p>暂无生成历史</p>
        <p class="empty-tip">开始创建图片后，历史记录将显示在这里</p>
      </div>

      <div v-else class="history-list">
        <div 
          v-for="history in displayHistoryList" 
          :key="history.id" 
          class="history-item"
          :class="{ active: selectedHistory?.id === history.id }"
          @click="selectHistory(history)"
        >
          <div class="history-preview">
            <div v-if="history.generated_images?.length > 0" class="preview-images">
              <img 
                v-for="(image, index) in history.generated_images.slice(0, 4)" 
                :key="index"
                :src="getImageUrl(image)"
                class="preview-image"
                :style="{ zIndex: 4 - index }"
              />
            </div>
            <div v-else class="no-images">
              <el-icon><Picture /></el-icon>
            </div>
          </div>

          <div class="history-info">
            <div class="history-title">
              <span class="product-form">{{ history.product_form || '未知产品' }}</span>
              <el-tag v-if="history.is_favorite" type="warning" size="small">
                <el-icon><Star /></el-icon>
              </el-tag>
            </div>
            
            <div class="history-meta">
              <span class="image-types">
                {{ formatImageTypes(history.selected_image_types) }}
              </span>
              <span class="generation-count">
                {{ history.success_count || 0 }}/{{ history.generated_image_count || 0 }} 张
              </span>
            </div>

            <div class="history-time">
              {{ formatTime(history.created_at) }}
            </div>

            <div class="history-prompt" v-if="history.main_prompt">
              "{{ truncateText(history.main_prompt, 50) }}"
            </div>
          </div>

          <div class="history-actions">
            <el-dropdown @command="handleHistoryAction" trigger="click">
              <el-button size="small" text>
                <el-icon><MoreFilled /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item :command="{ action: 'load', history }">
                    <el-icon><Upload /></el-icon>
                    加载配置
                  </el-dropdown-item>
                  <el-dropdown-item :command="{ action: 'favorite', history }">
                    <el-icon><Star /></el-icon>
                    {{ history.is_favorite ? '取消收藏' : '收藏' }}
                  </el-dropdown-item>
                  <el-dropdown-item :command="{ action: 'delete', history }" divided>
                    <el-icon><Delete /></el-icon>
                    删除
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div v-if="pagination.total > 0" class="history-pagination">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="pagination.total"
          layout="prev, pager, next"
          small
          @current-change="handlePageChange"
        />
      </div>
    </div>

    <!-- 历史记录详情对话框 -->
    <el-dialog 
      v-model="detailVisible" 
      title="历史记录详情" 
      width="800px"
      class="history-detail-dialog"
    >
      <div v-if="selectedHistory" class="history-detail">
        <div class="detail-section">
          <h4>基本信息</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="产品形态">
              {{ selectedHistory.product_form || '未设置' }}
            </el-descriptions-item>
            <el-descriptions-item label="生成模型">
              {{ selectedHistory.selected_model || 'qwen-plus' }}
            </el-descriptions-item>
            <el-descriptions-item label="图片尺寸">
              {{ selectedHistory.selected_size || '1024x1024' }}
            </el-descriptions-item>
            <el-descriptions-item label="图片比例">
              {{ selectedHistory.selected_ratio || '1:1' }}
            </el-descriptions-item>
            <el-descriptions-item label="生成时间">
              {{ formatTime(selectedHistory.created_at) }}
            </el-descriptions-item>
            <el-descriptions-item label="耗时">
              {{ selectedHistory.generation_time ? `${selectedHistory.generation_time.toFixed(2)}秒` : '未知' }}
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="detail-section" v-if="selectedHistory.main_prompt">
          <h4>主提示词</h4>
          <div class="prompt-content">{{ selectedHistory.main_prompt }}</div>
        </div>

        <div class="detail-section" v-if="selectedHistory.selected_image_types?.length > 0">
          <h4>选择的图片类型</h4>
          <div class="image-types-list">
            <el-tag 
              v-for="type in selectedHistory.selected_image_types" 
              :key="type" 
              class="type-tag"
            >
              {{ getImageTypeLabel(type) }}
            </el-tag>
          </div>
        </div>

        <div class="detail-section" v-if="selectedHistory.generated_images?.length > 0">
          <h4>生成的图片 ({{ selectedHistory.generated_images.length }}张)</h4>
          <div class="generated-images-grid">
            <div 
              v-for="image in selectedHistory.generated_images" 
              :key="image.id"
              class="generated-image-item"
              @click="previewImage(image)"
            >
              <img :src="getImageUrl(image)" :alt="getImageTypeLabel(image.image_type)" />
              <div class="image-overlay">
                <span class="image-type">{{ getImageTypeLabel(image.image_type) }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <h4>用户评价</h4>
          <div class="user-evaluation">
            <div class="rating-section">
              <span>评分：</span>
              <el-rate 
                v-model="selectedHistory.user_rating" 
                @change="updateHistoryRating"
                allow-half
              />
            </div>
            <div class="notes-section">
              <span>备注：</span>
              <el-input
                v-model="historyNotes"
                type="textarea"
                :rows="3"
                placeholder="添加备注..."
                @blur="updateHistoryNotes"
              />
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button type="primary" @click="loadHistoryConfig(selectedHistory)">
          加载配置
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import AIGCService from '../services/aigcService.js'
import config from '../config/index.js'

export default {
  name: 'HistoryPanel',
  props: {
    sessionId: {
      type: String,
      default: () => Date.now().toString()
    }
  },
  emits: ['load-config', 'preview-image'],
  data() {
    return {
      loading: false,
      historyList: [],
      selectedHistory: null,
      detailVisible: false,
      searchKeyword: '',
      currentPage: 1,
      pageSize: 10,
      pagination: {
        total: 0,
        pages: 0,
        has_prev: false,
        has_next: false
      },
      historyNotes: ''
    }
  },
  computed: {
    displayHistoryList() {
      if (!this.searchKeyword) {
        return this.historyList
      }
      
      const keyword = this.searchKeyword.toLowerCase()
      return this.historyList.filter(history => 
        (history.product_form && history.product_form.toLowerCase().includes(keyword)) ||
        (history.main_prompt && history.main_prompt.toLowerCase().includes(keyword)) ||
        (history.user_notes && history.user_notes.toLowerCase().includes(keyword))
      )
    }
  },
  mounted() {
    this.loadHistory()
  },
  methods: {
    async loadHistory() {
      this.loading = true
      try {
        const result = await AIGCService.getGenerationHistory({
          page: this.currentPage,
          perPage: this.pageSize,
          sessionId: this.sessionId
        })
        
        this.historyList = result.history || []
        this.pagination = result.pagination || {}
      } catch (error) {
        console.error('加载历史记录失败:', error)
        this.$message.error('加载历史记录失败: ' + error.message)
      } finally {
        this.loading = false
      }
    },

    async refreshHistory() {
      this.currentPage = 1
      await this.loadHistory()
      this.$message.success('历史记录已刷新')
    },

    async clearAllHistory() {
      const confirmResult = await this.$confirm(
        '确定要清空所有历史记录吗？此操作不可恢复！',
        '清空历史记录',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )

      if (confirmResult) {
        try {
          // 删除所有历史记录
          for (const history of this.historyList) {
            await AIGCService.deleteHistory(history.id)
          }
          
          this.historyList = []
          this.pagination = { total: 0, pages: 0 }
          this.selectedHistory = null
          this.$message.success('历史记录已清空')
        } catch (error) {
          console.error('清空历史记录失败:', error)
          this.$message.error('清空历史记录失败: ' + error.message)
        }
      }
    },

    handleSearch() {
      // 搜索是实时的，由计算属性处理
    },

    handlePageChange(page) {
      this.currentPage = page
      this.loadHistory()
    },

    selectHistory(history) {
      this.selectedHistory = history
      this.historyNotes = history.user_notes || ''
      this.detailVisible = true
    },

    async handleHistoryAction({ action, history }) {
      switch (action) {
        case 'load':
          this.loadHistoryConfig(history)
          break
        case 'favorite':
          await this.toggleFavorite(history)
          break
        case 'delete':
          await this.deleteHistory(history)
          break
      }
    },

    loadHistoryConfig(history) {
      if (!history) return
      
      const config = {
        productForm: history.product_form,
        selectedImageTypes: history.selected_image_types,
        mainPrompt: history.main_prompt,
        productImages: history.product_images,
        referenceImagesByType: history.reference_images_by_type,
        competitors: history.competitors,
        selectedSize: history.selected_size,
        selectedRatio: history.selected_ratio,
        selectedModel: history.selected_model
      }
      
      this.$emit('load-config', config)
      this.detailVisible = false
      this.$message.success('配置已加载')
    },

    async toggleFavorite(history) {
      try {
        const updateData = {
          isFavorite: !history.is_favorite
        }
        
        await AIGCService.updateHistory(history.id, updateData)
        
        // 更新本地数据
        history.is_favorite = !history.is_favorite
        if (this.selectedHistory?.id === history.id) {
          this.selectedHistory.is_favorite = history.is_favorite
        }
        
        this.$message.success(history.is_favorite ? '已收藏' : '已取消收藏')
      } catch (error) {
        console.error('更新收藏状态失败:', error)
        this.$message.error('操作失败: ' + error.message)
      }
    },

    async deleteHistory(history) {
      const confirmResult = await this.$confirm(
        '确定要删除这条历史记录吗？',
        '删除确认',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )

      if (confirmResult) {
        try {
          await AIGCService.deleteHistory(history.id)
          
          // 从列表中移除
          const index = this.historyList.findIndex(h => h.id === history.id)
          if (index > -1) {
            this.historyList.splice(index, 1)
          }
          
          // 如果删除的是当前选中的历史记录，关闭详情对话框
          if (this.selectedHistory?.id === history.id) {
            this.selectedHistory = null
            this.detailVisible = false
          }
          
          this.$message.success('历史记录已删除')
        } catch (error) {
          console.error('删除历史记录失败:', error)
          this.$message.error('删除失败: ' + error.message)
        }
      }
    },

    async updateHistoryRating(rating) {
      if (!this.selectedHistory) return
      
      try {
        await AIGCService.updateHistory(this.selectedHistory.id, {
          userRating: rating
        })
        
        // 更新本地数据
        const historyIndex = this.historyList.findIndex(h => h.id === this.selectedHistory.id)
        if (historyIndex > -1) {
          this.historyList[historyIndex].user_rating = rating
        }
        
      } catch (error) {
        console.error('更新评分失败:', error)
        this.$message.error('更新评分失败')
      }
    },

    async updateHistoryNotes() {
      if (!this.selectedHistory) return
      
      try {
        await AIGCService.updateHistory(this.selectedHistory.id, {
          userNotes: this.historyNotes
        })
        
        // 更新本地数据
        this.selectedHistory.user_notes = this.historyNotes
        const historyIndex = this.historyList.findIndex(h => h.id === this.selectedHistory.id)
        if (historyIndex > -1) {
          this.historyList[historyIndex].user_notes = this.historyNotes
        }
        
      } catch (error) {
        console.error('更新备注失败:', error)
        this.$message.error('更新备注失败')
      }
    },

    previewImage(image) {
      this.$emit('preview-image', image)
    },

    getImageUrl(image) {
      if (!image) return ''
      return AIGCService.getImageUrl(image.url || `/api/image/${image.filename}`)
    },

    formatImageTypes(types) {
      if (!types || types.length === 0) return '无'
      
      const typeMap = config.generation.supportedImageTypes.reduce((map, type) => {
        map[type.key] = type.label
        return map
      }, {})
      
      return types.map(type => typeMap[type] || type).join(', ')
    },

    getImageTypeLabel(type) {
      const typeMap = {
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
      return typeMap[type] || type || '未知类型'
    },

    formatTime(timeString) {
      if (!timeString) return '未知时间'
      try {
        const date = new Date(timeString)
        const now = new Date()
        const diff = now - date
        
        if (diff < 60000) { // 1分钟内
          return '刚刚'
        } else if (diff < 3600000) { // 1小时内
          return `${Math.floor(diff / 60000)}分钟前`
        } else if (diff < 86400000) { // 1天内
          return `${Math.floor(diff / 3600000)}小时前`
        } else {
          return date.toLocaleDateString('zh-CN')
        }
      } catch (error) {
        return timeString
      }
    },

    truncateText(text, maxLength) {
      if (!text) return ''
      if (text.length <= maxLength) return text
      return text.substring(0, maxLength) + '...'
    }
  }
}
</script>

<style scoped>
.history-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--dark-bg-secondary);
  border-radius: 8px;
  overflow: hidden;
}

:deep(.light-theme) .history-panel {
  background: var(--light-bg-secondary);
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--dark-border);
  background: var(--dark-bg-primary);
}

:deep(.light-theme) .history-header {
  border-bottom-color: var(--light-border);
  background: var(--light-bg-primary);
}

.history-header h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  color: var(--dark-text-primary);
  font-size: 16px;
}

:deep(.light-theme) .history-header h3 {
  color: var(--light-text-primary);
}

.history-actions {
  display: flex;
  gap: 8px;
}

.history-filters {
  padding: 16px 20px;
  border-bottom: 1px solid var(--dark-border);
}

:deep(.light-theme) .history-filters {
  border-bottom-color: var(--light-border);
}

.history-content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.empty-history {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: var(--dark-text-tertiary);
  padding: 40px 20px;
}

:deep(.light-theme) .empty-history {
  color: var(--light-text-tertiary);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  color: var(--dark-text-quaternary);
}

:deep(.light-theme) .empty-icon {
  color: var(--light-text-quaternary);
}

.empty-tip {
  font-size: 12px;
  margin-top: 8px;
}

.history-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.history-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 8px;
  border: 1px solid var(--dark-border);
  background: var(--dark-bg-tertiary);
  cursor: pointer;
  transition: all 0.2s;
}

:deep(.light-theme) .history-item {
  border-color: var(--light-border);
  background: var(--light-bg-primary);
}

.history-item:hover {
  border-color: var(--primary-color);
  transform: translateY(-1px);
}

.history-item.active {
  border-color: var(--primary-color);
  background: var(--primary-color-light);
}

.history-preview {
  width: 60px;
  height: 60px;
  flex-shrink: 0;
  border-radius: 6px;
  overflow: hidden;
  position: relative;
}

.preview-images {
  position: relative;
  width: 100%;
  height: 100%;
}

.preview-image {
  position: absolute;
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 4px;
  border: 1px solid var(--dark-border);
}

:deep(.light-theme) .preview-image {
  border-color: var(--light-border);
}

.preview-image:nth-child(2) {
  transform: translate(3px, 3px) scale(0.9);
}

.preview-image:nth-child(3) {
  transform: translate(6px, 6px) scale(0.8);
}

.preview-image:nth-child(4) {
  transform: translate(9px, 9px) scale(0.7);
}

.no-images {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  background: var(--dark-bg-quaternary);
  color: var(--dark-text-quaternary);
  border-radius: 4px;
}

:deep(.light-theme) .no-images {
  background: var(--light-bg-tertiary);
  color: var(--light-text-quaternary);
}

.history-info {
  flex: 1;
  min-width: 0;
}

.history-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.product-form {
  font-weight: 500;
  color: var(--dark-text-primary);
  font-size: 14px;
}

:deep(.light-theme) .product-form {
  color: var(--light-text-primary);
}

.history-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
  font-size: 12px;
  color: var(--dark-text-secondary);
}

:deep(.light-theme) .history-meta {
  color: var(--light-text-secondary);
}

.history-time {
  font-size: 11px;
  color: var(--dark-text-tertiary);
  margin-bottom: 4px;
}

:deep(.light-theme) .history-time {
  color: var(--light-text-tertiary);
}

.history-prompt {
  font-size: 11px;
  color: var(--dark-text-tertiary);
  font-style: italic;
  line-height: 1.3;
}

:deep(.light-theme) .history-prompt {
  color: var(--light-text-tertiary);
}

.history-actions {
  display: flex;
  align-items: flex-start;
  flex-shrink: 0;
}

.history-pagination {
  padding: 16px;
  border-top: 1px solid var(--dark-border);
  display: flex;
  justify-content: center;
}

:deep(.light-theme) .history-pagination {
  border-top-color: var(--light-border);
}

/* 历史记录详情对话框样式 */
:deep(.history-detail-dialog) {
  .el-dialog__body {
    max-height: 70vh;
    overflow-y: auto;
  }
}

.history-detail {
  padding: 0;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-section h4 {
  margin: 0 0 12px 0;
  color: var(--dark-text-primary);
  font-size: 14px;
  font-weight: 500;
}

:deep(.light-theme) .detail-section h4 {
  color: var(--light-text-primary);
}

.prompt-content {
  padding: 12px;
  background: var(--dark-bg-tertiary);
  border-radius: 6px;
  color: var(--dark-text-primary);
  line-height: 1.5;
  font-size: 13px;
}

:deep(.light-theme) .prompt-content {
  background: var(--light-bg-secondary);
  color: var(--light-text-primary);
}

.image-types-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.type-tag {
  margin: 0;
}

.generated-images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 12px;
}

.generated-image-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
  border: 1px solid var(--dark-border);
  transition: transform 0.2s;
}

:deep(.light-theme) .generated-image-item {
  border-color: var(--light-border);
}

.generated-image-item:hover {
  transform: scale(1.05);
}

.generated-image-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
  color: white;
  padding: 8px;
  font-size: 11px;
  text-align: center;
}

.user-evaluation {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.rating-section,
.notes-section {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.rating-section span,
.notes-section span {
  color: var(--dark-text-secondary);
  font-size: 14px;
  min-width: 60px;
  margin-top: 4px;
}

:deep(.light-theme) .rating-section span,
:deep(.light-theme) .notes-section span {
  color: var(--light-text-secondary);
}

.notes-section {
  align-items: flex-start;
}

.notes-section .el-input {
  flex: 1;
}
</style>
