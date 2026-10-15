import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import { backdropDismiss } from './directives/backdropDismiss'

const app = createApp(App)
app.directive('backdrop-dismiss', backdropDismiss)
app.mount('#app')
