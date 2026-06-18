<template>
  <section class="promotions-panel">
    <header class="promos-header">
      <div>
        <h2>Promociones</h2>
        <p>{{ activePromos }} activas ahora</p>
      </div>
      <div class="promo-badges">
        <span v-if="newCount" class="new-badge">{{ newCount }} NUEVA{{ newCount > 1 ? 'S' : '' }}</span>
        <span class="live-badge">
          <ion-icon :icon="flashOutline" />
          En vivo
        </span>
      </div>
    </header>

    <div class="promo-tabs">
      <button
        v-for="filter in filters"
        :key="filter.id"
        type="button"
        :class="{ active: activeFilter === filter.id }"
        @click="activeFilter = filter.id"
      >
        {{ filter.label }}
      </button>
    </div>

    <div class="promo-list">
      <article
        v-for="promo in filteredPromos"
        :key="promo.id"
        class="promo-card"
        :class="{ used: promo.used, expired: remaining(promo) <= 0, fresh: promo.isNew }"
        :style="promoCardStyle(promo)"
      >
        <div v-if="promo.isNew" class="fresh-banner" :style="{ color: promo.color, background: `${promo.color}22` }">
          <i :style="{ backgroundColor: promo.color }"></i>
          NUEVA · RECIEN LLEGADA
        </div>

        <header :style="{ backgroundColor: `${promo.color}20` }">
          <span :style="{ backgroundColor: `${promo.color}22`, color: promo.color }">{{ promo.icon }}</span>
          <div>
            <strong>{{ promo.stallName }}</strong>
            <small>{{ categoryLabel[promo.category] }}</small>
          </div>
          <b :style="{ color: promo.color, backgroundColor: `${promo.color}2c` }">{{ promo.discount }}</b>
        </header>

        <div class="promo-body">
          <h3>{{ promo.title }}</h3>
          <p>{{ promo.description }}</p>

          <small class="timer" :class="{ urgent: remaining(promo) < 120 && remaining(promo) > 0, expired: remaining(promo) <= 0 }">
            <ion-icon :icon="timeOutline" />
            <template v-if="remaining(promo) <= 0">Expirada</template>
            <template v-else>Vence en {{ countdownText(promo) }}</template>
          </small>

          <div v-if="remaining(promo) > 0 && !promo.used" class="promo-actions">
            <button type="button" :style="{ color: promo.color, borderColor: `${promo.color}55`, backgroundColor: `${promo.color}12` }" @click="navigatePromo(promo)">
              <ion-icon :icon="locationOutline" />
              Ver en mapa
            </button>
            <button type="button" :style="{ backgroundColor: promo.color }" @click="emit('use-promo', promo.id)">
              Canjear
            </button>
          </div>

          <strong v-if="promo.used" class="used-label">
            <ion-icon :icon="checkmarkCircleOutline" />
            Canjeada exitosamente
          </strong>
        </div>
      </article>

      <div v-if="!filteredPromos.length" class="empty-promos">
        <ion-icon :icon="pricetagOutline" />
        <p>Sin promos en esta categoria</p>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from 'vue';
import { IonIcon } from '@ionic/vue';
import {
  checkmarkCircleOutline,
  flashOutline,
  locationOutline,
  pricetagOutline,
  timeOutline,
} from 'ionicons/icons';
import type { Promotion, RouteTarget } from './types';

type PromoFilter = Promotion['category'] | 'all';

const props = defineProps<{
  promotions: Promotion[];
}>();

const emit = defineEmits<{
  'use-promo': [id: string];
  navigate: [target: RouteTarget];
  'switch-to-map': [];
  'clear-new': [id: string];
}>();

const activeFilter = ref<PromoFilter>('all');
const remainingById = ref<Record<string, number>>({});
const seenTimers = new Map<string, number>();

const filters = [
  { id: 'all' as const, label: 'Todo' },
  { id: 'drink' as const, label: 'Bebidas' },
  { id: 'food' as const, label: 'Comida' },
  { id: 'merch' as const, label: 'Merch' },
];

const categoryLabel: Record<Promotion['category'], string> = {
  drink: 'Bebidas',
  food: 'Comida',
  merch: 'Merch',
  experience: 'Experiencia',
};

const activePromos = computed(() => props.promotions.filter((promo) => !promo.used && remaining(promo) > 0).length);
const newCount = computed(() => props.promotions.filter((promo) => promo.isNew).length);
const filteredPromos = computed(() => {
  const sorted = [...props.promotions].sort((a, b) => Number(Boolean(b.isNew)) - Number(Boolean(a.isNew)) || remaining(a) - remaining(b));
  return activeFilter.value === 'all' ? sorted : sorted.filter((promo) => promo.category === activeFilter.value);
});

watch(
  () => props.promotions,
  (promotions) => {
    const next = { ...remainingById.value };
    promotions.forEach((promo) => {
      if (next[promo.id] === undefined) next[promo.id] = promo.expiresIn * 60;
      if (promo.isNew && !seenTimers.has(promo.id)) {
        const timer = window.setTimeout(() => {
          emit('clear-new', promo.id);
          seenTimers.delete(promo.id);
        }, 2000);
        seenTimers.set(promo.id, timer);
      }
    });
    remainingById.value = next;
  },
  { immediate: true, deep: true },
);

const interval = window.setInterval(() => {
  const next = { ...remainingById.value };
  Object.keys(next).forEach((id) => {
    next[id] = Math.max(0, next[id] - 1);
  });
  remainingById.value = next;
}, 1000);

onBeforeUnmount(() => {
  window.clearInterval(interval);
  seenTimers.forEach((timer) => window.clearTimeout(timer));
});

function remaining(promo: Promotion) {
  return remainingById.value[promo.id] ?? promo.expiresIn * 60;
}

function countdownText(promo: Promotion) {
  const total = remaining(promo);
  const minutes = Math.floor(total / 60);
  const seconds = total % 60;
  return `${minutes}:${String(seconds).padStart(2, '0')}`;
}

function promoCardStyle(promo: Promotion) {
  return {
    borderColor: promo.isNew ? `${promo.color}cc` : `${promo.color}55`,
    boxShadow: promo.isNew ? `0 0 20px ${promo.color}33` : undefined,
  };
}

function navigatePromo(promo: Promotion) {
  emit('navigate', {
    wx: promo.wx,
    wz: promo.wz,
    label: promo.stallName,
    color: promo.color,
    type: 'promo',
  });
  emit('clear-new', promo.id);
  emit('switch-to-map');
}
</script>

<style scoped>
.promotions-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
  height: 100%;
  overflow: hidden;
  padding: 8px 12px 12px;
}

.promos-header {
  align-items: center;
  display: flex;
  flex: 0 0 auto;
  justify-content: space-between;
  gap: 10px;
}

.promos-header h2 {
  color: #fff;
  font-size: 17px;
  font-weight: 900;
  margin: 0;
}

.promos-header p {
  color: #c084fc;
  font-size: 11px;
  margin: 3px 0 0;
}

.promo-badges {
  align-items: center;
  display: flex;
  gap: 7px;
}

.new-badge,
.live-badge {
  align-items: center;
  border-radius: 999px;
  display: flex;
  font-size: 10px;
  font-weight: 950;
  gap: 5px;
  min-height: 28px;
  padding: 0 9px;
  white-space: nowrap;
}

.new-badge {
  background: rgba(34, 197, 94, 0.18);
  border: 1px solid rgba(74, 222, 128, 0.42);
  color: #4ade80;
}

.live-badge {
  background: rgba(124, 58, 237, 0.2);
  border: 1px solid rgba(168, 85, 247, 0.3);
  color: #facc15;
}

.promo-tabs {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 14px;
  display: flex;
  flex: 0 0 auto;
  gap: 6px;
  padding: 5px;
}

.promo-tabs button {
  background: transparent;
  border: 0;
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.52);
  flex: 1;
  font-size: 11px;
  font-weight: 850;
  min-height: 34px;
}

.promo-tabs button.active {
  background: #7c3aed;
  box-shadow: 0 8px 22px rgba(124, 58, 237, 0.24);
  color: #fff;
}

.promo-list {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 11px;
  min-height: 0;
  overflow-y: auto;
  padding-bottom: 2px;
}

.promo-card {
  background: rgba(0, 0, 0, 0.34);
  border: 1px solid;
  border-radius: 16px;
  flex: 0 0 auto;
  overflow: hidden;
  transition: opacity 160ms ease, transform 160ms ease;
}

.promo-card.used,
.promo-card.expired {
  opacity: 0.5;
}

.fresh-banner {
  align-items: center;
  display: flex;
  font-size: 10px;
  font-weight: 950;
  gap: 8px;
  letter-spacing: 0.08em;
  min-height: 26px;
  padding: 0 12px;
}

.fresh-banner i {
  animation: pulseDot 1s ease infinite;
  border-radius: 999px;
  height: 7px;
  width: 7px;
}

.promo-card header {
  align-items: center;
  display: flex;
  gap: 10px;
  padding: 10px 12px;
}

.promo-card header > span {
  align-items: center;
  border-radius: 12px;
  display: flex;
  flex: 0 0 auto;
  font-size: 18px;
  height: 42px;
  justify-content: center;
  width: 42px;
}

.promo-card header div {
  flex: 1;
  min-width: 0;
}

.promo-card header strong,
.promo-card header small {
  display: block;
}

.promo-card header strong {
  color: #fff;
  font-size: 13px;
}

.promo-card header small {
  color: rgba(255, 255, 255, 0.5);
  font-size: 10px;
  margin-top: 2px;
}

.promo-card header b {
  border-radius: 10px;
  font-size: 14px;
  font-weight: 950;
  padding: 7px 9px;
}

.promo-body {
  background: rgba(0, 0, 0, 0.24);
  padding: 11px 12px 12px;
}

.promo-body h3 {
  color: #fff;
  font-size: 14px;
  margin: 0 0 5px;
}

.promo-body p {
  color: rgba(255, 255, 255, 0.56);
  font-size: 11px;
  line-height: 1.35;
  margin: 0 0 9px;
}

.timer {
  align-items: center;
  color: rgba(255, 255, 255, 0.46);
  display: flex;
  font-size: 11px;
  gap: 6px;
}

.timer.urgent {
  color: #f87171;
  font-weight: 850;
}

.timer.expired {
  color: #ef4444;
}

.promo-actions {
  display: flex;
  gap: 8px;
  padding-top: 10px;
}

.promo-actions button {
  align-items: center;
  border: 1px solid;
  border-radius: 12px;
  color: #fff;
  display: flex;
  flex: 1;
  font-size: 12px;
  font-weight: 850;
  gap: 6px;
  justify-content: center;
  min-height: 38px;
}

.used-label {
  align-items: center;
  color: #4ade80;
  display: flex;
  font-size: 12px;
  gap: 6px;
  margin-top: 10px;
}

.empty-promos {
  align-items: center;
  color: rgba(255, 255, 255, 0.3);
  display: flex;
  flex: 1;
  flex-direction: column;
  justify-content: center;
  min-height: 160px;
}

.empty-promos ion-icon {
  font-size: 34px;
  margin-bottom: 8px;
}

.empty-promos p {
  font-size: 14px;
  margin: 0;
}

@keyframes pulseDot {
  50% {
    opacity: 0.35;
    transform: scale(0.72);
  }
}
</style>
