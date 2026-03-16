<script setup lang="ts">
/**
 * 表单组件
 * 
 * 使用示例：
 * <edit-form ref="editForm" :options="{ projects: projectList }" />
 * 
 * 选项数据加载示例：
 * const projectList = ref([]);
 * const loadProjects = async () => {
 *   const { data } = await ProjectApi.getList();
 *   projectList.value = data || [];
 * };
 */

import dayjs, { Dayjs } from 'dayjs';
import { {{apiModule}}Api } from '@/api';
import { PAGE_NAME } from '../data';
import useDrawer from '@/hooks/useDrawer.ts';
import { useForm } from '@/hooks/useForm.ts';

// 使用provide/inject时init可能会获取不到值
const { drawer } = useDrawer(PAGE_NAME);

const props = defineProps<{
  options?: Record<string, any[]>;
}>();

/**
 * 表单注册
 */
const modelRef = reactive<Partial<{{apiModule}}EditType.Req>>({ annex: [] });
const schemas = computed<YcForm.Schema[]>(() => [
  {{#each fields}}
  {
    label: '{{label}}',
    {{#if (isArray name)}}
    field: {{{json name}}},
    {{else}}
    field: '{{name}}',
    {{/if}}
    component: '{{component}}',
    {{#if required}}required: true,{{/if}}
    {{#if tip}}tip: '{{tip}}',{{/if}}
    componentProps: {
      {{#if placeholder}}placeholder: '{{placeholder}}',{{/if}}
      {{#if options}}options: {{options}},{{/if}}
      {{#if componentProps}}{{{componentProps}}},{{/if}}
    }
  }{{#unless @last}},{{/unless}}
  {{/each}}
]);
const { validate, VBind, setFields } = useForm({
  schemas,
  modelRef,
  labelCol: { style: { width: '70px' } },
});

/**
 * 获取详情
 */
const detail = ref<Partial<{{apiModule}}GetDetailType.Res>>({});
const getDetail = async () => {
  const { data } = await {{apiModule}}Api.{{apiDetailMethod}}(drawer.record?.id || '');
  detail.value = data || {};
  setFields(detail.value);
};

/**
 * 保存--返回 Promise.resolve() 或 Promise.reject()
 */
const save = async () => {
  await validate();
  drawer.showSpinning();
  if (drawer.mode === 'add') {
    const { code } = await {{apiModule}}Api.{{apiCreateMethod}}(modelRef);
    if (code === 200) {
      message.success('新增成功');
    } else return Promise.reject();
  }
  if (drawer.mode === 'edit') {
    const { code } = await {{apiModule}}Api.{{apiUpdateMethod}}(modelRef);
    if (code === 200) {
      message.success('修改成功');
      return Promise.resolve();
    } else return Promise.reject();
  }
};

/**
 * 初始化
 */
const init = async () => {
  try {
    drawer.showSpinning();
    const promises: Promise<any>[] = [];
    if (drawer.mode === 'edit') {
      promises.push(getDetail());
    }
    await Promise.all(promises);
  } finally {
    drawer.hideSpinning();
  }
};
init();

defineExpose({ save });
</script>

<template>
  <div>
    <yc-form v-bind="VBind"></yc-form>
  </div>
</template>

<style scoped lang="less"></style>
