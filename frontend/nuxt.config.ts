// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },

  modules: ['@pinia/nuxt', '@nuxt/eslint'],

  components: [
    { path: '~/components/ui', pathPrefix: false },
    { path: '~/components/finance', pathPrefix: false },
    { path: '~/components/layout', pathPrefix: false },
    { path: '~/components/feedback', pathPrefix: false },
  ],

  css: [
    '~/assets/css/tokens.css',
    '~/assets/css/main.css',
    '~/assets/css/utilities.css',
  ],

  runtimeConfig: {
    public: {
      apiBaseUrl: 'http://127.0.0.1:8000/api/v1',
      featureFlags: {
        taxesMx: false,
        recurringDetection: false,
        advancedPayoff: false,
        taxEvidence: false,
        planning: true,
        taxes: true,
        debts: true,
        goals: true,
      },
    },
  },

  app: {
    head: {
      title: 'WealthOS',
      meta: [
        { name: 'description', content: 'WealthOS — gestión patrimonial personal' },
        { name: 'theme-color', content: '#0b3d3a' },
      ],
      htmlAttrs: { lang: 'es' },
    },
  },

  typescript: {
    strict: true,
    typeCheck: false,
  },

  experimental: {
    appManifest: false,
  },
})
