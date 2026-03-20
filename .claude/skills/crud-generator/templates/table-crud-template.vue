<script setup lang="ts">
import { reactive, ref } from 'vue';
import { Modal, message } from 'ant-design-vue';
import { useTable } from '@kt/unity-hooks';
import type { UseTableOptions } from '@kt/unity-hooks/src/useTable/types';
import { columns, PAGE_NAME, searchSchema, statusOptions } from './data';
import EditForm from './components/EditForm.vue';
import DetailForm from './components/DetailForm.vue';
import { {{apiModule}}Api } from '@/api';
import { getLabelByValue } from '@/utils';
import useDrawer from '@/hooks/useDrawer.ts';
import { useForm } from '@/hooks/useForm.ts';

defineOptions({ name: PAGE_NAME });

type ListMethod = typeof {{apiModule}}Api.{{apiListMethod}};
type ListReq = Parameters<ListMethod>[0];
type ListRes = Awaited<ReturnType<ListMethod>>['data'];
type SearchParams = Partial<
  Omit<ListReq, '{{currentKey}}' | '{{pageSizeKey}}'>
>;
type TableRecord = ListRes extends { records: infer T extends readonly unknown[] }
  ? T[number]
  : ListRes extends { items: infer U extends readonly unknown[] }
    ? U[number]
    : ListRes extends { list: infer V extends readonly unknown[] }
      ? V[number]
      : Record<string, any>;

const inParams = reactive<SearchParams>({
  {{inParamsFields}}
});

const { VBind: searchVBind, resetFields: reset } = useForm({
  schemas: searchSchema,
  modelRef: inParams,
  isForm: false,
});

const tableOptions = reactive<UseTableOptions>({
  currentKey: '{{currentKey}}',
  pageSizeKey: '{{pageSizeKey}}',
  dataSourceKey: '{{dataSourceKey}}',
  totalKey: '{{totalKey}}',
  immediate: false,
  columns,
  inParams,
});

const getTableData = async (params: ListReq) => {
  const { data } = await {{apiModule}}Api.{{apiListMethod}}(params);
  return data;
};

const { VBind, VOn, search } = useTable(getTableData, tableOptions);

const handleDel = (row: TableRecord) => {
  Modal.confirm({
    title: '确认删除该记录？',
    onOk: async () => {
      // If the delete API does not accept a raw id, adjust this call after generation.
      const { code } = await {{apiModule}}Api.{{apiDeleteMethod}}(
        row.{{recordKey}} as never,
      );
      if (code === 200) {
        message.success('操作成功');
        await search();
      }
    },
    cancelText: '取消',
  });
};

const handleToPro = (row: TableRecord) => {
  void row;
  // router.push('/example/detail');
};

const { drawer } = useDrawer(PAGE_NAME);
const editForm = ref<{ save: () => Promise<void> } | null>(null);

const handleSave = async () => {
  try {
    await editForm.value?.save();
    drawer.close();
    await search();
  } finally {
    drawer.hideSpinning();
  }
};

const init = async () => {
  await search();
};

init();
</script>

<template>
  <tl v-model:drawer="drawer.visible">
    <tl-main>
      <tl-filter>
        <yc-form v-bind="searchVBind" />
        <a-button type="primary" @click="search">查询</a-button>
        <a-button @click="reset">重置</a-button>
        <a-button type="primary" @click="drawer.open('add', '新增')">
          新增
        </a-button>
      </tl-filter>

      <tl-table :visibleColumns="[0, 1, 2]">
        <a-table v-on="VOn" v-bind="VBind" :columns="columns">
          <template #bodyCell="{ column: { dataIndex }, record, text }">
            <template v-if="dataIndex === 'status'">
              <yc-status
                :status="getLabelByValue(text, statusOptions, 'status')"
              >
                {{ getLabelByValue(text, statusOptions) }}
              </yc-status>
            </template>
            <template v-if="dataIndex === 'action'">
              <action-group>
                <a-button
                  type="link"
                  @click="drawer.open('detail', '详情', record)"
                >
                  详情
                </a-button>
                <a-button
                  type="link"
                  @click="drawer.open('edit', '编辑', record)"
                >
                  编辑
                </a-button>
                <a-button type="link" danger @click="handleDel(record)">
                  删除
                </a-button>
                <a-button type="link" @click="handleToPro(record)">
                  跳转
                </a-button>
              </action-group>
            </template>
          </template>
        </a-table>
      </tl-table>
    </tl-main>

    <tl-drawer
      :title="drawer.title"
      :spin="{ spinning: drawer.spinning }"
      buttonsPosition="fixed"
    >
      <template #buttons>
        <a-button
          v-if="['edit', 'add'].includes(drawer.mode)"
          type="primary"
          @click="handleSave"
        >
          保存
        </a-button>
        <a-button @click="drawer.close">返回</a-button>
      </template>

      <DetailForm v-if="drawer.mode === 'detail'" />
      <EditForm
        v-if="['edit', 'add'].includes(drawer.mode)"
        ref="editForm"
      />
    </tl-drawer>
  </tl>
</template>

<style scoped lang="less"></style>
