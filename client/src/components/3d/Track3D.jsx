/**
 * 3D Track Visualization
 * ----------------------
 * Interactive 3D railway track with zone markers.
 * Uses React Three Fiber for WebGL rendering.
 */
import React, { useRef, useMemo, Suspense } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { 
  OrbitControls, 
  PerspectiveCamera,
  Environment,
  Float,
  Html
} from '@react-three/drei';
import * as THREE from 'three';

// Railway track segment
function Track() {
  const trackRef = useRef();
  
  // Create curved track geometry
  const curve = useMemo(() => {
    return new THREE.CatmullRomCurve3([
      new THREE.Vector3(-8, 0, 0),
      new THREE.Vector3(-4, 0, -1),
      new THREE.Vector3(0, 0, 0.5),
      new THREE.Vector3(4, 0, -0.5),
      new THREE.Vector3(8, 0, 0),
    ]);
  }, []);
  
  const tubeGeometry = useMemo(() => {
    return new THREE.TubeGeometry(curve, 64, 0.05, 8, false);
  }, [curve]);
  
  return (
    <group ref={trackRef}>
      {/* Main rail - left */}
      <mesh position={[0, 0.02, 0.15]}>
        <tubeGeometry args={[curve, 64, 0.03, 8, false]} />
        <meshStandardMaterial color="#6b7280" metalness={0.8} roughness={0.2} />
      </mesh>
      
      {/* Main rail - right */}
      <mesh position={[0, 0.02, -0.15]}>
        <tubeGeometry args={[curve, 64, 0.03, 8, false]} />
        <meshStandardMaterial color="#6b7280" metalness={0.8} roughness={0.2} />
      </mesh>
      
      {/* Railroad ties */}
      {[...Array(40)].map((_, i) => {
        const t = i / 39;
        const point = curve.getPoint(t);
        const tangent = curve.getTangent(t);
        const angle = Math.atan2(tangent.z, tangent.x);
        
        return (
          <mesh 
            key={i} 
            position={[point.x, 0, point.z]}
            rotation={[0, -angle + Math.PI / 2, 0]}
          >
            <boxGeometry args={[0.08, 0.02, 0.5]} />
            <meshStandardMaterial color="#4a3f35" />
          </mesh>
        );
      })}
      
      {/* Ground plane */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.01, 0]}>
        <planeGeometry args={[20, 6]} />
        <meshStandardMaterial color="#1a1a2e" />
      </mesh>
    </group>
  );
}

// Zone marker in 3D
function ZoneMarker({ position, status = 'normal', label, onClick }) {
  const meshRef = useRef();
  const glowRef = useRef();
  
  const color = useMemo(() => {
    switch (status) {
      case 'critical': return '#ef4444';
      case 'warning': return '#f59e0b';
      case 'active': return '#3b82f6';
      default: return '#22c55e';
    }
  }, [status]);
  
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.position.y = 0.3 + Math.sin(state.clock.elapsedTime * 2) * 0.05;
    }
    if (glowRef.current) {
      glowRef.current.scale.setScalar(1 + Math.sin(state.clock.elapsedTime * 3) * 0.1);
    }
  });
  
  return (
    <Float speed={2} floatIntensity={0.3}>
      <group position={position} onClick={onClick}>
        {/* Glow sphere */}
        <mesh ref={glowRef}>
          <sphereGeometry args={[0.15, 16, 16]} />
          <meshStandardMaterial
            color={color}
            emissive={color}
            emissiveIntensity={0.5}
            transparent
            opacity={0.3}
          />
        </mesh>
        
        {/* Core sphere */}
        <mesh ref={meshRef}>
          <sphereGeometry args={[0.08, 16, 16]} />
          <meshStandardMaterial
            color={color}
            emissive={color}
            emissiveIntensity={1}
          />
        </mesh>
        
        {/* Label */}
        <Html
          position={[0, 0.5, 0]}
          center
          style={{
            pointerEvents: 'none',
            userSelect: 'none',
          }}
        >
          <div style={{
            background: 'rgba(10, 14, 26, 0.9)',
            color: '#fff',
            padding: '4px 8px',
            borderRadius: '4px',
            fontSize: '10px',
            fontFamily: 'monospace',
            whiteSpace: 'nowrap',
            border: `1px solid ${color}`,
          }}>
            {label}
          </div>
        </Html>
      </group>
    </Float>
  );
}

// Main 3D Track Scene
function TrackScene({ zones = [], selectedZone, onZoneSelect }) {
  return (
    <>
      <ambientLight intensity={0.3} />
      <directionalLight position={[10, 10, 5]} intensity={1} castShadow />
      <pointLight position={[-5, 5, -5]} intensity={0.5} color="#60a5fa" />
      
      <Track />
      
      {/* Zone markers */}
      {zones.map((zone, i) => (
        <ZoneMarker
          key={zone.id}
          position={[zone.x, 0.3, zone.z]}
          status={zone.status}
          label={zone.name}
          onClick={() => onZoneSelect(zone.id)}
        />
      ))}
      
      <OrbitControls 
        enableZoom={true}
        enablePan={false}
        maxPolarAngle={Math.PI / 2.2}
        minPolarAngle={Math.PI / 4}
        minDistance={3}
        maxDistance={15}
      />
      
      <Environment preset="night" />
    </>
  );
}

// Default zones for demo
const DEFAULT_ZONES = [
  { id: 'ZONE-001', name: 'Mumbai Central', x: -6, z: 0, status: 'normal' },
  { id: 'ZONE-002', name: 'Dadar', x: -3, z: -0.5, status: 'active' },
  { id: 'ZONE-003', name: 'Kurla', x: 0, z: 0.3, status: 'warning' },
  { id: 'ZONE-004', name: 'Thane', x: 3, z: -0.3, status: 'normal' },
  { id: 'ZONE-005', name: 'Kalyan', x: 6, z: 0, status: 'normal' },
];

// Exported Component
export function Track3D({ 
  zones = DEFAULT_ZONES, 
  selectedZone, 
  onZoneSelect = () => {},
  className = '' 
}) {
  return (
    <div className={`track-3d ${className}`} style={{ 
      width: '100%', 
      height: '400px',
      borderRadius: '12px',
      overflow: 'hidden',
      background: 'linear-gradient(to bottom, #0a0e1a, #111827)'
    }}>
      <Canvas
        camera={{ position: [0, 8, 10], fov: 35 }}
        dpr={[1, 2]}
        shadows
      >
        <Suspense fallback={null}>
          <TrackScene 
            zones={zones} 
            selectedZone={selectedZone}
            onZoneSelect={onZoneSelect}
          />
        </Suspense>
      </Canvas>
    </div>
  );
}

export default Track3D;
