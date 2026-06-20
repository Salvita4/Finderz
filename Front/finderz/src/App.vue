<template>
  <ion-app>
    <ion-page>
      <ion-content fullscreen class="finderz-content">
        <div class="app-shell">
          <div class="aurora"></div>

          <section v-if="adminMode" class="screen admin-screen">
            <header class="topbar admin-topbar">
              <div>
                <h1>Back Office</h1>
                <p>Admin · Finderz Festival</p>
              </div>
              <button class="pill ghost" type="button" @click="adminMode = false">
                <ion-icon :icon="closeOutline" />
                Salir
              </button>
            </header>

            <AdminDashboard @launch-promo="launchPromo" />
          </section>

          <section v-else class="screen">
            <header class="topbar">
              <button class="brand" type="button" @click="activeTab = 'map'">
                <span class="brand-mark">
                  <ion-img src="/logoFinderzSinTexto.png" />
                </span>
                <strong>FINDERZ</strong>
              </button>

              <button v-if="routeTarget" class="route-chip" type="button" :style="routeChipStyle" @click="routeTarget = null">
                <ion-icon :icon="locationOutline" />
                <span>{{ routeTarget.label }}</span>
                <ion-icon :icon="closeOutline" />
              </button>

              <button class="icon-btn" type="button" aria-label="Modo administrador" @click="adminMode = true">
                <ion-icon :icon="gridOutline" />
              </button>
            </header>

            <main class="content-stage">
              <section v-show="activeTab === 'map'" class="tab-panel map-panel">
                <div class="map-wrap">
                  <FestivalMapIsometric :key="mapKey" :friends="friends" :pois="pois" :route-target="routeTarget" />
                  <button class="panic-button" type="button" aria-label="Abrir asistencia" @click="showPanic = true">
                    <ion-icon :icon="shieldOutline" />
                  </button>
                </div>

                <div class="poi-strip">
                  <button
                    v-for="poi in quickPois"
                    :key="poi.id"
                    type="button"
                    :class="{ active: selectedPoi === poi.id }"
                    @click="navigatePoi(poi)"
                  >
                    <span>{{ poi.icon }}</span>
                    {{ poi.name }}
                  </button>
                </div>

                <div class="friend-strip">
                  <button v-for="friend in friends" :key="friend.id" type="button" @click="navigateFriend(friend)">
                    <i :style="friendDotStyle(friend)"></i>
                    <span>{{ friend.name }}</span>
                    <small v-if="friend.status === 'offline'">off</small>
                    <ion-icon v-if="friend.faro" :icon="star" />
                  </button>
                </div>
              </section>

              <section v-show="activeTab === 'groups'" class="tab-panel">
                <GroupsPanel
                  :friends="friends"
                  @toggle-faro="toggleFaro"
                  @add-friend="addFriend"
                  @navigate="routeTarget = $event"
                  @switch-to-map="activeTab = 'map'"
                />
              </section>

              <section v-show="activeTab === 'agenda'" class="tab-panel">
                <AgendaPanel
                  @navigate="routeTarget = $event"
                  @switch-to-map="activeTab = 'map'"
                />
              </section>

              <section v-show="activeTab === 'promos'" class="tab-panel">
                <PromotionsPanel
                  :promotions="promotions"
                  @use-promo="usePromo"
                  @navigate="routeTarget = $event"
                  @switch-to-map="activeTab = 'map'"
                  @clear-new="clearNewPromo"
                />
              </section>

              <section v-show="activeTab === 'profile'" class="tab-panel scroll-panel profile-panel">
                <div class="profile-avatar">
                  <ion-icon :icon="personOutline" />
                </div>
                <h2>Tu Perfil</h2>
                <p>ID: FNZ-4729</p>
                <div class="profile-stats">
                  <article v-for="stat in profileStats" :key="stat.label">
                    <span>{{ stat.label }}</span>
                    <strong>{{ stat.value }}</strong>
                  </article>
                </div>
                <button class="profile-admin" type="button" @click="adminMode = true">
                  <ion-icon :icon="gridOutline" />
                  Modo Administrador
                  <ion-icon :icon="chevronForwardOutline" />
                </button>
              </section>
            </main>

            <nav class="bottom-tabs">
              <button v-for="tab in tabs" :key="tab.id" type="button" :class="{ active: activeTab === tab.id }" @click="activeTab = tab.id">
                <span>
                  <ion-icon :icon="tab.icon" />
                  <b v-if="tab.id === 'promos' && promoBadge && activeTab !== 'promos'">{{ promoBadge }}</b>
                </span>
                {{ tab.label }}
              </button>
            </nav>
          </section>

          <div v-if="promoAlert" class="promo-toast" :style="{ borderColor: `${promoAlert.color}66` }">
            <button type="button" @click="promoAlert = null">
              <ion-icon :icon="closeOutline" />
            </button>
            <strong :style="{ color: promoAlert.color }">NUEVA PROMO</strong>
            <p>{{ promoAlert.title }}</p>
            <small>{{ promoAlert.stallName }} · {{ promoAlert.discount }}</small>
          </div>

          <PanicModal
            :open="showPanic"
            :friends="friends"
            @close="showPanic = false"
            @navigate="routeTarget = $event"
            @switch-to-map="activeTab = 'map'"
          />

        </div>
      </ion-content>
    </ion-page>
  </ion-app>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { IonApp, IonContent, IonIcon, IonPage } from '@ionic/vue';
import {
  calendarOutline,
  chevronForwardOutline,
  closeOutline,
  gridOutline,
  locationOutline,
  navigateCircleOutline,
  peopleOutline,
  personOutline,
  pricetagOutline,
  shieldOutline,
  star,
} from 'ionicons/icons';
import FestivalMapIsometric from './components/finderz/FestivalMapIsometric.vue';
import AdminDashboard from './components/finderz/AdminDashboard.vue';
import AgendaPanel from './components/finderz/AgendaPanel.vue';
import GroupsPanel from './components/finderz/GroupsPanel.vue';
import PanicModal from './components/finderz/PanicModal.vue';
import PromotionsPanel from './components/finderz/PromotionsPanel.vue';
import { api } from './services/api';
import {
  festivalPois,
  friendColors,
  initialFriends,
  initialPromotions,
  percentToWorld,
  type Friend,
  type POI,
  type Promotion,
  type RouteTarget,
} from './components/finderz/types';

type TabId = 'map' | 'groups' | 'agenda' | 'promos' | 'profile';

const activeTab = ref<TabId>('map');
const friends = ref<Friend[]>([...initialFriends]);
const promotions = ref<Promotion[]>([...initialPromotions]);
const pois = ref<POI[]>([...festivalPois]);
const routeTarget = ref<RouteTarget | null>(null);
const selectedPoi = ref<string | null>(null);
const showPanic = ref(false);
const adminMode = ref(false);
const promoAlert = ref<Promotion | null>(null);
const mapKey = ref(0);

const tabs = [
  { id: 'map' as const, label: 'Mapa', icon: navigateCircleOutline },
  { id: 'groups' as const, label: 'Grupos', icon: peopleOutline },
  { id: 'agenda' as const, label: 'Agenda', icon: calendarOutline },
  { id: 'promos' as const, label: 'Promos', icon: pricetagOutline },
  { id: 'profile' as const, label: 'Perfil', icon: personOutline },
];

const quickPois = computed(() => pois.value.filter((poi) => poi.type !== 'restroom').slice(0, 9));
const activePromos = computed(() => promotions.value.filter((promo) => !promo.used).length);
const newPromoCount = computed(() => promotions.value.filter((promo) => promo.isNew).length);
const promoBadge = computed(() => newPromoCount.value || activePromos.value);
const routeChipStyle = computed(() => routeTarget.value ? {
  color: routeTarget.value.color,
  borderColor: `${routeTarget.value.color}66`,
  backgroundColor: `${routeTarget.value.color}1f`,
} : undefined);

const profileStats = [
  { label: 'Distancia recorrida', value: '3.2 km' },
  { label: 'Amigos encontrados', value: '8/12' },
  { label: 'Eventos asistidos', value: '5' },
  { label: 'Bateria del dispositivo', value: '78%' },
];

function poiColor(type: POI['type']) {
  return {
    stage: '#9d4edd',
    food: '#f59e0b',
    bar: '#f59e0b',
    restroom: '#6b7280',
    info: '#3b82f6',
    medical: '#ef4444',
    exit: '#22c55e',
    vip: '#ffd700',
  }[type];
}

function navigatePoi(poi: POI) {
  selectedPoi.value = poi.id;
  routeTarget.value = { wx: poi.wx, wz: poi.wz, label: poi.name, color: poiColor(poi.type), type: poi.type === 'exit' ? 'exit' : 'poi' };
}

function navigateFriend(friend: Friend, switchToMap = false) {
  if (friend.status === 'offline') return;
  const [wx, wz] = percentToWorld(friend.x, friend.y);
  routeTarget.value = { wx, wz, label: friend.name, color: friendColors[friend.id]?.bg ?? '#00ff88', type: 'friend' };
  if (switchToMap) activeTab.value = 'map';
}

async function loadBackendData() {
  try {
    const [backendFriends, backendPois, backendPromotions] = await Promise.all([
      api.getFriends(),
      api.getPois(),
      api.getPromotions(),
    ]);
    friends.value = backendFriends;
    pois.value = backendPois;
    promotions.value = backendPromotions;
    mapKey.value += 1;
  } catch (error) {
    console.warn('No se pudo conectar con el backend, se usan datos locales.', error);
  }
}

async function toggleFaro(id: string) {
  const previous = [...friends.value];
  friends.value = friends.value.map((friend) => friend.id === id ? { ...friend, faro: !friend.faro } : friend);
  try {
    const updated = await api.toggleFaro(id);
    friends.value = friends.value.map((friend) => friend.id === id ? updated : friend);
  } catch (error) {
    friends.value = previous;
    console.warn('No se pudo actualizar el faro.', error);
  }
}

async function addFriend(friend: Friend) {
  if (friends.value.some((item) => item.id === friend.id)) return;
  friends.value = [...friends.value, friend];
  mapKey.value += 1;
  try {
    const created = await api.createFriend(friend);
    friends.value = friends.value.map((item) => item.id === friend.id ? created : item);
  } catch (error) {
    friends.value = friends.value.filter((item) => item.id !== friend.id);
    mapKey.value += 1;
    console.warn('No se pudo agregar el amigo.', error);
  }
}

async function usePromo(id: string) {
  const previous = [...promotions.value];
  promotions.value = promotions.value.map((promo) => promo.id === id ? { ...promo, used: true, isNew: false } : promo);
  try {
    const updated = await api.usePromotion(id);
    promotions.value = promotions.value.map((promo) => promo.id === id ? updated : promo);
  } catch (error) {
    promotions.value = previous;
    console.warn('No se pudo usar la promo.', error);
  }
}

async function clearNewPromo(id: string) {
  const previous = [...promotions.value];
  promotions.value = promotions.value.map((promo) => promo.id === id ? { ...promo, isNew: false } : promo);
  try {
    const updated = await api.clearNewPromotion(id);
    promotions.value = promotions.value.map((promo) => promo.id === id ? updated : promo);
  } catch (error) {
    promotions.value = previous;
    console.warn('No se pudo limpiar la promo nueva.', error);
  }
}

async function launchPromo(promo: Promotion) {
  promotions.value = [promo, ...promotions.value];
  promoAlert.value = promo;
  try {
    const created = await api.createPromotion(promo);
    promotions.value = promotions.value.map((item) => item.id === promo.id ? created : item);
    promoAlert.value = created;
  } catch (error) {
    promotions.value = promotions.value.filter((item) => item.id !== promo.id);
    promoAlert.value = null;
    console.warn('No se pudo lanzar la promo.', error);
    return;
  }
  setTimeout(() => {
    if (promoAlert.value?.id === promo.id) promoAlert.value = null;
  }, 5000);
}

function friendDotStyle(friend: Friend) {
  const color = friend.status === 'online' ? friendColors[friend.id]?.bg : '#555555';
  return {
    backgroundColor: color,
    boxShadow: friend.status === 'online' ? `0 0 7px ${friendColors[friend.id]?.glow}` : 'none',
  };
}

onMounted(loadBackendData);

</script>

<style>
:root {
  --finderz-bg: #090113;
  --finderz-panel: rgba(7, 2, 14, 0.62);
  --finderz-line: rgba(184, 129, 255, 0.24);
  --finderz-text-soft: rgba(255, 255, 255, 0.62);
}

html,
body,
#app {
  height: 100%;
  background: var(--finderz-bg);
}

ion-content.finderz-content {
  --background: #090113;
}

button {
  font: inherit;
}

.app-shell {
  background: radial-gradient(circle at 50% 0%, rgba(157, 78, 221, 0.34), transparent 34%), linear-gradient(135deg, #240046, #3c096c 42%, #0a0014);
  color: #fff;
  height: 100dvh;
  overflow: hidden;
  position: relative;
}

.screen {
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
  z-index: 1;
}

.aurora {
  background: radial-gradient(circle at 16% 20%, rgba(0, 217, 255, 0.18), transparent 22%), radial-gradient(circle at 84% 72%, rgba(255, 51, 102, 0.18), transparent 20%);
  inset: 0;
  pointer-events: none;
  position: absolute;
}

.topbar {
  align-items: center;
  display: flex;
  flex: 0 0 auto;
  justify-content: space-between;
  min-height: 56px;
  padding: calc(var(--ion-safe-area-top, 0px) + 8px) 12px 8px;
}

.brand,
.icon-btn,
.pill,
.route-chip,
.bottom-tabs button,
.poi-strip button,
.friend-strip button {
  align-items: center;
  border: 0;
  color: inherit;
  display: inline-flex;
}

.brand {
  background: transparent;
  gap: 8px;
  padding: 0;
}

.brand-mark,
.icon-btn {
  align-items: center;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 10px;
  display: inline-flex;
  height: 34px;
  justify-content: center;
  width: 34px;
}

.brand-mark {
  background: rgba(157, 78, 221, 0.46);
  color: #d9c2ff;
}

.icon-btn {
  flex: 0 0 auto;
}

.icon-btn.small {
  border-radius: 9px;
  height: 34px;
  width: 34px;
}

.icon-btn.accent {
  background: rgba(157, 78, 221, 0.28);
  border-color: rgba(157, 78, 221, 0.52);
  color: #d9c2ff;
}

.route-chip {
  border: 1px solid;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 800;
  gap: 5px;
  max-width: 44%;
  overflow: hidden;
  padding: 6px 8px;
  white-space: nowrap;
}

.route-chip span {
  overflow: hidden;
  text-overflow: ellipsis;
}

.content-stage {
  flex: 1;
  min-height: 0;
  position: relative;
}

.tab-panel {
  inset: 0;
  position: absolute;
}

.map-panel {
  display: flex;
  flex-direction: column;
}

.map-wrap {
  flex: 1;
  min-height: 0;
  position: relative;
}

.panic-button {
  align-items: center;
  background: #dc2626;
  border: 2px solid rgba(252, 165, 165, 0.7);
  border-radius: 999px;
  box-shadow: 0 0 24px rgba(239, 68, 68, 0.68);
  color: #fff;
  display: flex;
  font-size: 22px;
  height: 50px;
  justify-content: center;
  position: absolute;
  right: 14px;
  top: 14px;
  width: 50px;
  z-index: 3;
}

.poi-strip,
.friend-strip {
  background: rgba(0, 0, 0, 0.62);
  border-top: 1px solid var(--finderz-line);
  display: flex;
  flex: 0 0 auto;
  gap: 7px;
  overflow-x: auto;
  padding: 8px 10px;
}

.poi-strip button {
  background: rgba(0, 0, 0, 0.38);
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 9px;
  flex: 0 0 auto;
  font-size: 11px;
  font-weight: 700;
  gap: 5px;
  padding: 7px 9px;
}

.poi-strip button.active {
  background: #7c3aed;
  border-color: #c4b5fd;
}

.friend-strip {
  padding-bottom: calc(var(--ion-safe-area-bottom, 0px) + 8px);
}

.friend-strip button {
  background: transparent;
  flex: 0 0 auto;
  gap: 6px;
  padding: 4px 2px;
}

.friend-strip i {
  border: 1px solid rgba(255, 255, 255, 0.36);
  border-radius: 999px;
  height: 12px;
  width: 12px;
}

.friend-strip span {
  color: rgba(255, 255, 255, 0.82);
  font-size: 11px;
  font-weight: 700;
}

.friend-strip small {
  color: rgba(255, 255, 255, 0.34);
  font-size: 9px;
}

.scroll-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
  height: 100%;
  overflow-y: auto;
  padding: 8px 12px 12px;
}

.profile-stats article,
.profile-admin {
  background: var(--finderz-panel);
  border: 1px solid var(--finderz-line);
  border-radius: 14px;
}

.profile-panel p {
  color: var(--finderz-text-soft);
  font-size: 11px;
}

.profile-panel h2 {
  font-size: 16px;
  line-height: 1.2;
  margin: 0;
}

.profile-panel {
  align-items: center;
  text-align: center;
}

.profile-avatar {
  align-items: center;
  background: linear-gradient(135deg, #7c3aed, #ec4899);
  border-radius: 999px;
  box-shadow: 0 0 32px rgba(157, 78, 221, 0.5);
  display: flex;
  font-size: 42px;
  height: 84px;
  justify-content: center;
  margin-top: 18px;
  width: 84px;
}

.profile-stats {
  display: grid;
  gap: 9px;
  margin-top: 18px;
  width: 100%;
}

.profile-stats article,
.profile-admin {
  align-items: center;
  display: flex;
  justify-content: space-between;
  padding: 13px;
  text-align: left;
}

.profile-stats span {
  color: var(--finderz-text-soft);
  font-size: 12px;
}

.profile-admin {
  color: #d8b4fe;
  font-weight: 900;
  margin-top: 10px;
  width: 100%;
}

.bottom-tabs {
  align-items: center;
  background: rgba(0, 0, 0, 0.82);
  border-top: 1px solid rgba(184, 129, 255, 0.32);
  display: flex;
  flex: 0 0 auto;
  gap: 4px;
  left: 0;
  padding: 8px 8px calc(var(--ion-safe-area-bottom, 0px) + 8px);
  position: relative;
  right: 0;
  z-index: 4;
}

.bottom-tabs button {
  background: transparent;
  flex: 1;
  flex-direction: column;
  font-size: 10px;
  font-weight: 700;
  gap: 3px;
  min-width: 0;
  opacity: 0.55;
}

.bottom-tabs button.active {
  color: #d8b4fe;
  opacity: 1;
}

.bottom-tabs span {
  align-items: center;
  border-radius: 13px;
  display: flex;
  font-size: 20px;
  height: 38px;
  justify-content: center;
  position: relative;
  width: 42px;
}

.bottom-tabs button.active span {
  background: #7c3aed;
  box-shadow: 0 0 16px rgba(124, 58, 237, 0.62);
}

.bottom-tabs b {
  align-items: center;
  background: #ef4444;
  border-radius: 999px;
  color: #fff;
  display: flex;
  font-size: 9px;
  height: 16px;
  justify-content: center;
  position: absolute;
  right: 3px;
  top: -2px;
  width: 16px;
}

.promo-toast {
  background: rgba(10, 0, 26, 0.94);
  border: 1px solid;
  border-radius: 18px;
  box-shadow: 0 12px 42px rgba(0, 0, 0, 0.42);
  left: 12px;
  padding: 12px 44px 12px 14px;
  position: absolute;
  right: 12px;
  top: calc(var(--ion-safe-area-top, 0px) + 60px);
  z-index: 9;
}

.promo-toast button {
  background: transparent;
  border: 0;
  color: rgba(255, 255, 255, 0.58);
  position: absolute;
  right: 10px;
  top: 10px;
}

.promo-toast p {
  font-weight: 900;
  margin: 4px 0 2px;
}

.admin-topbar h1 {
  font-size: 18px;
  margin: 0;
}

.admin-topbar p {
  color: #c084fc;
  font-size: 11px;
  margin: 2px 0 0;
}

.pill {
  border-radius: 999px;
  gap: 6px;
  padding: 8px 11px;
}

.pill.ghost {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.16);
}

@media (min-width: 720px) {
  .app-shell {
    margin: 0 auto;
    max-width: 520px;
  }
}
</style>
