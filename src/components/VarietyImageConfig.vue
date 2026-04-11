<template>
  <div class="variety-image-config">
    <el-form-item label="产品变体">
      <div class="variety-list">
        <div 
          v-for="(variety, index) in config.varieties" 
          :key="index"
          class="variety-item"
        >
          <el-row :gutter="12">
            <el-col :span="8">
              <el-input 
                v-model="variety.name" 
                placeholder="变体名称"
              />
            </el-col>
            <el-col :span="8">
              <el-input 
                v-model="variety.color" 
                placeholder="颜色"
              />
            </el-col>
            <el-col :span="6">
              <el-input 
                v-model="variety.size" 
                placeholder="尺寸"
              />
            </el-col>
            <el-col :span="2">
              <el-button 
                type="danger" 
                size="small" 
                @click="removeVariety(index)"
                :disabled="config.varieties.length <= 1"
              >
                删除
              </el-button>
            </el-col>
          </el-row>
        </div>
        <el-button 
          type="dashed" 
          @click="addVariety"
          class="add-variety-btn"
          :disabled="config.varieties.length >= 6"
        >
          <el-icon><Plus /></el-icon>
          添加产品变体
        </el-button>
      </div>
    </el-form-item>

    <el-form-item label="排列方式">
      <el-radio-group v-model="config.arrangement">
        <el-radio label="horizontal">水平排列</el-radio>
        <el-radio label="vertical">垂直排列</el-radio>
        <el-radio label="grid">网格布局</el-radio>
        <el-radio label="circular">环形排列</el-radio>
        <el-radio label="scattered">自然散布</el-radio>
      </el-radio-group>
    </el-form-item>

    <el-form-item label="背景设定">
      <el-select v-model="config.background" style="width: 100%">
        <el-option label="纯白背景" value="pure-white" />
        <el-option label="渐变背景" value="gradient" />
        <el-option label="木质台面" value="wooden-surface" />
        <el-option label="大理石台面" value="marble-surface" />
        <el-option label="生活场景" value="lifestyle-scene" />
      </el-select>
    </el-form-item>

    <el-form-item label="尺寸统一">
      <el-switch v-model="config.uniformSize" />
      <span class="form-tip">所有变体显示相同大小</span>
    </el-form-item>

    <el-form-item label="标签显示">
      <el-checkbox-group v-model="config.labelOptions">
        <el-checkbox label="show-names">显示产品名称</el-checkbox>
        <el-checkbox label="show-colors">显示颜色标签</el-checkbox>
        <el-checkbox label="show-sizes">显示尺寸标签</el-checkbox>
        <el-checkbox label="show-prices">显示价格(如适用)</el-checkbox>
      </el-checkbox-group>
    </el-form-item>

    <el-form-item label="重点突出">
      <el-select v-model="config.highlightVariety" style="width: 100%">
        <el-option 
          v-for="(variety, index) in config.varieties" 
          :key="index"
          :label="variety.name || `变体${index + 1}`"
          :value="index"
        />
        <el-option label="无重点突出" value="-1" />
      </el-select>
    </el-form-item>

    <el-form-item label="间距调整">
      <el-slider
        v-model="config.spacing"
        :min="5"
        :max="50"
        :step="5"
        show-input
        :format-tooltip="formatSpacingTooltip"
      />
    </el-form-item>

    <el-form-item label="使用场景">
      <el-checkbox-group v-model="config.usageScenes">
        <el-checkbox label="size-comparison">尺寸对比展示</el-checkbox>
        <el-checkbox label="color-selection">颜色选择展示</el-checkbox>
        <el-checkbox label="style-variety">款式多样性</el-checkbox>
        <el-checkbox label="value-proposition">价值主张展示</el-checkbox>
      </el-checkbox-group>
    </el-form-item>

    <el-form-item label="光线设定">
      <el-radio-group v-model="config.lighting">
        <el-radio label="even-lighting">均匀光线</el-radio>
        <el-radio label="dramatic-lighting">戏剧性光线</el-radio>
        <el-radio label="soft-diffused">柔和散射</el-radio>
        <el-radio label="studio-lighting">专业影棚</el-radio>
      </el-radio-group>
    </el-form-item>

    <el-form-item label="特殊要求">
      <el-input
        v-model="config.specialRequirements"
        type="textarea"
        :rows="2"
        placeholder="例如：突出颜色差异，保持品牌一致性等"
      />
    </el-form-item>
  </div>
</template>

<script>
export default {
  name: 'VarietyImageConfig',
  props: {
    modelValue: {
      type: Object,
      default: () => ({})
    },
    taskInfo: {
      type: Object,
      default: () => ({})
    }
  },
  computed: {
    config: {
      get() {
        return {
          varieties: [
            { name: '红色款', color: '红色', size: 'M' },
            { name: '蓝色款', color: '蓝色', size: 'M' },
            { name: '绿色款', color: '绿色', size: 'M' }
          ],
          arrangement: 'horizontal',
          background: 'pure-white',
          uniformSize: true,
          labelOptions: ['show-colors'],
          highlightVariety: -1,
          spacing: 20,
          usageScenes: ['color-selection'],
          lighting: 'even-lighting',
          specialRequirements: '',
          ...this.modelValue
        }
      },
      set(value) {
        this.$emit('update:modelValue', value)
      }
    }
  },
  methods: {
    addVariety() {
      if (this.config.varieties.length < 6) {
        this.config.varieties.push({
          name: '',
          color: '',
          size: ''
        })
      }
    },
    removeVariety(index) {
      if (this.config.varieties.length > 1) {
        this.config.varieties.splice(index, 1)
      }
    },
    formatSpacingTooltip(value) {
      return `${value}px`
    }
  }
}
</script>

<style scoped>
.variety-list {
  border: 1px dashed #dcdfe6;
  border-radius: 6px;
  padding: 16px;
}

.variety-item {
  margin-bottom: 12px;
}

.variety-item:last-child {
  margin-bottom: 0;
}

.add-variety-btn {
  width: 100%;
  margin-top: 12px;
  border-style: dashed;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-left: 8px;
}
</style>

