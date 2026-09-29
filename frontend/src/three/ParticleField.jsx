import { useMemo, useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import * as THREE from "three";

function seededRandom(seed) {
  const value = Math.sin(seed * 12.9898) * 43758.5453;
  return value - Math.floor(value);
}

function Starfield({ count = 350 }) {
  const ref = useRef();

  const positions = useMemo(() => {
    const arr = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      arr[i * 3] = (seededRandom(i * 3) - 0.5) * 60;
      arr[i * 3 + 1] = (seededRandom(i * 3 + 1) - 0.5) * 30;
      arr[i * 3 + 2] = -10 - seededRandom(i * 3 + 2) * 20; // pushed DEEP behind content
    }
    return arr;
  }, [count]);

  useFrame((_, delta) => {
    ref.current.rotation.z += delta * 0.004; // almost imperceptible drift
  });

  return (
    <points ref={ref}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" args={[positions, 3]} />
      </bufferGeometry>
      <pointsMaterial
        size={0.05}
        color="#8b7cf6"
        transparent
        opacity={0.22} // whisper, not shout
        sizeAttenuation
        depthWrite={false}
        blending={THREE.AdditiveBlending}
      />
    </points>
  );
}

export default function ParticleField() {
  return (
    <div className="fixed inset-0 -z-10 pointer-events-none opacity-70">
      {/* soft vignette so edges fade to void */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_0%,#0b0d12_78%)]" />
      <Canvas camera={{ position: [0, 0, 14], fov: 60 }} dpr={[1, 1.5]}>
        <Starfield />
      </Canvas>
    </div>
  );
}
