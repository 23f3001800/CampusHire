
<template>
  <div id="app">
    <Navbar v-if="showShell" />
    <main class="flex-grow-1">
      <router-view />
    </main>
    <Footer v-if="showShell" />
  </div>
</template>

<script>
import Navbar from "./components/Nabvar.vue";
import Footer from "./components/Footer.vue";
import { useUserStore } from '@/stores/userStore'

const AUTH_PAGES = ['/login', '/signup']

export default {
  name: 'App',
  components: { Navbar, Footer },
  setup() {
    const userStore = useUserStore()
    return { userStore }
  },
  computed: {
    showShell() {
      return !AUTH_PAGES.includes(this.$route.path)
    },
  },
  async mounted() {
    await this.userStore.initialize()
  },
}
</script>

<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f8f9fa;
}
</style>