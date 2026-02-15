<template>
  <div class="chart-container">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js'
Chart.register(...registerables)

export default {
  name: 'ApplicationsChart',
  props: {
    data: {
      type: Object,
      required: true,
      // Expected: { applied: 10, shortlisted: 5, selected: 2, rejected: 3 }
    },
    type: {
      type: String,
      default: 'pie', // 'pie', 'doughnut', 'bar'
    },
  },
  data: () => ({
    chart: null,
  }),
  mounted() {
    this.renderChart()
  },
  watch: {
    data: {
      deep: true,
      handler() {
        this.renderChart()
      },
    },
  },
  beforeUnmount() {
    if (this.chart) this.chart.destroy()
  },
  methods: {
    renderChart() {
      if (this.chart) this.chart.destroy()
      
      const ctx = this.$refs.chartCanvas.getContext('2d')
      
      const labels = ['Applied', 'Shortlisted', 'Selected', 'Rejected']
      const values = [
        this.data.applied || 0,
        this.data.shortlisted || 0,
        this.data.selected || 0,
        this.data.rejected || 0,
      ]
      
      this.chart = new Chart(ctx, {
        type: this.type,
        data: {
          labels,
          datasets: [{
            data: values,
            backgroundColor: [
              'rgba(13, 110, 253, 0.8)',  // blue
              'rgba(13, 202, 240, 0.8)',  // cyan
              'rgba(25, 135, 84, 0.8)',   // green
              'rgba(220, 53, 69, 0.8)',   // red
            ],
            borderColor: [
              'rgb(13, 110, 253)',
              'rgb(13, 202, 240)',
              'rgb(25, 135, 84)',
              'rgb(220, 53, 69)',
            ],
            borderWidth: 2,
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          plugins: {
            legend: {
              display: true,
              position: 'bottom',
            },
            tooltip: {
              callbacks: {
                label: (ctx) => `${ctx.label}: ${ctx.parsed}`,
              },
            },
          },
        },
      })
    },
  },
}
</script>

<style scoped>
.chart-container {
  position: relative;
  height: 300px;
  width: 100%;
}
</style>