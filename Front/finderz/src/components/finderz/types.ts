export interface Friend {
  id: string;
  name: string;
  x: number;
  y: number;
  status: 'online' | 'offline';
  faro: boolean;
  battery: number;
  group?: string;
}

export interface RouteTarget {
  wx: number;
  wz: number;
  label: string;
  color: string;
  type: 'friend' | 'poi' | 'exit' | 'panic' | 'promo';
}

export interface Promotion {
  id: string;
  title: string;
  description: string;
  discount: string;
  stallName: string;
  stallId: string;
  wx: number;
  wz: number;
  expiresIn: number;
  color: string;
  icon: string;
  category: 'drink' | 'food' | 'merch' | 'experience';
  used: boolean;
  isNew?: boolean;
}

export interface POI {
  id: string;
  name: string;
  type: 'stage' | 'food' | 'bar' | 'restroom' | 'info' | 'medical' | 'exit' | 'vip';
  wx: number;
  wz: number;
  icon: string;
}

export const friendColors: Record<string, { bg: string; glow: string }> = {
  '1': { bg: '#ff3366', glow: 'rgba(255,51,102,0.8)' },
  '2': { bg: '#00d9ff', glow: 'rgba(0,217,255,0.8)' },
  '3': { bg: '#ffd700', glow: 'rgba(255,215,0,0.8)' },
  '4': { bg: '#888888', glow: 'rgba(136,136,136,0.5)' },
  '5': { bg: '#00ff88', glow: 'rgba(0,255,136,0.8)' },
  '6': { bg: '#fb7185', glow: 'rgba(251,113,133,0.8)' },
  '7': { bg: '#38bdf8', glow: 'rgba(56,189,248,0.8)' },
  '8': { bg: '#34d399', glow: 'rgba(52,211,153,0.8)' },
};

export const festivalPois: POI[] = [
  { id: 'mainStage', name: 'Main Stage', type: 'stage', wx: 0, wz: -12, icon: '🎤' },
  { id: 'stage2', name: 'Stage 2', type: 'stage', wx: 11.5, wz: -7, icon: '🎸' },
  { id: 'techDome', name: 'Techno Dome', type: 'stage', wx: -11.5, wz: -7, icon: '🎧' },
  { id: 'vip', name: 'VIP Zone', type: 'vip', wx: 7, wz: -3, icon: '⭐' },
  { id: 'foodCourt', name: 'Food Court', type: 'food', wx: 9.5, wz: 9.5, icon: '🍔' },
  { id: 'beerGarden', name: 'Beer Garden', type: 'bar', wx: -5.5, wz: 2, icon: '🍺' },
  { id: 'camping', name: 'Camping', type: 'food', wx: -9.5, wz: 9.5, icon: '⛺' },
  { id: 'medical', name: 'Medico', type: 'medical', wx: -3.5, wz: 5.8, icon: '🏥' },
  { id: 'info', name: 'Info / Merch', type: 'info', wx: 3.5, wz: 4, icon: 'ℹ️' },
  { id: 'restroomW', name: 'Banos Oeste', type: 'restroom', wx: -13.5, wz: 2, icon: '🚻' },
  { id: 'restroomE', name: 'Banos Este', type: 'restroom', wx: 13.5, wz: 2, icon: '🚻' },
  { id: 'exitN', name: 'Salida Norte', type: 'exit', wx: 0, wz: -16, icon: '🚪' },
  { id: 'exitS', name: 'Salida Sur', type: 'exit', wx: 0, wz: 16, icon: '🚪' },
];

export const initialFriends: Friend[] = [
  { id: '1', name: 'Ana', x: 62, y: 38, status: 'online', faro: true, battery: 84, group: 'crew' },
  { id: '2', name: 'Carlos', x: 30, y: 55, status: 'online', faro: true, battery: 61, group: 'crew' },
  { id: '3', name: 'Maria', x: 78, y: 62, status: 'online', faro: false, battery: 23, group: 'crew' },
  { id: '4', name: 'Juan', x: 22, y: 42, status: 'offline', faro: false, battery: 0, group: 'col' },
  { id: '5', name: 'Sofia', x: 52, y: 72, status: 'online', faro: false, battery: 55, group: 'col' },
];

export const initialPromotions: Promotion[] = [
  {
    id: 'p1',
    title: '2x1 en Corona',
    description: 'Dos cervezas al precio de una en barra principal.',
    discount: '2x1',
    stallName: 'Beer Garden',
    stallId: 'beerGarden',
    wx: -5.5,
    wz: 2,
    expiresIn: 18,
    color: '#f59e0b',
    icon: '🍺',
    category: 'drink',
    used: false,
  },
  {
    id: 'p2',
    title: 'Combo Burger + Papas',
    description: 'Hamburguesa completa con papas por precio especial.',
    discount: '-30%',
    stallName: 'Food Court',
    stallId: 'foodCourt',
    wx: 9.5,
    wz: 9.5,
    expiresIn: 35,
    color: '#ef4444',
    icon: '🍔',
    category: 'food',
    used: false,
  },
  {
    id: 'p3',
    title: 'Merch Oficial Exclusivo',
    description: 'Remeras y gorras del festival con 25% off.',
    discount: '-25%',
    stallName: 'Info / Merch',
    stallId: 'info',
    wx: 3.5,
    wz: 4,
    expiresIn: 60,
    color: '#8b5cf6',
    icon: '👕',
    category: 'merch',
    used: false,
  },
  {
    id: 'p4',
    title: 'Shot de Tequila Gratis',
    description: 'Un shot gratis con cualquier compra en VIP Bar.',
    discount: 'FREE',
    stallName: 'VIP Zone',
    stallId: 'vip',
    wx: 7,
    wz: -3,
    expiresIn: 8,
    color: '#06b6d4',
    icon: '🥃',
    category: 'drink',
    used: false,
  },
];

export function percentToWorld(px: number, py: number): [number, number] {
  return [(px / 100) * 30 - 15, (py / 100) * 30 - 15];
}
