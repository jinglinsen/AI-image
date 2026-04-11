<template>
  <div id="app" :class="themeClass">
    <!-- 主题切换按钮 -->
    <div class="theme-toggle-container">
      <button 
        @click="toggleTheme" 
        class="theme-toggle-btn"
        :title="isDark ? '切换到浅色模式' : '切换到深色模式'"
      >
        <span class="theme-icon" :class="{ 'is-dark': isDark }">
          {{ isDark ? '☀️' : '🌙' }}
        </span>
      </button>
    </div>
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      isDark: false // 默认浅色主题
    }
  },
  computed: {
    themeClass() {
      return this.isDark ? 'dark-theme' : 'light-theme'
    }
  },
  mounted() {
    // 从localStorage恢复主题设置
    const savedTheme = localStorage.getItem('app-theme')
    if (savedTheme) {
      this.isDark = savedTheme === 'dark'
    }
    
    // 添加主题类到document.body，确保全局弹出层也能获得主题
    this.updateBodyTheme()
  },
  watch: {
    isDark: {
      handler() {
        this.updateBodyTheme()
      },
      immediate: true
    }
  },
  methods: {
    toggleTheme() {
      this.isDark = !this.isDark
      // 保存主题设置到localStorage
      localStorage.setItem('app-theme', this.isDark ? 'dark' : 'light')
      this.$message.success(this.isDark ? '已切换到深色模式' : '已切换到浅色模式')
    },
    
    updateBodyTheme() {
      // 移除之前的主题类
      document.body.classList.remove('dark-theme', 'light-theme')
      // 添加当前主题类到body
      document.body.classList.add(this.isDark ? 'dark-theme' : 'light-theme')
    }
  }
}
</script>

<style>
/* CSS变量定义 */
:root {
  /* 深色主题变量 */
  --dark-bg-primary: #1a1a1a;
  --dark-bg-secondary: #262626;
  --dark-bg-tertiary: #333333;
  --dark-border: #404040;
  --dark-text-primary: #ffffff;
  --dark-text-secondary: #e6e6e6;
  --dark-text-tertiary: #909399;
  
  /* 浅色主题变量 - 优化后的配色 */
  --light-bg-primary: #ffffff;
  --light-bg-secondary: #f0f2f5;
  --light-bg-tertiary: #e4e7ed;
  --light-border: #c0c4cc;
  --light-text-primary: #1f2329;
  --light-text-secondary: #4e5969;
  --light-text-tertiary: #86909c;
  
  /* 通用变量 */
  --primary-color: #409eff;
  --primary-hover: #66b1ff;
  --success-color: #67c23a;
  --warning-color: #e6a23c;
  --danger-color: #f56c6c;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body * {
  transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
}

html,
body {
  height: 100%;
  overflow: hidden;
}

#app {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  height: 100vh;
  transition: all 0.3s ease;
}

/* 深色主题 */
.dark-theme {
  background: var(--dark-bg-primary);
  color: var(--dark-text-primary);
}
body.dark-theme {
  --bg-primary: var(--dark-bg-primary);
  --bg-secondary: var(--dark-bg-secondary);
  --bg-tertiary: var(--dark-bg-tertiary);
  --bg-hover: #3a3a3a;
  --border-color: var(--dark-border);
  --text-primary: var(--dark-text-primary);
  --text-secondary: var(--dark-text-secondary);
  --text-tertiary: var(--dark-text-tertiary);
}

/* 浅色主题 */
.light-theme {
  background: var(--light-bg-primary);
  color: var(--light-text-primary);
}
body.light-theme {
  --bg-primary: var(--light-bg-primary);
  --bg-secondary: var(--light-bg-secondary);
  --bg-tertiary: var(--light-bg-tertiary);
  --bg-hover: #e4e7ed;
  --border-color: var(--light-border);
  --text-primary: var(--light-text-primary);
  --text-secondary: var(--light-text-secondary);
  --text-tertiary: var(--light-text-tertiary);
}

/* 主题切换按钮容器 */
.theme-toggle-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
}

.theme-toggle-btn {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  border: 2px solid transparent;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 12px rgba(102, 126, 234, 0.35);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.theme-toggle-btn::before {
  content: '';
  position: absolute;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, rgba(255,255,255,0.2) 0%, transparent 70%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.theme-toggle-btn:hover {
  transform: scale(1.15) rotate(15deg);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

.theme-toggle-btn:hover::before {
  opacity: 1;
}

.theme-toggle-btn:active {
  transform: scale(0.95);
}

.theme-icon {
  font-size: 20px;
  display: inline-block;
  transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  line-height: 1;
}

.theme-icon.is-dark {
  transform: rotate(360deg);
}

/* Element Plus 主题适配 */
.el-button {
  border-radius: 6px;
}

.el-button--primary {
  background: var(--primary-color);
  border-color: var(--primary-color);
}

.el-button--primary:hover {
  background: var(--primary-hover);
  border-color: var(--primary-hover);
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

/* 深色主题滚动条 */
.dark-theme ::-webkit-scrollbar-track {
  background: var(--dark-bg-tertiary);
  border-radius: 4px;
}

.dark-theme ::-webkit-scrollbar-thumb {
  background: #606266;
  border-radius: 4px;
}

.dark-theme ::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

/* 浅色主题滚动条 */
.light-theme ::-webkit-scrollbar-track {
  background: var(--light-bg-tertiary);
  border-radius: 4px;
}

.light-theme ::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 4px;
}

.light-theme ::-webkit-scrollbar-thumb:hover {
  background: #a8abb2;
}

/* 深色主题 Element Plus 组件适配 */
.dark-theme .el-card {
  background: var(--dark-bg-secondary);
  border: 1px solid var(--dark-border);
  color: var(--dark-text-primary);
}

.dark-theme .el-dialog {
  background: var(--dark-bg-secondary);
  border: 1px solid var(--dark-border);
}

.dark-theme .el-dialog__header {
  background: var(--dark-bg-tertiary);
  border-bottom: 1px solid var(--dark-border);
}

.dark-theme .el-dialog__title {
  color: var(--dark-text-primary);
}

.dark-theme .el-dialog__body {
  background: var(--dark-bg-secondary);
  color: var(--dark-text-primary);
}

.dark-theme .el-message-box {
  background: var(--dark-bg-secondary);
  border: 1px solid var(--dark-border);
}

.dark-theme .el-message-box__title {
  color: var(--dark-text-primary);
}

.dark-theme .el-message-box__content {
  color: var(--dark-text-primary);
}

.dark-theme .el-table {
  background: var(--dark-bg-secondary);
  color: var(--dark-text-primary);
}

.dark-theme .el-table th {
  background: var(--dark-bg-tertiary);
  color: var(--dark-text-primary);
  border-bottom: 1px solid var(--dark-border);
}

.dark-theme .el-table td {
  border-bottom: 1px solid var(--dark-border);
}

.dark-theme .el-table tr {
  background: var(--dark-bg-secondary);
}

.dark-theme .el-table tr:hover {
  background: var(--dark-bg-tertiary);
}

.dark-theme .el-select-dropdown {
  background: var(--dark-bg-secondary);
  border: 1px solid var(--dark-border);
}

.dark-theme .el-select-dropdown__item {
  color: var(--dark-text-primary);
}

.dark-theme .el-select-dropdown__item:hover {
  background: var(--dark-bg-tertiary);
}

.dark-theme .el-select-dropdown__item.selected {
  background: var(--primary-color);
  color: var(--dark-text-primary);
}

/* 浅色主题 Element Plus 组件适配 */
.light-theme .el-card {
  background: var(--light-bg-primary);
  border: 1px solid var(--light-border);
  color: var(--light-text-primary);
}

.light-theme .el-dialog {
  background: var(--light-bg-primary);
  border: 1px solid var(--light-border);
}

.light-theme .el-dialog__header {
  background: var(--light-bg-secondary);
  border-bottom: 1px solid var(--light-border);
}

.light-theme .el-dialog__title {
  color: var(--light-text-primary);
}

.light-theme .el-dialog__body {
  background: var(--light-bg-primary);
  color: var(--light-text-primary);
}

.light-theme .el-message-box {
  background: var(--light-bg-primary);
  border: 1px solid var(--light-border);
}

.light-theme .el-message-box__title {
  color: var(--light-text-primary);
}

.light-theme .el-message-box__content {
  color: var(--light-text-primary);
}

.light-theme .el-table {
  background: var(--light-bg-primary);
  color: var(--light-text-primary);
}

.light-theme .el-table th {
  background: var(--light-bg-secondary);
  color: var(--light-text-primary);
  border-bottom: 1px solid var(--light-border);
}

.light-theme .el-table td {
  border-bottom: 1px solid var(--light-border);
}

.light-theme .el-table tr {
  background: var(--light-bg-primary);
}

.light-theme .el-table tr:hover {
  background: var(--light-bg-secondary);
}

/* 浅色主题下拉框重点修复 */
.light-theme .el-select-dropdown {
  background: var(--light-bg-primary) !important;
  border: 1px solid var(--light-border) !important;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1) !important;
}

.light-theme .el-select-dropdown__item {
  color: var(--light-text-primary) !important;
  background: transparent !important;
}

.light-theme .el-select-dropdown__item:hover {
  background: var(--light-bg-secondary) !important;
  color: var(--light-text-primary) !important;
}

.light-theme .el-select-dropdown__item.selected {
  background: var(--primary-color) !important;
  color: white !important;
}

.light-theme .el-select-dropdown__item.is-disabled {
  color: var(--light-text-tertiary) !important;
}

/* 浅色主题输入框 */
.light-theme .el-input__wrapper {
  background: var(--light-bg-primary) !important;
  border: 1px solid var(--light-border) !important;
  color: var(--light-text-primary) !important;
}

.light-theme .el-input__inner {
  color: var(--light-text-primary) !important;
}

.light-theme .el-textarea__inner {
  background: var(--light-bg-primary) !important;
  border: 1px solid var(--light-border) !important;
  color: var(--light-text-primary) !important;
}

/* 浅色主题按钮 */
.light-theme .el-button {
  border: 1px solid var(--light-border) !important;
}

.light-theme .el-button--default {
  background: var(--light-bg-primary) !important;
  color: var(--light-text-primary) !important;
}

.light-theme .el-button--default:hover {
  background: var(--light-bg-secondary) !important;
  border-color: var(--primary-color) !important;
}

/* 浅色主题折叠面板 */
.light-theme .el-collapse {
  background: var(--light-bg-primary) !important;
  border: 1px solid var(--light-border) !important;
}

.light-theme .el-collapse-item__header {
  background: var(--light-bg-secondary) !important;
  color: var(--light-text-primary) !important;
}

.light-theme .el-collapse-item__content {
  background: var(--light-bg-primary) !important;
  color: var(--light-text-primary) !important;
}

/* 全局Popper样式 - 下拉菜单弹出层 */
.light-theme .el-popper.is-light {
  background: var(--light-bg-primary) !important;
  border: 1px solid var(--light-border) !important;
  color: var(--light-text-primary) !important;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1) !important;
}

.light-theme .el-popper.is-light .el-popper__arrow::before {
  background: var(--light-bg-primary) !important;
  border: 1px solid var(--light-border) !important;
}

/* 动态生成的下拉菜单 - 使用属性选择器 */
.light-theme .el-select-dropdown.el-popper {
  background: var(--light-bg-primary) !important;
  border: 1px solid var(--light-border) !important;
}

/* Message和Notification */
.light-theme .el-message {
  background: var(--light-bg-primary) !important;
  border: 1px solid var(--light-border) !important;
  color: var(--light-text-primary) !important;
}

/* ========================================
   Body级别的全局主题样式
   用于Element Plus的全局弹出组件
======================================== */

/* 全局浅色主题下拉框 */
body.light-theme .el-select-dropdown {
  background: var(--light-bg-primary) !important;
  border: 1px solid var(--light-border) !important;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1) !important;
}

body.light-theme .el-select-dropdown__item {
  color: var(--light-text-primary) !important;
  background: transparent !important;
}

body.light-theme .el-select-dropdown__item:hover {
  background: var(--light-bg-secondary) !important;
  color: var(--light-text-primary) !important;
}

body.light-theme .el-select-dropdown__item.selected {
  background: var(--primary-color) !important;
  color: white !important;
}

body.light-theme .el-select-dropdown__item.is-disabled {
  color: var(--light-text-tertiary) !important;
}

/* 全局浅色主题Popper */
body.light-theme .el-popper {
  background: var(--light-bg-primary) !important;
  border: 1px solid var(--light-border) !important;
  color: var(--light-text-primary) !important;
}

body.light-theme .el-popper.is-light {
  background: var(--light-bg-primary) !important;
  border: 1px solid var(--light-border) !important;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1) !important;
}

/* 全局深色主题下拉框（确保深色模式正常） */
body.dark-theme .el-select-dropdown {
  background: var(--dark-bg-secondary) !important;
  border: 1px solid var(--dark-border) !important;
}

body.dark-theme .el-select-dropdown__item {
  color: var(--dark-text-primary) !important;
}

body.dark-theme .el-select-dropdown__item:hover {
  background: var(--dark-bg-tertiary) !important;
}

body.dark-theme .el-select-dropdown__item.selected {
  background: var(--primary-color) !important;
  color: var(--dark-text-primary) !important;
}
</style>

