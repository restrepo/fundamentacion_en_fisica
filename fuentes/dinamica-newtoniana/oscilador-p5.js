/**
 * Oscilador Armónico 1D — Integración Numérica (Euler-Cromer) en p5.js
 * F = -k * x, con k = 1 N/m, m = 1 kg, x0 = 1 m, p0 = 0 kg·m/s
 * Intervalo: 1 ciclo completo T = 2π√(m/k) ≈ 6.283 s
 */

// Parámetros físicos del sistema
const k = 1.0;          // Constante elástica (N/m)
const m = 1.0;          // Masa (kg)
const x0 = 1.0;         // Posición inicial (m)
const p0 = 0.0;         // Momento inicial (kg·m/s)
const omega = Math.sqrt(k / m);
const T_period = (2 * Math.PI) / omega; // ≈ 6.283185 s

// Controles de interfaz
let sliderDt;
let checkPosition, checkMomentum, checkExact, checkPoints;
let btnCapture, btnReset;
let presetButtons = [];
const presets = [1.0, 0.5, 0.25, 0.1, 0.05, 0.01];

// Dimensiones del lienzo y del área de trazado
const canvasW = 860;
const canvasH = 670;
const margin = { top: 112, right: 45, bottom: 50, left: 65 };
const plotW = canvasW - margin.left - margin.right; // 750 px
const plotH = 240; // Altura del gráfico

let cnv;

function setup() {
  cnv = createCanvas(canvasW, canvasH);

  // Posicionar controles relativos al canvas
  positionElements();
}

function positionElements() {
  // Limpiar si ya existían
  if (checkPosition) checkPosition.remove();
  if (checkMomentum) checkMomentum.remove();
  if (checkExact) checkExact.remove();
  if (checkPoints) checkPoints.remove();
  if (btnCapture) btnCapture.remove();
  if (btnReset) btnReset.remove();
  if (sliderDt) sliderDt.remove();
  presetButtons.forEach(b => b.remove());
  presetButtons = [];

  const originX = cnv ? cnv.position().x : 0;
  const originY = cnv ? cnv.position().y : 0;

  // -------------------------------------------------------------
  // FILA 1: CASILLAS DE SELECCIÓN Y BOTÓN CAPTURA (Y = 74)
  // -------------------------------------------------------------
  const rowControlsY = originY + 74;

  checkPosition = createCheckbox(' Posición x(t)', true);
  checkPosition.position(originX + margin.left, rowControlsY);
  styleCheckbox(checkPosition, '#1d4ed8', true);

  checkMomentum = createCheckbox(' Momento p(t)', false);
  checkMomentum.position(originX + margin.left + 140, rowControlsY);
  styleCheckbox(checkMomentum, '#047857', false);

  checkExact = createCheckbox(' Analítica cos(t)', false);
  checkExact.position(originX + margin.left + 280, rowControlsY);
  styleCheckbox(checkExact, '#b45309', false);

  // PUNTOS ACTIVOS POR DEFECTO
  checkPoints = createCheckbox(' Puntos', true);
  checkPoints.position(originX + margin.left + 435, rowControlsY);
  styleCheckbox(checkPoints, '#334155', true);

  // Botón de captura PNG
  btnCapture = createButton('📷 Captura PNG');
  btnCapture.position(originX + margin.left + plotW - 120, rowControlsY - 4);
  btnCapture.style('background-color', '#4f46e5');
  btnCapture.style('color', '#ffffff');
  btnCapture.style('border', 'none');
  btnCapture.style('padding', '5px 12px');
  btnCapture.style('border-radius', '6px');
  btnCapture.style('font-size', '12px');
  btnCapture.style('font-weight', 'bold');
  btnCapture.style('cursor', 'pointer');
  btnCapture.mousePressed(() => {
    saveCanvas('oscilador_euler_cromer_dt_' + nf(sliderDt.value(), 1, 2), 'png');
  });

  // -------------------------------------------------------------
  // BOTÓN RESTABLECER (Y = 432)
  // -------------------------------------------------------------
  btnReset = createButton('↺ Restablecer enunciado');
  btnReset.position(originX + margin.left + plotW - 165, originY + 428);
  btnReset.style('font-size', '11px');
  btnReset.style('padding', '4px 9px');
  btnReset.style('cursor', 'pointer');
  btnReset.style('border', '1px solid #cbd5e1');
  btnReset.style('border-radius', '6px');
  btnReset.style('background', '#f8fafc');
  btnReset.style('color', '#475569');
  btnReset.mousePressed(() => sliderDt.value(1.00));

  // -------------------------------------------------------------
  // DESLIZADOR (SLIDER) DE Δt (Y = 496)
  // -------------------------------------------------------------
  sliderDt = createSlider(0.01, 1.00, 1.00, 0.01);
  sliderDt.position(originX + margin.left, originY + 496);
  sliderDt.style('width', plotW + 'px');
  sliderDt.style('cursor', 'pointer');
  sliderDt.style('accent-color', '#0284c7');

  // -------------------------------------------------------------
  // BOTONES DE PREAJUSTE RÁPIDO (Y = 552)
  // -------------------------------------------------------------
  const presetY = originY + 550;
  const startX = originX + margin.left + 145;
  presets.forEach((val, idx) => {
    let label = nf(val, 1, 2) + ' s' + (val === 1.0 ? ' (Defecto)' : '');
    let btn = createButton(label);
    btn.position(startX + idx * 96, presetY);
    btn.style('font-size', '11px');
    btn.style('font-family', 'monospace');
    btn.style('cursor', 'pointer');
    btn.style('padding', '4px 8px');
    btn.style('border', '1px solid #cbd5e1');
    btn.style('background', '#ffffff');
    btn.style('border-radius', '5px');
    btn.mousePressed(() => sliderDt.value(val));
    presetButtons.push(btn);
  });
}

function styleCheckbox(elem, color, isBold) {
  elem.style('font-family', 'system-ui, -apple-system, sans-serif');
  elem.style('font-size', '12px');
  elem.style('color', color);
  elem.style('cursor', 'pointer');
  if (isBold) elem.style('font-weight', 'bold');
}

function windowResized() {
  // Mantener alineados los controles al redimensionar la ventana
  positionElements();
}

function draw() {
  background(241, 245, 249);

  // 1. Tarjeta unificada exterior
  fill(255);
  stroke(226, 232, 240);
  strokeWeight(1);
  rect(15, 12, width - 30, height - 24, 16);

  const dt = sliderDt ? sliderDt.value() : 1.00;

  // 2. Ejecutar algoritmo de integración Euler-Cromer
  const points = runEulerCromer(dt);

  // 3. Título principal (Y = 32)
  noStroke();
  fill(15, 23, 42);
  textSize(15);
  textStyle(BOLD);
  textAlign(LEFT, BASELINE);
  text('Evolución Temporal: Posición x(t) vs Tiempo t', margin.left, 36);

  fill(2, 132, 199);
  textSize(11);
  textStyle(NORMAL);
  text('[1 Ciclo Completo: T = 2π ≈ 6.283 s]', margin.left + 355, 36);

  // 4. Subtítulo con valores actuales (Y = 56)
  fill(100, 116, 139);
  textSize(11);
  text(`Paso de integración: Δt = ${nf(dt, 1, 2)} s  ·  Total de pasos: ${points.length - 1}  ·  Intervalo: t ∈ [0, 6.283 s]`, margin.left, 56);

  // (Las casillas de selección se encuentran en Y = 74)

  // 5. Dibujar cuadrícula y ejes del gráfico (Y = 112 a 352)
  drawGrid();

  // 6. Curva analítica exacta (si está activa)
  if (checkExact && checkExact.checked()) {
    drawExact();
  }

  // 7. Curvas numéricas Euler-Cromer y puntos
  drawCurves(points);

  // 8. Inspección interactiva con el mouse
  drawHover(points);

  // 9. Leyenda inferior del gráfico (Y = 388)
  drawLegend();

  // 10. Sección de control de Δt (Y = 415 en adelante)
  drawControlSection(dt);
}

// ============================================================
// INTEGRACIÓN NUMÉRICA: ALGORITMO DE EULER-CROMER
// ============================================================
function runEulerCromer(dt) {
  let pts = [];
  let t = 0.0;
  let x = x0;
  let p = p0;
  let step = 0;

  pts.push({
    step: 0,
    t: 0.0,
    x: x,
    p: p,
    xExact: Math.cos(0),
    E: 0.5 * (p * p / m) + 0.5 * k * x * x
  });

  while (t < T_period - 1e-9) {
    step++;
    const stepDt = Math.min(dt, T_period - t);

    // Fuerza restauradora: F = -k * x
    const F = -k * x;

    // 1. Momento actualizado con la fuerza actual
    p = p + F * stepDt;

    // 2. Velocidad: v = p / m
    const v = p / m;

    // 3. Posición actualizada con el NUEVO momento
    x = x + v * stepDt;

    t += stepDt;

    pts.push({
      step: step,
      t: t,
      x: x,
      p: p,
      xExact: Math.cos(omega * t),
      E: 0.5 * (p * p / m) + 0.5 * k * x * x
    });
  }

  return pts;
}

function toScreenX(t) {
  return margin.left + (t / T_period) * plotW;
}

function toScreenY(val) {
  const minY = -1.25;
  const maxY = 1.25;
  return margin.top + plotH - ((val - minY) / (maxY - minY)) * plotH;
}

function drawGrid() {
  // Fondo del área gráfica
  fill(250, 252, 255);
  stroke(226, 232, 240);
  rect(margin.left, margin.top, plotW, plotH, 8);

  // Líneas horizontales de nivel
  const yTicks = [-1.0, -0.5, 0.0, 0.5, 1.0];
  for (let val of yTicks) {
    const y = toScreenY(val);
    stroke(val === 0 ? 148 : 226, val === 0 ? 163 : 232, val === 0 ? 184 : 240);
    strokeWeight(val === 0 ? 1.5 : 1);
    line(margin.left, y, margin.left + plotW, y);

    noStroke();
    fill(100, 116, 139);
    textSize(10);
    textAlign(RIGHT, CENTER);
    text(val.toFixed(1), margin.left - 8, y);
  }

  // Líneas verticales de tiempo
  const xTicksCount = 7;
  for (let i = 0; i < xTicksCount; i++) {
    const tVal = (i / (xTicksCount - 1)) * T_period;
    const x = toScreenX(tVal);

    stroke(226, 232, 240);
    strokeWeight(1);
    line(x, margin.top, x, margin.top + plotH);

    noStroke();
    fill(100, 116, 139);
    textSize(10);
    textAlign(CENTER, TOP);
    text(nf(tVal, 1, 2) + ' s', x, margin.top + plotH + 6);
  }

  // Etiquetas de los ejes
  noStroke();
  fill(30, 41, 59);
  textSize(11);
  textStyle(BOLD);
  textAlign(CENTER, TOP);
  text('Tiempo t (segundos)', margin.left + plotW / 2, margin.top + plotH + 20);

  push();
  translate(20, margin.top + plotH / 2);
  rotate(-HALF_PI);
  textAlign(CENTER, CENTER);
  text('Posición x(t) [m]', 0, 0);
  pop();
}

function drawExact() {
  noFill();
  stroke(245, 158, 11);
  strokeWeight(2);
  beginShape();
  for (let t = 0; t <= T_period; t += 0.04) {
    vertex(toScreenX(t), toScreenY(Math.cos(t)));
  }
  endShape();
}

function drawCurves(points) {
  // 1. Curva de Momento p(t)
  if (checkMomentum && checkMomentum.checked()) {
    noFill();
    stroke(5, 150, 105);
    strokeWeight(2.5);
    beginShape();
    for (let pt of points) vertex(toScreenX(pt.t), toScreenY(pt.p));
    endShape();

    if (checkPoints && checkPoints.checked()) {
      fill(5, 150, 105);
      stroke(255);
      strokeWeight(1);
      for (let pt of points) circle(toScreenX(pt.t), toScreenY(pt.p), points.length > 50 ? 5 : 7);
    }
  }

  // 2. Curva de Posición x(t)
  if (checkPosition && checkPosition.checked()) {
    noFill();
    stroke(2, 132, 199);
    strokeWeight(3);
    beginShape();
    for (let pt of points) vertex(toScreenX(pt.t), toScreenY(pt.x));
    endShape();

    // PUNTOS DISCRETOS
    if (checkPoints && checkPoints.checked()) {
      fill(2, 132, 199);
      stroke(255);
      strokeWeight(1.2);
      for (let pt of points) circle(toScreenX(pt.t), toScreenY(pt.x), points.length > 50 ? 5 : 7.5);
    }
  }

  // Marcador inicial t = 0 (círculo rojo)
  stroke(220, 38, 38);
  strokeWeight(2);
  line(toScreenX(0), margin.top, toScreenX(0), margin.top + plotH);
  fill(220, 38, 38);
  noStroke();
  circle(toScreenX(0), toScreenY(x0), 8);
}

function drawLegend() {
  fill(248, 250, 252);
  stroke(226, 232, 240);
  rect(margin.left, margin.top + plotH + 36, plotW, 26, 6);

  noStroke();
  fill(2, 132, 199);
  rect(margin.left + 12, margin.top + plotH + 47, 14, 4, 2);

  fill(51, 65, 85);
  textSize(11);
  textAlign(LEFT, CENTER);
  text('x(t) (Euler-Cromer)', margin.left + 32, margin.top + plotH + 49);

  fill(100, 116, 139);
  textAlign(RIGHT, CENTER);
  text('ⓘ Pasa el cursor sobre el gráfico para inspeccionar valores numéricos', margin.left + plotW - 12, margin.top + plotH + 49);
}

function drawHover(points) {
  if (mouseX >= margin.left && mouseX <= margin.left + plotW &&
      mouseY >= margin.top && mouseY <= margin.top + plotH) {

    const targetT = ((mouseX - margin.left) / plotW) * T_period;
    let closest = points[0];
    let minD = Math.abs(points[0].t - targetT);

    for (let pt of points) {
      const d = Math.abs(pt.t - targetT);
      if (d < minD) {
        minD = d;
        closest = pt;
      }
    }

    const hx = toScreenX(closest.t);
    const hy = toScreenY(closest.x);

    // Línea guía vertical
    stroke(100, 116, 139);
    strokeWeight(1);
    line(hx, margin.top, hx, margin.top + plotH);

    fill(2, 132, 199);
    stroke(255);
    strokeWeight(2);
    circle(hx, hy, 10);

    // Tooltip
    const ttW = 165;
    const ttH = 75;
    const ttX = mouseX > width - 210 ? mouseX - ttW - 12 : mouseX + 12;
    const ttY = mouseY < 170 ? mouseY + 10 : mouseY - ttH - 10;

    fill(255, 245);
    stroke(203, 213, 225);
    strokeWeight(1);
    rect(ttX, ttY, ttW, ttH, 6);

    noStroke();
    fill(15, 23, 42);
    textSize(10);
    textAlign(LEFT, TOP);
    textStyle(BOLD);
    text(`Paso #${closest.step} (t = ${nf(closest.t, 1, 3)} s)`, ttX + 8, ttY + 6);

    textStyle(NORMAL);
    fill(2, 132, 199);
    text(`x(t) = ${nf(closest.x, 1, 4)} m`, ttX + 8, ttY + 22);

    fill(5, 150, 105);
    text(`p(t) = ${nf(closest.p, 1, 4)} kg·m/s`, ttX + 8, ttY + 36);

    fill(100, 116, 139);
    text(`Exacta = ${nf(closest.xExact, 1, 4)} m`, ttX + 8, ttY + 50);
    text(`E = ${nf(closest.E, 1, 4)} J`, ttX + 8, ttY + 62);
  }
}

function drawControlSection(dt) {
  // Línea divisoria
  stroke(226, 232, 240);
  strokeWeight(1);
  line(margin.left, 415, margin.left + plotW, 415);

  // Encabezado de la sección (Y = 432)
  noStroke();
  fill(15, 23, 42);
  textSize(13);
  textStyle(BOLD);
  textAlign(LEFT, CENTER);
  text('Control de Δt (Paso de Integración Numérica)', margin.left, 436);

  // Rótulo del deslizador y valor actual (Y = 472)
  fill(30, 41, 59);
  textSize(12);
  textStyle(BOLD);
  textAlign(LEFT, CENTER);
  text('Paso de tiempo (Δt):', margin.left, 472);

  // Distintivo azul para el valor numérico
  fill(219, 234, 254);
  stroke(191, 219, 254);
  rect(margin.left + 140, 462, 64, 20, 4);

  noStroke();
  fill(29, 78, 216);
  textAlign(CENTER, CENTER);
  text(nf(dt, 1, 2) + ' s', margin.left + 172, 472);

  // Rango disponible a la derecha
  fill(100, 116, 139);
  textSize(11);
  textStyle(NORMAL);
  textAlign(RIGHT, CENTER);
  text('Rango disponible: 0.01 s — 1.00 s', margin.left + plotW, 472);

  // (El slider se encuentra en Y = 496)

  // Etiquetas de los extremos del slider (Y = 526)
  fill(100, 116, 139);
  textSize(11);
  textAlign(LEFT, TOP);
  text('0.01 s (Mayor resolución)', margin.left, 526);

  textAlign(CENTER, TOP);
  text('0.50 s', margin.left + plotW / 2, 526);

  textAlign(RIGHT, TOP);
  text('1.00 s (Paso grueso por defecto)', margin.left + plotW, 526);

  // Rótulo de preajustes rápidos (Y = 556)
  fill(51, 65, 85);
  textSize(11);
  textStyle(BOLD);
  textAlign(LEFT, CENTER);
  text('Preajustes rápidos:', margin.left, 560);

  // (Los botones de preajustes se encuentran en Y = 550)

  // Caja de nota didáctica sobre impacto físico (Y = 598 a 642)
  fill(239, 246, 255);
  stroke(191, 219, 254);
  rect(margin.left, 598, plotW, 44, 8);

  noStroke();
  fill(30, 64, 175);
  textSize(11);
  textStyle(NORMAL);
  textAlign(LEFT, CENTER);
  text('Impacto físico del paso Δt: Con Δt = 1.00 s, la posición x(t) avanza en pasos discretos notables pero se mantiene acotada.\nAl reducir Δt ≤ 0.10 s, converge exactamente hacia la solución analítica x(t) = cos(t).', margin.left + 14, 620);
}
