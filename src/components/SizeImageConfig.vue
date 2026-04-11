<template>
  <div class="size-image-config">
    <el-form-item label="产品尺寸">
      <el-row :gutter="12">
        <el-col :span="8">
          <el-input 
            v-model="config.dimensions.length" 
            placeholder="长度"
            type="number"
          >
            <template #append>cm</template>
          </el-input>
        </el-col>
        <el-col :span="8">
          <el-input 
            v-model="config.dimensions.width" 
            placeholder="宽度"
            type="number"
          >
            <template #append>cm</template>
          </el-input>
        </el-col>
        <el-col :span="8">
          <el-input 
            v-model="config.dimensions.height" 
            placeholder="高度"
            type="number"
          >
            <template #append>cm</template>
          </el-input>
        </el-col>
      </el-row>
    </el-form-item>

    <el-form-item label="参照物">
      <el-select v-model="config.referenceObject" style="width: 100%">
        <el-option label="标准尺子" value="ruler" />
        <el-option label="iPhone手机" value="iphone" />
        <el-option label="成年人手掌" value="hand" />
        <el-option label="硬币" value="coin" />
        <el-option label="A4纸张" value="a4-paper" />
        <el-option label="信用卡" value="credit-card" />
      </el-select>
    </el-form-item>

    <el-form-item label="标注方式">
      <el-radio-group v-model="config.annotationStyle">
        <el-radio label="dimensional-lines">尺寸线标注</el-radio>
        <el-radio label="overlay-text">文字覆盖</el-radio>
        <el-radio label="side-by-side">并排对比</el-radio>
      </el-radio-group>
    </el-form-item>

    <el-form-item label="测量单位">
      <el-select v-model="config.unit" style="width: 100%">
        <el-option label="厘米 (cm)" value="cm" />
        <el-option label="英寸 (inch)" value="inch" />
        <el-option label="毫米 (mm)" value="mm" />
      </el-select>
    </el-form-item>

    <el-form-item label="显示重量">
      <el-switch v-model="config.showWeight" />
      <el-input 
        v-if="config.showWeight"
        v-model="config.weight" 
        placeholder="重量"
        type="number"
        style="width: 120px; margin-left: 12px;"
      >
        <template #append>g</template>
      </el-input>
    </el-form-item>

    <el-form-item label="适用对象">
      <el-input
        v-model="config.suitableFor"
        placeholder="例如：适合中小型犬(10-25kg)"
      />
    </el-form-item>
  </div>
</template>

<script>
export default {
  name: 'SizeImageConfig',
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
          dimensions: {
            length: '',
            width: '',
            height: ''
          },
          referenceObject: 'ruler',
          annotationStyle: 'dimensional-lines',
          unit: 'cm',
          showWeight: false,
          weight: '',
          suitableFor: '',
          ...this.modelValue
        }
      },
      set(value) {
        this.$emit('update:modelValue', value)
      }
    }
  }
}
</script>

