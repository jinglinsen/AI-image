<template>
  <div class="detail-image-config">
    <el-form-item label="重点展示部位">
      <el-select v-model="config.focusArea" style="width: 100%">
        <el-option label="金属卡扣" value="metal-clasp" />
        <el-option label="材质纹理" value="material-texture" />
        <el-option label="缝合线" value="stitching" />
        <el-option label="调节装置" value="adjustment-mechanism" />
        <el-option label="舒适垫层" value="comfort-padding" />
        <el-option label="防滑设计" value="anti-slip-design" />
        <el-option label="其他" value="custom" />
      </el-select>
    </el-form-item>

    <el-form-item v-if="config.focusArea === 'custom'" label="自定义部位描述">
      <el-input
        v-model="config.customFocusDescription"
        placeholder="详细描述要突出的功能部位"
      />
    </el-form-item>

    <el-form-item label="宠物互动">
      <el-radio-group v-model="config.petInteraction">
        <el-radio label="wearing">宠物佩戴使用</el-radio>
        <el-radio label="playing">宠物玩耍互动</el-radio>
        <el-radio label="resting">宠物舒适休息</el-radio>
        <el-radio label="none">仅产品特写</el-radio>
      </el-radio-group>
    </el-form-item>

    <el-form-item v-if="config.petInteraction !== 'none'" label="宠物类型">
      <el-select v-model="config.petType" style="width: 100%">
        <el-option label="小型犬" value="small-dog" />
        <el-option label="中型犬" value="medium-dog" />
        <el-option label="大型犬" value="large-dog" />
        <el-option label="猫咪" value="cat" />
        <el-option label="根据产品自动选择" value="auto" />
      </el-select>
    </el-form-item>

    <el-form-item label="拍摄角度">
      <el-select v-model="config.shootingAngle" style="width: 100%">
        <el-option label="45度斜角" value="45-degree" />
        <el-option label="正面平视" value="front-view" />
        <el-option label="侧面特写" value="side-close-up" />
        <el-option label="俯视角度" value="top-down" />
        <el-option label="微距特写" value="macro-close-up" />
      </el-select>
    </el-form-item>

    <el-form-item label="背景环境">
      <el-radio-group v-model="config.backgroundEnvironment">
        <el-radio label="pure-white">纯白背景</el-radio>
        <el-radio label="natural">自然环境</el-radio>
        <el-radio label="home">家居环境</el-radio>
      </el-radio-group>
    </el-form-item>

    <el-form-item label="光线重点">
      <el-checkbox-group v-model="config.lightingFocus">
        <el-checkbox label="highlight-texture">突出材质纹理</el-checkbox>
        <el-checkbox label="show-reflections">展现金属光泽</el-checkbox>
        <el-checkbox label="soft-shadows">柔和阴影层次</el-checkbox>
        <el-checkbox label="detail-clarity">细节清晰锐利</el-checkbox>
      </el-checkbox-group>
    </el-form-item>

    <el-form-item label="功能说明">
      <el-input
        v-model="config.functionDescription"
        type="textarea"
        :rows="2"
        placeholder="简要描述这个部位的功能特点，如：一键式卡扣设计，方便快速佩戴和拆卸"
      />
    </el-form-item>
  </div>
</template>

<script>
export default {
  name: 'DetailImageConfig',
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
          focusArea: 'metal-clasp',
          customFocusDescription: '',
          petInteraction: 'wearing',
          petType: 'medium-dog',
          shootingAngle: '45-degree',
          backgroundEnvironment: 'natural',
          lightingFocus: ['highlight-texture'],
          functionDescription: '',
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

