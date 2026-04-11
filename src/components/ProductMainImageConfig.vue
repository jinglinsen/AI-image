<template>
  <div class="product-main-config">
    <el-form-item label="光影效果">
      <el-select v-model="config.lightingEffect" style="width: 100%">
        <el-option label="柔和阴影" value="soft-shadow" />
        <el-option label="无阴影" value="no-shadow" />
        <el-option label="增强高光" value="enhanced-highlight" />
        <el-option label="自然光影" value="natural-lighting" />
      </el-select>
    </el-form-item>

    <el-form-item label="产品摆放">
      <el-radio-group v-model="config.arrangement">
        <el-radio label="single">单个产品居中</el-radio>
        <el-radio label="group">多产品组合</el-radio>
        <el-radio label="scattered">自然散布</el-radio>
      </el-radio-group>
    </el-form-item>

    <el-form-item label="背景类型">
      <el-select v-model="config.backgroundType" style="width: 100%">
        <el-option label="纯白背景" value="pure-white" />
        <el-option label="渐变白背景" value="gradient-white" />
        <el-option label="带纹理白背景" value="textured-white" />
      </el-select>
    </el-form-item>

    <el-form-item label="产品角度">
      <el-slider
        v-model="config.productAngle"
        :min="0"
        :max="360"
        :step="15"
        show-input
        :format-tooltip="formatAngleTooltip"
      />
    </el-form-item>

    <el-form-item label="特殊要求">
      <el-checkbox-group v-model="config.specialRequirements">
        <el-checkbox label="highlight-materials">突出材质纹理</el-checkbox>
        <el-checkbox label="show-scale">显示尺寸比例</el-checkbox>
        <el-checkbox label="premium-look">高端商品感</el-checkbox>
        <el-checkbox label="color-accuracy">色彩还原准确</el-checkbox>
      </el-checkbox-group>
    </el-form-item>
  </div>
</template>

<script>
export default {
  name: 'ProductMainImageConfig',
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
          lightingEffect: 'soft-shadow',
          arrangement: 'single',
          backgroundType: 'pure-white',
          productAngle: 45,
          specialRequirements: [],
          ...this.modelValue
        }
      },
      set(value) {
        this.$emit('update:modelValue', value)
      }
    }
  },
  methods: {
    formatAngleTooltip(value) {
      return `${value}°`
    }
  }
}
</script>

