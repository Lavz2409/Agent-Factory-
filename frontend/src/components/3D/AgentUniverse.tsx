/**
 * AgentUniverse — Three.js scene with 7 agent nodes in a circular orbit.
 *
 * Layout:
 *  - Dark space background with subtle star field
 *  - 7 glowing spheres, each representing one agent
 *  - Active agent: animated pulse + cyan glow
 *  - Animated arc lines between consecutive agents in the pipeline
 *  - Click agent → set it as the active view in the agent store
 *  - OrbitControls for rotate/zoom
 */
import { useEffect, useRef, useMemo } from 'react'
import * as THREE from 'three'
import { useAgentStore, AGENT_ORDER } from '@/store/agentStore'
import type { AgentName, AgentStatus } from '@/types'

// Colour palette per status
const STATUS_COLOR: Record<AgentStatus, number> = {
  idle:    0x1e1e32,
  running: 0x00d9ff,
  success: 0x00ff88,
  error:   0xff0055,
}

const EMISSIVE: Record<AgentStatus, number> = {
  idle:    0x000000,
  running: 0x004466,
  success: 0x003322,
  error:   0x330011,
}

function buildStarField(count = 800): THREE.Points {
  const geo  = new THREE.BufferGeometry()
  const pos  = new Float32Array(count * 3)
  for (let i = 0; i < count; i++) {
    pos[i * 3]     = (Math.random() - 0.5) * 60
    pos[i * 3 + 1] = (Math.random() - 0.5) * 60
    pos[i * 3 + 2] = (Math.random() - 0.5) * 60
  }
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3))
  const mat = new THREE.PointsMaterial({ color: 0x555577, size: 0.08 })
  return new THREE.Points(geo, mat)
}

function buildAgentNodes(radius: number): THREE.Mesh[] {
  return AGENT_ORDER.map((_, i) => {
    const angle = (i / AGENT_ORDER.length) * Math.PI * 2
    const x     = Math.cos(angle) * radius
    const y     = Math.sin(angle) * radius
    const geo   = new THREE.SphereGeometry(0.22, 32, 32)
    const mat   = new THREE.MeshPhongMaterial({
      color:    STATUS_COLOR.idle,
      emissive: EMISSIVE.idle,
      shininess: 80,
    })
    const mesh = new THREE.Mesh(geo, mat)
    mesh.position.set(x, y, 0)
    mesh.userData.index = i
    return mesh
  })
}

function buildFlowLines(nodes: THREE.Mesh[]): THREE.Line[] {
  return nodes.slice(0, -1).map((node, i) => {
    const next = nodes[i + 1]
    const pts  = [node.position, next.position]
    const geo  = new THREE.BufferGeometry().setFromPoints(pts)
    const mat  = new THREE.LineBasicMaterial({ color: 0x1e1e32, transparent: true, opacity: 0.5 })
    return new THREE.Line(geo, mat)
  })
}

function buildParticles(count = 60): THREE.Points {
  const geo = new THREE.BufferGeometry()
  const pos = new Float32Array(count * 3)
  for (let i = 0; i < count; i++) {
    pos[i * 3]     = (Math.random() - 0.5) * 0.8
    pos[i * 3 + 1] = (Math.random() - 0.5) * 0.8
    pos[i * 3 + 2] = (Math.random() - 0.5) * 0.8
  }
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3))
  const mat = new THREE.PointsMaterial({ color: 0x00d9ff, size: 0.05, transparent: true, opacity: 0.7 })
  return new THREE.Points(geo, mat)
}

export default function AgentUniverse() {
  const mountRef   = useRef<HTMLDivElement>(null)
  const sceneRef   = useRef<{ cleanup: () => void } | null>(null)
  const agents     = useAgentStore(s => s.agents)
  const activeAgent = useAgentStore(s => s.activeAgent)
  const setActive  = useAgentStore(s => s.setActiveAgent)

  // Keep latest agent state accessible inside the render loop without re-creating the scene
  const agentsRef = useRef(agents)
  agentsRef.current = agents
  const activeRef = useRef(activeAgent)
  activeRef.current = activeAgent

  useEffect(() => {
    const el = mountRef.current
    if (!el) return

    // ── scene setup ──────────────────────────────────────────────
    const scene    = new THREE.Scene()
    scene.background = new THREE.Color(0x0f0f1e)
    scene.fog        = new THREE.Fog(0x0f0f1e, 20, 60)

    const W = el.clientWidth
    const H = el.clientHeight
    const camera = new THREE.PerspectiveCamera(55, W / H, 0.1, 100)
    camera.position.set(0, 0, 6)

    const renderer = new THREE.WebGLRenderer({ antialias: true })
    renderer.setPixelRatio(window.devicePixelRatio)
    renderer.setSize(W, H)
    el.appendChild(renderer.domElement)

    // ── lights ────────────────────────────────────────────────────
    scene.add(new THREE.AmbientLight(0xffffff, 0.3))
    const point = new THREE.PointLight(0x00d9ff, 2, 10)
    point.position.set(0, 0, 3)
    scene.add(point)

    // ── objects ───────────────────────────────────────────────────
    scene.add(buildStarField())

    const RADIUS = 2.2
    const nodes  = buildAgentNodes(RADIUS)
    nodes.forEach(n => scene.add(n))

    const lines = buildFlowLines(nodes)
    lines.forEach(l => scene.add(l))

    const particles = buildParticles()
    scene.add(particles)
    particles.visible = false

    // Agent labels (sprites)
    const labelCanvas = (text: string) => {
      const c = document.createElement('canvas')
      c.width = 256; c.height = 64
      const ctx = c.getContext('2d')!
      ctx.font = '600 20px Inter, sans-serif'
      ctx.fillStyle = '#7070a0'
      ctx.textAlign = 'center'
      ctx.fillText(text.replace('Agent', ''), 128, 42)
      return c
    }
    const labelSprites = AGENT_ORDER.map((name, i) => {
      const tex      = new THREE.CanvasTexture(labelCanvas(name))
      const mat      = new THREE.SpriteMaterial({ map: tex, transparent: true, opacity: 0.85 })
      const sprite   = new THREE.Sprite(mat)
      const angle    = (i / AGENT_ORDER.length) * Math.PI * 2
      sprite.position.set(
        Math.cos(angle) * (RADIUS + 0.55),
        Math.sin(angle) * (RADIUS + 0.55),
        0,
      )
      sprite.scale.set(0.9, 0.22, 1)
      scene.add(sprite)
      return sprite
    })

    // ── simple orbit controls (manual) ────────────────────────────
    let isDragging = false, lastX = 0, lastY = 0
    let rotX = 0, rotY = 0, zoom = 6

    const onDown = (e: MouseEvent) => { isDragging = true; lastX = e.clientX; lastY = e.clientY }
    const onUp   = ()              => { isDragging = false }
    const onMove = (e: MouseEvent) => {
      if (!isDragging) return
      rotY += (e.clientX - lastX) * 0.008
      rotX += (e.clientY - lastY) * 0.008
      lastX = e.clientX; lastY = e.clientY
    }
    const onWheel = (e: WheelEvent) => {
      zoom = Math.max(3, Math.min(12, zoom + e.deltaY * 0.01))
    }
    el.addEventListener('mousedown', onDown)
    window.addEventListener('mouseup', onUp)
    window.addEventListener('mousemove', onMove)
    el.addEventListener('wheel', onWheel, { passive: true })

    // ── click raycasting ──────────────────────────────────────────
    const raycaster = new THREE.Raycaster()
    const mouse     = new THREE.Vector2()
    const onClick   = (e: MouseEvent) => {
      const rect = el.getBoundingClientRect()
      mouse.x = ((e.clientX - rect.left) / rect.width)  * 2 - 1
      mouse.y = -((e.clientY - rect.top)  / rect.height) * 2 + 1
      raycaster.setFromCamera(mouse, camera)
      const hits = raycaster.intersectObjects(nodes)
      if (hits.length) {
        const idx  = hits[0].object.userData.index as number
        const name = AGENT_ORDER[idx]
        setActive(activeRef.current === name ? null : name)
      }
    }
    el.addEventListener('click', onClick)

    // ── resize handler ────────────────────────────────────────────
    const onResize = () => {
      const W = el.clientWidth, H = el.clientHeight
      camera.aspect = W / H
      camera.updateProjectionMatrix()
      renderer.setSize(W, H)
    }
    window.addEventListener('resize', onResize)

    // ── animation loop ────────────────────────────────────────────
    const clock = new THREE.Clock()
    let animId: number

    const animate = () => {
      animId = requestAnimationFrame(animate)
      const t  = clock.getElapsedTime()

      // Camera orbit
      camera.position.x = Math.sin(rotY) * Math.cos(rotX) * zoom
      camera.position.y = Math.sin(rotX) * zoom
      camera.position.z = Math.cos(rotY) * Math.cos(rotX) * zoom
      camera.lookAt(scene.position)

      const agentsNow = agentsRef.current
      const activeNow = activeRef.current

      nodes.forEach((node, i) => {
        const name    = AGENT_ORDER[i]
        const status  = agentsNow[name]?.status ?? 'idle'
        const mat     = node.material as THREE.MeshPhongMaterial

        // Smoothly lerp colour toward target
        const targetColor = new THREE.Color(STATUS_COLOR[status])
        mat.color.lerp(targetColor, 0.1)
        mat.emissive.lerp(new THREE.Color(EMISSIVE[status]), 0.1)

        // Pulse active / running node
        if (status === 'running') {
          node.scale.setScalar(1 + Math.sin(t * 4) * 0.1)
        } else if (name === activeNow) {
          node.scale.setScalar(1 + Math.sin(t * 2) * 0.05)
        } else {
          node.scale.lerp(new THREE.Vector3(1, 1, 1), 0.1)
        }

        // Flow line glow when running
        if (i < lines.length) {
          const lineMat = lines[i].material as THREE.LineBasicMaterial
          lineMat.color.lerp(
            status === 'running' ? new THREE.Color(0x00d9ff) : new THREE.Color(0x1e1e32),
            0.08,
          )
        }
      })

      // Show particles around active running agent
      const runningIdx = AGENT_ORDER.findIndex(n => agentsNow[n]?.status === 'running')
      if (runningIdx >= 0) {
        particles.position.copy(nodes[runningIdx].position)
        particles.visible  = true
        particles.rotation.z = t * 0.8
      } else {
        particles.visible = false
      }

      renderer.render(scene, camera)
    }
    animate()

    sceneRef.current = {
      cleanup: () => {
        cancelAnimationFrame(animId)
        el.removeEventListener('mousedown', onDown)
        window.removeEventListener('mouseup', onUp)
        window.removeEventListener('mousemove', onMove)
        el.removeEventListener('wheel', onWheel)
        el.removeEventListener('click', onClick)
        window.removeEventListener('resize', onResize)
        renderer.dispose()
        if (el.contains(renderer.domElement)) el.removeChild(renderer.domElement)
      },
    }

    return () => sceneRef.current?.cleanup()
  }, [setActive]) // mount once — reads agent state via refs

  return (
    <div
      ref={mountRef}
      className="w-full h-full"
      style={{ cursor: 'grab', background: '#0f0f1e' }}
    />
  )
}
