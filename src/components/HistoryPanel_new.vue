<template>
  <div class="history-panel-new">
    <!-- 历史记录头部 -->
    <div class="history-header">
      <div class="search-box">
        <el-input
          v-model="searchQuery"
          placeholder="搜索历史记录..."
          clearable
          @input="debounceSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      <el-button size="small" @click="loadHistory" :loading="loading">
        <el-icon><Refresh /></el-icon>
      </el-button>
    </div>

    <!-- 历史记录列表 -->
    <div class="history-list" v-loading="loading">
      <el-empty v-if="!loading && historyList.length === 0" description="暂无历史记录" />
      
      <div
        v-for="item in historyList"
        :key="item.id"
        class="history-item"
        :class="{ active: selectedHistoryId === item.id, pinned: item.is_pinned }"
        @click="selectHistory(item)"
      >
        <!-- 置顶图标 -->
        <el-icon v-if="item.is_pinned" class="pin-icon"><Star /></el-icon>
        
        <!-- 历史记录内容 -->
        <div class="history-content">
          <div class="history-title-row">
            <span class="history-title">{{ item.title || '未命名任务' }}</span>
            
            <!-- 操作按钮 -->
            <el-dropdown trigger="click" @click.stop>
              <el-icon class="more-icon"><MoreFilled /></el-icon>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="togglePin(item)">
                    <el-icon><Star /></el-icon>
                    {{ item.is_pinned ? '取消置顶' : '置顶' }}
                  </el-dropdown-item>
                  <el-dropdown-item @click="renameHistory(item)">
                    <el-icon><Edit /></el-icon>
                    重命名
                  </el-dropdown-item>
                  <el-dropdown-item @click="deleteHistory(item)" divided>
                    <el-icon><Delete /></el-icon>
                    删除
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
          
          <div class="history-meta">
            <span>{{ formatDate(item.created_at) }}</span>
            <span v-if="item.generated_image_count">
              · {{ item.generated_image_count }}张图片
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载更多 -->
    <div class="load-more" v-if="hasMore && !loading">
      <el-button text @click="loadMore">
        加载更多
      </el-button>
    </div>

    <!-- 重命名对话框 -->
    <el-dialog
      v-model="renameDialogVisible"
      title="重命名历史记录"
      width="400px"
    >
      <el-input
        v-model="newTitle"
        placeholder="请输入新标题"
        maxlength="50"
        show-word-limit
      />
      <template #footer>
        <el-button @click="renameDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmRename">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Star, MoreFilled, Edit, Delete } from '@element-plus/icons-vue'
import AIGCService from '../services/aigcService'

export default {
  name: 'HistoryPanelNew',
  components: {
    Search,
    Refresh,
    Star,
    MoreFilled,
    Edit,
    Delete
  },
  emits: ['history-selected'],
  setup(props, { emit }) {
    const loading = ref(false)
    const searchQuery = ref('')
    const historyList = ref([])
    const selectedHistoryId = ref(null)
    const hasMore = ref(false)
    const currentPage = ref(1)
    const perPage = 20

    // 重命名相关
    const renameDialogVisible = ref(false)
    const renamingHistory = ref(null)
    const newTitle = ref('')

    // 加载历史记录
    const loadHistory = async (page = 1) => {
      loading.value = true
      try {
        const result = await AIGCService.getGenerationHistory({
          page,
          perPage,
          search: searchQuery.value
        })

        if (page === 1) {
          historyList.value = result.history
        } else {
          historyList.value.push(...result.history)
        }

        currentPage.value = page
        hasMore.value = result.pagination.page < result.pagination.pages
      } catch (error) {
        ElMessage.error('加载历史记录失败: ' + error.message)
      } finally {
        loading.value = false
      }
    }

    // 加载更多
    const loadMore = () => {
      loadHistory(currentPage.value + 1)
    }

    // 防抖搜索
    let searchTimeout = null
    const debounceSearch = () => {
      if (searchTimeout) clearTimeout(searchTimeout)
      searchTimeout = setTimeout(() => {
        loadHistory(1)
      }, 500)
    }

    // 选择历史记录
    const selectHistory = async (item) => {
      selectedHistoryId.value = item.id
      
      try {
        const result = await AIGCService.getHistoryDetail(item.id)
        emit('history-selected', result.history)
      } catch (error) {
        ElMessage.error('加载历史记录详情失败: ' + error.message)
      }
    }

    // 切换置顶
    const togglePin = async (item) => {
      try {
        await AIGCService.updateHistory(item.id, {
          isPinned: !item.is_pinned
        })
        
        ElMessage.success(item.is_pinned ? '已取消置顶' : '已置顶')
        loadHistory(1)
      } catch (error) {
        ElMessage.error('操作失败: ' + error.message)
      }
    }

    // 重命名历史记录
    const renameHistory = (item) => {
      renamingHistory.value = item
      newTitle.value = item.title || ''
      renameDialogVisible.value = true
    }

    const confirmRename = async () => {
      if (!newTitle.value.trim()) {
        ElMessage.warning('标题不能为空')
        return
      }

      try {
        await AIGCService.updateHistory(renamingHistory.value.id, {
          title: newTitle.value.trim()
        })
        
        ElMessage.success('重命名成功')
        renameDialogVisible.value = false
        loadHistory(1)
      } catch (error) {
        ElMessage.error('重命名失败: ' + error.message)
      }
    }

    // 删除历史记录
    const deleteHistory = async (item) => {
      try {
        await ElMessageBox.confirm(
          `确定要删除历史记录"${item.title || '未命名任务'}"吗？`,
          '警告',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        await AIGCService.deleteHistory(item.id)
        ElMessage.success('删除成功')
        
        // 如果删除的是当前选中的，清空选中
        if (selectedHistoryId.value === item.id) {
          selectedHistoryId.value = null
          emit('history-selected', null)
        }
        
        loadHistory(1)
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除失败: ' + error.message)
        }
      }
    }

    // 格式化日期
    const formatDate = (dateStr) => {
      if (!dateStr) return ''
      
      const date = new Date(dateStr)
      const now = new Date()
      const diff = now - date
      
      // 小于1分钟
      if (diff < 60000) {
        return '刚刚'
      }
      // 小于1小时
      if (diff < 3600000) {
        return Math.floor(diff / 60000) + '分钟前'
      }
      // 小于1天
      if (diff < 86400000) {
        return Math.floor(diff / 3600000) + '小时前'
      }
      // 小于7天
      if (diff < 604800000) {
        return Math.floor(diff / 86400000) + '天前'
      }
      
      // 超过7天显示具体日期
      return date.toLocaleDateString('zh-CN', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    onMounted(() => {
      loadHistory()
    })

    return {
      loading,
      searchQuery,
      historyList,
      selectedHistoryId,
      hasMore,
      renameDialogVisible,
      newTitle,
      loadHistory,
      loadMore,
      debounceSearch,
      selectHistory,
      togglePin,
      renameHistory,
      confirmRename,
      deleteHistory,
      formatDate
    }
  }
}
</script>

<style scoped>
.history-panel-new {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.history-header {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.search-box {
  flex: 1;
}

.history-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-item {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px;
  background: var(--dark-bg-tertiary);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid transparent;
}

:deep(.light-theme) .history-item {
  background: var(--light-bg-tertiary);
}

.history-item:hover {
  background: rgba(255, 215, 0, 0.1);
  border-color: rgba(255, 215, 0, 0.3);
}

.history-item.active {
  background: rgba(255, 215, 0, 0.15);
  border-color: #FFD700;
}

.history-item.pinned {
  background: rgba(255, 215, 0, 0.05);
}

.pin-icon {
  color: #FFD700;
  font-size: 16px;
  flex-shrink: 0;
  margin-top: 2px;
}

.history-content {
  flex: 1;
  min-width: 0;
}

.history-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.history-title {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
  color: var(--dark-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

:deep(.light-theme) .history-title {
  color: var(--light-text-primary);
}

.more-icon {
  font-size: 16px;
  color: var(--dark-text-tertiary);
  cursor: pointer;
  transition: color 0.2s;
}

.more-icon:hover {
  color: #FFD700;
}

.history-meta {
  font-size: 12px;
  color: var(--dark-text-tertiary);
}

:deep(.light-theme) .history-meta {
  color: var(--light-text-tertiary);
}

.load-more {
  text-align: center;
  padding: 12px 0;
}

/* 滚动条样式 */
.history-list::-webkit-scrollbar {
  width: 6px;
}

.history-list::-webkit-scrollbar-thumb {
  background: rgba(255, 215, 0, 0.3);
  border-radius: 3px;
}

.history-list::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 215, 0, 0.5);
}
</style>

