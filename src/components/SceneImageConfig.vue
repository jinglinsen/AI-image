<template>
  <div class="scene-image-config">
    <el-form-item label="场景类型">
      <el-select v-model="config.sceneType" style="width: 100%">
        <el-option label="温馨客厅" value="cozy-living-room" />
        <el-option label="阳光卧室" value="sunny-bedroom" />
        <el-option label="户外公园" value="outdoor-park" />
        <el-option label="后院草坪" value="backyard-lawn" />
        <el-option label="海边沙滩" value="beach" />
        <el-option label="森林小径" value="forest-path" />
        <el-option label="城市街道" value="city-street" />
        <el-option label="自定义" value="custom" />
      </el-select>
    </el-form-item>

    <el-form-item v-if="config.sceneType === 'custom'" label="自定义场景描述">
      <el-input
        v-model="config.customSceneDescription"
        type="textarea"
        :rows="2"
        placeholder="详细描述您想要的场景环境"
      />
    </el-form-item>

    <el-form-item label="时间设定">
      <el-radio-group v-model="config.timeOfDay">
        <el-radio label="morning">清晨时光</el-radio>
        <el-radio label="afternoon">午后阳光</el-radio>
        <el-radio label="evening">黄昏时分</el-radio>
        <el-radio label="golden-hour">黄金时刻</el-radio>
      </el-radio-group>
    </el-form-item>

    <el-form-item label="宠物状态">
      <el-select v-model="config.petActivity" style="width: 100%">
        <el-option label="开心玩耍" value="playing-happily" />
        <el-option label="舒适休息" value="resting-comfortably" />
        <el-option label="专注使用" value="focused-using" />
        <el-option label="活跃运动" value="active-exercise" />
        <el-option label="好奇探索" value="curious-exploring" />
      </el-select>
    </el-form-item>

    <el-form-item label="宠物品种">
      <el-select v-model="config.petBreed" style="width: 100%">
        <el-option label="金毛寻回犬" value="golden-retriever" />
        <el-option label="拉布拉多" value="labrador" />
        <el-option label="哈士奇" value="husky" />
        <el-option label="柯基" value="corgi" />
        <el-option label="贵宾犬" value="poodle" />
        <el-option label="英短猫" value="british-shorthair" />
        <el-option label="橘猫" value="orange-cat" />
        <el-option label="根据产品适配" value="auto-match" />
      </el-select>
    </el-form-item>

    <el-form-item label="氛围营造">
      <el-checkbox-group v-model="config.atmosphere">
        <el-checkbox label="warm-lighting">温暖光线</el-checkbox>
        <el-checkbox label="family-friendly">家庭温馨</el-checkbox>
        <el-checkbox label="natural-environment">自然环境</el-checkbox>
        <el-checkbox label="lifestyle-appeal">生活品质感</el-checkbox>
        <el-checkbox label="emotional-connection">情感共鸣</el-checkbox>
      </el-checkbox-group>
    </el-form-item>

    <el-form-item label="构图布局">
      <el-radio-group v-model="config.composition">
        <el-radio label="center-focus">中心焦点</el-radio>
        <el-radio label="rule-of-thirds">三分法构图</el-radio>
        <el-radio label="diagonal">对角线构图</el-radio>
        <el-radio label="background-blur">背景虚化</el-radio>
      </el-radio-group>
    </el-form-item>

    <el-form-item label="留白区域">
      <el-select v-model="config.whitespaceArea" style="width: 100%">
        <el-option label="顶部留白" value="top" />
        <el-option label="右侧留白" value="right" />
        <el-option label="左侧留白" value="left" />
        <el-option label="底部留白" value="bottom" />
        <el-option label="不需要留白" value="none" />
      </el-select>
    </el-form-item>

    <el-form-item label="情感表达">
      <el-input
        v-model="config.emotionalExpression"
        placeholder="例如：展现宠物与产品的快乐互动，体现产品带来的生活乐趣"
      />
    </el-form-item>
  </div>
</template>

<script>
export default {
  name: 'SceneImageConfig',
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
          sceneType: 'cozy-living-room',
          customSceneDescription: '',
          timeOfDay: 'afternoon',
          petActivity: 'playing-happily',
          petBreed: 'golden-retriever',
          atmosphere: ['warm-lighting', 'family-friendly'],
          composition: 'rule-of-thirds',
          whitespaceArea: 'top',
          emotionalExpression: '',
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

