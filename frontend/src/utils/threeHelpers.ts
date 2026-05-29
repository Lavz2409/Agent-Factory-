import * as THREE from 'three'

/** Create a glowing ring around a position (used for active agent highlight). */
export function createGlowRing(radius: number, color: number): THREE.Mesh {
  const geo = new THREE.TorusGeometry(radius, 0.02, 8, 64)
  const mat = new THREE.MeshBasicMaterial({
    color,
    transparent: true,
    opacity: 0.6,
    side: THREE.FrontSide,
  })
  return new THREE.Mesh(geo, mat)
}

/** Linearly interpolate a colour towards target each frame. */
export function lerpColor(mat: THREE.MeshPhongMaterial, targetHex: number, alpha = 0.1) {
  mat.color.lerp(new THREE.Color(targetHex), alpha)
}

/** Convert hex colour to CSS string. */
export function hexToCSS(hex: number): string {
  return `#${hex.toString(16).padStart(6, '0')}`
}

/** Build a BufferGeometry arc between two 3D points (used for data flow lines). */
export function buildArc(a: THREE.Vector3, b: THREE.Vector3, segments = 32): THREE.BufferGeometry {
  const mid = a.clone().lerp(b, 0.5).add(new THREE.Vector3(0, 0, 0.5))
  const curve = new THREE.QuadraticBezierCurve3(a, mid, b)
  return new THREE.BufferGeometry().setFromPoints(curve.getPoints(segments))
}
