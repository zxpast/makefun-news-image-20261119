// news-image-20261119: a newspaper front page summing up Thursday 19 November 2026.
// Drawn entirely in code (Node 22, stdlib only): my own 5x7 bitmap font, geometric
// pictograms, and a hand-rolled PNG encoder. No network, no copied image,
// fully deterministic: two runs write byte-identical output.
// Stories (all verified from live news sources on 19 Nov 2026, as reported so far):
//   Trump, Xi and Putin meet in Shenzhen (APEC trilateral); Anthropic debuts on
//   Nasdaq after a record $81.3bn IPO; GTA VI rolls out worldwide; Cyclone Akvan
//   nears India with 50,000 evacuated; Australia jobless rate jumps to 4.9%;
//   Pew projects Islam to be the world's largest faith by 2035.

import { mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { deflateSync } from 'node:zlib';

// ------------------------------------------------------------ canvas ------
const W = 1024;
const H = 1024;
const canvas = Buffer.alloc(W * H * 3);

type RGB = [number, number, number];
const PAPER: RGB = [250, 246, 236];   // warm newsprint
const PANEL: RGB = [255, 253, 247];   // panel paper
const INK: RGB = [24, 24, 28];
const CRIMSON: RGB = [178, 34, 34];
const TEAL: RGB = [12, 74, 82];
const GOLD: RGB = [198, 141, 24];
const NAVY: RGB = [28, 58, 104];
const SLATE: RGB = [70, 80, 96];
const SKY: RGB = [168, 200, 222];
const DUSK: RGB = [52, 44, 92];
const GREEN: RGB = [44, 122, 60];
const WHITE: RGB = [255, 255, 255];
const SEA: RGB = [56, 108, 158];
const RUST: RGB = [176, 84, 20];

function setPx(x: number, y: number, c: RGB): void {
  if (x < 0 || y < 0 || x >= W || y >= H) return;
  const i = (y * W + x) * 3;
  canvas[i] = c[0];
  canvas[i + 1] = c[1];
  canvas[i + 2] = c[2];
}

function fillRect(x: number, y: number, w: number, h: number, c: RGB): void {
  for (let yy = y; yy < y + h; yy++) {
    for (let xx = x; xx < x + w; xx++) setPx(xx, yy, c);
  }
}

function outlineRect(x: number, y: number, w: number, h: number, c: RGB, t: number): void {
  fillRect(x, y, w, t, c);
  fillRect(x, y + h - t, w, t, c);
  fillRect(x, y, t, h, c);
  fillRect(x + w - t, y, t, h, c);
}

function hRule(x0: number, x1: number, y: number, c: RGB, t = 1): void {
  for (let yy = y; yy < y + t; yy++) {
    for (let xx = x0; xx <= x1; xx++) setPx(xx, yy, c);
  }
}

function vRule(x: number, y0: number, y1: number, c: RGB, t = 1): void {
  for (let xx = x; xx < x + t; xx++) {
    for (let yy = y0; yy <= y1; yy++) setPx(xx, yy, c);
  }
}

// Bresenham line.
function drawLine(x0: number, y0: number, x1: number, y1: number, c: RGB): void {
  const dx = Math.abs(x1 - x0);
  const dy = -Math.abs(y1 - y0);
  const sx = x0 < x1 ? 1 : -1;
  const sy = y0 < y1 ? 1 : -1;
  let err = dx + dy;
  let x = x0;
  let y = y0;
  for (;;) {
    setPx(x, y, c);
    if (x === x1 && y === y1) break;
    const e2 = 2 * err;
    if (e2 >= dy) { err += dy; x += sx; }
    if (e2 <= dx) { err += dx; y += sy; }
  }
}

function fillDisc(cx: number, cy: number, r: number, c: RGB): void {
  for (let yy = cy - r; yy <= cy + r; yy++) {
    const dx = Math.floor(Math.sqrt(r * r - (yy - cy) * (yy - cy)));
    for (let xx = cx - dx; xx <= cx + dx; xx++) setPx(xx, yy, c);
  }
}

function drawRing(cx: number, cy: number, r: number, c: RGB): void {
  for (let a = 0; a < 360; a++) {
    const rad = (a * Math.PI) / 180;
    setPx(Math.round(cx + r * Math.cos(rad)), Math.round(cy + r * Math.sin(rad)), c);
  }
}

function fillTri(x0: number, y0: number, x1: number, y1: number, x2: number, y2: number, c: RGB): void {
  const lo = Math.min(y0, y1, y2);
  const hi = Math.max(y0, y1, y2);
  const edges: [number, number, number, number][] = [
    [x0, y0, x1, y1],
    [x1, y1, x2, y2],
    [x2, y2, x0, y0],
  ];
  for (let y = lo; y <= hi; y++) {
    const xs: number[] = [];
    for (const [ax, ay, bx, by] of edges) {
      if ((ay <= y && by > y) || (by <= y && ay > y)) {
        xs.push(ax + ((y - ay) / (by - ay)) * (bx - ax));
      }
    }
    if (xs.length >= 2) {
      const a = Math.min(...xs);
      const b = Math.max(...xs);
      for (let x = Math.ceil(a); x <= Math.floor(b); x++) setPx(x, y, c);
    }
  }
}

// ------------------------------------------------------- 5x7 bitmap font --
// My own glyph set: each letter is 7 rows of 5 cells, '#' = ink.
const GLYPHS: Record<string, string[]> = {
  A: ['.###.', '#...#', '#...#', '#####', '#...#', '#...#', '#...#'],
  B: ['####.', '#...#', '#...#', '####.', '#...#', '#...#', '####.'],
  C: ['.####', '#....', '#....', '#....', '#....', '#....', '.####'],
  D: ['####.', '#...#', '#...#', '#...#', '#...#', '#...#', '####.'],
  E: ['#####', '#....', '#....', '####.', '#....', '#....', '#####'],
  F: ['#####', '#....', '#....', '####.', '#....', '#....', '#....'],
  G: ['.####', '#....', '#....', '#.###', '#...#', '#...#', '.###.'],
  H: ['#...#', '#...#', '#...#', '#####', '#...#', '#...#', '#...#'],
  I: ['.###.', '..#..', '..#..', '..#..', '..#..', '..#..', '.###.'],
  J: ['..###', '...#.', '...#.', '...#.', '...#.', '#..#.', '.##..'],
  K: ['#...#', '#..#.', '#.#..', '##...', '#.#..', '#..#.', '#...#'],
  L: ['#....', '#....', '#....', '#....', '#....', '#....', '#####'],
  M: ['#...#', '##.##', '#.#.#', '#.#.#', '#...#', '#...#', '#...#'],
  N: ['#...#', '##..#', '#.#.#', '#..##', '#...#', '#...#', '#...#'],
  O: ['.###.', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'],
  P: ['####.', '#...#', '#...#', '####.', '#....', '#....', '#....'],
  Q: ['.###.', '#...#', '#...#', '#...#', '#.#.#', '#..#.', '.##.#'],
  R: ['####.', '#...#', '#...#', '####.', '#.#..', '#..#.', '#...#'],
  S: ['.####', '#....', '#....', '.###.', '....#', '....#', '####.'],
  T: ['#####', '..#..', '..#..', '..#..', '..#..', '..#..', '..#..'],
  U: ['#...#', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'],
  V: ['#...#', '#...#', '#...#', '#...#', '#...#', '.#.#.', '..#..'],
  W: ['#...#', '#...#', '#...#', '#.#.#', '#.#.#', '##.##', '#...#'],
  X: ['#...#', '#...#', '.#.#.', '..#..', '.#.#.', '#...#', '#...#'],
  Y: ['#...#', '#...#', '.#.#.', '..#..', '..#..', '..#..', '..#..'],
  Z: ['#####', '....#', '...#.', '..#..', '.#...', '#....', '#####'],
  '0': ['.###.', '#...#', '#..##', '#.#.#', '##..#', '#...#', '.###.'],
  '1': ['..#..', '.##..', '..#..', '..#..', '..#..', '..#..', '.###.'],
  '2': ['.###.', '#...#', '....#', '...#.', '..#..', '.#...', '#####'],
  '3': ['####.', '....#', '....#', '.###.', '....#', '....#', '####.'],
  '4': ['...#.', '..##.', '.#.#.', '#..#.', '#####', '...#.', '...#.'],
  '5': ['#####', '#....', '####.', '....#', '....#', '#...#', '.###.'],
  '6': ['.###.', '#....', '#....', '####.', '#...#', '#...#', '.###.'],
  '7': ['#####', '....#', '...#.', '...#.', '..#..', '..#..', '..#..'],
  '8': ['.###.', '#...#', '#...#', '.###.', '#...#', '#...#', '.###.'],
  '9': ['.###.', '#...#', '#...#', '.####', '....#', '....#', '.###.'],
  ' ': ['.....', '.....', '.....', '.....', '.....', '.....', '.....'],
  '.': ['.....', '.....', '.....', '.....', '.....', '.##..', '.##..'],
  ',': ['.....', '.....', '.....', '.....', '.##..', '.##..', '.#...'],
  ':': ['.....', '.##..', '.##..', '.....', '.##..', '.##..', '.....'],
  '-': ['.....', '.....', '.....', '#####', '.....', '.....', '.....'],
  '!': ['..#..', '..#..', '..#..', '..#..', '..#..', '.....', '..#..'],
  '?': ['.###.', '#...#', '....#', '...#.', '..#..', '.....', '..#..'],
  '/': ['....#', '...#.', '...#.', '..#..', '.#...', '.#...', '#....'],
  '(': ['...##', '..#..', '.#...', '.#...', '.#...', '..#..', '...##'],
  ')': ['##...', '..#..', '...#.', '...#.', '...#.', '..#..', '##...'],
  '&': ['.##..', '#..#.', '#.#..', '.#...', '#.#.#', '#..#.', '.##.#'],
  '%': ['##..#', '##.#.', '...#.', '..#..', '.#...', '#.##.', '#..##'],
  '+': ['.....', '..#..', '..#..', '#####', '..#..', '..#..', '.....'],
  '=': ['.....', '.....', '#####', '.....', '#####', '.....', '.....'],
  "'": ['..#..', '..#..', '.....', '.....', '.....', '.....', '.....'],
  $: ['..#..', '.####', '#.#..', '.###.', '..#.#', '####.', '..#..'],
};

function textW(s: string, scale: number): number {
  return s.length * 6 * scale - scale;
}

function drawText(s: string, x: number, y: number, scale: number, c: RGB): void {
  let cx = x;
  for (const ch of s) {
    const g = GLYPHS[ch] ?? GLYPHS[' '];
    for (let r = 0; r < 7; r++) {
      for (let col = 0; col < 5; col++) {
        if (g[r][col] === '#') fillRect(cx + col * scale, y + r * scale, scale, scale, c);
      }
    }
    cx += 6 * scale;
  }
}

function drawTextMid(s: string, cx: number, y: number, scale: number, c: RGB): void {
  drawText(s, cx - Math.floor(textW(s, scale) / 2), y, scale, c);
}

// Greedy word wrap: lines no wider than maxW pixels.
function wrapText(s: string, maxW: number, scale: number): string[] {
  const out: string[] = [];
  let cur = '';
  for (const w of s.split(' ')) {
    const test = cur === '' ? w : cur + ' ' + w;
    if (textW(test, scale) <= maxW || cur === '') cur = test;
    else { out.push(cur); cur = w; }
  }
  if (cur !== '') out.push(cur);
  return out;
}

// ------------------------------------------------------------ PNG encoder --
// CRC-32 (IEEE) table, built once at load.
const CRC_TAB: number[] = (() => {
  const t: number[] = [];
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    t[n] = c >>> 0;
  }
  return t;
})();

function crc32Bytes(b: Buffer): number {
  let c = 0xffffffff;
  for (const byte of b) c = CRC_TAB[(c ^ byte) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}

function pngChunk(type: string, data: Buffer): Buffer {
  const out = Buffer.alloc(12 + data.length);
  out.writeUInt32BE(data.length, 0);
  out.write(type, 4, 'ascii');
  data.copy(out, 8);
  const crcIn = Buffer.concat([Buffer.from(type, 'ascii'), data]);
  out.writeUInt32BE(crc32Bytes(crcIn), 8 + data.length);
  return out;
}

function encodePng(): Buffer {
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(W, 0);
  ihdr.writeUInt32BE(H, 4);
  ihdr[8] = 8; // bit depth
  ihdr[9] = 2; // colour type 2 = RGB
  ihdr[10] = 0;
  ihdr[11] = 0;
  ihdr[12] = 0;
  const raw = Buffer.alloc(H * (1 + W * 3));
  for (let y = 0; y < H; y++) {
    raw[y * (1 + W * 3)] = 0; // filter: none
    canvas.copy(raw, y * (1 + W * 3) + 1, y * W * 3, (y + 1) * W * 3);
  }
  const idat = deflateSync(raw, { level: 9 });
  return Buffer.concat([
    Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]),
    pngChunk('IHDR', ihdr),
    pngChunk('IDAT', idat),
    pngChunk('IEND', Buffer.alloc(0)),
  ]);
}

// ------------------------------------------------------------ pictograms ----
// All scenes are simple original geometry: no faces, no copied artwork.

// Three flags over a Shenzhen skyline: the trilateral summit.
function drawSummit(x: number, y: number, w: number, h: number): void {
  fillRect(x, y, w, h, SKY);
  fillDisc(x + w - 46, y + 30, 20, GOLD);
  const base = y + h;
  // towers, left to right, with lit windows
  const towers: [number, number, number][] = [
    [0.03, 0.50, 0.12], [0.17, 0.68, 0.12], [0.31, 0.42, 0.11],
    [0.44, 0.80, 0.13], [0.59, 0.55, 0.12], [0.73, 0.66, 0.11],
    [0.86, 0.46, 0.11],
  ];
  for (const [fx, fh, fw] of towers) {
    const tx = x + Math.floor(fx * w);
    const tw = Math.floor(fw * w);
    const th = Math.floor(fh * h);
    fillRect(tx, base - th, tw, th, NAVY);
    for (let wy = base - th + 10; wy < base - 10; wy += 16) {
      for (let wx = tx + 6; wx < tx + tw - 6; wx += 13) {
        if ((wx * 7 + wy * 3) % 5 < 2) fillRect(wx, wy, 5, 7, [255, 214, 130]);
      }
    }
  }
  // three flags on poles above the tallest tower
  const poleX = x + Math.floor(0.44 * w) + 8;
  const poleTop = base - Math.floor(0.80 * h);
  const flagCols: RGB[] = [CRIMSON, WHITE, NAVY];
  for (let i = 0; i < 3; i++) {
    const fx = poleX + i * 18;
    vRule(fx, poleTop - 26, poleTop, INK, 2);
    fillTri(fx + 2, poleTop - 26, fx + 2, poleTop - 12, fx + 17, poleTop - 19, flagCols[i]);
    outlineRect(fx + 2, poleTop - 26, 15, 14, INK, 1);
  }
  // three stars for the three leaders
  for (let i = 0; i < 3; i++) {
    const sx = x + 24 + i * 22;
    const sy = y + 22;
    fillDisc(sx, sy, 4, CRIMSON);
    drawRing(sx, sy, 7, WHITE);
  }
}

// Rising bars and an arrow: the record IPO debut.
function drawChart(x: number, y: number, w: number, h: number): void {
  fillRect(x, y, w, h, [232, 240, 236]);
  const base = y + h - 18;
  hRule(x + 10, x + w - 10, base, INK, 2);
  vRule(x + 14, y + 12, base, INK, 2);
  const bars: [number, number][] = [
    [0.12, 0.22], [0.28, 0.34], [0.44, 0.30], [0.60, 0.52], [0.76, 0.72],
  ];
  for (const [fx, fh] of bars) {
    const bx = x + Math.floor(fx * w);
    const bh = Math.floor(fh * (h - 40));
    fillRect(bx, base - bh, 26, bh, TEAL);
    outlineRect(bx, base - bh, 26, bh, INK, 1);
  }
  // last bar in gold: the record day
  const lbx = x + Math.floor(0.76 * w);
  const lbh = Math.floor(0.72 * (h - 40));
  fillRect(lbx, base - lbh, 26, lbh, GOLD);
  outlineRect(lbx, base - lbh, 26, lbh, INK, 1);
  // trend arrow over the bars
  drawLine(x + 30, base - 20, x + w - 24, y + 16, CRIMSON);
  drawLine(x + w - 24, y + 16, x + w - 44, y + 18, CRIMSON);
  drawLine(x + w - 24, y + 16, x + w - 26, y + 36, CRIMSON);
  drawText('$', x + 16, y + 10, 3, CRIMSON);
}

// A game controller over a dusk city: GTA VI rolls out.
function drawGame(x: number, y: number, w: number, h: number): void {
  fillRect(x, y, w, h, DUSK);
  // stars
  const stars: [number, number][] = [
    [0.08, 0.14], [0.24, 0.08], [0.42, 0.18], [0.62, 0.10], [0.80, 0.16],
    [0.92, 0.08], [0.16, 0.30], [0.70, 0.28],
  ];
  for (const [fx, fy] of stars) setPx(x + Math.floor(fx * w), y + Math.floor(fy * h), WHITE);
  // low city silhouette
  const base = y + h;
  const blocks: [number, number, number][] = [
    [0.02, 0.24, 0.14], [0.18, 0.32, 0.12], [0.32, 0.20, 0.13],
    [0.47, 0.30, 0.12], [0.61, 0.24, 0.13], [0.76, 0.34, 0.12],
  ];
  for (const [fx, fh, fw] of blocks) {
    const bx = x + Math.floor(fx * w);
    const bw = Math.floor(fw * w);
    const bh = Math.floor(fh * h);
    fillRect(bx, base - bh, bw, bh, [24, 24, 44]);
    for (let wy = base - bh + 8; wy < base - 6; wy += 14) {
      for (let wx = bx + 5; wx < bx + bw - 5; wx += 12) {
        if ((wx + wy) % 4 === 0) fillRect(wx, wy, 4, 5, GOLD);
      }
    }
  }
  // controller, centre foreground, clear of the skyline
  const cx = x + Math.floor(w / 2);
  const cy = y + Math.floor(h * 0.44);
  fillRect(cx - 62, cy - 18, 124, 40, [240, 240, 240]);
  outlineRect(cx - 62, cy - 18, 124, 40, INK, 2);
  fillDisc(cx - 62, cy + 22, 12, [240, 240, 240]);
  fillDisc(cx + 62, cy + 22, 12, [240, 240, 240]);
  // d-pad (left)
  fillRect(cx - 48, cy - 8, 8, 24, INK);
  fillRect(cx - 56, cy, 24, 8, INK);
  // buttons (right)
  const btn: RGB[] = [CRIMSON, GOLD, GREEN, NAVY];
  const offs: [number, number][] = [[0, -10], [10, 0], [0, 10], [-10, 0]];
  for (let i = 0; i < 4; i++) {
    fillDisc(cx + 44 + offs[i][0], cy + offs[i][1], 6, btn[i]);
  }
  // sticks
  fillDisc(cx - 14, cy + 8, 7, SLATE);
  fillDisc(cx + 12, cy - 8, 7, SLATE);
}

// Spiral storm over the coast: Cyclone Akvan.
function drawStorm(x: number, y: number, w: number, h: number): void {
  fillRect(x, y, w, h, [178, 206, 224]);
  const cx = x + Math.floor(w * 0.5);
  const cy = y + Math.floor(h * 0.42);
  for (let r = 10; r <= 58; r += 9) {
    for (let a = 0; a < 300; a += 3) {
      const rad = ((a + r * 5) * Math.PI) / 180;
      setPx(Math.round(cx + r * Math.cos(rad)), Math.round(cy + r * 0.7 * Math.sin(rad)), WHITE);
      setPx(Math.round(cx + (r + 1) * Math.cos(rad)), Math.round(cy + (r + 1) * 0.7 * Math.sin(rad)), WHITE);
    }
  }
  fillDisc(cx, cy, 7, [110, 150, 185]);
  // rain streaks, top and sides
  for (let i = 0; i < 7; i++) {
    const rx = x + 14 + i * 20;
    drawLine(rx, y + 10, rx - 7, y + 30, [90, 130, 160]);
    drawLine(rx, y + h - 30, rx - 7, y + h - 10, [90, 130, 160]);
  }
  // coastline strip
  fillRect(x, y + h - 16, w, 16, [108, 138, 88]);
  fillTri(x + Math.floor(w * 0.18), y + h - 16, x + Math.floor(w * 0.18), y + h - 38, x + Math.floor(w * 0.32), y + h - 16, [88, 118, 78]);
  fillTri(x + Math.floor(w * 0.60), y + h - 16, x + Math.floor(w * 0.60), y + h - 30, x + Math.floor(w * 0.72), y + h - 16, [88, 118, 78]);
}

// Falling bars with a red down arrow: Australia's jobs slide.
function drawJobs(x: number, y: number, w: number, h: number): void {
  fillRect(x, y, w, h, [236, 232, 226]);
  const base = y + h - 16;
  hRule(x + 12, x + w - 12, base, INK, 2);
  const heights = [0.78, 0.70, 0.62, 0.50, 0.38, 0.26];
  for (let i = 0; i < 6; i++) {
    const bx = x + 22 + i * Math.floor((w - 60) / 6);
    const bh = Math.floor(heights[i] * (h - 44));
    const col: RGB = i === 5 ? CRIMSON : SLATE;
    fillRect(bx, base - bh, 34, bh, col);
    outlineRect(bx, base - bh, 34, bh, INK, 1);
  }
  // down arrow over the bars
  const ax = x + w - 70;
  drawLine(ax, y + 12, ax, y + 44, CRIMSON);
  fillTri(ax - 10, y + 44, ax + 10, y + 44, ax, y + 62, CRIMSON);
  drawText('4.9%', x + 16, y + 10, 3, CRIMSON);
}

// A globe with a rising arrow: the Pew projection to 2035.
function drawGlobe(x: number, y: number, w: number, h: number): void {
  fillRect(x, y, w, h, [214, 230, 238]);
  const cx = x + Math.floor(w * 0.32);
  const cy = y + Math.floor(h / 2);
  const r = Math.floor(h * 0.38);
  fillDisc(cx, cy, r, SEA);
  // land blobs
  fillDisc(cx - 10, cy - 8, 10, GREEN);
  fillDisc(cx + 12, cy + 10, 8, GREEN);
  fillDisc(cx + 6, cy - 14, 6, GREEN);
  // meridians
  drawRing(cx, cy, r, WHITE);
  for (let k = -2; k <= 2; k++) {
    const dx = Math.round((k * r) / 3);
    for (let a = 0; a < 360; a += 4) {
      const rad = (a * Math.PI) / 180;
      const yy = Math.round(cy + r * Math.sin(rad));
      const xx = Math.round(cx + dx * Math.cos(rad) * 0.9);
      setPx(xx, yy, WHITE);
    }
  }
  hRule(cx - r, cx + r, cy, WHITE, 1);
  // rising bars to the right, 2035 above them
  const bx0 = x + Math.floor(w * 0.58);
  const bBase = y + h - 18;
  const bh2 = [14, 22, 32];
  for (let i = 0; i < 3; i++) {
    fillRect(bx0 + i * 26, bBase - bh2[i], 18, bh2[i], TEAL);
    outlineRect(bx0 + i * 26, bBase - bh2[i], 18, bh2[i], INK, 1);
  }
  drawText('2035', x + w - 92, y + 8, 3, INK);
}

// --------------------------------------------------------------- layout ----
// One story panel: kicker, picture, headline lines, wrapped sub-lines.
function storyPanel(
  x: number, y: number, w: number, h: number,
  kicker: string, kc: RGB, pic: (x: number, y: number, w: number, h: number) => void,
  picH: number, head: string[], headScale: number, sub: string,
): void {
  fillRect(x, y, w, h, PANEL);
  outlineRect(x, y, w, h, INK, 2);
  drawText(kicker, x + 14, y + 12, 2, kc);
  hRule(x + 14, x + w - 14, y + 32, kc, 2);
  pic(x + 14, y + 40, w - 28, picH);
  outlineRect(x + 14, y + 40, w - 28, picH, INK, 1);
  let yy = y + 40 + picH + 12;
  for (const ln of head) {
    drawText(ln, x + 14, yy, headScale, INK);
    yy += 7 * headScale + 6;
  }
  yy += 2;
  for (const ln of wrapText(sub, w - 28, 2)) {
    drawText(ln, x + 14, yy, 2, SLATE);
    yy += 18;
  }
}

function headlineLines(lines: string[], x: number, y: number, scale: number): number {
  let yy = y;
  for (const ln of lines) {
    drawText(ln, x, yy, scale, INK);
    yy += 7 * scale + 6;
  }
  return yy;
}

function buildPage(): void {
  fillRect(0, 0, W, H, PAPER);
  outlineRect(8, 8, W - 16, H - 16, INK, 3);
  outlineRect(14, 14, W - 28, H - 28, INK, 1);

  // Masthead
  drawTextMid('THE WORLD TODAY', W / 2, 30, 6, TEAL);
  hRule(20, W - 20, 78, INK, 2);
  fillRect(20, 84, W - 40, 38, CRIMSON);
  drawTextMid('THURSDAY 19 NOVEMBER 2026', W / 2, 90, 4, WHITE);

  // ---- Lead: the Shenzhen trilateral ----
  const lx = 20;
  const ly = 134;
  const lw = W - 40;
  const lh = 318;
  fillRect(lx, ly, lw, lh, PANEL);
  outlineRect(lx, ly, lw, lh, INK, 2);
  drawSummit(lx + 16, ly + 16, 360, lh - 32);
  outlineRect(lx + 16, ly + 16, 360, lh - 32, INK, 2);
  const tx = lx + 396;
  drawText('ASIA - DIPLOMACY', tx, ly + 22, 2, CRIMSON);
  hRule(tx, lx + lw - 20, ly + 42, CRIMSON, 2);
  let yy = headlineLines(['THREE LEADERS', 'MEET IN SHENZHEN'], tx, ly + 56, 5);
  yy += 6;
  for (const ln of wrapText('FIRST THREE-WAY TALKS TODAY AT APEC; NUCLEAR ARMS, TRADE AND UKRAINE ON THE AGENDA', 560, 2)) {
    drawText(ln, tx, yy, 2, SLATE);
    yy += 20;
  }
  yy += 12;
  drawText('XI HOSTS TRUMP AND PUTIN', tx, yy, 2, INK);
  drawText('IN CHINA TECH CAPITAL', tx, yy + 20, 2, INK);

  // ---- Row 2: three panels ----
  const r2y = 468;
  const r2h = 254;
  const pw = 312;
  const gap = 18;
  const r2x = [20, 20 + pw + gap, 20 + 2 * (pw + gap)];

  storyPanel(r2x[0], r2y, pw, r2h, 'TECH - MARKETS', TEAL, drawChart, 92,
    ['ANTHROPIC', 'ON NASDAQ'], 3,
    'RECORD $81.3BN IPO AT $83 A SHARE; TRADING STARTS TODAY');
  storyPanel(r2x[1], r2y, pw, r2h, 'CULTURE - GAMES', RUST, drawGame, 92,
    ['GTA VI ROLLS', 'OUT WORLDWIDE'], 3,
    '13-YEAR WAIT ENDS AS GAME UNLOCKS AT MIDNIGHT, NZ FIRST');
  storyPanel(r2x[2], r2y, pw, r2h, 'WEATHER', NAVY, drawStorm, 92,
    ['AKVAN NEARS', 'INDIA COAST'], 3,
    '50,000 EVACUATED IN ODISHA; LANDFALL DUE FRIDAY');

  // ---- Row 3: two wide panels ----
  const r3y = 738;
  const r3h = 240;
  const w3 = 482;
  const r3x = [20, 20 + w3 + 18];

  storyPanel(r3x[0], r3y, w3, r3h, 'ECONOMY', CRIMSON, drawJobs, 76,
    ['JOBLESS RATE', 'HITS 4.9 PCT'], 4,
    'AUSTRALIA SHEDS 43,500 JOBS IN OCTOBER; HIGHEST SINCE 2021');
  storyPanel(r3x[1], r3y, w3, r3h, 'SOCIETY', GREEN, drawGlobe, 76,
    ['ISLAM TO BE', 'LARGEST FAITH'], 4,
    'PEW PROJECTS MUSLIMS TO OUTNUMBER CHRISTIANS BY 2035');

  // Footer: honest scope note — the day is still young at build time.
  drawTextMid('AS REPORTED SO FAR TODAY - 19 NOV 2026', W / 2, 992, 2, INK);
}

// ----------------------------------------------------------------- main ----
function main(): void {
  buildPage();
  const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
  mkdirSync(outDir, { recursive: true });
  writeFileSync(join(outDir, 'entry.png'), encodePng());
}

main();
