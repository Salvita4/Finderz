<template>
  <div class="festival-map">
    <svg viewBox="0 0 400 400" preserveAspectRatio="xMidYMid meet" aria-label="Mapa 2D del festival">
      <defs>
        <linearGradient id="fm-bg" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#1a0033" />
          <stop offset="50%" stop-color="#20003d" />
          <stop offset="100%" stop-color="#130026" />
        </linearGradient>
        <linearGradient id="fm-grass" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#1a3a1a" />
          <stop offset="100%" stop-color="#0f2a10" />
        </linearGradient>
        <filter id="fm-shadow" x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="rgba(0,0,0,0.7)" />
        </filter>
        <filter id="fm-glow" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="4" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
        <clipPath id="fm-bounds">
          <path d="M 30 10 Q 80 5 140 8 Q 200 10 260 6 Q 320 3 370 15
                   Q 395 25 392 80 Q 390 140 393 200 Q 396 260 390 320
                   Q 384 370 340 388 Q 280 398 220 395 Q 160 392 100 396
                   Q 50 398 18 375 Q 5 350 8 290 Q 10 230 6 170
                   Q 2 110 10 60 Q 15 30 30 10 Z" />
        </clipPath>
      </defs>

      <rect width="400" height="400" fill="url(#fm-bg)" />

      <g clip-path="url(#fm-bounds)">
        <rect x="12" y="12" width="376" height="376" fill="url(#fm-grass)" opacity="0.82" />

        <ellipse cx="198" cy="310" rx="38" ry="22" fill="#001a33" stroke="rgba(0,180,255,0.35)" stroke-width="1.5" />

        <path d="M 20 195 Q 100 190 200 192 Q 300 194 385 190" stroke="rgba(80,50,130,0.58)" stroke-width="22" fill="none" stroke-linecap="round" />
        <path d="M 198 12 Q 195 80 196 140 Q 197 195 196 260 Q 195 320 196 390" stroke="rgba(80,50,130,0.48)" stroke-width="20" fill="none" stroke-linecap="round" />
        <path d="M 260 130 Q 290 160 310 190" stroke="rgba(60,40,100,0.5)" stroke-width="14" fill="none" stroke-linecap="round" />
        <path d="M 140 130 Q 110 160 90 190" stroke="rgba(60,40,100,0.5)" stroke-width="14" fill="none" stroke-linecap="round" />
        <path d="M 260 260 Q 285 280 310 295" stroke="rgba(60,40,100,0.4)" stroke-width="12" fill="none" stroke-linecap="round" />
        <path d="M 140 260 Q 118 280 95 295" stroke="rgba(60,40,100,0.4)" stroke-width="12" fill="none" stroke-linecap="round" />

        <g filter="url(#fm-shadow)">
          <path d="M 110 14 L 290 14 L 288 75 L 112 75 Z" fill="#5600b7" stroke="rgba(200,150,255,0.75)" stroke-width="1.5" />
          <rect x="118" y="14" width="164" height="28" rx="2" fill="rgba(40,0,100,0.7)" />
          <path d="M 118 14 L 200 8 L 282 14" stroke="rgba(200,150,255,0.62)" stroke-width="1.5" fill="none" />
          <text x="200" y="90" text-anchor="middle" font-size="9" fill="white" font-family="sans-serif" font-weight="900" letter-spacing="2">MAIN STAGE</text>
        </g>

        <g filter="url(#fm-shadow)">
          <path d="M 298 106 L 389 106 L 388 156 L 298 156 Z" fill="#79004a" stroke="rgba(255,100,180,0.6)" stroke-width="1.2" />
          <text x="343" y="168" text-anchor="middle" font-size="7.5" fill="#ffc0dc" font-family="sans-serif" font-weight="bold">STAGE 2</text>
        </g>

        <g filter="url(#fm-shadow)">
          <path d="M 12 106 L 102 106 L 101 156 L 12 156 Z" fill="#004d7d" stroke="rgba(80,180,255,0.62)" stroke-width="1.2" />
          <text x="57" y="168" text-anchor="middle" font-size="7.5" fill="#a6e4ff" font-family="sans-serif" font-weight="bold">TECHNO DOME</text>
        </g>

        <g filter="url(#fm-shadow)">
          <rect x="240" y="95" width="52" height="67" rx="4" fill="#241700" stroke="rgba(255,200,50,0.7)" stroke-width="1.2" />
          <text x="266" y="132" text-anchor="middle" font-size="8" fill="rgba(255,200,50,0.85)">★ ★ ★</text>
          <text x="266" y="168" text-anchor="middle" font-size="7.5" fill="#ffd166" font-family="sans-serif" font-weight="bold">VIP</text>
        </g>

        <g filter="url(#fm-shadow)">
          <rect x="285" y="260" width="102" height="97" rx="5" fill="#754300" stroke="rgba(255,180,50,0.58)" stroke-width="1.2" />
          <text x="336" y="311" text-anchor="middle" font-size="7" fill="#ffd28a" font-family="sans-serif">FOOD COURT</text>
        </g>

        <g filter="url(#fm-shadow)">
          <rect x="18" y="255" width="99" height="100" rx="5" fill="rgba(20,50,20,0.86)" stroke="rgba(80,180,80,0.5)" stroke-width="1.2" />
          <text x="65" y="362" text-anchor="middle" font-size="8" fill="#86efac" font-family="sans-serif" font-weight="bold">CAMPING</text>
        </g>

        <rect x="152" y="255" width="42" height="36" rx="3" fill="rgba(200,0,0,0.3)" stroke="rgba(255,80,80,0.6)" stroke-width="1.2" />
        <rect x="218" y="255" width="52" height="36" rx="3" fill="rgba(127,0,255,0.35)" stroke="rgba(180,100,255,0.6)" stroke-width="1.2" />
        <rect x="124" y="200" width="62" height="42" rx="3" fill="rgba(60,20,0,0.64)" stroke="rgba(200,120,0,0.5)" stroke-width="1" />
        <rect x="216" y="200" width="62" height="42" rx="3" fill="rgba(60,20,0,0.64)" stroke="rgba(200,120,0,0.5)" stroke-width="1" />

        <g v-for="tree in trees" :key="`${tree[0]}-${tree[1]}`">
          <circle :cx="tree[0]" :cy="tree[1]" r="6" fill="rgba(20,80,20,0.7)" />
          <circle :cx="tree[0]" :cy="tree[1] - 2" r="4.5" fill="rgba(30,100,30,0.8)" />
        </g>
      </g>

      <path d="M 30 10 Q 80 5 140 8 Q 200 10 260 6 Q 320 3 370 15
               Q 395 25 392 80 Q 390 140 393 200 Q 396 260 390 320
               Q 384 370 340 388 Q 280 398 220 395 Q 160 392 100 396
               Q 50 398 18 375 Q 5 350 8 290 Q 10 230 6 170
               Q 2 110 10 60 Q 15 30 30 10 Z"
            fill="none" stroke="rgba(150,80,255,0.7)" stroke-width="2.5" />

      <g filter="url(#fm-glow)">
        <circle cx="196" cy="192" r="12" fill="rgba(127,0,255,0.15)">
          <animate attributeName="r" from="8" to="18" dur="2.5s" repeatCount="indefinite" />
          <animate attributeName="opacity" from="0.4" to="0" dur="2.5s" repeatCount="indefinite" />
        </circle>
        <circle cx="196" cy="192" r="6" fill="#7c3aed" stroke="rgba(255,255,255,0.38)" stroke-width="2" />
      </g>
    </svg>

    <div class="you-marker">
      <ion-icon :icon="compassOutline" />
    </div>

    <button
      v-for="friend in friends"
      :key="friend.id"
      type="button"
      class="friend-marker"
      :class="{ offline: friend.status === 'offline' }"
      :style="friendStyle(friend)"
      :aria-label="friend.name"
    >
      <ion-icon :icon="navigateOutline" />
      <span>{{ friend.name }}</span>
    </button>

    <div class="map-north">N ↑</div>
  </div>
</template>

<script setup lang="ts">
import { IonIcon } from '@ionic/vue';
import { compassOutline, navigateOutline } from 'ionicons/icons';
import { friendColors, type Friend } from './types';

defineProps<{
  friends: Friend[];
}>();

const trees = [
  [52, 130], [72, 118], [62, 142], [78, 135],
  [320, 130], [340, 118], [328, 142], [348, 135],
  [52, 380], [70, 370], [62, 388],
  [340, 375], [356, 383], [348, 365],
  [148, 380], [162, 374], [218, 377], [232, 385],
];

function friendStyle(friend: Friend) {
  const color = friend.status === 'online' ? friendColors[friend.id]?.bg ?? '#888888' : '#555555';
  const glow = friendColors[friend.id]?.glow ?? 'rgba(136,136,136,0.8)';
  return {
    left: `${friend.x}%`,
    top: `${friend.y}%`,
    backgroundColor: color,
    boxShadow: friend.status === 'online' ? `0 0 16px ${glow}, 0 0 32px ${glow}60` : '0 2px 8px rgba(0,0,0,0.5)',
  };
}
</script>

<style scoped>
.festival-map {
  border: 2px solid rgba(168, 85, 247, 0.6);
  border-radius: 18px;
  box-shadow: 0 0 60px rgba(127, 0, 255, 0.5), inset 0 0 40px rgba(127, 0, 255, 0.08);
  height: 100%;
  overflow: hidden;
  position: relative;
  width: 100%;
}

.festival-map svg {
  display: block;
  height: 100%;
  width: 100%;
}

.you-marker,
.friend-marker {
  align-items: center;
  border-radius: 999px;
  display: flex;
  justify-content: center;
  position: absolute;
  transform: translate(-50%, -50%);
}

.you-marker {
  background: linear-gradient(135deg, #a855f7, #5b21b6);
  border: 2px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 0 28px rgba(127, 0, 255, 0.9);
  color: #fff;
  font-size: 20px;
  height: 44px;
  left: 49%;
  top: 48%;
  width: 44px;
  z-index: 3;
}

.friend-marker {
  border: 2px solid rgba(255, 255, 255, 0.72);
  color: #fff;
  font-size: 17px;
  height: 36px;
  width: 36px;
  z-index: 4;
}

.friend-marker::before {
  animation: ping 2.4s infinite;
  background: currentColor;
  border-radius: inherit;
  content: '';
  inset: -5px;
  opacity: 0.18;
  position: absolute;
}

.friend-marker.offline {
  border-color: rgba(100, 100, 100, 0.5);
  opacity: 0.7;
}

.friend-marker.offline::before {
  display: none;
}

.friend-marker span {
  background: rgba(0, 0, 0, 0.78);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 9px;
  bottom: -30px;
  font-size: 11px;
  font-weight: 850;
  left: 50%;
  opacity: 0;
  padding: 4px 8px;
  pointer-events: none;
  position: absolute;
  transform: translateX(-50%);
  transition: opacity 160ms ease;
  white-space: nowrap;
}

.friend-marker:hover span {
  opacity: 1;
}

.map-north {
  background: rgba(0, 0, 0, 0.72);
  border: 1px solid rgba(168, 85, 247, 0.5);
  border-radius: 999px;
  color: #d8b4fe;
  font-family: monospace;
  font-size: 13px;
  font-weight: 900;
  left: 50%;
  padding: 5px 14px;
  position: absolute;
  top: 8px;
  transform: translateX(-50%);
}

@keyframes ping {
  to {
    opacity: 0;
    transform: scale(1.8);
  }
}
</style>
