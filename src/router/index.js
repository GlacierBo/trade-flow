import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/home' },
  { path: '/home', name: 'home' },
  { path: '/stocks', name: 'stocks' },
  { path: '/allocator', name: 'allocator' },
  { path: '/allocator2', name: 'allocator2' },
  { path: '/contracts', name: 'contracts' },
  { path: '/portfolio', name: 'portfolio' },
  { path: '/users', name: 'users' },
  { path: '/sponsor', name: 'sponsor' },
]

const router = createRouter({
  history: createWebHistory('/trade-flow/'),
  routes,
})

export default router
