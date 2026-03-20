<script setup lang="ts">
import { computed, reactive } from 'vue';
import { message } from 'ant-design-vue';
import { {{apiModule}}Api } from '@/api';
import { PAGE_NAME } from '../data';
import useDrawer from '@/hooks/useDrawer.ts';
import { useForm } from '@/hooks/useForm.ts';

const props = defineProps<{
  options?: Record<string, any[]>;
}>();

type CreateMethod = typeof {{apiModule}}Api.{{apiCreateMethod}};
type UpdateMethod = typeof {{apiModule}}Api.{{apiUpdateMethod}};
type DetailMethod = typeof {{apiModule}}Api.{{apiDetailMethod}};
type CreateReq = Parameters<CreateMethod>[0];
type UpdateReq = Parameters<UpdateMethod>[0];
type DetailRes = Awaited<ReturnType<DetailMethod>>['data'];
type FormModel = Partial<CreateReq & UpdateReq>;

const { drawer } = useDrawer(PAGE_NAME);

const modelRef = reactive<FormModel>({});
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
    },
  }{{#unless @last}},{{/unless}}
  {{/each}}
]);

const { validate, VBind, setFields } = useForm({
  schemas,
  modelRef,
  labelCol: { style: { width: '70px' } },
});

const getDetail = async () => {
  const recordId = drawer.record?.{{recordKey}};
  if (!recordId) return;
  const { data } = await {{apiModule}}Api.{{apiDetailMethod}}(recordId);
  Object.assign(modelRef, (data || {}) as DetailRes);
  setFields(data || {});
};

const save = async () => {
  await validate();
  drawer.showSpinning();

  if (drawer.mode === 'add') {
    const { code } = await {{apiModule}}Api.{{apiCreateMethod}}(
      modelRef as CreateReq,
    );
    if (code === 200) {
      message.success('新增成功');
      return;
    }
    return Promise.reject();
  }

  if (drawer.mode === 'edit') {
    const { code } = await {{apiModule}}Api.{{apiUpdateMethod}}(
      modelRef as UpdateReq,
    );
    if (code === 200) {
      message.success('编辑成功');
      return;
    }
  }

  return Promise.reject();
};

const init = async () => {
  try {
    drawer.showSpinning();
    const tasks: Promise<unknown>[] = [];

    void props;
    // Load remote options here when needed, then push the promises into tasks.

    if (drawer.mode === 'edit') {
      tasks.push(getDetail());
    }

    await Promise.all(tasks);
  } finally {
    drawer.hideSpinning();
  }
};

init();

defineExpose({ save });
</script>

<template>
  <div>
    <yc-form v-bind="VBind" />
  </div>
</template>

<style scoped lang="less"></style>
