# Guia practica para trabajar con Three.js en Finderz

Esta guia esta pensada para el mapa de `src/components/finderz/FestivalMapIsometric.vue`, usando Vue 3, Ionic y Three.js.

## 1. Entender la estructura basica

Una escena Three.js suele tener estas piezas:

- `Scene`: el mundo donde viven los objetos.
- `Camera`: el punto de vista.
- `Renderer`: dibuja la escena en un `<canvas>`.
- `Geometry`: la forma de un objeto, por ejemplo caja, esfera o cilindro.
- `Material`: como se ve la superficie, color, brillo, transparencia.
- `Mesh`: una geometria + un material.
- `Lights`: luces que afectan materiales como `MeshLambertMaterial`.
- `Controls`: controles de camara, en Finderz usamos `OrbitControls`.

Ejemplo minimo:

```ts
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 100);
const renderer = new THREE.WebGLRenderer({ antialias: true });

const mesh = new THREE.Mesh(
  new THREE.BoxGeometry(1, 1, 1),
  new THREE.MeshLambertMaterial({ color: 0x7c3aed }),
);

scene.add(mesh);
renderer.render(scene, camera);
```

## 2. Montarlo bien en Vue

En Vue, Three.js se inicializa en `onMounted` porque necesita un nodo real del DOM.

```ts
const containerRef = ref<HTMLDivElement | null>(null);

onMounted(() => {
  const container = containerRef.value;
  if (!container) return;

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  container.appendChild(renderer.domElement);
});
```

Y se limpia en `onBeforeUnmount`:

```ts
onBeforeUnmount(() => {
  cancelAnimationFrame(frameId);
  controls.dispose();
  renderer.dispose();
});
```

Esto evita fugas de memoria cuando se cambia de vista o se remonta el componente.

## 3. Crear objetos con helpers

En Finderz usamos un helper `box(...)` para no repetir siempre `BoxGeometry`, material, posicion y sombras.

```ts
function box(x: number, y: number, z: number, w: number, h: number, d: number, color: number) {
  const mesh = new THREE.Mesh(
    new THREE.BoxGeometry(w, h, d),
    new THREE.MeshLambertMaterial({ color }),
  );
  mesh.position.set(x, y + h / 2, z);
  scene?.add(mesh);
  return mesh;
}
```

La regla importante: en Three.js el centro del objeto es su posicion. Por eso se usa `y + h / 2` para que la base quede apoyada en el piso.

## 4. Coordenadas del mapa

El mapa de Finderz usa un plano aproximado de `32 x 32` unidades:

- `x`: izquierda/derecha.
- `z`: fondo/frente.
- `y`: altura.

Ejemplos:

- Centro del usuario: `(0, 0, 0)`.
- Main Stage: `(0, 0, -12)`.
- Food Court: `(9.5, 0, 9.5)`.
- Techno Dome: `(-11.5, 0, -7)`.

Si algo atraviesa otra estructura, revisa primero su `x` y `z`.

## 5. Materiales utiles

Para este proyecto:

```ts
new THREE.MeshLambertMaterial({ color: 0x003060 });
```

Bueno para objetos afectados por luces.

```ts
new THREE.MeshBasicMaterial({ color: 0x00aaff });
```

No depende de luces. Bueno para glows, rutas, overlays y anillos.

```ts
new THREE.MeshLambertMaterial({
  color: 0x003060,
  emissive: 0x001533,
  emissiveIntensity: 0.5,
  transparent: true,
  opacity: 0.9,
});
```

Bueno para objetos con brillo propio y transparencia, como el domo.

## 6. Animar

La animacion vive dentro de un loop:

```ts
const animate = () => {
  frameId = requestAnimationFrame(animate);
  t += 0.016;

  mesh.rotation.y = t;
  renderer.render(scene, camera);
};
```

Para movimiento suave tipo flotacion:

```ts
mesh.position.y = baseY + Math.sin(t * speed) * amplitude;
```

Ejemplo:

```ts
domeRing.position.y = 2.28 + Math.sin(t * 1.4) * 0.08;
```

## 7. Interaccion con raycasting

Para detectar hover o click sobre objetos 3D usamos `Raycaster`.

La idea:

1. Convertir el mouse a coordenadas normalizadas.
2. Tirar un rayo desde la camara.
3. Ver que objetos toca.

```ts
pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

raycaster.setFromCamera(pointer, camera);
const hits = raycaster.intersectObjects(pickTargets, false);
```

En Finderz usamos hitboxes invisibles:

```ts
const hitbox = new THREE.Mesh(
  new THREE.BoxGeometry(w, h, d),
  new THREE.MeshBasicMaterial({
    transparent: true,
    opacity: 0,
    colorWrite: false,
  }),
);
hitbox.userData.poi = poi;
```

Esto permite mostrar labels sin obligar al usuario a tocar exactamente una forma complicada.

## 8. Resize responsive

Cuando cambia el tamano del contenedor, hay que actualizar renderer y camara.

```ts
const syncSize = () => {
  const w = container.clientWidth;
  const h = container.clientHeight;
  camera.left = -frustum * (w / h) / 2;
  camera.right = frustum * (w / h) / 2;
  camera.updateProjectionMatrix();
  renderer.setSize(w, h, false);
};

const ro = new ResizeObserver(syncSize);
ro.observe(container);
```

## 9. Limpieza de memoria

Cada geometria y material ocupa memoria en GPU. Cuando el componente se destruye, hay que liberar.

```ts
mesh.geometry.dispose();
material.dispose();
renderer.dispose();
controls.dispose();
```

En Finderz existe `track(...)`, que registra objetos para limpiarlos despues.

## 10. Flujo recomendado para editar el mapa

1. Ubica la zona en coordenadas `x/z`.
2. Crea la base con `box(...)`.
3. Agrega volumen principal.
4. Agrega detalles chicos despues.
5. Si debe ser clickeable, agrega `addPoiHitbox(...)`.
6. Si debe animarse, guarda la referencia en una constante.
7. Anima dentro de `animate()`.
8. Corre `npm run build`.

## 11. Consejos para no romper la escena

- Evita poner objetos nuevos en `(0, 0, 0)`, ahi esta el usuario.
- Si algo atraviesa otra estructura, mueve `x/z`, no solo escala.
- Si un aro se ve vertical, revisa `rotation.x`; para un aro plano sobre el suelo suele ser `Math.PI / 2`.
- Si un objeto no se ve, revisa material, luces, posicion `y` y si la camara lo esta mirando.
- Para mobile, evita geometria excesivamente compleja. Muchas esferas con segmentos altos bajan FPS.
- Corre build seguido: TypeScript ayuda a encontrar referencias rotas como objetos eliminados.

