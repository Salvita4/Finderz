<template>
  <section class="agenda-panel">
    <header class="agenda-header">
      <div>
        <h2>Agenda del Festival</h2>
        <p>{{ liveCount }} en vivo ahora · {{ starred.size }} guardados</p>
      </div>
      <span>
        <ion-icon :icon="musicalNotesOutline" />
        {{ acts.length }} shows
      </span>
    </header>

    <div class="stage-filter">
      <button type="button" :class="{ active: stageFilter === 'all' }" @click="stageFilter = 'all'">
        Grilla completa
      </button>
      <button
        v-for="(stage, stageId) in stages"
        :key="stageId"
        type="button"
        :class="{ active: stageFilter === stageId }"
        :style="stageFilter === stageId ? activeStageStyle(stage.color) : undefined"
        @click="stageFilter = stageId"
      >
        {{ stage.label }}
      </button>
    </div>

    <div v-if="starred.size && stageFilter === 'all'" class="starred-strip">
      <span v-for="act in savedActs" :key="act.id" :style="{ borderColor: `${stages[act.stage].color}55` }">
        <ion-icon :icon="star" />
        {{ act.artist }}
        <b>{{ formatTime(act.startH, act.startM) }}</b>
      </span>
    </div>

    <div class="agenda-content">
      <template v-if="stageFilter === 'all'">
        <div class="grid-header">
          <span v-for="stageId in stageIds" :key="stageId" :style="{ borderColor: `${stages[stageId].color}44`, color: stages[stageId].color }">
            {{ shortStageName(stages[stageId].label) }}
          </span>
        </div>

        <div v-for="time in gridTimes" :key="time" class="time-slot">
          <div class="time-label">
            <strong>{{ minuteLabel(time) }}</strong>
            <template v-if="isCurrentSlot(time)">
              <i></i>
              <em>AHORA</em>
              <i></i>
            </template>
            <i v-else></i>
          </div>

          <div class="grid-row">
            <button
              v-for="stageId in stageIds"
              :key="stageId"
              type="button"
              class="grid-act"
              :class="{ empty: !actAt(stageId, time), live: actAt(stageId, time) && isNow(actAt(stageId, time)!), past: actAt(stageId, time) && isPast(actAt(stageId, time)!) }"
              :style="actAt(stageId, time) ? gridActStyle(actAt(stageId, time)!) : undefined"
              :disabled="!actAt(stageId, time)"
              @click="goToStage(stageId)"
            >
              <template v-if="actAt(stageId, time)">
                <small v-if="isNow(actAt(stageId, time)!)">EN VIVO</small>
                <strong>{{ actAt(stageId, time)!.artist }}</strong>
                <span>{{ formatTime(actAt(stageId, time)!.startH, actAt(stageId, time)!.startM) }}-{{ formatTime(actAt(stageId, time)!.endH, actAt(stageId, time)!.endM) }}</span>
                <ion-icon v-if="starred.has(actAt(stageId, time)!.id)" :icon="star" />
              </template>
            </button>
          </div>
        </div>
      </template>

      <template v-else>
        <article class="stage-card" :style="{ borderColor: `${stages[stageFilter].color}55`, backgroundColor: `${stages[stageFilter].color}18` }">
          <div>
            <h3>{{ stages[stageFilter].label }}</h3>
            <p>{{ filteredActs.length }} shows · {{ stageSubtitle }}</p>
          </div>
          <button type="button" :style="{ color: stages[stageFilter].color, borderColor: `${stages[stageFilter].color}55` }" @click="goToStage(stageFilter)">
            <ion-icon :icon="navigateOutline" />
            Ir al escenario
          </button>
        </article>

        <template v-for="(act, index) in filteredActs" :key="act.id">
          <div v-if="showNowMarker(index)" ref="nowMarker" class="now-marker">
            <i></i>
            <span>AHORA</span>
            <i></i>
          </div>
          <article class="act-card" :class="{ live: isNow(act), past: isPast(act) }" :style="{ borderColor: isNow(act) ? `${stages[act.stage].color}88` : 'rgba(255,255,255,0.08)' }">
            <button type="button" class="act-main" :style="{ backgroundColor: isNow(act) ? `${stages[act.stage].color}14` : 'rgba(0,0,0,0.35)' }" @click="expanded = expanded === act.id ? null : act.id">
              <time>
                <strong>{{ formatTime(act.startH, act.startM) }}</strong>
                <span>{{ formatTime(act.endH, act.endM) }}</span>
              </time>
              <b :style="{ backgroundColor: stages[act.stage].color, opacity: isNow(act) ? 1 : 0.45 }"></b>
              <div>
                <p>
                  <em v-if="isNow(act)" :style="{ color: stages[act.stage].color, backgroundColor: `${stages[act.stage].color}28` }">EN VIVO</em>
                  {{ act.artist }}
                  <ion-icon v-if="starred.has(act.id)" :icon="star" />
                </p>
                <small :style="{ color: stages[act.stage].color }">{{ stages[act.stage].label }}</small>
                <small>{{ act.genre }}</small>
              </div>
              <ion-icon :icon="expanded === act.id ? chevronUpOutline : chevronDownOutline" />
            </button>

            <Transition name="expand">
              <div v-if="expanded === act.id" class="act-actions">
                <span>
                  <ion-icon :icon="timeOutline" />
                  {{ durationText(act) }}
                </span>
                <button type="button" :class="{ saved: starred.has(act.id) }" @click="toggleStar(act.id)">
                  <ion-icon :icon="starred.has(act.id) ? star : starOutline" />
                  {{ starred.has(act.id) ? 'Guardado' : 'Guardar' }}
                </button>
                <button type="button" :style="{ color: stages[act.stage].color, borderColor: `${stages[act.stage].color}55` }" @click="goToStage(act.stage)">
                  <ion-icon :icon="navigateOutline" />
                  Ir
                </button>
              </div>
            </Transition>
          </article>
        </template>
      </template>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue';
import { IonIcon } from '@ionic/vue';
import {
  chevronDownOutline,
  chevronUpOutline,
  musicalNotesOutline,
  navigateOutline,
  star,
  starOutline,
  timeOutline,
} from 'ionicons/icons';
import type { RouteTarget } from './types';

type StageId = 'main' | 'stage2' | 'techno';
type StageFilter = StageId | 'all';

interface Act {
  id: string;
  artist: string;
  genre: string;
  stage: StageId;
  startH: number;
  startM: number;
  endH: number;
  endM: number;
}

const emit = defineEmits<{
  navigate: [target: RouteTarget];
  'switch-to-map': [];
}>();

const acts: Act[] = [
  { id: 'm1', artist: 'Los Amigos Invisibles', genre: 'Latin Funk', stage: 'main', startH: 18, startM: 0, endH: 19, endM: 30 },
  { id: 'm2', artist: 'Nicki Nicole', genre: 'Urban Pop', stage: 'main', startH: 20, startM: 0, endH: 21, endM: 30 },
  { id: 'm3', artist: 'DJ Snake', genre: 'EDM / Trap', stage: 'main', startH: 22, startM: 0, endH: 23, endM: 30 },
  { id: 'm4', artist: 'Martin Garrix', genre: 'Progressive H', stage: 'main', startH: 0, startM: 0, endH: 1, endM: 30 },
  { id: 'm5', artist: 'Tiesto', genre: 'Big Room', stage: 'main', startH: 2, startM: 0, endH: 4, endM: 0 },
  { id: 's1', artist: 'La Delio Valdez', genre: 'Cumbia', stage: 'stage2', startH: 18, startM: 30, endH: 20, endM: 0 },
  { id: 's2', artist: 'Tini', genre: 'Pop', stage: 'stage2', startH: 20, startM: 30, endH: 22, endM: 0 },
  { id: 's3', artist: 'Becky Hill', genre: 'Dance / House', stage: 'stage2', startH: 22, startM: 30, endH: 0, endM: 0 },
  { id: 's4', artist: 'Fisher', genre: 'Tech House', stage: 'stage2', startH: 0, startM: 30, endH: 2, endM: 30 },
  { id: 's5', artist: 'Skrillex', genre: 'Dubstep', stage: 'stage2', startH: 3, startM: 0, endH: 4, endM: 30 },
  { id: 't1', artist: 'Paula Tape', genre: 'Techno', stage: 'techno', startH: 18, startM: 0, endH: 19, endM: 30 },
  { id: 't2', artist: 'Amelie Lens', genre: 'Dark Techno', stage: 'techno', startH: 20, startM: 0, endH: 22, endM: 0 },
  { id: 't3', artist: 'Charlotte de Witte', genre: 'Industrial Techno', stage: 'techno', startH: 22, startM: 30, endH: 0, endM: 30 },
  { id: 't4', artist: 'Adam Beyer', genre: 'Techno', stage: 'techno', startH: 1, startM: 0, endH: 3, endM: 0 },
  { id: 't5', artist: 'Bicep', genre: 'Electronic', stage: 'techno', startH: 3, startM: 30, endH: 5, endM: 0 },
];

const stages: Record<StageId, { label: string; color: string; wx: number; wz: number }> = {
  main: { label: 'Main Stage', color: '#9d4edd', wx: 0, wz: -12 },
  stage2: { label: 'Stage 2', color: '#ff3366', wx: 11.5, wz: -7 },
  techno: { label: 'Techno Dome', color: '#00d9ff', wx: -11.5, wz: -7 },
};

const stageIds: StageId[] = ['main', 'stage2', 'techno'];
const refHour = 17;
const stageFilter = ref<StageFilter>('all');
const starred = ref(new Set<string>(['m3']));
const expanded = ref<string | null>(null);
const nowM = ref(nowMinute());
const nowMarker = ref<HTMLElement[] | null>(null);

const liveCount = computed(() => acts.filter((act) => isNow(act)).length);
const savedActs = computed(() => acts.filter((act) => starred.value.has(act.id)));
const filteredActs = computed(() => {
  const visible = stageFilter.value === 'all' ? acts : acts.filter((act) => act.stage === stageFilter.value);
  return [...visible].sort((a, b) => toMinute(a.startH, a.startM) - toMinute(b.startH, b.startM));
});
const gridTimes = computed(() => Array.from(new Set(acts.map((act) => toMinute(act.startH, act.startM)))).sort((a, b) => a - b));
const stageSubtitle = computed(() => {
  if (stageFilter.value === 'all') return '';
  const live = filteredActs.value.filter((act) => isNow(act)).length;
  if (live) return 'EN VIVO AHORA';
  const next = filteredActs.value.find((act) => !isPast(act));
  return next ? `Proximo: ${formatTime(next.startH, next.startM)}` : 'Cierre de jornada';
});

onMounted(() => {
  const timer = window.setInterval(() => {
    nowM.value = nowMinute();
  }, 60_000);
  window.setTimeout(scrollToNow, 400);
  window.addEventListener('beforeunload', () => window.clearInterval(timer), { once: true });
});

watch(stageFilter, () => {
  expanded.value = null;
  nextTick(() => window.setTimeout(scrollToNow, 120));
});

function toMinute(hour: number, minute: number) {
  const adjusted = hour < refHour ? hour + 24 : hour;
  return (adjusted - refHour) * 60 + minute;
}

function nowMinute() {
  const now = new Date();
  return toMinute(now.getHours(), now.getMinutes());
}

function formatTime(hour: number, minute: number) {
  return `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`;
}

function minuteLabel(minuteValue: number) {
  const hour = Math.floor(minuteValue / 60 + refHour) % 24;
  const minute = minuteValue % 60;
  return formatTime(hour, minute);
}

function durationText(act: Act) {
  const mins = toMinute(act.endH, act.endM) - toMinute(act.startH, act.startM);
  const hours = Math.floor(mins / 60);
  const minutes = mins % 60;
  if (!hours) return `${minutes}m`;
  return minutes ? `${hours}h ${minutes}m` : `${hours}h`;
}

function isNow(act: Act) {
  return nowM.value >= toMinute(act.startH, act.startM) && nowM.value < toMinute(act.endH, act.endM);
}

function isPast(act: Act) {
  return nowM.value >= toMinute(act.endH, act.endM);
}

function showNowMarker(index: number) {
  const previousPast = index > 0 ? isPast(filteredActs.value[index - 1]) : true;
  const currentPast = isPast(filteredActs.value[index]);
  return previousPast && !currentPast && index > 0;
}

function isCurrentSlot(slot: number) {
  const slotIndex = gridTimes.value.indexOf(slot);
  const nextSlot = gridTimes.value[slotIndex + 1] ?? slot + 120;
  return nowM.value >= slot && nowM.value < nextSlot;
}

function actAt(stageId: StageId, slot: number) {
  return acts.find((act) => act.stage === stageId && toMinute(act.startH, act.startM) === slot);
}

function toggleStar(id: string) {
  const next = new Set(starred.value);
  if (next.has(id)) next.delete(id);
  else next.add(id);
  starred.value = next;
}

function goToStage(stageId: StageId) {
  const stage = stages[stageId];
  emit('navigate', { wx: stage.wx, wz: stage.wz, label: stage.label, color: stage.color, type: 'poi' });
  emit('switch-to-map');
}

function scrollToNow() {
  const marker = nowMarker.value?.[0];
  marker?.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function activeStageStyle(color: string) {
  return { backgroundColor: `${color}33`, borderColor: `${color}66`, color };
}

function gridActStyle(act: Act) {
  const color = stages[act.stage].color;
  return {
    backgroundColor: isNow(act) ? `${color}20` : isPast(act) ? 'rgba(0,0,0,0.2)' : `${color}0e`,
    borderColor: isNow(act) ? `${color}88` : isPast(act) ? 'rgba(255,255,255,0.05)' : `${color}33`,
  };
}

function shortStageName(label: string) {
  return label.replace(' Stage', '').replace(' Dome', '');
}
</script>

<style scoped>
.agenda-panel {
  display: flex;
  flex-direction: column;
  gap: 10px;
  height: 100%;
  overflow: hidden;
  padding: 8px 12px 12px;
}

.agenda-header,
.stage-card {
  align-items: center;
  display: flex;
  flex: 0 0 auto;
  justify-content: space-between;
}

.agenda-header h2 {
  color: #fff;
  font-size: 16px;
  font-weight: 950;
  margin: 0;
}

.agenda-header p,
.stage-card p {
  color: #c084fc;
  font-size: 11px;
  margin: 3px 0 0;
}

.agenda-header > span {
  align-items: center;
  background: rgba(124, 58, 237, 0.2);
  border: 1px solid rgba(168, 85, 247, 0.3);
  border-radius: 999px;
  color: #d8b4fe;
  display: flex;
  font-size: 11px;
  font-weight: 850;
  gap: 5px;
  padding: 7px 10px;
}

.stage-filter {
  display: flex;
  flex: 0 0 auto;
  gap: 6px;
  overflow-x: auto;
  padding-bottom: 2px;
}

.stage-filter button {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.55);
  flex: 0 0 auto;
  font-size: 11px;
  font-weight: 850;
  min-height: 34px;
  padding: 0 12px;
}

.stage-filter button.active {
  background: #7c3aed;
  color: #fff;
}

.starred-strip {
  display: flex;
  flex: 0 0 auto;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 2px;
}

.starred-strip span {
  align-items: center;
  background: rgba(250, 204, 21, 0.12);
  border: 1px solid;
  border-radius: 12px;
  color: #fff;
  display: flex;
  flex: 0 0 auto;
  font-size: 11px;
  font-weight: 800;
  gap: 6px;
  padding: 7px 9px;
}

.starred-strip ion-icon {
  color: #facc15;
}

.starred-strip b {
  color: rgba(255, 255, 255, 0.45);
  font-weight: 700;
}

.agenda-content {
  display: grid;
  flex: 1;
  gap: 9px;
  min-height: 0;
  overflow-y: auto;
  padding-bottom: 2px;
}

.grid-header {
  background: rgba(10, 0, 20, 0.92);
  display: grid;
  gap: 6px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  margin-bottom: 2px;
  padding: 4px 0 6px;
  position: sticky;
  top: 0;
  z-index: 2;
}

.grid-header span {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid;
  border-radius: 12px;
  align-items: center;
  display: flex;
  font-size: 11px;
  font-weight: 950;
  justify-content: center;
  min-height: 36px;
  padding: 9px 6px;
  text-align: center;
}

.time-slot {
  display: grid;
  gap: 6px;
}

.time-label {
  align-items: center;
  display: flex;
  gap: 8px;
}

.time-label strong {
  color: rgba(255, 255, 255, 0.42);
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 10px;
}

.time-label i,
.now-marker i {
  background: rgba(255, 255, 255, 0.08);
  flex: 1;
  height: 1px;
}

.time-label em,
.now-marker span {
  background: rgba(127, 29, 29, 0.38);
  border-radius: 999px;
  color: #f87171;
  font-size: 9px;
  font-style: normal;
  font-weight: 950;
  padding: 3px 7px;
}

.grid-row {
  display: grid;
  gap: 6px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.grid-act {
  background: transparent;
  border: 1px solid transparent;
  border-radius: 12px;
  color: #fff;
  min-height: 70px;
  padding: 8px;
  text-align: left;
}

.grid-act.empty {
  opacity: 0;
}

.grid-act.past {
  opacity: 0.48;
}

.grid-act small {
  display: block;
  font-size: 8px;
  font-weight: 950;
  margin-bottom: 3px;
}

.grid-act strong {
  display: -webkit-box;
  font-size: 10px;
  font-weight: 900;
  line-height: 1.15;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.grid-act span {
  color: rgba(255, 255, 255, 0.42);
  display: block;
  font-size: 9px;
  margin-top: 5px;
}

.grid-act ion-icon {
  color: #facc15;
  margin-top: 4px;
}

.stage-card,
.act-card {
  background: rgba(0, 0, 0, 0.35);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 15px;
  overflow: hidden;
}

.stage-card {
  padding: 13px;
}

.stage-card h3 {
  color: #fff;
  font-size: 15px;
  margin: 0;
}

.stage-card button {
  align-items: center;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid;
  border-radius: 12px;
  display: flex;
  font-size: 11px;
  font-weight: 850;
  gap: 6px;
  min-height: 36px;
  padding: 0 11px;
}

.act-card.past {
  opacity: 0.48;
}

.act-card.live {
  box-shadow: 0 0 16px rgba(255, 255, 255, 0.08);
}

.act-main {
  align-items: center;
  background: transparent;
  border: 0;
  color: #fff;
  display: flex;
  gap: 10px;
  padding: 12px;
  text-align: left;
  width: 100%;
}

.act-main time {
  display: grid;
  flex: 0 0 46px;
  font-size: 10px;
  gap: 4px;
  line-height: 1.05;
  text-align: right;
}

.act-main time strong {
  color: rgba(255, 255, 255, 0.9);
}

.act-main time span {
  color: rgba(255, 255, 255, 0.35);
}

.act-main > b {
  border-radius: 999px;
  flex: 0 0 auto;
  height: 9px;
  width: 9px;
}

.act-main div {
  flex: 1;
  min-width: 0;
}

.act-main p {
  align-items: center;
  display: flex;
  font-size: 14px;
  font-weight: 900;
  gap: 6px;
  margin: 0;
  min-width: 0;
}

.act-main p em {
  border-radius: 999px;
  flex: 0 0 auto;
  font-size: 9px;
  font-style: normal;
  font-weight: 950;
  padding: 3px 6px;
}

.act-main p ion-icon {
  color: #facc15;
}

.act-main small {
  color: rgba(255, 255, 255, 0.38);
  font-size: 10px;
  margin-right: 7px;
}

.act-actions {
  align-items: center;
  display: flex;
  gap: 8px;
  overflow: hidden;
  padding: 0 12px 12px;
}

.act-actions span,
.act-actions button {
  align-items: center;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.52);
  display: flex;
  font-size: 11px;
  font-weight: 850;
  gap: 6px;
  min-height: 34px;
  padding: 0 10px;
}

.act-actions span {
  border: 0;
  padding-left: 0;
}

.act-actions button.saved {
  background: rgba(250, 204, 21, 0.16);
  border-color: rgba(250, 204, 21, 0.42);
  color: #facc15;
}

.now-marker {
  align-items: center;
  display: flex;
  gap: 8px;
  padding: 3px 0;
}

.expand-enter-active,
.expand-leave-active {
  transition: opacity 170ms ease, transform 170ms ease;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
