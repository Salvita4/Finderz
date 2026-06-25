<template>
  <Transition name="panic-fade">
    <div v-if="open" class="panic-modal">
      <Transition name="panic-sheet" appear>
        <section class="panic-sheet">
          <div class="sheet-handle"></div>

          <header>
            <div class="panic-title">
              <span>
                <ion-icon :icon="shieldOutline" />
              </span>
              <div>
                <h2>Modo Panico</h2>
                <p>Selecciona donde ir</p>
              </div>
            </div>
            <button type="button" aria-label="Cerrar" @click="emit('close')">
              <ion-icon :icon="closeOutline" />
            </button>
          </header>

          <div class="panic-options">
            <template v-if="faros.length">
              <button v-for="faro in faros" :key="faro.id" type="button" class="panic-option faro" @click="goToFaro(faro)">
                <span class="option-icon" :style="{ backgroundColor: friendColors[faro.id]?.bg, borderColor: friendColors[faro.id]?.bg }">
                  <ion-icon :icon="star" />
                </span>
                <div>
                  <strong>
                    Ir a {{ faro.name }}
                    <em>FARO</em>
                  </strong>
                  <small>Contacto de seguridad · bateria {{ faro.battery }}%</small>
                </div>
                <ion-icon :icon="navigateOutline" />
              </button>
            </template>

            <div v-else class="panic-option disabled">
              <span class="option-icon">
                <ion-icon :icon="star" />
              </span>
              <div>
                <strong>Sin faros activos</strong>
                <small>Marca un amigo como faro en Grupos</small>
              </div>
            </div>

            <button type="button" class="panic-option exit" @click="goTo({ wx: 0, wz: -16, label: 'Salida Norte', color: '#f97316', type: 'panic' })">
              <span class="option-icon">
                <ion-icon :icon="exitOutline" />
              </span>
              <div>
                <strong>Salida mas cercana</strong>
                <small>Salida Norte · ~2 min caminando</small>
              </div>
              <ion-icon :icon="navigateOutline" />
            </button>

            <button type="button" class="panic-option medical" @click="goTo({ wx: -3.8, wz: -3.8, label: 'Puesto Medico', color: '#ef4444', type: 'panic' })">
              <span class="option-icon">
                <ion-icon :icon="heartOutline" />
              </span>
              <div>
                <strong>Puesto Medico</strong>
                <small>Emergencias · Abierto 24hs</small>
              </div>
              <ion-icon :icon="navigateOutline" />
            </button>
          </div>

          <button class="security-call" type="button">
            <ion-icon :icon="callOutline" />
            Llamar a Seguridad · 911
          </button>
        </section>
      </Transition>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { IonIcon } from '@ionic/vue';
import {
  callOutline,
  closeOutline,
  exitOutline,
  heartOutline,
  navigateOutline,
  shieldOutline,
  star,
} from 'ionicons/icons';
import { friendColors, percentToWorld, type Friend, type RouteTarget } from './types';

const props = defineProps<{
  open: boolean;
  friends: Friend[];
}>();

const emit = defineEmits<{
  close: [];
  navigate: [target: RouteTarget];
  'switch-to-map': [];
}>();

const faros = computed(() => props.friends.filter((friend) => friend.faro && friend.status === 'online'));

function goTo(target: RouteTarget) {
  emit('navigate', target);
  emit('switch-to-map');
  emit('close');
}

function goToFaro(faro: Friend) {
  const [wx, wz] = percentToWorld(faro.x, faro.y);
  goTo({
    wx,
    wz,
    label: faro.name,
    color: friendColors[faro.id]?.bg ?? '#ff3366',
    type: 'panic',
  });
}
</script>

<style scoped>
.panic-modal {
  align-items: flex-end;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(10px);
  display: flex;
  inset: 0;
  position: absolute;
  z-index: 50;
}

.panic-sheet {
  background: #1a0015;
  border-radius: 28px 28px 0 0;
  border-top: 2px solid rgba(239, 68, 68, 0.62);
  box-shadow: 0 -20px 60px rgba(220, 38, 38, 0.25);
  padding: 14px 18px calc(var(--ion-safe-area-bottom, 0px) + 20px);
  width: 100%;
}

.sheet-handle {
  background: rgba(255, 255, 255, 0.22);
  border-radius: 999px;
  height: 4px;
  margin: 0 auto 17px;
  width: 42px;
}

.panic-sheet header {
  align-items: center;
  display: flex;
  justify-content: space-between;
  margin-bottom: 18px;
}

.panic-title {
  align-items: center;
  display: flex;
  gap: 11px;
}

.panic-title > span,
.option-icon {
  align-items: center;
  border-radius: 999px;
  display: flex;
  flex: 0 0 auto;
  justify-content: center;
}

.panic-title > span {
  background: rgba(220, 38, 38, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.5);
  color: #f87171;
  font-size: 22px;
  height: 42px;
  width: 42px;
}

.panic-title h2 {
  color: #fff;
  font-size: 19px;
  font-weight: 950;
  margin: 0;
}

.panic-title p {
  color: rgba(248, 113, 113, 0.82);
  font-size: 11px;
  margin: 2px 0 0;
}

.panic-sheet header button {
  align-items: center;
  background: rgba(255, 255, 255, 0.1);
  border: 0;
  border-radius: 999px;
  color: rgba(255, 255, 255, 0.64);
  display: flex;
  height: 34px;
  justify-content: center;
  width: 34px;
}

.panic-options {
  display: grid;
  gap: 10px;
  margin-bottom: 14px;
}

.panic-option {
  align-items: center;
  border: 1px solid;
  border-radius: 17px;
  display: flex;
  gap: 12px;
  min-height: 74px;
  padding: 12px;
  text-align: left;
}

.panic-option.faro {
  background: rgba(127, 29, 29, 0.32);
  border-color: rgba(239, 68, 68, 0.42);
}

.panic-option.exit {
  background: rgba(124, 45, 18, 0.24);
  border-color: rgba(249, 115, 22, 0.34);
}

.panic-option.medical {
  background: rgba(127, 29, 29, 0.24);
  border-color: rgba(239, 68, 68, 0.34);
}

.panic-option.disabled {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.1);
  opacity: 0.55;
}

.option-icon {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.14);
  color: #fff;
  font-size: 22px;
  height: 45px;
  width: 45px;
}

.exit .option-icon {
  background: rgba(249, 115, 22, 0.18);
  border-color: rgba(249, 115, 22, 0.42);
  color: #fb923c;
}

.medical .option-icon {
  background: rgba(239, 68, 68, 0.18);
  border-color: rgba(239, 68, 68, 0.42);
  color: #f87171;
}

.panic-option div {
  flex: 1;
  min-width: 0;
}

.panic-option strong,
.panic-option small {
  display: block;
}

.panic-option strong {
  align-items: center;
  color: #fff;
  display: flex;
  flex-wrap: wrap;
  font-size: 14px;
  gap: 6px;
}

.panic-option em {
  background: rgba(250, 204, 21, 0.18);
  border-radius: 999px;
  color: #facc15;
  font-size: 9px;
  font-style: normal;
  padding: 3px 6px;
}

.panic-option small {
  color: rgba(255, 255, 255, 0.52);
  font-size: 11px;
  margin-top: 3px;
}

.panic-option > ion-icon {
  color: rgba(255, 255, 255, 0.62);
  flex: 0 0 auto;
}

.security-call {
  align-items: center;
  background: #dc2626;
  border: 0;
  border-radius: 17px;
  box-shadow: 0 4px 20px rgba(239, 68, 68, 0.5);
  color: #fff;
  display: flex;
  font-size: 16px;
  font-weight: 950;
  gap: 8px;
  justify-content: center;
  min-height: 52px;
  width: 100%;
}

.panic-fade-enter-active,
.panic-fade-leave-active {
  transition: opacity 180ms ease;
}

.panic-fade-enter-from,
.panic-fade-leave-to {
  opacity: 0;
}

.panic-sheet-enter-active {
  transition: transform 320ms cubic-bezier(0.2, 0.8, 0.2, 1);
}

.panic-sheet-leave-active {
  transition: transform 200ms ease;
}

.panic-sheet-enter-from,
.panic-sheet-leave-to {
  transform: translateY(100%);
}
</style>
