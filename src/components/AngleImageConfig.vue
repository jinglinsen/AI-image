<template>
  <div class="angle-image-config">
    <el-form-item label="展示角度">
      <el-checkbox-group v-model="config.angles">
        <el-checkbox label="front">正面视角</el-checkbox>
        <el-checkbox label="back">背面视角</el-checkbox>
        <el-checkbox label="left-side">左侧面</el-checkbox>
        <el-checkbox label="right-side">右侧面</el-checkbox>
        <el-checkbox label="top">俯视角度</el-checkbox>
        <el-checkbox label="bottom">底部视角</el-checkbox>
        <el-checkbox label="45-degree">45度斜角</el-checkbox>
        <el-checkbox label="135-degree">135度角</el-checkbox>
      </el-checkbox-group>
    </el-form-item>

    <el-form-item label="布局方式">
      <el-radio-group v-model="config.layout">
        <el-radio label="grid">网格排列</el-radio>
        <el-radio label="circular">环形排列</el-radio>
        <el-radio label="linear">直线排列</el-radio>
        <el-radio label="stepped">阶梯式排列</el-radio>
      </el-radio-group>
    </el-form-item>

    <el-form-item label="背景统一">
      <el-switch v-model="config.unifiedBackground" />
      <span class="form-tip">所有角度使用相同背景</span>
    </el-form-item>

    <el-form-item label="标注说明">
      <el-switch v-model="config.showLabels" />
      <span class="form-tip">为每个角度添加文字标注</span>
    </el-form-item>

    <el-form-item v-if="config.showLabels" label="标注语言">
      <el-select v-model="config.labelLanguage" style="width: 100%">
        <el-option label="中文" value="chinese" />
        <el-option label="英文" value="english" />
        <el-option label="双语" value="bilingual" />
      </el-select>
    </el-form-item>

    <el-form-item label="间距调整">
      <el-slider
        v-model="config.spacing"
        :min="0"
        :max="50"
        :step="5"
        show-input
        :format-tooltip="formatSpacingTooltip"
      />
    </el-form-item>

    <el-form-item label="图片尺寸">
      <el-radio-group v-model="config.imageSize">
        <el-radio label="uniform">统一尺寸</el-radio>
        <el-radio label="adaptive">自适应尺寸</el-radio>
        <el-radio label="highlight-main">突出主视角</el-radio>
      </el-radio-group>
    </el-form-item>

    <el-form-item label="重点角度">
      <el-select v-model="config.primaryAngle" style="width: 100%">
        <el-option label="正面视角" value="front" />
        <el-option label="45度斜角" value="45-degree" />
        <el-option label="侧面视角" value="side" />
        <el-option label="俯视角度" value="top" />
        <el-option label="无重点" value="none" />
      </el-select>
    </el-form-item>

    <el-form-item label="细节展示">
      <el-checkbox-group v-model="config.detailFeatures">
        <el-checkbox label="texture-detail">材质纹理细节</el-checkbox>
        <el-checkbox label="functional-parts">功能部件特写</el-checkbox>
        <el-checkbox label="size-reference">尺寸参考对比</el-checkbox>
        <el-checkbox label="color-accuracy">颜色准确还原</el-checkbox>
      </el-checkbox-group>
    </el-form-item>
  </div>
</template>

<script>
export default {
  name: 'AngleImageConfig',
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
          angles: ['front', 'left-side', '45-degree'],
          layout: 'grid',
          unifiedBackground: true,
          showLabels: true,
          labelLanguage: 'english',
          spacing: 20,
          imageSize: 'uniform',
          primaryAngle: 'front',
          detailFeatures: ['texture-detail'],
          ...this.modelValue
        }
      },
      set(value) {
        this.$emit('update:modelValue', value)
      }
    }
  },
  methods: {
    formatSpacingTooltip(value) {
      return `${value}px`
    }
  }
}
</script>

<style scoped>
.form-tip {
  font-size: 12px;
  color: #909399;
  margin-left: 8px;
}
</style>

