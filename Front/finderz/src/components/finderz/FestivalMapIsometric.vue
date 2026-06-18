<template>
  <div ref="containerRef" class="festival-map" @pointerdown="hintVisible = false">
    <div v-if="hintVisible" class="map-hint">
      <span>Arrastra · Pinch zoom</span>
    </div>

    <div class="north-indicator">N ↑</div>

    <div class="zone-legend">
      <div v-for="item in legendItems" :key="item.label">
        <i :class="{ round: item.round }" :style="{ backgroundColor: item.color, boxShadow: item.round ? '0 0 6px rgba(200,150,255,0.9)' : undefined }"></i>
        <span :class="{ bright: item.round }">{{ item.label }}</span>
      </div>
    </div>

    <div class="mini-radar">
      <div class="radar-face">
        <i class="ring one"></i>
        <i class="ring two"></i>
        <i class="ring three"></i>
        <i class="sweep"></i>
        <i class="center"></i>
        <b
          v-for="friend in radarFriends"
          :key="friend.id"
          :style="{
            backgroundColor: friendColors[friend.id]?.bg,
            left: `${(friend.x / 100) * 36 + 2}px`,
            top: `${(friend.y / 100) * 36 + 2}px`,
          }"
        ></b>
      </div>
    </div>

    <div
      v-if="activeLabel"
      class="poi-label"
      :style="{ left: `${activeLabel.x}px`, top: `${activeLabel.y}px`, borderColor: activeLabel.color }"
    >
      <span>{{ activeLabel.icon }}</span>
      <strong>{{ activeLabel.label }}</strong>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import type { Friend, POI, RouteTarget } from './types';
import { festivalPois, friendColors, percentToWorld } from './types';

const props = defineProps<{
  friends: Friend[];
  routeTarget: RouteTarget | null;
}>();

const containerRef = ref<HTMLDivElement | null>(null);
let frameId = 0;
let scene: THREE.Scene | null = null;
let renderer: THREE.WebGLRenderer | null = null;
let controls: OrbitControls | null = null;
let camera: THREE.OrthographicCamera | null = null;
let resizeObserver: ResizeObserver | null = null;
let routeGroup: THREE.Group | null = null;
let routeTube: THREE.Mesh | null = null;
let routeCone: THREE.Mesh | null = null;
let routeRing: THREE.Mesh | null = null;
let disposeFns: Array<() => void> = [];
let pickTargets: THREE.Object3D[] = [];
let pinnedLabelTimer = 0;
const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();
const hintVisible = ref(true);
const activeLabel = ref<{
  id: string;
  icon: string;
  label: string;
  color: string;
  world: THREE.Vector3;
  x: number;
  y: number;
} | null>(null);

const legendItems = [
  { color: '#ffffff', label: 'Tu', round: true },
  { color: '#6600cc', label: 'Main Stage' },
  { color: '#880055', label: 'Stage 2' },
  { color: '#005588', label: 'Techno Dome' },
  { color: '#885500', label: 'Food Court' },
  { color: '#2a5a2a', label: 'Camping' },
];

const radarFriends = computed(() => props.friends.filter((friend) => friend.status === 'online'));

function poiColor(type: POI['type']) {
  return {
    stage: '#9d4edd',
    food: '#f59e0b',
    bar: '#f59e0b',
    restroom: '#60a5fa',
    info: '#3b82f6',
    medical: '#ef4444',
    exit: '#22c55e',
    vip: '#ffd700',
  }[type];
}

function track<T extends THREE.Object3D>(object: T): T {
  disposeFns.push(() => {
    object.traverse((child) => {
      const mesh = child as THREE.Mesh;
      const geometry = mesh.geometry as THREE.BufferGeometry | undefined;
      const material = mesh.material as THREE.Material | THREE.Material[] | undefined;
      geometry?.dispose();
      if (Array.isArray(material)) material.forEach((mat) => mat.dispose());
      else material?.dispose();
    });
  });
  return object;
}

function box(x: number, y: number, z: number, w: number, h: number, d: number, color: number, emissive = 0x000000, intensity = 0) {
  const mesh = track(new THREE.Mesh(
    new THREE.BoxGeometry(w, h, d),
    new THREE.MeshLambertMaterial({ color, emissive, emissiveIntensity: intensity }),
  ));
  mesh.position.set(x, y + h / 2, z);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  scene?.add(mesh);
  return mesh;
}

function buildRoutePath(destX: number, destZ: number) {
  const points = [new THREE.Vector3(0, 0.5, 0)];
  if (Math.abs(destX) > 3 && Math.abs(destZ) > 3) {
    if (Math.abs(destZ) > Math.abs(destX)) {
      points.push(new THREE.Vector3(0, 0.5, destZ * 0.55));
      points.push(new THREE.Vector3(destX * 0.55, 0.5, destZ * 0.55));
    } else {
      points.push(new THREE.Vector3(destX * 0.55, 0.5, 0));
      points.push(new THREE.Vector3(destX * 0.55, 0.5, destZ * 0.55));
    }
  } else {
    points.push(new THREE.Vector3(destX * 0.5, 0.5, destZ * 0.5));
  }
  points.push(new THREE.Vector3(destX, 0.5, destZ));
  return points;
}

function clearRoute() {
  if (!scene || !routeGroup) return;
  scene.remove(routeGroup);
  routeGroup.traverse((child) => {
    const mesh = child as THREE.Mesh;
    mesh.geometry?.dispose();
    const material = mesh.material as THREE.Material | THREE.Material[] | undefined;
    if (Array.isArray(material)) material.forEach((mat) => mat.dispose());
    else material?.dispose();
  });
  routeGroup = null;
  routeTube = null;
  routeCone = null;
  routeRing = null;
}

function syncRoute() {
  if (!scene) return;
  clearRoute();
  const target = props.routeTarget;
  if (!target) return;

  routeGroup = new THREE.Group();
  const color = new THREE.Color(target.color);
  const curve = new THREE.CatmullRomCurve3(buildRoutePath(target.wx, target.wz));
  routeTube = new THREE.Mesh(
    new THREE.TubeGeometry(curve, 48, 0.22, 8, false),
    new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.82 }),
  );
  const glow = new THREE.Mesh(
    new THREE.TubeGeometry(curve, 48, 0.5, 8, false),
    new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.2 }),
  );
  routeGroup.add(routeTube, glow);

  routeCone = new THREE.Mesh(
    new THREE.ConeGeometry(0.7, 1.6, 8),
    new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.95 }),
  );
  routeCone.rotation.x = Math.PI;
  routeCone.position.set(target.wx, 3.2, target.wz);
  routeGroup.add(routeCone);

  routeRing = new THREE.Mesh(
    new THREE.RingGeometry(0.9, 1.2, 32),
    new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.6, side: THREE.DoubleSide }),
  );
  routeRing.rotation.x = -Math.PI / 2;
  routeRing.position.set(target.wx, 0.18, target.wz);
  routeGroup.add(routeRing);
  scene.add(routeGroup);
}

function createStageLight(x: number, z: number, color: number, stageLights: THREE.Mesh[], y = 4.4) {
  const light = box(x, y, z, 0.46, 0.46, 0.46, color, color, 1.2);
  stageLights.push(light);
}

function addRingNodes(group: THREE.Group, radius: number, color: number, count: number, offset = 0) {
  for (let i = 0; i < count; i += 1) {
    const angle = offset + (i / count) * Math.PI * 2;
    const node = track(new THREE.Mesh(
      new THREE.SphereGeometry(0.16, 12, 8),
      new THREE.MeshBasicMaterial({ color }),
    ));
    node.position.set(Math.cos(angle) * radius, 0, Math.sin(angle) * radius);
    group.add(node);
  }
}

function projectLabelPosition() {
  if (!activeLabel.value || !camera || !containerRef.value) return;
  const projected = activeLabel.value.world.clone().project(camera);
  activeLabel.value.x = (projected.x * 0.5 + 0.5) * containerRef.value.clientWidth;
  activeLabel.value.y = (-projected.y * 0.5 + 0.5) * containerRef.value.clientHeight;
}

function showPoiLabel(poi: POI) {
  const heightByType: Record<POI['type'], number> = {
    stage: poi.id === 'techDome' ? 6.1 : 6.8,
    food: 3.6,
    bar: 3.3,
    restroom: 3.3,
    info: 3.2,
    medical: 3.1,
    exit: 5.1,
    vip: 4.3,
  };
  activeLabel.value = {
    id: poi.id,
    icon: poi.icon,
    label: poi.name,
    color: poiColor(poi.type),
    world: new THREE.Vector3(poi.wx, heightByType[poi.type], poi.wz),
    x: 0,
    y: 0,
  };
  projectLabelPosition();
}

function addPoiHitbox(poi: POI, x: number, z: number, w: number, h: number, d: number) {
  const hitbox = track(new THREE.Mesh(
    new THREE.BoxGeometry(w, h, d),
    new THREE.MeshBasicMaterial({ transparent: true, opacity: 0, depthWrite: false, colorWrite: false }),
  ));
  hitbox.position.set(x, h / 2, z);
  hitbox.userData.poi = poi;
  pickTargets.push(hitbox);
  scene?.add(hitbox);
}

function findPoi(id: string) {
  return festivalPois.find((poi) => poi.id === id);
}

function pickPoi(event: PointerEvent, persist = false) {
  if (!renderer || !camera) return null;
  const rect = renderer.domElement.getBoundingClientRect();
  pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
  raycaster.setFromCamera(pointer, camera);
  const [hit] = raycaster.intersectObjects(pickTargets, false);
  const poi = hit?.object.userData.poi as POI | undefined;
  renderer.domElement.style.cursor = poi ? 'pointer' : 'grab';
  if (poi) {
    showPoiLabel(poi);
    if (persist) {
      window.clearTimeout(pinnedLabelTimer);
      pinnedLabelTimer = window.setTimeout(() => {
        activeLabel.value = null;
      }, 2500);
    }
  } else if (!persist) {
    activeLabel.value = null;
  }
  return poi;
}

function mountScene() {
  const container = containerRef.value;
  if (!container) return;
  const width = Math.max(container.clientWidth, 1);
  const height = Math.max(container.clientHeight, 1);
  const aspect = width / height;
  const frustum = 34;

  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x130022);
  scene.fog = new THREE.Fog(0x130022, 55, 80);

  camera = new THREE.OrthographicCamera(
    -frustum * aspect / 2,
    frustum * aspect / 2,
    frustum / 2,
    -frustum / 2,
    -200,
    300,
  );
  camera.position.set(20, 22, 20);
  camera.lookAt(0, 0, -1);

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
  renderer.setSize(width, height);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFShadowMap;
  renderer.domElement.className = 'festival-map-webgl';
  container.appendChild(renderer.domElement);
  renderer.domElement.style.cursor = 'grab';

  const handlePointerMove = (event: PointerEvent) => pickPoi(event);
  const handleClick = (event: PointerEvent) => pickPoi(event, true);
  const handlePointerLeave = () => {
    renderer?.domElement.style.setProperty('cursor', 'grab');
    activeLabel.value = null;
  };
  renderer.domElement.addEventListener('pointermove', handlePointerMove);
  renderer.domElement.addEventListener('click', handleClick);
  renderer.domElement.addEventListener('pointerleave', handlePointerLeave);
  disposeFns.push(() => {
    renderer?.domElement.removeEventListener('pointermove', handlePointerMove);
    renderer?.domElement.removeEventListener('click', handleClick);
    renderer?.domElement.removeEventListener('pointerleave', handlePointerLeave);
  });

  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableRotate = false;
  controls.enableDamping = true;
  controls.dampingFactor = 0.1;
  controls.screenSpacePanning = true;
  controls.minZoom = 0.42;
  controls.maxZoom = 6;
  controls.zoomSpeed = 1.35;
  controls.panSpeed = 0.9;
  controls.mouseButtons = { LEFT: THREE.MOUSE.PAN, MIDDLE: THREE.MOUSE.DOLLY, RIGHT: THREE.MOUSE.PAN };
  controls.touches = { ONE: THREE.TOUCH.PAN, TWO: THREE.TOUCH.DOLLY_PAN };

  scene.add(new THREE.AmbientLight(0x9b74cc, 0.75));
  const sun = new THREE.DirectionalLight(0xffffff, 1.35);
  sun.position.set(12, 24, 8);
  sun.castShadow = true;
  sun.shadow.mapSize.setScalar(1024);
  sun.shadow.camera.left = sun.shadow.camera.bottom = -25;
  sun.shadow.camera.right = sun.shadow.camera.top = 25;
  scene.add(sun);
  const fill = new THREE.DirectionalLight(0x3322ff, 0.35);
  fill.position.set(-10, 6, -10);
  scene.add(fill);

  const ground = track(new THREE.Mesh(
    new THREE.PlaneGeometry(32, 32),
    new THREE.MeshLambertMaterial({ color: 0x0f2a10 }),
  ));
  ground.rotation.x = -Math.PI / 2;
  ground.receiveShadow = true;
  scene.add(ground);

  const grid = new THREE.GridHelper(32, 16, 0x3a1a5a, 0x250a45);
  const gridMaterials = Array.isArray(grid.material) ? grid.material : [grid.material];
  gridMaterials.forEach((mat) => {
    mat.opacity = 0.35;
    mat.transparent = true;
  });
  grid.position.y = 0.02;
  scene.add(grid);

  const borderLines = track(new THREE.LineSegments(
    new THREE.EdgesGeometry(new THREE.BoxGeometry(32.1, 0.05, 32.1)),
    new THREE.LineBasicMaterial({ color: 0x8800ff }),
  ));
  borderLines.position.set(0, 0.02, 0);
  scene.add(borderLines);

  box(0, 0, 0, 32, 0.06, 4.5, 0x2a1a4a);
  box(0, 0, 0, 4.5, 0.06, 32, 0x2a1a4a);
  box(0, 0, 0, 7, 0.1, 7, 0x3a2460);
  [[-9, -9], [9, -9], [-9, 9], [9, 9]].forEach(([x, z]) => box(x, 0, z, 13, 0.055, 13, 0x1a3a1a));

  const stageLights: THREE.Mesh[] = [];
  box(0, 0, -12.5, 13, 0.35, 6, 0x2d0066);
  box(0, 0.35, -15, 13, 5, 0.9, 0x4400aa, 0x3300aa, 0.2);
  box(0, 5.35, -12.5, 14, 0.45, 7, 0x3300aa, 0x2200aa, 0.15);
  box(-5.8, 0.35, -12.5, 1, 5.5, 1, 0x110028);
  box(5.8, 0.35, -12.5, 1, 5.5, 1, 0x110028);
  box(0, 1.5, -14.7, 9, 3, 0.18, 0x110033, 0x7700ee, 0.7);
  [0xff0055, 0x8800ff, 0x00eeff, 0xff6600, 0x7700ff].forEach((color, index) => {
    createStageLight((index - 2) * 2.4, -12.5, color, stageLights, 6.08);
    const cone = track(new THREE.Mesh(
      new THREE.ConeGeometry(0.5, 4, 8),
      new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.12, side: THREE.DoubleSide }),
    ));
    cone.position.set((index - 2) * 2.4, 5.2, -12.5);
    scene?.add(cone);
  });
  box(0, 0.36, -9.2, 7, 0.06, 1.8, 0x9d4edd, 0x6600cc, 0.4);

  box(11.5, 0, -7, 7, 0.3, 4.5, 0x3a0022);
  box(11.5, 0.3, -9.7, 7, 3.5, 0.8, 0x660033, 0x440022, 0.2);
  box(11.5, 3.8, -7, 8, 0.35, 5.5, 0x550028);
  box(11.5, 2, -9.5, 5.5, 2.5, 0.18, 0x220011, 0xaa0044, 0.8);
  [9, 10.8, 12.6, 14.4].forEach((x) => createStageLight(x, -7, 0xff2255, stageLights));

  const domeBase = track(new THREE.Mesh(
    new THREE.CylinderGeometry(3.9, 3.9, 2.2, 32),
    new THREE.MeshLambertMaterial({ color: 0x001e3c, emissive: 0x000a22, emissiveIntensity: 0.42 }),
  ));
  domeBase.position.set(-11.5, 1.1, -7);
  domeBase.castShadow = true;
  scene.add(domeBase);

  const domeWallGlow = track(new THREE.Mesh(
    new THREE.CylinderGeometry(4.04, 4.04, 2.28, 32, 1, true),
    new THREE.MeshBasicMaterial({ color: 0x009dff, transparent: true, opacity: 0.1, side: THREE.DoubleSide }),
  ));
  domeWallGlow.position.set(-11.5, 1.14, -7);
  scene.add(domeWallGlow);

  const dome = track(new THREE.Mesh(
    new THREE.SphereGeometry(3.85, 32, 14, 0, Math.PI * 2, 0, Math.PI / 2),
    new THREE.MeshLambertMaterial({ color: 0x003060, emissive: 0x001533, emissiveIntensity: 0.5, transparent: true, opacity: 0.9 }),
  ));
  dome.position.set(-11.5, 2.25, -7);
  scene.add(dome);

  const domeRingGroup = track(new THREE.Group());
  domeRingGroup.position.set(-11.5, 2.28, -7);
  scene.add(domeRingGroup);
  const domeRing = track(new THREE.Mesh(
    new THREE.TorusGeometry(4.08, 0.14, 8, 48),
    new THREE.MeshLambertMaterial({ color: 0x00aaff, emissive: 0x0077cc, emissiveIntensity: 1 }),
  ));
  domeRing.rotation.x = Math.PI / 2;
  domeRingGroup.add(domeRing);
  addRingNodes(domeRingGroup, 4.08, 0xb8f3ff, 3, 0.35);

  const domeRing2Group = track(new THREE.Group());
  domeRing2Group.position.set(-11.5, 3.45, -7);
  scene.add(domeRing2Group);
  const domeRing2 = track(new THREE.Mesh(
    new THREE.TorusGeometry(3.35, 0.08, 6, 40),
    new THREE.MeshLambertMaterial({ color: 0x0055ff, emissive: 0x0033aa, emissiveIntensity: 0.8 }),
  ));
  domeRing2.rotation.x = Math.PI / 2;
  domeRing2Group.add(domeRing2);
  addRingNodes(domeRing2Group, 3.35, 0x8fb4ff, 2, 1.1);
  box(-11.5, 0, -3.3, 2.5, 1.8, 0.6, 0x004477);

  box(7, 0, -3, 5.5, 0.08, 5.5, 0x1e1200);
  for (let i = 0; i < 6; i += 1) {
    const px = 4.5 + i * 1.1;
    box(px, 0.08, -5.5, 0.12, 1, 0.12, 0xddaa00);
    box(px, 0.08, -0.5, 0.12, 1, 0.12, 0xddaa00);
  }
  box(7, 0.8, -5.5, 5.5, 0.1, 0.12, 0xbb9900);
  box(7, 0.8, -0.5, 5.5, 0.1, 0.12, 0xbb9900);
  box(4.5, 0.8, -3, 0.12, 0.1, 5, 0xbb9900);
  box(9.5, 0.8, -3, 0.12, 0.1, 5, 0xbb9900);
  const vipTent = track(new THREE.Mesh(
    new THREE.ConeGeometry(2.8, 2.2, 4),
    new THREE.MeshLambertMaterial({ color: 0x2e1a00, emissive: 0x100800, emissiveIntensity: 0.2 }),
  ));
  vipTent.position.set(7, 2.3, -3);
  vipTent.rotation.y = Math.PI / 4;
  scene.add(vipTent);

  box(9.5, 0, 9.5, 12, 0.08, 12, 0x1e0d00);
  for (let row = 0; row < 2; row += 1) {
    for (let col = 0; col < 3; col += 1) {
      const sx = 6.5 + col * 3.3;
      const sz = 6.8 + row * 3.3;
      box(sx, 0.08, sz, 2.2, 1.3, 1.8, [0x883300, 0x664400, 0x772200, 0x995500, 0x553300, 0x773300][row * 3 + col]);
      box(sx, 1.38, sz - 0.6, 2.8, 0.1, 1, 0xcc6600);
    }
  }
  const canopy = track(new THREE.Mesh(
    new THREE.ConeGeometry(2.8, 1.8, 4),
    new THREE.MeshLambertMaterial({ color: 0xcc5500 }),
  ));
  canopy.position.set(9.5, 1.9, 10);
  canopy.rotation.y = Math.PI / 4;
  canopy.castShadow = true;
  scene.add(canopy);
  box(9.5, 0.08, 10, 4, 0.08, 4, 0x2a1000);

  box(-9.5, 0, 9.5, 12, 0.06, 12, 0x0d2010);
  const tentRots = [0.3, 1, 0.6, 1.5, 0.2, 0.9, 1.2, 0.4, 0.7];
  for (let row = 0; row < 3; row += 1) {
    for (let col = 0; col < 3; col += 1) {
      const tent = track(new THREE.Mesh(
        new THREE.ConeGeometry(1.2, 1.8, 3),
        new THREE.MeshLambertMaterial({ color: row % 2 === 0 ? 0x2a5a2a : 0x1a4a1a }),
      ));
      tent.position.set(-13 + col * 3.3, 0.9, 6.5 + row * 3.3);
      tent.rotation.y = tentRots[row * 3 + col];
      scene.add(tent);
    }
  }

  box(-5.5, 0, 2, 5.5, 0.08, 5.5, 0x181000);
  [-7, -5.3, -3.6].forEach((x, index) => {
    box(x, 0.08, 2, 0.9, 0.55, 0.9, 0x2e1a00);
    box(x, 0.63, 2, 0.07, 1.6, 0.07, 0x7a4400);
    const umbrella = track(new THREE.Mesh(
      new THREE.ConeGeometry(0.85, 0.5, 8),
      new THREE.MeshLambertMaterial({ color: [0xff6600, 0xcc4400, 0xff8800][index] }),
    ));
    umbrella.position.set(x, 2.4, 2);
    scene?.add(umbrella);
  });

  const medicalX = -3.8;
  const medicalZ = -3.8;
  box(medicalX, 0, medicalZ, 3.1, 0.12, 2.6, 0x3a0707);
  box(medicalX, 0.12, medicalZ, 2.7, 1.45, 2.2, 0xf8fafc, 0x331111, 0.04);
  box(medicalX, 1.57, medicalZ, 3.1, 0.22, 2.6, 0xef4444, 0x7f1d1d, 0.25);
  box(medicalX, 0.72, medicalZ - 1.12, 0.42, 0.9, 0.08, 0xef4444, 0xaa1111, 0.4);
  box(medicalX, 0.96, medicalZ - 1.14, 1.1, 0.32, 0.08, 0xef4444, 0xaa1111, 0.4);
  box(medicalX - 0.95, 0.12, medicalZ + 0.86, 0.48, 0.9, 0.08, 0x111827);
  box(medicalX + 0.95, 0.12, medicalZ + 0.86, 0.48, 0.9, 0.08, 0x111827);
  const medicalBeacon = track(new THREE.Mesh(
    new THREE.SphereGeometry(0.18, 12, 8),
    new THREE.MeshBasicMaterial({ color: 0xffdddd }),
  ));
  medicalBeacon.position.set(medicalX, 2.08, medicalZ);
  scene?.add(medicalBeacon);

  const treeData: [number, number, number, number][] = [
    [-14, -12, 1.05, 0.3], [-9, -13.5, 0.9, 0.8], [9, -13.5, 0.95, 1.1], [14, -12, 1.05, 0.5],
    [-15, -7, 0.9, 0.7], [15, -1, 1.05, 0.9], [-15, 7.5, 1, 0.4], [15, 7.5, 0.95, 1.4],
    [-14, 14, 1.05, 1], [-5, 14, 0.9, 0.2], [5, 14, 1, 1.2], [14, 14, 1, 0.7],
    [-2, 12.8, 0.85, 0.8], [2, 12.8, 0.85, 1.2], [-14.5, -1.5, 0.85, 0.2], [14.5, -10.5, 0.9, 0.1],
    [-15.2, -14.6, 0.78, 0.6], [-12.2, -14.8, 0.86, 1.2], [-6.5, -15, 0.74, 0.4], [6.5, -15, 0.82, 1.6],
    [12.2, -14.7, 0.78, 0.9], [15.1, -14.2, 0.9, 0.2], [-15.2, 12.1, 0.82, 1.5], [-11.7, 15, 0.72, 0.7],
    [11.7, 15, 0.76, 1.1], [15.2, 12.4, 0.86, 0.5], [-15.4, 4.6, 0.78, 0.9], [15.4, 4.8, 0.8, 1.7],
    [-12.8, -0.2, 0.74, 1.4], [12.8, -4.2, 0.76, 0.3],
  ];
  treeData.forEach(([x, z, scale, rot]) => {
    box(x, 0, z, 0.42, 1.35, 0.42, 0x3d2010);
    const foliage = track(new THREE.Mesh(
      new THREE.SphereGeometry(scale, 8, 6),
      new THREE.MeshLambertMaterial({ color: 0x1a5a1a }),
    ));
    foliage.position.set(x, 1.4 + scale * 0.5, z);
    foliage.rotation.y = rot;
    foliage.castShadow = true;
    scene?.add(foliage);
  });

  [
    ['mainStage', 0, -12.5, 14, 7, 7],
    ['stage2', 11.5, -7, 8, 5, 6],
    ['techDome', -11.5, -7, 8.4, 5, 8.4],
    ['vip', 7, -3, 6.2, 4.5, 6.2],
    ['foodCourt', 9.5, 9.5, 12.5, 3.8, 12.5],
    ['beerGarden', -5.5, 2, 6.2, 3.2, 6.2],
    ['medical', medicalX, medicalZ, 3.4, 3.1, 2.9],
    ['camping', -9.5, 9.5, 12.5, 3.2, 12.5],
  ].forEach(([id, x, z, w, h, d]) => {
    const poi = findPoi(id as string);
    if (poi) addPoiHitbox(poi, x as number, z as number, w as number, h as number, d as number);
  });

  const youPole = track(new THREE.Mesh(
    new THREE.CylinderGeometry(0.12, 0.12, 2.4, 10),
    new THREE.MeshLambertMaterial({ color: 0xffffff, emissive: 0xddddff, emissiveIntensity: 0.5 }),
  ));
  youPole.position.set(0, 1.2, 0);
  scene.add(youPole);
  const youMarker = track(new THREE.Mesh(
    new THREE.SphereGeometry(0.8, 20, 16),
    new THREE.MeshLambertMaterial({ color: 0xffffff, emissive: 0xbb88ff, emissiveIntensity: 1.2 }),
  ));
  youMarker.position.set(0, 2.6, 0);
  scene.add(youMarker);
  const youArrow = track(new THREE.Mesh(
    new THREE.ConeGeometry(0.45, 0.9, 8),
    new THREE.MeshLambertMaterial({ color: 0xcc88ff, emissive: 0x9933ff, emissiveIntensity: 1 }),
  ));
  youArrow.position.set(0, 3.85, 0);
  scene.add(youArrow);
  const pulseRing = track(new THREE.Mesh(
    new THREE.RingGeometry(1.2, 1.5, 40),
    new THREE.MeshBasicMaterial({ color: 0xcc88ff, transparent: true, opacity: 0.7, side: THREE.DoubleSide }),
  ));
  pulseRing.rotation.x = -Math.PI / 2;
  pulseRing.position.set(0, 0.13, 0);
  scene.add(pulseRing);
  const pulseRing2 = track(new THREE.Mesh(
    new THREE.RingGeometry(1.8, 2.1, 40),
    new THREE.MeshBasicMaterial({ color: 0x9933ff, transparent: true, opacity: 0.35, side: THREE.DoubleSide }),
  ));
  pulseRing2.rotation.x = -Math.PI / 2;
  pulseRing2.position.set(0, 0.13, 0);
  scene.add(pulseRing2);

  const friendMeshes: Array<{ mesh: THREE.Mesh; ring: THREE.Mesh | null; status: Friend['status'] }> = [];
  props.friends.forEach((friend) => {
    const [wx, wz] = percentToWorld(friend.x, friend.y);
    const color = new THREE.Color(friendColors[friend.id]?.bg ?? '#888888');
    const marker = track(new THREE.Mesh(
      new THREE.SphereGeometry(0.58, 14, 10),
      new THREE.MeshLambertMaterial({
        color,
        emissive: color,
        emissiveIntensity: friend.status === 'online' ? 0.6 : 0.1,
        transparent: friend.status === 'offline',
        opacity: friend.status === 'offline' ? 0.45 : 1,
      }),
    ));
    marker.position.set(wx, 1.3, wz);
    scene?.add(marker);
    box(wx, 0, wz, 0.16, 1, 0.16, color.getHex());

    let ring: THREE.Mesh | null = null;
    if (friend.status === 'online') {
      ring = track(new THREE.Mesh(
        new THREE.RingGeometry(0.75, 0.95, 20),
        new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.55, side: THREE.DoubleSide }),
      ));
      ring.rotation.x = -Math.PI / 2;
      ring.position.set(wx, 0.12, wz);
      scene?.add(ring);
    }
    friendMeshes.push({ mesh: marker, ring, status: friend.status });
  });

  const syncSize = () => {
    if (!containerRef.value || !renderer || !camera) return;
    const w = containerRef.value.clientWidth;
    const h = containerRef.value.clientHeight;
    if (w === 0 || h === 0) return;
    const nextAspect = w / h;
    camera.left = -frustum * nextAspect / 2;
    camera.right = frustum * nextAspect / 2;
    camera.top = frustum / 2;
    camera.bottom = -frustum / 2;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h, false);
    renderer.domElement.style.width = '100%';
    renderer.domElement.style.height = '100%';
  };
  resizeObserver = new ResizeObserver(syncSize);
  resizeObserver.observe(container);
  window.addEventListener('resize', syncSize);
  disposeFns.push(() => window.removeEventListener('resize', syncSize));
  Promise.resolve().then(syncSize);

  let t = 0;
  const animate = () => {
    frameId = requestAnimationFrame(animate);
    t += 0.016;
    const bob = Math.sin(t * 2.2) * 0.2;
    youMarker.position.y = 2.6 + bob;
    youArrow.position.y = 3.85 + bob;
    youPole.position.y = 1.2 + bob * 0.5;
    youMarker.scale.setScalar(1 + Math.sin(t * 2.2) * 0.06);
    const pulseScale = 1 + ((Math.sin(t * 1.6) + 1) / 2) * 1.4;
    pulseRing.scale.setScalar(pulseScale);
    (pulseRing.material as THREE.MeshBasicMaterial).opacity = Math.max(0, 0.7 - (pulseScale - 1) * 0.4);
    const pulseScale2 = 1 + ((Math.sin(t * 1.6 - 1.2) + 1) / 2) * 1.6;
    pulseRing2.scale.setScalar(pulseScale2);
    (pulseRing2.material as THREE.MeshBasicMaterial).opacity = Math.max(0, 0.4 - (pulseScale2 - 1) * 0.2);
    friendMeshes.forEach(({ mesh, ring, status }, index) => {
      if (status !== 'online') return;
      mesh.position.y = 1.3 + Math.sin(t * 1.7 + index) * 0.14;
      if (ring) {
        const scale = 1 + ((Math.sin(t * 1.2 + index) + 1) / 2) * 0.9;
        ring.scale.setScalar(scale);
        (ring.material as THREE.MeshBasicMaterial).opacity = Math.max(0, 0.55 - (scale - 1) * 0.25);
      }
    });
    stageLights.forEach((mesh, index) => {
      (mesh.material as THREE.MeshLambertMaterial).emissiveIntensity = 0.8 + Math.sin(t * 3 + index * 1.1) * 0.7;
    });
    domeRingGroup.position.y = 2.28 + Math.sin(t * 0.75) * 0.035;
    domeRingGroup.rotation.y = t * 0.55;
    domeRing.rotation.x = Math.PI / 2;
    domeRing2Group.position.y = 3.45 + Math.sin(t * 0.82 + 0.7) * 0.04;
    domeRing2Group.rotation.y = -t * 0.72;
    domeRing2.rotation.x = Math.PI / 2;
    if (routeTube) (routeTube.material as THREE.MeshBasicMaterial).opacity = 0.62 + Math.sin(t * 5) * 0.28;
    if (routeCone) routeCone.position.y = 3.2 + Math.sin(t * 3) * 0.3;
    if (routeRing) {
      const routeRingScale = 1 + Math.sin(t * 2.5) * 0.2;
      routeRing.scale.set(routeRingScale, routeRingScale, routeRingScale);
    }
    controls?.update();
    projectLabelPosition();
    if (scene && camera && renderer) renderer.render(scene, camera);
  };
  animate();
  syncRoute();
}

watch(() => props.routeTarget, syncRoute, { deep: true });

onMounted(mountScene);

onBeforeUnmount(() => {
  cancelAnimationFrame(frameId);
  window.clearTimeout(pinnedLabelTimer);
  clearRoute();
  resizeObserver?.disconnect();
  controls?.dispose();
  disposeFns.forEach((dispose) => dispose());
  disposeFns = [];
  if (renderer && containerRef.value?.contains(renderer.domElement)) {
    containerRef.value.removeChild(renderer.domElement);
  }
  renderer?.dispose();
  pickTargets = [];
  renderer = null;
  scene = null;
  camera = null;
});
</script>

<style scoped>
.festival-map {
  position: absolute;
  inset: 0;
  overflow: hidden;
  background: #130022;
  border: 2px solid rgba(168, 85, 247, 0.6);
  border-radius: 18px;
  box-shadow: 0 0 60px rgba(127, 0, 255, 0.5), inset 0 0 40px rgba(127, 0, 255, 0.06);
}

:deep(.festival-map-webgl) {
  display: block;
  height: 100%;
  width: 100%;
  touch-action: none;
}

.map-hint,
.north-indicator,
.zone-legend,
.mini-radar {
  pointer-events: none;
  position: absolute;
  z-index: 2;
}

.map-hint {
  animation: hintIn 0.3s ease, hintOut 0.4s ease 2.8s forwards;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
}

.map-hint span,
.north-indicator,
.zone-legend,
.mini-radar {
  background: rgba(0, 0, 0, 0.7);
  border: 1px solid rgba(168, 85, 247, 0.42);
  backdrop-filter: blur(10px);
}

.map-hint span {
  border-radius: 999px;
  color: rgba(255, 255, 255, 0.84);
  display: block;
  font-size: 11px;
  font-weight: 700;
  padding: 7px 12px;
}

.north-indicator {
  border-radius: 999px;
  color: #d8b4fe;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 14px;
  font-weight: 900;
  left: 50%;
  letter-spacing: 0.2em;
  padding: 5px 14px;
  top: 8px;
  transform: translateX(-50%);
}

.zone-legend {
  border-radius: 14px;
  bottom: 10px;
  display: grid;
  gap: 5px;
  left: 10px;
  padding: 9px 10px;
}

.zone-legend div {
  align-items: center;
  display: flex;
  gap: 7px;
}

.zone-legend i {
  border-radius: 3px;
  flex: 0 0 auto;
  height: 8px;
  width: 8px;
}

.zone-legend i.round {
  border-radius: 999px;
}

.zone-legend span {
  color: rgba(255, 255, 255, 0.72);
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 9px;
  white-space: nowrap;
}

.zone-legend span.bright {
  color: #fff;
  font-weight: 900;
}

.mini-radar {
  border-radius: 14px;
  bottom: 10px;
  padding: 8px;
  right: 10px;
}

.poi-label {
  align-items: center;
  background: rgba(7, 2, 14, 0.86);
  border: 1px solid;
  border-radius: 999px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
  color: #fff;
  display: inline-flex;
  gap: 7px;
  max-width: min(210px, calc(100% - 24px));
  padding: 7px 10px 7px 8px;
  pointer-events: none;
  position: absolute;
  transform: translate(-50%, -120%);
  z-index: 4;
}

.poi-label::after {
  background: currentColor;
  border-radius: 999px;
  bottom: -8px;
  box-shadow: 0 0 10px currentColor;
  content: '';
  height: 5px;
  left: 50%;
  opacity: 0.8;
  position: absolute;
  transform: translateX(-50%);
  width: 5px;
}

.poi-label span {
  align-items: center;
  background: rgba(255, 255, 255, 0.12);
  border-radius: 999px;
  display: flex;
  flex: 0 0 auto;
  font-size: 15px;
  height: 25px;
  justify-content: center;
  width: 25px;
}

.poi-label strong {
  display: block;
  font-size: 12px;
  line-height: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.radar-face {
  height: 40px;
  position: relative;
  width: 40px;
}

.radar-face .ring {
  border: 1px solid rgba(168, 85, 247, 0.32);
  border-radius: 999px;
  position: absolute;
}

.radar-face .one {
  inset: 0;
}

.radar-face .two {
  inset: 6px;
}

.radar-face .three {
  inset: 12px;
}

.radar-face .sweep {
  animation: radarSweep 3s linear infinite;
  background: linear-gradient(to bottom, rgba(216, 180, 254, 0.9), transparent);
  height: 20px;
  left: 19px;
  position: absolute;
  top: 0;
  transform-origin: 1px 20px;
  width: 2px;
}

.radar-face .center,
.radar-face b {
  border-radius: 999px;
  position: absolute;
}

.radar-face .center {
  background: #c084fc;
  height: 6px;
  left: 17px;
  top: 17px;
  width: 6px;
}

.radar-face b {
  height: 4px;
  width: 4px;
}

@keyframes radarSweep {
  to {
    transform: rotate(360deg);
  }
}

@keyframes hintIn {
  from {
    opacity: 0;
    transform: translate(-50%, calc(-50% + 6px));
  }
  to {
    opacity: 1;
    transform: translate(-50%, -50%);
  }
}

@keyframes hintOut {
  to {
    opacity: 0;
  }
}
</style>
