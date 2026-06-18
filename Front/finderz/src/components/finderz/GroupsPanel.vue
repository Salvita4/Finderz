<template>
  <section class="groups-panel">
    <div class="groups-stats">
      <article v-for="stat in stats" :key="stat.label">
        <strong :style="{ color: stat.color }">{{ stat.value }}</strong>
        <span>{{ stat.label }}</span>
      </article>
    </div>

    <div class="group-tabs" role="tablist" aria-label="Grupos">
      <button
        v-for="group in groups"
        :key="group.id"
        type="button"
        :class="{ active: activeGroup === group.id }"
        @click="activeGroup = group.id"
      >
        {{ group.label }}
        <span>({{ group.count }})</span>
      </button>
    </div>

    <div class="friends-list">
      <article
        v-for="(friend, index) in displayedFriends"
        :key="friend.id"
        class="group-friend"
        :style="{ animationDelay: `${index * 45}ms` }"
      >
        <div class="friend-avatar" :style="avatarStyle(friend)">
          <span>{{ friend.name[0] }}</span>
          <i :class="{ online: friend.status === 'online' }"></i>
        </div>

        <div class="friend-info">
          <h3>
            <span>{{ friend.name }}</span>
            <ion-icon v-if="friend.faro" :icon="star" />
          </h3>
          <p>
            <ion-icon :icon="friend.status === 'online' ? wifiOutline : cloudOfflineOutline" />
            <span>{{ friend.status === 'online' ? 'En linea' : 'Sin senal' }}</span>
            <template v-if="friend.status === 'online'">
              <ion-icon :icon="batteryHalfOutline" />
              <b :style="{ color: friend.battery > 30 ? '#22c55e' : '#ef4444' }">{{ friend.battery }}%</b>
            </template>
          </p>
        </div>

        <div class="friend-actions">
          <button
            type="button"
            class="friend-action"
            :class="{ faro: friend.faro }"
            :aria-label="friend.faro ? 'Quitar faro' : 'Marcar como faro'"
            @click="emit('toggle-faro', friend.id)"
          >
            <ion-icon :icon="friend.faro ? star : starOutline" />
          </button>
          <button
            v-if="friend.status === 'online'"
            type="button"
            class="friend-action navigate"
            aria-label="Ir al amigo"
            @click="handleNavigate(friend)"
          >
            <ion-icon :icon="navigateOutline" />
          </button>
        </div>
      </article>
    </div>

    <button class="add-friend" type="button" @click="openAddSheet">
      <ion-icon :icon="personAddOutline" />
      Agregar amigo al grupo
    </button>

    <Transition name="modal-fade">
      <div v-if="showAddFriend" class="group-modal" @click="showAddFriend = false">
        <Transition name="sheet-slide" appear>
          <section class="group-sheet" @click.stop>
            <div class="sheet-handle"></div>
            <h2>
              <ion-icon :icon="peopleOutline" />
              Agregar al grupo
            </h2>

            <template v-if="addMode === 'menu'">
              <button
                v-for="option in addOptions"
                :key="option.id"
                type="button"
                class="sheet-option"
                @click="openAddMode(option.id)"
              >
                <span>
                  <ion-icon :icon="option.icon" />
                  {{ option.label }}
                </span>
                <ion-icon :icon="chevronForwardOutline" />
              </button>
            </template>

            <div v-else-if="addMode === 'share'" class="add-flow">
              <div class="qr-card">
                <div class="qr-grid" aria-label="Codigo QR del grupo">
                  <i v-for="(cell, index) in qrCells" :key="index" :class="{ dark: cell }"></i>
                </div>
                <strong>{{ inviteCode }}</strong>
                <p>Compartilo para que se sumen a {{ targetGroupLabel }}</p>
              </div>

              <button class="primary-sheet-action" type="button" @click="copyInviteCode">
                <ion-icon :icon="copiedInvite ? checkmarkCircleOutline : copyOutline" />
                {{ copiedInvite ? 'Codigo copiado' : 'Copiar codigo' }}
              </button>
              <button class="back-sheet-action" type="button" @click="addMode = 'menu'">Volver</button>
            </div>

            <div v-else-if="addMode === 'search'" class="add-flow">
              <label class="search-box">
                <ion-icon :icon="searchOutline" />
                <input v-model="searchTerm" type="search" placeholder="Usuario, nombre o codigo" />
              </label>

              <div class="candidate-list">
                <article v-for="candidate in filteredCandidates" :key="candidate.id">
                  <div class="candidate-avatar" :style="{ backgroundColor: candidate.color }">{{ candidate.name[0] }}</div>
                  <div>
                    <strong>{{ candidate.name }}</strong>
                    <small>@{{ candidate.username }} · {{ candidate.note }}</small>
                  </div>
                  <button type="button" :disabled="isFriendAdded(candidate.id)" @click="addCandidate(candidate)">
                    {{ isFriendAdded(candidate.id) ? 'Agregado' : 'Agregar' }}
                  </button>
                </article>

                <p v-if="!filteredCandidates.length" class="empty-add">No encontramos usuarios con ese dato.</p>
              </div>

              <button class="back-sheet-action" type="button" @click="addMode = 'menu'">Volver</button>
            </div>

            <div v-else class="add-flow">
              <div class="scanner-card" :class="{ scanning }">
                <span></span>
                <ion-icon :icon="qrCodeOutline" />
                <p>{{ scanning ? 'Escaneando QR...' : 'Apunta al QR de tu amigo' }}</p>
              </div>

              <article v-if="scanResult" class="scan-result">
                <div class="candidate-avatar" :style="{ backgroundColor: scanResult.color }">{{ scanResult.name[0] }}</div>
                <div>
                  <strong>{{ scanResult.name }}</strong>
                  <small>@{{ scanResult.username }}</small>
                </div>
                <button type="button" :disabled="isFriendAdded(scanResult.id)" @click="addCandidate(scanResult)">
                  {{ isFriendAdded(scanResult.id) ? 'Agregado' : 'Agregar' }}
                </button>
              </article>

              <button class="primary-sheet-action" type="button" @click="simulateScan">
                <ion-icon :icon="scanOutline" />
                {{ scanning ? 'Buscando...' : 'Escanear QR' }}
              </button>
              <button class="back-sheet-action" type="button" @click="addMode = 'menu'">Volver</button>
            </div>

            <button class="sheet-cancel" type="button" @click="showAddFriend = false">Cancelar</button>
          </section>
        </Transition>
      </div>
    </Transition>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { IonIcon } from '@ionic/vue';
import {
  batteryHalfOutline,
  chevronForwardOutline,
  cloudOfflineOutline,
  checkmarkCircleOutline,
  copyOutline,
  navigateOutline,
  peopleOutline,
  personAddOutline,
  qrCodeOutline,
  scanOutline,
  searchOutline,
  star,
  starOutline,
  wifiOutline,
} from 'ionicons/icons';
import { friendColors, percentToWorld, type Friend, type RouteTarget } from './types';

type GroupId = 'all' | 'crew' | 'col';
type AddMode = 'menu' | 'share' | 'search' | 'scan';
type Candidate = {
  id: string;
  name: string;
  username: string;
  note: string;
  color: string;
  battery: number;
};

const props = defineProps<{
  friends: Friend[];
}>();

const emit = defineEmits<{
  'toggle-faro': [id: string];
  'add-friend': [friend: Friend];
  navigate: [target: RouteTarget];
  'switch-to-map': [];
}>();

const activeGroup = ref<GroupId>('all');
const showAddFriend = ref(false);
const addMode = ref<AddMode>('menu');
const searchTerm = ref('');
const copiedInvite = ref(false);
const scanning = ref(false);
const scanResult = ref<Candidate | null>(null);

const groups = computed(() => [
  { id: 'all' as const, label: 'Todos', count: props.friends.length },
  { id: 'crew' as const, label: 'Crew Principal', count: props.friends.filter((friend) => friend.group === 'crew').length },
  { id: 'col' as const, label: 'Amigos del Cole', count: props.friends.filter((friend) => friend.group === 'col').length },
]);

const displayedFriends = computed(() => (
  activeGroup.value === 'all'
    ? props.friends
    : props.friends.filter((friend) => friend.group === activeGroup.value)
));

const stats = computed(() => [
  { label: 'En linea', value: `${props.friends.filter((friend) => friend.status === 'online').length}/${props.friends.length}`, color: '#00ff88' },
  { label: 'Con faros', value: props.friends.filter((friend) => friend.faro).length.toString(), color: '#ffd700' },
  { label: 'Grupos', value: '2', color: '#9d4edd' },
]);

const addOptions = [
  { id: 'share' as const, label: 'Compartir codigo QR', icon: qrCodeOutline },
  { id: 'search' as const, label: 'Buscar por usuario', icon: searchOutline },
  { id: 'scan' as const, label: 'Escanear QR de amigo', icon: scanOutline },
];

const candidates: Candidate[] = [
  { id: '6', name: 'Luca', username: 'luca.beats', note: 'Cerca del Main Stage', color: '#fb7185', battery: 72 },
  { id: '7', name: 'Valen', username: 'valen.river', note: 'Amiga en comun: Ana', color: '#38bdf8', battery: 66 },
  { id: '8', name: 'Nico', username: 'nico.foodie', note: 'Ultima vez en Food Court', color: '#34d399', battery: 48 },
];

const targetGroup = computed(() => activeGroup.value === 'all' ? 'crew' : activeGroup.value);
const targetGroupLabel = computed(() => groups.value.find((group) => group.id === targetGroup.value)?.label ?? 'tu grupo');
const inviteCode = computed(() => `FNZ-${targetGroup.value.toUpperCase()}-4729`);
const qrCells = computed(() => (
  Array.from({ length: 81 }, (_, index) => {
    const row = Math.floor(index / 9);
    const col = index % 9;
    const finder = (row < 3 && col < 3) || (row < 3 && col > 5) || (row > 5 && col < 3);
    return finder || ((index * 7 + inviteCode.value.length * 3) % 5 < 2);
  })
));
const filteredCandidates = computed(() => {
  const query = searchTerm.value.trim().toLowerCase();
  if (!query) return candidates;
  return candidates.filter((candidate) => (
    candidate.name.toLowerCase().includes(query)
    || candidate.username.toLowerCase().includes(query)
    || candidate.id.includes(query)
  ));
});

function avatarStyle(friend: Friend) {
  const color = friend.status === 'online' ? friendColors[friend.id]?.bg : '#333333';
  return {
    backgroundColor: color,
    borderColor: friend.status === 'online' ? color : '#444444',
    boxShadow: friend.status === 'online' ? `0 0 14px ${friendColors[friend.id]?.glow}` : 'none',
  };
}

function handleNavigate(friend: Friend) {
  const [wx, wz] = percentToWorld(friend.x, friend.y);
  emit('navigate', {
    wx,
    wz,
    label: friend.name,
    color: friendColors[friend.id]?.bg ?? '#00ff88',
    type: 'friend',
  });
  emit('switch-to-map');
}

function openAddSheet() {
  showAddFriend.value = true;
  addMode.value = 'menu';
  searchTerm.value = '';
  copiedInvite.value = false;
  scanning.value = false;
  scanResult.value = null;
}

function openAddMode(mode: AddMode) {
  addMode.value = mode;
  copiedInvite.value = false;
  if (mode === 'search') searchTerm.value = '';
  if (mode === 'scan') {
    scanResult.value = null;
    scanning.value = false;
  }
}

async function copyInviteCode() {
  try {
    await navigator.clipboard?.writeText(inviteCode.value);
  } catch {
    // The UI still confirms the action in browser previews without clipboard permission.
  }
  copiedInvite.value = true;
  window.setTimeout(() => {
    copiedInvite.value = false;
  }, 1600);
}

function isFriendAdded(id: string) {
  return props.friends.some((friend) => friend.id === id);
}

function addCandidate(candidate: Candidate) {
  if (isFriendAdded(candidate.id)) return;
  emit('add-friend', {
    id: candidate.id,
    name: candidate.name,
    x: 42 + Number(candidate.id) * 6,
    y: 35 + Number(candidate.id) * 4,
    status: 'online',
    faro: false,
    battery: candidate.battery,
    group: targetGroup.value,
  });
}

function simulateScan() {
  if (scanning.value) return;
  scanning.value = true;
  scanResult.value = null;
  window.setTimeout(() => {
    scanResult.value = candidates.find((candidate) => !isFriendAdded(candidate.id)) ?? candidates[0];
    scanning.value = false;
  }, 900);
}
</script>

<style scoped>
.groups-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
  height: 100%;
  overflow: hidden;
  padding: 8px 12px 12px;
  position: relative;
}

.groups-stats {
  display: grid;
  flex: 0 0 auto;
  gap: 8px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.groups-stats article {
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(168, 85, 247, 0.2);
  border-radius: 14px;
  padding: 10px 8px;
  text-align: center;
}

.groups-stats strong {
  display: block;
  font-size: 18px;
  line-height: 1.1;
}

.groups-stats span {
  color: rgba(255, 255, 255, 0.5);
  display: block;
  font-size: 10px;
  margin-top: 3px;
}

.group-tabs {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 14px;
  display: flex;
  flex: 0 0 auto;
  gap: 6px;
  padding: 5px;
}

.group-tabs button {
  background: transparent;
  border: 0;
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.52);
  flex: 1;
  font-size: 11px;
  font-weight: 800;
  min-height: 34px;
  transition: background 160ms ease, color 160ms ease;
}

.group-tabs button.active {
  background: #7c3aed;
  box-shadow: 0 8px 22px rgba(124, 58, 237, 0.24);
  color: #fff;
}

.group-tabs span {
  opacity: 0.65;
}

.friends-list {
  align-content: flex-start;
  display: flex;
  flex-direction: column;
  flex: 1;
  gap: 8px;
  min-height: 0;
  overflow-y: auto;
  padding-bottom: 2px;
}

.group-friend {
  animation: friendIn 240ms ease both;
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(168, 85, 247, 0.2);
  border-radius: 12px;
  display: flex;
  flex: 0 0 auto;
  gap: 8px;
  min-height: 54px;
  padding: 7px 9px;
}

.friend-avatar {
  align-items: center;
  border: 2px solid;
  border-radius: 999px;
  display: flex;
  flex: 0 0 auto;
  height: 36px;
  justify-content: center;
  position: relative;
  width: 36px;
}

.friend-avatar span {
  color: #fff;
  font-size: 13px;
  font-weight: 900;
}

.friend-avatar i {
  background: #6b7280;
  border: 2px solid #05010a;
  border-radius: 999px;
  bottom: -2px;
  height: 11px;
  position: absolute;
  right: -2px;
  width: 11px;
}

.friend-avatar i.online {
  background: #4ade80;
}

.friend-info {
  flex: 1;
  min-width: 0;
}

.friend-info h3 {
  align-items: center;
  display: flex;
  gap: 5px;
  margin: 0;
}

.friend-info h3 span {
  color: #fff;
  font-size: 13px;
  font-weight: 850;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.friend-info h3 ion-icon {
  color: #facc15;
  flex: 0 0 auto;
}

.friend-info p {
  align-items: center;
  color: rgba(255, 255, 255, 0.52);
  display: flex;
  font-size: 10px;
  gap: 4px;
  margin: 3px 0 0;
}

.friend-info p ion-icon:first-child {
  color: #4ade80;
}

.friend-info b {
  font-weight: 850;
}

.friend-actions {
  align-items: center;
  display: flex;
  flex: 0 0 auto;
  gap: 4px;
}

.friend-action {
  align-items: center;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.34);
  display: flex;
  height: 28px;
  justify-content: center;
  width: 28px;
}

.friend-action.faro {
  background: rgba(250, 204, 21, 0.18);
  border-color: rgba(250, 204, 21, 0.48);
  color: #facc15;
}

.friend-action.navigate {
  background: rgba(124, 58, 237, 0.28);
  border-color: rgba(168, 85, 247, 0.44);
  color: #d8b4fe;
}

.add-friend {
  align-items: center;
  background: transparent;
  border: 1px dashed rgba(168, 85, 247, 0.46);
  border-radius: 15px;
  color: #c084fc;
  display: flex;
  flex: 0 0 auto;
  font-size: 14px;
  font-weight: 850;
  gap: 8px;
  justify-content: center;
  min-height: 50px;
}

.group-modal {
  align-items: flex-end;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  inset: 0;
  position: absolute;
  z-index: 20;
}

.group-sheet {
  background: #1a0033;
  border-radius: 24px 24px 0 0;
  border-top: 1px solid rgba(168, 85, 247, 0.32);
  max-height: 88%;
  overflow-y: auto;
  padding: 14px 18px 18px;
  width: 100%;
}

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 180ms ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.sheet-slide-enter-active {
  transition: transform 260ms cubic-bezier(0.2, 0.8, 0.2, 1), opacity 220ms ease;
}

.sheet-slide-leave-active {
  transition: transform 190ms ease, opacity 160ms ease;
}

.sheet-slide-enter-from,
.sheet-slide-leave-to {
  opacity: 0;
  transform: translateY(100%);
}

.sheet-handle {
  background: rgba(255, 255, 255, 0.22);
  border-radius: 999px;
  height: 4px;
  margin: 0 auto 16px;
  width: 42px;
}

.group-sheet h2 {
  align-items: center;
  color: #fff;
  display: flex;
  font-size: 17px;
  gap: 8px;
  margin: 0 0 12px;
}

.group-sheet h2 ion-icon {
  color: #c084fc;
}

.sheet-option {
  align-items: center;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(168, 85, 247, 0.2);
  border-radius: 13px;
  color: rgba(255, 255, 255, 0.84);
  display: flex;
  font-size: 14px;
  justify-content: space-between;
  margin-bottom: 8px;
  min-height: 46px;
  padding: 0 14px;
  width: 100%;
}

.sheet-option span {
  align-items: center;
  display: flex;
  gap: 9px;
}

.sheet-option ion-icon {
  color: #c084fc;
}

.add-flow {
  display: grid;
  gap: 10px;
}

.qr-card,
.scanner-card,
.scan-result,
.candidate-list article,
.search-box {
  background: rgba(0, 0, 0, 0.28);
  border: 1px solid rgba(168, 85, 247, 0.2);
  border-radius: 16px;
}

.qr-card {
  align-items: center;
  display: flex;
  flex-direction: column;
  padding: 14px;
  text-align: center;
}

.qr-grid {
  background: #f8fafc;
  border: 6px solid #f8fafc;
  border-radius: 12px;
  display: grid;
  gap: 2px;
  grid-template-columns: repeat(9, 1fr);
  height: 148px;
  width: 148px;
}

.qr-grid i {
  background: transparent;
  border-radius: 2px;
}

.qr-grid i.dark {
  background: #12031f;
}

.qr-card strong {
  color: #fff;
  font-family: monospace;
  font-size: 16px;
  margin-top: 12px;
}

.qr-card p,
.scanner-card p,
.empty-add {
  color: rgba(255, 255, 255, 0.52);
  font-size: 12px;
  margin: 4px 0 0;
}

.primary-sheet-action,
.back-sheet-action {
  align-items: center;
  border-radius: 13px;
  display: flex;
  font-size: 13px;
  font-weight: 850;
  gap: 7px;
  justify-content: center;
  min-height: 43px;
  width: 100%;
}

.primary-sheet-action {
  background: #7c3aed;
  border: 1px solid rgba(216, 180, 254, 0.44);
  color: #fff;
}

.back-sheet-action {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.62);
}

.search-box {
  align-items: center;
  display: flex;
  gap: 8px;
  min-height: 44px;
  padding: 0 12px;
}

.search-box ion-icon {
  color: #c084fc;
  flex: 0 0 auto;
}

.search-box input {
  background: transparent;
  border: 0;
  color: #fff;
  flex: 1;
  font: inherit;
  font-size: 13px;
  min-width: 0;
  outline: 0;
}

.search-box input::placeholder {
  color: rgba(255, 255, 255, 0.36);
}

.candidate-list {
  display: grid;
  gap: 8px;
}

.candidate-list article,
.scan-result {
  align-items: center;
  display: flex;
  gap: 9px;
  min-height: 58px;
  padding: 8px;
}

.candidate-avatar {
  align-items: center;
  border-radius: 999px;
  color: #fff;
  display: flex;
  flex: 0 0 auto;
  font-size: 13px;
  font-weight: 900;
  height: 36px;
  justify-content: center;
  width: 36px;
}

.candidate-list article div:not(.candidate-avatar),
.scan-result div:not(.candidate-avatar) {
  flex: 1;
  min-width: 0;
}

.candidate-list strong,
.candidate-list small,
.scan-result strong,
.scan-result small {
  display: block;
}

.candidate-list strong,
.scan-result strong {
  color: #fff;
  font-size: 13px;
}

.candidate-list small,
.scan-result small {
  color: rgba(255, 255, 255, 0.46);
  font-size: 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.candidate-list article button,
.scan-result button {
  background: rgba(124, 58, 237, 0.28);
  border: 1px solid rgba(168, 85, 247, 0.38);
  border-radius: 10px;
  color: #d8b4fe;
  flex: 0 0 auto;
  font-size: 11px;
  font-weight: 850;
  min-height: 32px;
  padding: 0 9px;
}

.candidate-list article button:disabled,
.scan-result button:disabled {
  background: rgba(34, 197, 94, 0.18);
  border-color: rgba(74, 222, 128, 0.3);
  color: #86efac;
}

.empty-add {
  padding: 14px 4px;
  text-align: center;
}

.scanner-card {
  align-items: center;
  display: flex;
  flex-direction: column;
  min-height: 178px;
  overflow: hidden;
  padding: 24px 14px 18px;
  position: relative;
  text-align: center;
}

.scanner-card::before,
.scanner-card::after {
  border: 2px solid rgba(216, 180, 254, 0.68);
  content: '';
  height: 42px;
  position: absolute;
  width: 42px;
}

.scanner-card::before {
  border-bottom: 0;
  border-right: 0;
  left: 28px;
  top: 24px;
}

.scanner-card::after {
  border-left: 0;
  border-top: 0;
  bottom: 38px;
  right: 28px;
}

.scanner-card > span {
  background: linear-gradient(90deg, transparent, #4ade80, transparent);
  height: 2px;
  left: 28px;
  opacity: 0;
  position: absolute;
  right: 28px;
  top: 54px;
}

.scanner-card.scanning > span {
  animation: scanLine 900ms ease-in-out infinite;
  opacity: 1;
}

.scanner-card ion-icon {
  color: #d8b4fe;
  font-size: 54px;
  margin-top: 16px;
}

.sheet-cancel {
  background: transparent;
  border: 0;
  color: rgba(255, 255, 255, 0.5);
  min-height: 42px;
  width: 100%;
}

@keyframes scanLine {
  50% {
    transform: translateY(74px);
  }
}

@keyframes friendIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
