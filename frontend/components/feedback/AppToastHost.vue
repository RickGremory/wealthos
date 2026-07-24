<script setup lang="ts">
const notifications = useNotificationsStore()
</script>

<template>
  <div class="toast-host" aria-live="polite" aria-relevant="additions">
    <div
      v-for="toast in notifications.toasts"
      :key="toast.id"
      class="toast"
      :class="`toast--${toast.tone}`"
      role="status"
    >
      <div class="stack-sm">
        <strong>{{ toast.title }}</strong>
        <p v-if="toast.message" class="toast__message">{{ toast.message }}</p>
      </div>
      <button type="button" class="toast__close" @click="notifications.dismiss(toast.id)">
        ×
      </button>
    </div>
  </div>
</template>

<style scoped>
.toast-host {
  position: fixed;
  right: var(--space-4);
  bottom: var(--space-4);
  z-index: 100;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  width: min(100% - 2rem, 22rem);
  pointer-events: none;
}

.toast {
  pointer-events: auto;
  display: flex;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-lg);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-lg);
  animation: toast-in 220ms ease-out;
}

.toast--success {
  border-color: #abefc6;
  background: var(--color-success-muted);
}

.toast--danger {
  border-color: #fecdca;
  background: var(--color-danger-muted);
}

.toast--warning {
  border-color: #fedf89;
  background: var(--color-warning-muted);
}

.toast__message {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-text-muted);
}

.toast__close {
  border: 0;
  background: transparent;
  cursor: pointer;
  font-size: 1.25rem;
  line-height: 1;
  color: var(--color-text-muted);
}

@keyframes toast-in {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
