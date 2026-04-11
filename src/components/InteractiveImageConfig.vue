<template>
  <div class="interactive-image-config">
    <el-form-item label="互动类型">
      <el-select v-model="config.interactionType" style="width: 100%">
        <el-option label="主人与狗狗散步" value="walking-with-dog" />
        <el-option label="主人与猫咪玩耍" value="playing-with-cat" />
        <el-option label="家庭游戏时光" value="family-game-time" />
        <el-option label="训练互动" value="training-interaction" />
        <el-option label="喂食时刻" value="feeding-time" />
        <el-option label="休息陪伴" value="resting-companionship" />
        <el-option label="自定义互动" value="custom" />
      </el-select>
    </el-form-item>

    <el-form-item v-if="config.interactionType === 'custom'" label="自定义互动描述">
      <el-input
        v-model="config.customInteractionDescription"
        type="textarea"
        :rows="2"
        placeholder="详细描述主人与宠物的互动场景"
      />
    </el-form-item>

    <el-form-item label="主人特征">
      <el-row :gutter="12">
        <el-col :span="12">
          <el-select v-model="config.owner.gender" placeholder="性别">
            <el-option label="女性" value="female" />
            <el-option label="男性" value="male" />
            <el-option label="不限" value="any" />
          </el-select>
        </el-col>
        <el-col :span="12">
          <el-select v-model="config.owner.ageGroup" placeholder="年龄段">
            <el-option label="青年人(20-35岁)" value="young-adult" />
            <el-option label="中年人(35-50岁)" value="middle-aged" />
            <el-option label="儿童" value="child" />
            <el-option label="老年人" value="elderly" />
          </el-select>
        </el-col>
      </el-row>
    </el-form-item>

    <el-form-item label="宠物设定">
      <el-row :gutter="12">
        <el-col :span="12">
          <el-select v-model="config.pet.type" placeholder="宠物类型">
            <el-option label="小型犬" value="small-dog" />
            <el-option label="中型犬" value="medium-dog" />
            <el-option label="大型犬" value="large-dog" />
            <el-option label="猫咪" value="cat" />
          </el-select>
        </el-col>
        <el-col :span="12">
          <el-select v-model="config.pet.mood" placeholder="宠物情绪">
            <el-option label="开心兴奋" value="happy-excited" />
            <el-option label="温顺乖巧" value="gentle-obedient" />
            <el-option label="活泼好动" value="lively-active" />
            <el-option label="专注认真" value="focused-serious" />
          </el-select>
        </el-col>
      </el-row>
    </el-form-item>

    <el-form-item label="环境设定">
      <el-select v-model="config.environment" style="width: 100%">
        <el-option label="家中客厅" value="home-living-room" />
        <el-option label="户外公园" value="outdoor-park" />
        <el-option label="后院花园" value="backyard-garden" />
        <el-option label="海边沙滩" value="beach" />
        <el-option label="城市街道" value="city-street" />
        <el-option label="森林小径" value="forest-path" />
      </el-select>
    </el-form-item>

    <el-form-item label="情感氛围">
      <el-checkbox-group v-model="config.emotionalAtmosphere">
        <el-checkbox label="warm-love">温暖关爱</el-checkbox>
        <el-checkbox label="joyful-fun">欢乐有趣</el-checkbox>
        <el-checkbox label="peaceful-calm">宁静安详</el-checkbox>
        <el-checkbox label="energetic-vibrant">活力四射</el-checkbox>
        <el-checkbox label="intimate-bonding">亲密默契</el-checkbox>
      </el-checkbox-group>
    </el-form-item>

    <el-form-item label="构图焦点">
      <el-radio-group v-model="config.compositionFocus">
        <el-radio label="equal-emphasis">人宠并重</el-radio>
        <el-radio label="pet-focused">以宠物为主</el-radio>
        <el-radio label="interaction-focused">突出互动</el-radio>
        <el-radio label="product-integrated">产品融入</el-radio>
      </el-radio-group>
    </el-form-item>

    <el-form-item label="光线设定">
      <el-select v-model="config.lighting" style="width: 100%">
        <el-option label="自然光线" value="natural-light" />
        <el-option label="温暖夕阳" value="warm-sunset" />
        <el-option label="柔和室内光" value="soft-indoor" />
        <el-option label="明亮阳光" value="bright-sunlight" />
        <el-option label="黄金时刻" value="golden-hour" />
      </el-select>
    </el-form-item>

    <el-form-item label="产品融入方式">
      <el-radio-group v-model="config.productIntegration">
        <el-radio label="natural-use">自然使用状态</el-radio>
        <el-radio label="prominent-display">突出展示</el-radio>
        <el-radio label="subtle-presence">巧妙融入</el-radio>
        <el-radio label="action-moment">动作瞬间</el-radio>
      </el-radio-group>
    </el-form-item>

    <el-form-item label="表情要求">
      <el-input
        v-model="config.expressionRequirement"
        placeholder="例如：主人和宠物都要显示出愉悦轻松的表情"
      />
    </el-form-item>
  </div>
</template>

<script>
export default {
  name: 'InteractiveImageConfig',
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
          interactionType: 'walking-with-dog',
          customInteractionDescription: '',
          owner: {
            gender: 'female',
            ageGroup: 'young-adult'
          },
          pet: {
            type: 'medium-dog',
            mood: 'happy-excited'
          },
          environment: 'outdoor-park',
          emotionalAtmosphere: ['warm-love', 'joyful-fun'],
          compositionFocus: 'interaction-focused',
          lighting: 'natural-light',
          productIntegration: 'natural-use',
          expressionRequirement: '',
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

