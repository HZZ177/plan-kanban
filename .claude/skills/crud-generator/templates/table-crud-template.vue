<script setup lang="ts">
import { reactive, ref } from 'vue';
import { Modal } from 'ant-design-vue';
import { columns, PAGE_NAME, searchSchema, statusOptions } from './data';
import EditForm from './components/EditForm.vue';
import type { UseTableOptions } from '@kt/unity-hooks/src/useTable/types';
import { {{apiModule}}Api } from '@/api';
import { getLabelByValue } from '@/utils';
import useDrawer from '@/hooks/useDrawer.ts';
import { useForm } from '@/hooks/useForm.ts';

defineOptions({ name: PAGE_NAME });

// const router = useRouter();

/**@desc 筛选项 - 根据 searchSchema 自动生成初始值 */
const inParams = reactive<{{apiModule}}GetTableType.InParams>({
  // 初始值由 searchSchema 中的字段决定
  // 字符串类型默认为 ''，数组类型默认为 []
  {{inParamsFields}}
});
const { VBind: searchVBind, resetFields: reset } = useForm({
  schemas: searchSchema,
  modelRef: inParams,
  // 为false时默认支持url参数
  isForm: false,
  // 输入框回车时会触发
  onEnter: () => search(),
});

/**@desc 表格数据
 * */
const tableOptions = reactive<UseTableOptions>({
  currentKey: 'pageNo',
  pageSizeKey: 'pageSize',
  dataSourceKey: 'records',
  totalKey: 'total',
  immediate: false,
  columns,
  inParams,
});
const getTableData = async (params: {{apiModule}}GetTableType.Req) => {
  const { data } = await {{apiModule}}Api.{{apiListMethod}}(params);
  return data;
};
const { VBind, VOn, search, run, pagination, dataSource } = useTable(
  getTableData,
  tableOptions,
);

/**@desc 表格操作
 * */
// 删除
const handleDel = (row: any) => {
  Modal.confirm({
    title: `确定删除？`,
    onOk: async () => {
      const { code } = await {{apiModule}}Api.{{apiDeleteMethod}}(row.id);
      if (code === 200) {
        message.success('操作成功');
        await search();
      }
    },
    cancelText: '取消',
  });
};
// 跳转
const handleToPro = (row: {{apiModule}}GetTableType.record) => {
  // 示例
  // router.push('/demo/detail')
};

/**@desc 抽屉
 * */
const { drawer } = useDrawer(PAGE_NAME);
const editForm = ref();
const handleSave = async () => {
  try {
    await editForm.value?.save();
    drawer.close();
    search();
  } finally {
    drawer.hideSpinning();
  }
};

/**
 * 初始化--所有进入页面时就执行的逻辑都放在这里
 */
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
        <a-table v-on="VOn" v-bind="VBind">
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
          type="primary"
          @click="handleSave"
          v-if="['edit', 'add'].includes(drawer.mode)"
        >
          {{ '保存' }}
        </a-button>
        <a-button @click="drawer.close">{{ '返回' }}</a-button>
      </template>

      <!--     修改-->
      <edit-form ref="editForm" v-if="['edit', 'add'].includes(drawer.mode)" />
    </tl-drawer>
  </tl>
</template>

<style scoped lang="less"></style>
