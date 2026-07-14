import { createRouter, createWebHistory } from 'vue-router'

// 占位组件：实际渲染在 App.vue 中通过 v-if 控制
const Placeholder = { render: () => null }

const routes = [
  { path: '/', redirect: '/home' },
  { path: '/home', name: 'home', component: Placeholder },
  { path: '/stocks', name: 'stocks', component: Placeholder },
  { path: '/allocator2', name: 'allocator2', component: Placeholder },
  { path: '/contracts', name: 'contracts', component: Placeholder },
  { path: '/portfolio', name: 'portfolio', component: Placeholder },
  { path: '/users', name: 'users', component: Placeholder },
  { path: '/data', name: 'data', component: Placeholder },
  { path: '/sponsor', name: 'sponsor', component: Placeholder },
]

const router = createRouter({
  history: createWebHistory('/'),
  routes,
})

export default router
