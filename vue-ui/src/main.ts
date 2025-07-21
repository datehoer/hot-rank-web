import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createI18n } from 'vue-i18n'
import en from './locales/en'
import zh from './locales/zh'
import { createHead } from '@vueuse/head';


const app = createApp(App)
const i18n = createI18n({
  legacy: false,
  locale: localStorage.getItem('locale') || 'zh',
  fallbackLocale: 'en',
  messages: {
    en,
    zh,
  },
})
const head = createHead();

app.use(head);
app.use(router)
app.use(i18n)
app.mount('#app')
