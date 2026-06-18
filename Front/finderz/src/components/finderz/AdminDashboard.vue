<template>
  <section class="admin-panel">
    <div class="admin-tabs">
      <button
        v-for="item in tabs"
        :key="item.id"
        type="button"
        :class="{ active: tab === item.id }"
        @click="tab = item.id"
      >
        <ion-icon :icon="item.icon" />
        {{ item.label }}
      </button>
    </div>

    <div class="admin-body">
      <section v-if="tab === 'heat'" class="heat-view">
        <div class="heat-stats">
          <article v-for="stat in heatStats" :key="stat.label">
            <strong :style="{ color: stat.color }">{{ stat.value }}</strong>
            <span>{{ stat.label }}</span>
          </article>
        </div>

        <div class="heat-map-card">
          <svg viewBox="0 0 360 270" class="heat-map" preserveAspectRatio="xMidYMid meet">
            <defs>
              <filter id="hm-blur" x="-60%" y="-60%" width="220%" height="220%">
                <feGaussianBlur in="SourceGraphic" stdDeviation="17" />
              </filter>
              <filter id="hm-glow" x="-30%" y="-30%" width="160%" height="160%">
                <feGaussianBlur in="SourceGraphic" stdDeviation="4" result="blur" />
                <feMerge>
                  <feMergeNode in="blur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
              <radialGradient id="hm-vignette" cx="50%" cy="50%" r="70%">
                <stop offset="55%" stop-color="transparent" />
                <stop offset="100%" stop-color="rgba(0,0,0,0.55)" />
              </radialGradient>
            </defs>

            <rect x="8" y="8" width="344" height="254" rx="10" fill="#0c1810" stroke="rgba(127,0,255,0.25)" stroke-width="1" />
            <rect x="8" y="8" width="344" height="254" rx="10" fill="url(#hm-vignette)" opacity="0.6" />

            <rect x="172" y="8" width="16" height="254" fill="#12203a" opacity="0.8" />
            <rect x="8" y="127" width="344" height="16" fill="#12203a" opacity="0.8" />
            <line x1="180" y1="70" x2="307" y2="100" stroke="#12203a" stroke-width="8" opacity="0.7" />
            <line x1="180" y1="70" x2="53" y2="100" stroke="#12203a" stroke-width="8" opacity="0.7" />
            <line x1="180" y1="135" x2="287" y2="183" stroke="#12203a" stroke-width="7" opacity="0.7" />
            <line x1="180" y1="135" x2="73" y2="183" stroke="#12203a" stroke-width="7" opacity="0.7" />

            <g filter="url(#hm-blur)" opacity="0.78">
              <ellipse
                v-for="zone in heatZones"
                :key="`heat-${zone.id}`"
                :cx="zone.x"
                :cy="zone.y"
                :rx="zone.rx * 2"
                :ry="zone.ry * 2"
                :fill="heatColor(zone.density)"
                :opacity="0.35 + zone.density * 0.65"
              />
            </g>

            <g
              v-for="zone in heatZones"
              :key="zone.id"
              class="heat-zone"
              @click="toggleZone(zone)"
            >
              <ellipse
                :cx="zone.x"
                :cy="zone.y"
                :rx="zone.rx"
                :ry="zone.ry"
                :fill="heatColor(zone.density)"
                :opacity="selectedZone?.id === zone.id ? 0.3 : 0.12"
              />
              <ellipse
                :cx="zone.x"
                :cy="zone.y"
                :rx="zone.rx"
                :ry="zone.ry"
                fill="none"
                :stroke="heatColor(zone.density)"
                :stroke-width="selectedZone?.id === zone.id ? 2 : zone.density >= 0.78 ? 1.2 : 0.8"
                :opacity="selectedZone?.id === zone.id ? 1 : zone.density >= 0.78 ? 0.9 : 0.6"
                :filter="selectedZone?.id === zone.id ? 'url(#hm-glow)' : undefined"
              />
              <ellipse
                v-if="zone.density >= 0.78"
                :cx="zone.x"
                :cy="zone.y"
                :rx="zone.rx + 3"
                :ry="zone.ry + 3"
                fill="none"
                :stroke="heatColor(zone.density)"
                stroke-width="0.7"
                opacity="0.4"
              >
                <animate attributeName="opacity" values="0.4;0;0.4" dur="2s" repeatCount="indefinite" />
                <animate attributeName="rx" :values="`${zone.rx + 3};${zone.rx + 8};${zone.rx + 3}`" dur="2s" repeatCount="indefinite" />
                <animate attributeName="ry" :values="`${zone.ry + 3};${zone.ry + 8};${zone.ry + 3}`" dur="2s" repeatCount="indefinite" />
              </ellipse>
              <circle :cx="zone.x" :cy="zone.y" r="2.5" :fill="heatColor(zone.density)" opacity="0.95" />
              <text
                v-if="zone.rx >= 24"
                :x="zone.x"
                :y="zone.y - zone.ry - 4"
                text-anchor="middle"
                font-size="6"
                fill="rgba(255,255,255,0.75)"
                font-family="system-ui, sans-serif"
                font-weight="700"
              >
                {{ zone.label }}
              </text>
              <text
                v-if="zone.rx >= 28"
                :x="zone.x"
                :y="zone.y + 3.5"
                text-anchor="middle"
                font-size="5.5"
                fill="rgba(255,255,255,0.55)"
                font-family="monospace"
              >
                {{ zone.people.toLocaleString() }} p.
              </text>
            </g>

            <g v-for="gate in gates" :key="gate.id">
              <rect :x="gate.x - 28" :y="gate.y - 5" width="56" height="11" rx="3" fill="#22c55e" opacity="0.18" />
              <rect :x="gate.x - 28" :y="gate.y - 5" width="56" height="11" rx="3" fill="none" stroke="#22c55e" stroke-width="0.7" opacity="0.6" />
              <text :x="gate.x" :y="gate.y + 2.5" text-anchor="middle" font-size="4.8" fill="#22c55e" opacity="0.85" font-family="monospace" font-weight="700">
                {{ gate.label }}
              </text>
            </g>

            <text x="345" y="22" text-anchor="middle" font-size="7" fill="rgba(255,255,255,0.25)" font-family="sans-serif" font-weight="700">N</text>
            <line x1="345" y1="25" x2="345" y2="32" stroke="rgba(255,255,255,0.2)" stroke-width="1" />
            <polygon points="345,20 343,26 345,24 347,26" fill="rgba(255,255,255,0.25)" />
            <text x="15" y="262" font-size="5" fill="rgba(255,255,255,0.2)" font-family="monospace">Live</text>
          </svg>

          <div v-if="selectedZone" class="zone-tooltip" :style="{ borderColor: `${heatColor(selectedZone.density)}55` }">
            <span>{{ selectedZone.icon }}</span>
            <div>
              <strong>{{ selectedZone.label }}</strong>
              <small>{{ selectedZone.people.toLocaleString() }} personas · {{ Math.round(selectedZone.density * 100) }}% capacidad</small>
            </div>
            <b :style="{ backgroundColor: `${heatColor(selectedZone.density)}25`, color: heatColor(selectedZone.density) }">
              {{ heatLabel(selectedZone.density) }}
            </b>
          </div>
        </div>

        <div class="heat-scale">
          <span>Densidad</span>
          <i></i>
          <b>Libre</b>
          <b>Critico</b>
        </div>

        <div class="critical-list">
          <button v-for="zone in criticalZones" :key="zone.id" type="button" @click="toggleZone(zone)">
            <ion-icon :icon="warningOutline" />
            <span>{{ zone.icon }} {{ zone.label }}</span>
            <strong>{{ Math.round(zone.density * 100) }}%</strong>
            <small>{{ zone.people }} p.</small>
          </button>
        </div>
      </section>

      <section v-else-if="tab === 'sales'" class="sales-view">
        <div v-if="launched && selectedStall" class="launch-success">
          <span>
            <ion-icon :icon="checkmarkCircleOutline" />
          </span>
          <h3>Promocion lanzada</h3>
          <p>Enviada a <strong>{{ audience.count.toLocaleString() }}</strong> usuarios</p>
          <div class="promo-preview" :style="{ borderColor: `${selectedStall.color}55` }">
            <header :style="{ backgroundColor: `${selectedStall.color}22` }">
              <span>{{ selectedStall.icon }}</span>
              <div>
                <strong>{{ selectedStall.name }}</strong>
                <small>{{ selectedStall.category }}</small>
              </div>
              <b :style="{ color: selectedStall.color, backgroundColor: `${selectedStall.color}33` }">{{ buildDiscount(promoType, discount) }}</b>
            </header>
            <p>{{ buildPromoTitle(selectedStall, promoType, discount) }}</p>
          </div>
          <button type="button" @click="resetSales">Crear otra</button>
        </div>

        <template v-else>
          <div class="sales-chart">
            <span>Toca un puesto para crear promo</span>
            <div class="bar-chart">
              <button
                v-for="item in salesData"
                :key="item.name"
                type="button"
                :class="{ active: selectedStall?.name.startsWith(item.name.split(' ')[0]) }"
                :style="{ '--bar-color': stallBySale(item)?.color ?? '#7f00ff', '--bar-height': `${(item.ventas / maxSales) * 100}%` }"
                @click="selectedStall = stallBySale(item) ?? null"
              >
                <i></i>
                <small>{{ item.name }}</small>
              </button>
            </div>
          </div>

          <div v-if="!selectedStall" class="stall-list">
            <button v-for="stall in stalls" :key="stall.id" type="button" @click="selectedStall = stall">
              <span>{{ stall.icon }}</span>
              <div>
                <strong>{{ stall.name }}</strong>
                <small>{{ stall.ventas }} ventas · ${{ stall.ingresos.toLocaleString() }}</small>
              </div>
              <b :class="{ down: stall.trend < 0 }">{{ stall.trend > 0 ? '+' : '' }}{{ stall.trend }}%</b>
              <ion-icon :icon="chevronForwardOutline" />
            </button>
          </div>

          <div v-else class="promo-builder">
            <div class="selected-stall" :style="{ backgroundColor: `${selectedStall.color}18`, borderColor: `${selectedStall.color}44` }">
              <span>{{ selectedStall.icon }}</span>
              <div>
                <strong>{{ selectedStall.name }}</strong>
                <small>{{ selectedStall.ventas }} ventas · ${{ selectedStall.ingresos.toLocaleString() }} ingresos</small>
              </div>
              <b :class="{ down: selectedStall.trend < 0 }">{{ selectedStall.trend > 0 ? '+' : '' }}{{ selectedStall.trend }}%</b>
              <button type="button" @click="resetSales">x</button>
            </div>

            <label>Tipo de oferta</label>
            <div class="option-grid">
              <button
                v-for="type in promoTypes"
                :key="type.id"
                type="button"
                :class="{ active: promoType === type.id }"
                :style="promoType === type.id ? activeOptionStyle : undefined"
                @click="promoType = type.id"
              >
                <span>{{ type.icon }}</span>
                {{ type.label }}
              </button>
            </div>

            <template v-if="promoType === 'pct'">
              <label>Descuento</label>
              <div class="chip-row">
                <button
                  v-for="value in discounts"
                  :key="value"
                  type="button"
                  :class="{ active: discount === value }"
                  :style="discount === value ? activeOptionStyle : undefined"
                  @click="discount = value"
                >
                  -{{ value }}%
                </button>
              </div>
            </template>

            <label>Validez</label>
            <div class="chip-row">
              <button
                v-for="item in durations"
                :key="item.val"
                type="button"
                :class="{ active: duration === item.val }"
                :style="duration === item.val ? activeOptionStyle : undefined"
                @click="duration = item.val"
              >
                {{ item.label }}
              </button>
            </div>

            <label>Enviar a</label>
            <div class="audience-row">
              <button
                v-for="item in audiences"
                :key="item.id"
                type="button"
                :class="{ active: audience.id === item.id }"
                :style="audience.id === item.id ? activeOptionStyle : undefined"
                @click="audience = item"
              >
                <span>{{ item.icon }}</span>
                {{ item.label }}
                <small>{{ item.count.toLocaleString() }}</small>
              </button>
            </div>

            <div class="promo-preview" :style="{ borderColor: `${selectedStall.color}55` }">
              <header :style="{ backgroundColor: `${selectedStall.color}22` }">
                <span>{{ selectedStall.icon }}</span>
                <div>
                  <strong>{{ selectedStall.name }}</strong>
                  <small>{{ selectedStall.category }}</small>
                </div>
                <b :style="{ color: selectedStall.color, backgroundColor: `${selectedStall.color}33` }">{{ buildDiscount(promoType, discount) }}</b>
              </header>
              <p>{{ buildPromoDesc(selectedStall, promoType, discount) }}</p>
            </div>

            <button class="launch-button" type="button" :disabled="launching" :style="{ background: `linear-gradient(135deg, ${selectedStall.color}cc, ${selectedStall.color}88)` }" @click="handleLaunch">
              <i v-if="launching"></i>
              <ion-icon v-else :icon="rocketOutline" />
              {{ launching ? 'Enviando...' : `Lanzar a ${audience.count.toLocaleString()} usuarios` }}
            </button>
          </div>
        </template>
      </section>

      <section v-else class="metrics-view">
        <div class="metric-cards">
          <article v-for="metric in metricsData" :key="metric.label">
            <ion-icon :icon="metric.icon" />
            <span>{{ metric.label }}</span>
            <strong>{{ metric.value }}</strong>
            <small :class="{ down: !metric.up }">{{ metric.trend }}</small>
          </article>
        </div>

        <div class="line-panel">
          <span>Cuellos de botella por hora</span>
          <svg viewBox="0 0 320 120" preserveAspectRatio="none" @mouseleave="hoveredLinePoint = null">
            <polyline
              fill="none"
              stroke="rgba(255,255,255,0.08)"
              stroke-width="1"
              points="0,100 320,100"
            />
            <polyline :points="linePoints" fill="none" stroke="#ff3366" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
            <g
              v-for="point in lineDots"
              :key="point.label"
              class="line-point"
              tabindex="0"
              @mouseenter="hoveredLinePoint = point"
              @focus="hoveredLinePoint = point"
              @mouseleave="hoveredLinePoint = null"
              @blur="hoveredLinePoint = null"
            >
              <line
                v-if="hoveredLinePoint?.label === point.label"
                :x1="point.x"
                y1="10"
                :x2="point.x"
                y2="104"
                stroke="rgba(255,255,255,0.16)"
                stroke-dasharray="3 4"
              />
              <circle :cx="point.x" :cy="point.y" r="12" fill="transparent" />
              <circle
                :cx="point.x"
                :cy="point.y"
                :r="hoveredLinePoint?.label === point.label ? 5 : 3"
                fill="#ff3366"
                stroke="rgba(255,255,255,0.75)"
                :stroke-width="hoveredLinePoint?.label === point.label ? 2 : 0"
              />
            </g>

            <g v-if="hoveredLinePoint" class="line-tooltip" :transform="lineTooltipTransform">
              <rect x="-34" y="-35" width="68" height="28" rx="7" />
              <path d="M -5 -7 L 0 -1 L 5 -7 Z" />
              <text x="0" y="-24" text-anchor="middle">{{ hoveredLinePoint.value.toLocaleString() }} pers.</text>
              <text x="0" y="-13" text-anchor="middle">{{ hoveredLinePoint.label }}</text>
            </g>
          </svg>
          <div class="line-axis">
            <small v-for="point in bottleneckData" :key="point.hora">{{ point.hora }}</small>
          </div>
        </div>

        <div class="zone-share">
          <div class="donut" :style="{ background: donutGradient }">
            <strong>{{ topZone.value }}%</strong>
          </div>
          <div>
            <p v-for="zone in zoneData" :key="zone.name">
              <i :style="{ backgroundColor: zone.color }"></i>
              <span>{{ zone.name }}</span>
              <b>{{ zone.value }}%</b>
            </p>
          </div>
        </div>

        <div class="lost-zones">
          <h3>
            <ion-icon :icon="locationOutline" />
            Mayores desencuentros
          </h3>
          <article v-for="item in lostZones" :key="item.lugar">
            <div>
              <strong>{{ item.lugar }}</strong>
              <small>{{ item.hora }}</small>
            </div>
            <b>{{ item.casos }} casos</b>
          </article>
        </div>
      </section>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { IonIcon } from '@ionic/vue';
import {
  barChartOutline,
  checkmarkCircleOutline,
  chevronForwardOutline,
  flameOutline,
  locationOutline,
  rocketOutline,
  statsChartOutline,
  trendingUpOutline,
  warningOutline,
} from 'ionicons/icons';
import type { Promotion } from './types';

type AdminTab = 'heat' | 'sales' | 'metrics';
type PromoType = 'pct' | '2x1' | 'gift';

interface Stall {
  id: string;
  name: string;
  icon: string;
  category: Promotion['category'];
  color: string;
  wx: number;
  wz: number;
  ventas: number;
  ingresos: number;
  trend: number;
}

interface HZone {
  id: string;
  label: string;
  icon: string;
  x: number;
  y: number;
  rx: number;
  ry: number;
  density: number;
  people: number;
}

const emit = defineEmits<{
  'launch-promo': [promo: Promotion];
}>();

const tab = ref<AdminTab>('sales');
const selectedZone = ref<HZone | null>(null);
const selectedStall = ref<Stall | null>(null);
const promoType = ref<PromoType>('pct');
const discount = ref(25);
const duration = ref(30);
const audience = ref({ id: 'all', label: 'Todos', icon: '👥', count: 4280 });
const launched = ref(false);
const launching = ref(false);
const hoveredLinePoint = ref<{ label: string; value: number; x: number; y: number } | null>(null);

const tabs = [
  { id: 'heat' as const, label: 'Mapa Calor', icon: flameOutline },
  { id: 'sales' as const, label: 'Promos', icon: rocketOutline },
  { id: 'metrics' as const, label: 'Metricas', icon: trendingUpOutline },
];

const salesData = [
  { name: 'Main Bar', ventas: 340, ingresos: 5100 },
  { name: 'Food Court', ventas: 210, ingresos: 3800 },
  { name: 'Beer Gdn', ventas: 280, ingresos: 4200 },
  { name: 'VIP Bar', ventas: 95, ingresos: 2850 },
  { name: 'Merch', ventas: 78, ingresos: 3120 },
  { name: 'Tacos', ventas: 145, ingresos: 1900 },
];

const stalls: Stall[] = [
  { id: 'mainBar', name: 'Main Bar', icon: '🍻', category: 'drink', color: '#f97316', wx: -2, wz: 0, ventas: 340, ingresos: 5100, trend: 8 },
  { id: 'foodCourt', name: 'Food Court', icon: '🍔', category: 'food', color: '#ef4444', wx: 9.5, wz: 9.5, ventas: 210, ingresos: 3800, trend: -5 },
  { id: 'beerGarden', name: 'Beer Garden', icon: '🍺', category: 'drink', color: '#f59e0b', wx: -5.5, wz: 2, ventas: 280, ingresos: 4200, trend: 3 },
  { id: 'vipBar', name: 'VIP Bar', icon: '🥂', category: 'drink', color: '#06b6d4', wx: 7, wz: -3, ventas: 95, ingresos: 2850, trend: -12 },
  { id: 'merch', name: 'Merch', icon: '👕', category: 'merch', color: '#8b5cf6', wx: 3.5, wz: 4, ventas: 78, ingresos: 3120, trend: -18 },
  { id: 'tacos', name: 'Tacos', icon: '🌮', category: 'food', color: '#10b981', wx: 8, wz: 7, ventas: 145, ingresos: 1900, trend: 15 },
];

const audiences = [
  { id: 'all', label: 'Todos', icon: '👥', count: 4280 },
  { id: 'drink', label: 'Cerveceros', icon: '🍺', count: 1240 },
  { id: 'food', label: 'Foodies', icon: '🍔', count: 890 },
  { id: 'merch', label: 'Merch fans', icon: '👕', count: 320 },
  { id: 'vip', label: 'VIP', icon: '⭐', count: 95 },
];

const heatZones: HZone[] = [
  { id: 'mainStage', label: 'Main Stage', icon: '🎵', x: 180, y: 47, rx: 58, ry: 23, density: 0.95, people: 1820 },
  { id: 'stage2', label: 'Stage 2', icon: '🎵', x: 307, y: 79, rx: 32, ry: 21, density: 0.58, people: 420 },
  { id: 'techno', label: 'Techno Dome', icon: '🎧', x: 53, y: 79, rx: 32, ry: 21, density: 0.45, people: 310 },
  { id: 'vip', label: 'VIP Zone', icon: '⭐', x: 258, y: 111, rx: 25, ry: 17, density: 0.28, people: 95 },
  { id: 'beerGarden', label: 'Beer Garden', icon: '🍺', x: 121, y: 151, rx: 28, ry: 18, density: 0.6, people: 280 },
  { id: 'foodCourt', label: 'Food Court', icon: '🍔', x: 287, y: 207, rx: 36, ry: 24, density: 0.82, people: 510 },
  { id: 'camping', label: 'Camping', icon: '⛺', x: 73, y: 207, rx: 36, ry: 24, density: 0.18, people: 95 },
  { id: 'medical', label: 'Medico', icon: '🏥', x: 143, y: 167, rx: 17, ry: 12, density: 0.15, people: 12 },
  { id: 'info', label: 'Info/Merch', icon: 'ℹ️', x: 217, y: 167, rx: 17, ry: 12, density: 0.3, people: 68 },
  { id: 'banosW', label: 'Banos O', icon: '🚻', x: 36, y: 151, rx: 13, ry: 17, density: 0.88, people: 145 },
  { id: 'banosE', label: 'Banos E', icon: '🚻', x: 324, y: 151, rx: 13, ry: 17, density: 0.85, people: 138 },
];

const gates = [
  { id: 'exitN', label: 'ENTRADA N', x: 180, y: 14 },
  { id: 'exitS', label: 'ENTRADA S', x: 180, y: 261 },
];

const promoTypes = [
  { id: 'pct' as const, label: '% Descuento', icon: '🏷️' },
  { id: '2x1' as const, label: '2x1', icon: '✌️' },
  { id: 'gift' as const, label: 'Regalo', icon: '🎁' },
];

const discounts = [15, 20, 25, 30, 40, 50];
const durations = [{ label: '15 min', val: 15 }, { label: '30 min', val: 30 }, { label: '1 hora', val: 60 }, { label: '2 horas', val: 120 }];
const bottleneckData = [
  { hora: '18h', personas: 120 },
  { hora: '19h', personas: 280 },
  { hora: '20h', personas: 540 },
  { hora: '21h', personas: 890 },
  { hora: '22h', personas: 1200 },
  { hora: '23h', personas: 980 },
  { hora: '00h', personas: 750 },
  { hora: '01h', personas: 430 },
];
const zoneData = [
  { name: 'Main Stage', value: 38, color: '#7f00ff' },
  { name: 'Food/Bar', value: 22, color: '#f97316' },
  { name: 'Camping', value: 12, color: '#22c55e' },
  { name: 'Stage 2', value: 14, color: '#ff3366' },
  { name: 'Techno', value: 10, color: '#00d9ff' },
  { name: 'Otros', value: 4, color: '#666666' },
];
const metricsData = [
  { label: 'Asistentes', value: '4,280', icon: barChartOutline, trend: '+12%', up: true },
  { label: 'Desencuentros', value: '23', icon: warningOutline, trend: '-8%', up: false },
  { label: 'Ingresos', value: '$21k', icon: statsChartOutline, trend: '+18%', up: true },
  { label: 'Zonas criticas', value: '2', icon: flameOutline, trend: 'Banos', up: false },
];
const lostZones = [
  { lugar: 'Cruce central avdas.', hora: '21-22h', casos: 8 },
  { lugar: 'Salida Main Stage', hora: '23:30h', casos: 7 },
  { lugar: 'Food Court', hora: '20-21h', casos: 5 },
];

const maxSales = computed(() => Math.max(...salesData.map((item) => item.ventas)));
const totalPeople = computed(() => heatZones.reduce((sum, zone) => sum + zone.people, 0));
const criticalZones = computed(() => heatZones.filter((zone) => zone.density >= 0.78));
const heatStats = computed(() => [
  { label: 'Total personas', value: totalPeople.value.toLocaleString(), color: '#9d4edd' },
  { label: 'Zonas criticas', value: String(criticalZones.value.length), color: '#ef4444' },
  { label: 'Capacidad avg', value: `${Math.round((heatZones.reduce((sum, zone) => sum + zone.density, 0) / heatZones.length) * 100)}%`, color: '#f97316' },
]);
const activeOptionStyle = computed(() => selectedStall.value ? {
  backgroundColor: `${selectedStall.value.color}25`,
  borderColor: `${selectedStall.value.color}55`,
  color: selectedStall.value.color,
} : undefined);
const lineDots = computed(() => {
  const max = Math.max(...bottleneckData.map((item) => item.personas));
  const width = 320;
  return bottleneckData.map((item, index) => ({
    label: item.hora,
    value: item.personas,
    x: (index / (bottleneckData.length - 1)) * width,
    y: 108 - (item.personas / max) * 96,
  }));
});
const linePoints = computed(() => lineDots.value.map((point) => `${point.x},${point.y}`).join(' '));
const lineTooltipTransform = computed(() => {
  if (!hoveredLinePoint.value) return '';
  const x = Math.min(286, Math.max(34, hoveredLinePoint.value.x));
  const y = Math.max(42, hoveredLinePoint.value.y);
  return `translate(${x} ${y})`;
});
const donutGradient = computed(() => {
  let cursor = 0;
  const parts = zoneData.map((zone) => {
    const from = cursor;
    cursor += zone.value;
    return `${zone.color} ${from}% ${cursor}%`;
  });
  return `conic-gradient(${parts.join(', ')})`;
});
const topZone = computed(() => zoneData[0]);

function heatColor(density: number) {
  if (density < 0.2) return '#22c55e';
  if (density < 0.4) return '#84cc16';
  if (density < 0.6) return '#eab308';
  if (density < 0.78) return '#f97316';
  return '#ef4444';
}

function heatLabel(density: number) {
  if (density < 0.2) return 'Libre';
  if (density < 0.4) return 'Bajo';
  if (density < 0.6) return 'Moderado';
  if (density < 0.78) return 'Alto';
  return 'Critico';
}

function toggleZone(zone: HZone) {
  selectedZone.value = selectedZone.value?.id === zone.id ? null : zone;
}

function stallBySale(item: { name: string }) {
  return stalls.find((stall) => stall.name.startsWith(item.name.split(' ')[0]));
}

function buildPromoTitle(stall: Stall, type: PromoType, pct: number) {
  if (type === '2x1') return `2x1 en ${stall.name}`;
  if (type === 'gift') return `Regalo con tu compra en ${stall.name}`;
  return `${pct}% OFF en ${stall.name}`;
}

function buildPromoDesc(stall: Stall, type: PromoType, pct: number) {
  if (type === '2x1') return `Lleva dos y paga uno. Valido en ${stall.name} hasta agotar stock.`;
  if (type === 'gift') return `Con cualquier compra en ${stall.name} te llevas un regalo sorpresa.`;
  return `${pct}% de descuento en todos los productos. Solo por tiempo limitado.`;
}

function buildDiscount(type: PromoType, pct: number) {
  if (type === '2x1') return '2x1';
  if (type === 'gift') return '🎁';
  return `-${pct}%`;
}

function resetSales() {
  selectedStall.value = null;
  launched.value = false;
  launching.value = false;
  promoType.value = 'pct';
  discount.value = 25;
  duration.value = 30;
  audience.value = audiences[0];
}

function handleLaunch() {
  if (!selectedStall.value || launching.value) return;
  const stall = selectedStall.value;
  launching.value = true;
  window.setTimeout(() => {
    emit('launch-promo', {
      id: `admin-${Date.now()}`,
      title: buildPromoTitle(stall, promoType.value, discount.value),
      description: buildPromoDesc(stall, promoType.value, discount.value),
      discount: buildDiscount(promoType.value, discount.value),
      stallName: stall.name,
      stallId: stall.id,
      wx: stall.wx,
      wz: stall.wz,
      expiresIn: duration.value,
      color: stall.color,
      icon: stall.icon,
      category: stall.category,
      used: false,
      isNew: true,
    });
    launching.value = false;
    launched.value = true;
  }, 900);
}
</script>

<style scoped>
.admin-panel {
  display: flex;
  flex-direction: column;
  gap: 10px;
  height: 100%;
  overflow: hidden;
  padding: 8px 12px 12px;
}

.admin-tabs {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 14px;
  display: flex;
  flex: 0 0 auto;
  gap: 5px;
  padding: 5px;
}

.admin-tabs button,
.option-grid button,
.chip-row button,
.audience-row button,
.launch-success > button,
.launch-button {
  align-items: center;
  border: 0;
  border-radius: 10px;
  display: flex;
  font-weight: 850;
  justify-content: center;
}

.admin-tabs button {
  background: transparent;
  color: rgba(255, 255, 255, 0.54);
  flex: 1;
  font-size: 10px;
  gap: 5px;
  min-height: 34px;
}

.admin-tabs button.active {
  background: #7c3aed;
  color: #fff;
}

.admin-body {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}

.heat-view,
.sales-view,
.metrics-view {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 100%;
}

.heat-stats,
.metric-cards {
  display: grid;
  gap: 8px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.heat-stats article,
.metric-cards article,
.line-panel,
.lost-zones,
.sales-chart,
.selected-stall,
.promo-preview {
  background: rgba(0, 0, 0, 0.32);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 14px;
}

.heat-stats article {
  padding: 8px 6px;
  text-align: center;
}

.heat-stats strong {
  display: block;
  font-size: 14px;
}

.heat-stats span,
.metric-cards span,
.sales-chart > span,
.promo-builder label,
.line-panel > span {
  color: rgba(255, 255, 255, 0.42);
  font-size: 10px;
}

.heat-map-card {
  background: linear-gradient(145deg, #060d08, #0a140c);
  border-radius: 18px;
  flex: 1;
  min-height: 270px;
  overflow: hidden;
  position: relative;
}

.heat-map {
  display: block;
  height: 100%;
  width: 100%;
}

.heat-zone {
  cursor: pointer;
}

.zone-tooltip {
  align-items: center;
  background: rgba(0, 0, 0, 0.86);
  border: 1px solid;
  border-radius: 14px;
  bottom: 8px;
  display: flex;
  gap: 10px;
  left: 8px;
  padding: 9px 10px;
  position: absolute;
  right: 8px;
}

.zone-tooltip > span {
  font-size: 24px;
}

.zone-tooltip div {
  flex: 1;
  min-width: 0;
}

.zone-tooltip strong,
.zone-tooltip small {
  display: block;
}

.zone-tooltip strong {
  color: #fff;
  font-size: 13px;
}

.zone-tooltip small {
  color: rgba(255, 255, 255, 0.52);
  font-size: 10px;
}

.zone-tooltip b {
  border-radius: 9px;
  font-size: 11px;
  padding: 6px 8px;
}

.heat-scale {
  align-items: center;
  display: grid;
  gap: 7px;
  grid-template-columns: auto 1fr auto auto;
}

.heat-scale span,
.heat-scale b {
  color: rgba(255, 255, 255, 0.35);
  font-size: 9px;
}

.heat-scale b:last-child {
  color: #ef4444;
}

.heat-scale i {
  background: linear-gradient(to right, #22c55e, #84cc16, #eab308, #f97316, #ef4444);
  border-radius: 999px;
  height: 10px;
}

.critical-list {
  display: grid;
  gap: 7px;
}

.critical-list button,
.stall-list button {
  align-items: center;
  border: 1px solid;
  display: flex;
  text-align: left;
}

.critical-list button {
  background: rgba(127, 29, 29, 0.36);
  border-color: rgba(239, 68, 68, 0.28);
  border-radius: 13px;
  color: #fca5a5;
  gap: 8px;
  min-height: 39px;
  padding: 0 10px;
}

.critical-list span {
  flex: 1;
  font-size: 11px;
}

.critical-list strong {
  color: #f87171;
  font-size: 11px;
}

.critical-list small {
  color: rgba(255, 255, 255, 0.35);
  font-size: 9px;
}

.sales-chart {
  flex: 0 0 auto;
  padding: 10px;
}

.bar-chart {
  align-items: end;
  display: grid;
  gap: 5px;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  height: 132px;
  margin-top: 8px;
}

.bar-chart button {
  align-items: center;
  background: transparent;
  border: 0;
  color: rgba(255, 255, 255, 0.46);
  display: flex;
  flex-direction: column;
  gap: 5px;
  height: 100%;
  justify-content: end;
  min-width: 0;
}

.bar-chart i {
  background: var(--bar-color);
  border-radius: 7px 7px 2px 2px;
  height: var(--bar-height);
  min-height: 18px;
  opacity: 0.52;
  transition: opacity 160ms ease, transform 160ms ease;
  width: 100%;
}

.bar-chart button.active i,
.bar-chart button:hover i {
  opacity: 1;
  transform: translateY(-2px);
}

.bar-chart small {
  font-size: 8px;
  line-height: 1;
}

.stall-list {
  display: grid;
  gap: 7px;
}

.stall-list button {
  background: rgba(0, 0, 0, 0.24);
  border-color: rgba(255, 255, 255, 0.08);
  border-radius: 14px;
  color: #fff;
  gap: 10px;
  min-height: 54px;
  padding: 0 10px;
}

.stall-list button > span,
.selected-stall > span {
  font-size: 20px;
}

.stall-list div,
.selected-stall div {
  flex: 1;
  min-width: 0;
}

.stall-list strong,
.stall-list small,
.selected-stall strong,
.selected-stall small {
  display: block;
}

.stall-list strong,
.selected-stall strong {
  font-size: 12px;
}

.stall-list small,
.selected-stall small {
  color: rgba(255, 255, 255, 0.42);
  font-size: 10px;
}

.stall-list b,
.selected-stall b {
  color: #4ade80;
  font-size: 10px;
}

.stall-list b.down,
.selected-stall b.down,
.metric-cards small.down {
  color: #f87171;
}

.promo-builder {
  display: flex;
  flex-direction: column;
  gap: 9px;
}

.selected-stall {
  align-items: center;
  display: flex;
  gap: 10px;
  padding: 11px;
}

.selected-stall button {
  background: transparent;
  border: 0;
  color: rgba(255, 255, 255, 0.38);
}

.option-grid {
  display: grid;
  gap: 7px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.option-grid button,
.chip-row button,
.audience-row button {
  background: rgba(0, 0, 0, 0.24);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.48);
  font-size: 10px;
  min-height: 40px;
}

.option-grid button {
  flex-direction: column;
  gap: 2px;
}

.option-grid span {
  font-size: 16px;
}

.chip-row,
.audience-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.chip-row button {
  min-height: 31px;
  padding: 0 11px;
}

.audience-row {
  flex-wrap: nowrap;
  overflow-x: auto;
  padding-bottom: 2px;
}

.audience-row button {
  flex: 0 0 auto;
  gap: 5px;
  min-height: 32px;
  padding: 0 9px;
}

.audience-row small {
  opacity: 0.65;
}

.promo-preview {
  overflow: hidden;
}

.promo-preview header {
  align-items: center;
  display: flex;
  gap: 8px;
  padding: 8px 10px;
}

.promo-preview header > span {
  font-size: 18px;
}

.promo-preview header div {
  flex: 1;
}

.promo-preview header strong,
.promo-preview header small {
  display: block;
}

.promo-preview header strong {
  font-size: 11px;
}

.promo-preview header small {
  color: rgba(255, 255, 255, 0.42);
  font-size: 9px;
}

.promo-preview header b {
  border-radius: 8px;
  font-size: 12px;
  padding: 5px 8px;
}

.promo-preview p {
  background: rgba(0, 0, 0, 0.34);
  color: rgba(255, 255, 255, 0.76);
  font-size: 11px;
  line-height: 1.35;
  margin: 0;
  padding: 9px 10px;
}

.launch-button {
  color: #fff;
  font-size: 13px;
  gap: 8px;
  min-height: 48px;
}

.launch-button:disabled {
  opacity: 0.78;
}

.launch-button i {
  animation: spin 0.8s linear infinite;
  border: 2px solid rgba(255, 255, 255, 0.38);
  border-radius: 999px;
  border-top-color: #fff;
  height: 16px;
  width: 16px;
}

.launch-success {
  align-items: center;
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 12px;
  justify-content: center;
  text-align: center;
}

.launch-success > span {
  align-items: center;
  background: rgba(34, 197, 94, 0.18);
  border: 2px solid rgba(74, 222, 128, 0.58);
  border-radius: 999px;
  color: #4ade80;
  display: flex;
  font-size: 42px;
  height: 78px;
  justify-content: center;
  width: 78px;
}

.launch-success h3,
.lost-zones h3 {
  margin: 0;
}

.launch-success p {
  color: rgba(255, 255, 255, 0.52);
  margin: -6px 0 0;
}

.launch-success .promo-preview {
  text-align: left;
  width: 100%;
}

.launch-success > button {
  background: rgba(124, 58, 237, 0.28);
  border: 1px solid rgba(168, 85, 247, 0.42);
  color: #fff;
  min-height: 44px;
  width: 100%;
}

.metric-cards {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.metric-cards article {
  padding: 11px;
}

.metric-cards ion-icon {
  color: #c084fc;
  font-size: 16px;
}

.metric-cards strong {
  display: block;
  font-size: 20px;
  margin-top: 3px;
}

.metric-cards small {
  color: #4ade80;
  font-size: 9px;
}

.line-panel {
  padding: 11px;
}

.line-panel svg {
  display: block;
  height: 112px;
  margin-top: 6px;
  overflow: visible;
  width: 100%;
}

.line-axis {
  display: flex;
  justify-content: space-between;
}

.line-panel small {
  color: rgba(255, 255, 255, 0.34);
  font-size: 8px;
}

.line-point {
  cursor: pointer;
  outline: none;
}

.line-tooltip {
  pointer-events: none;
}

.line-tooltip rect,
.line-tooltip path {
  fill: rgba(8, 0, 20, 0.94);
  stroke: rgba(255, 51, 102, 0.45);
}

.line-tooltip text {
  fill: #fff;
  font-family: system-ui, sans-serif;
  font-size: 8px;
  font-weight: 800;
}

.line-tooltip text:last-child {
  fill: rgba(255, 255, 255, 0.52);
  font-size: 7px;
}

.zone-share {
  align-items: center;
  display: flex;
  gap: 14px;
}

.donut {
  align-items: center;
  border-radius: 999px;
  display: flex;
  flex: 0 0 auto;
  height: 112px;
  justify-content: center;
  position: relative;
  width: 112px;
}

.donut::after {
  background: #11021f;
  border-radius: inherit;
  content: '';
  inset: 28px;
  position: absolute;
}

.donut strong {
  font-size: 18px;
  position: relative;
  z-index: 1;
}

.zone-share > div:last-child {
  flex: 1;
}

.zone-share p {
  align-items: center;
  display: flex;
  gap: 8px;
  margin: 0 0 8px;
}

.zone-share i {
  border-radius: 999px;
  height: 8px;
  width: 8px;
}

.zone-share span {
  color: rgba(255, 255, 255, 0.62);
  flex: 1;
  font-size: 10px;
}

.zone-share b {
  font-size: 10px;
}

.lost-zones {
  border-color: rgba(249, 115, 22, 0.25);
  padding: 12px;
}

.lost-zones h3 {
  align-items: center;
  color: #fdba74;
  display: flex;
  font-size: 12px;
  gap: 6px;
  margin-bottom: 7px;
}

.lost-zones article {
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  display: flex;
  justify-content: space-between;
  padding: 7px 0;
}

.lost-zones article:last-child {
  border-bottom: 0;
}

.lost-zones strong,
.lost-zones small {
  display: block;
}

.lost-zones strong {
  font-size: 10px;
}

.lost-zones small {
  color: rgba(255, 255, 255, 0.32);
  font-size: 9px;
}

.lost-zones b {
  color: #fb923c;
  font-size: 10px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
