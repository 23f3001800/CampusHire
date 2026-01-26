<script>
import Navbar from "./componet/Nabvar.vue";
import Footer from "./componet/Footer.vue";

export default {
  data() {
    return {};
  },
  components: {
    Navbar,
    Footer,
  },
};
</script>

<template>
  <Navbar />
  <router-view />
  <Footer />
</template>

<style scoped></style>