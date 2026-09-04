---
name: react-three-fiber
description: Build performant 3D scenes with React Three Fiber (@react-three/fiber) and drei. Use when creating or optimizing R3F/Three.js scenes, animations, loaders, or controlling draw calls and frame cost.
---

# React Three Fiber

Declarative Three.js in React. The GPU is rarely the bottleneck — React reconciliation, draw calls, and per-frame allocations usually are.

## Canvas setup

```tsx
<Canvas
  dpr={[1, 2]}                 // clamp pixel ratio; Retina at 3x is brutal
  gl={{ powerPreference: 'high-performance', antialias: true }}
  frameloop="demand"           // render only when something changes (static scenes)
  camera={{ position: [0, 0, 5], fov: 50 }}
>
```

- `powerPreference: 'high-performance'` asks the OS for the discrete GPU, not the iGPU. Big win on laptops.
- Use `frameloop="demand"` for scenes that come to rest (configurators, viewers). Use the default loop only when something always moves.

## The #1 rule: animate by mutation in `useFrame`, never `setState`

```tsx
const ref = useRef<THREE.Mesh>(null!);
useFrame((state, delta) => {
  ref.current.rotation.y += delta;   // use delta -> refresh-rate independent
});
return <mesh ref={ref}>{/* ... */}</mesh>;
```

- `setState` in `useFrame` routes a 60fps update through React's scheduler — never do it.
- Use `delta` (not fixed increments) so motion runs the same speed on every display.
- For smoothing use `THREE.MathUtils.lerp` / `damp` inside `useFrame`.

## Don't allocate in the frame loop

- No `new THREE.Vector3()` / `new Color()` inside `useFrame`. Allocate once outside and reuse.
- Reuse geometries and materials across meshes:

```tsx
const geom = useMemo(() => new THREE.BoxGeometry(), []);
const mat  = useMemo(() => new THREE.MeshStandardMaterial({ color: 'orange' }), []);
return items.map((p) => <mesh key={p.id} geometry={geom} material={mat} position={p.pos} />);
```

## Draw calls — keep them low

- Each mesh ≈ one draw call. Aim for a few hundred; ~1000 is the ceiling.
- **Instance** repeated objects — hundreds of thousands in one draw call:

```tsx
import { Instances, Instance } from '@react-three/drei';
<Instances limit={10000}>
  <boxGeometry /><meshStandardMaterial />
  {data.map((d, i) => <Instance key={i} position={d.pos} />)}
</Instances>
```

- Merge static geometry with drei `<Merged>`; use texture atlases to share materials.

## Loading & assets

- Load with `useLoader` / `useGLTF` so results are cached and reused.
- Preload: `useGLTF.preload('/model.glb')`.
- Compress: Draco for geometry, KTX2/Basis for textures (`useKTX2`).
- Nest `<Suspense>` for progressive low → high quality loading.

## Level of detail & adaptivity

- `<Detailed distances={[0, 10, 20]}>` swaps high/mid/low meshes by camera distance.
- `<PerformanceMonitor onDecline={…} onIncline={…}>` adapts DPR/quality to the device.
- drei `<AdaptiveDpr pixelated />` and `<AdaptiveEvents />` regress quality during movement.

## Lights & shadows (expensive)

- Each real-time light multiplies fragment cost — keep to a few; prefer baked lighting/IBL (`<Environment />`).
- Shadows: small `shadow-mapSize` (512–1024); bake with drei `<BakeShadows />` for static scenes.

## Post-processing

- Use `@react-three/postprocessing` (merges passes) over raw `EffectComposer`.
- Bloom/SSAO/DOF are costly — add deliberately, render effects at reduced resolution if needed.

## Cleanup

- R3F auto-disposes objects it created on unmount. Manually `.dispose()` anything you created imperatively (render targets, manual geometries/materials/textures).

## Debug

- drei `<Stats />` for FPS/ms; inspect `gl.info.render.calls` and `.triangles`.
- Confirm the active GPU via `WEBGL_debug_renderer_info` (see the `webgl` skill).

## Reference

- R3F docs: "Scaling performance", "Performance pitfalls".
- drei: `Instances`, `Merged`, `Detailed`, `PerformanceMonitor`, `AdaptiveDpr`, `Environment`, `BakeShadows`.
- Verified against R3F 8.x / drei 9.x / three r160+. Check installed versions for API drift.
