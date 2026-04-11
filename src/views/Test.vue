<template>
  <div class="test-page">
    <h1>测试页面</h1>
    <p>如果您能看到这个页面，说明基本的Vue和Element Plus配置是正常的。</p>
    
    <el-button type="primary" @click="showMessage">测试按钮</el-button>
    
    <el-card style="margin-top: 20px;">
      <template #header>
        <span>测试卡片</span>
      </template>
      <p>这是一个测试卡片内容</p>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'Test',
  methods: {
    showMessage() {
      this.$message.success('Element Plus 工作正常!')
    }
  }
}
</script>

<style scoped>
.test-page {
  padding: 20px;
}
</style>





