import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import WorkbenchPage from '../pages/kanban/WorkbenchPage.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'workbench',
    component: WorkbenchPage,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
