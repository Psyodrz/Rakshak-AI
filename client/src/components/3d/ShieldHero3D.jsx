/**
 * 3D Shield Hero Component (Simplified)
 * -------------------------------------
 * Floating 3D shield visualization using React Three Fiber.
 * Includes error boundary for graceful fallback.
 */
import React, { useRef, useMemo, Suspense } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Float, Environment, Stars } from '@react-three/drei';
import * as THREE from 'three';

// Simple floating shield mesh
function Shield({ color = '#3b82f6' }) {
  const meshRef = useRef();
  
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.5) * 0.2;
      meshRef.current.rotation.x = Math.cos(state.clock.elapsedTime * 0.3) * 0.1;
    }
  });
  
  // Shield geometry using simple shapes
  const shieldGeometry = useMemo(() => {
    const shape = new THREE.Shape();
    shape.moveTo(0, 1.2);
    shape.quadraticCurveTo(0.8, 1, 0.8, 0.5);
    shape.quadraticCurveTo(0.8, -0.3, 0, -1.2);
    shape.quadraticCurveTo(-0.8, -0.3, -0.8, 0.5);
    shape.quadraticCurveTo(-0.8, 1, 0, 1.2);
    
    return new THREE.ExtrudeGeometry(shape, {
      depth: 0.2,
      bevelEnabled: true,
      bevelThickness: 0.05,
      bevelSize: 0.05,
      bevelSegments: 3
    });
  }, []);
  
  return (
    <Float speed={2} floatIntensity={0.5}>
      <mesh ref={meshRef} geometry={shieldGeometry}>
        <meshStandardMaterial
          color={color}
          metalness={0.6}
          roughness={0.3}
          emissive={color}
          emissiveIntensity={0.2}
        />
      </mesh>
      
      {/* Glow sphere */}
      <mesh position={[0, 0, 0.15]}>
        <sphereGeometry args={[0.4, 16, 16]} />
        <meshStandardMaterial
          color="#60a5fa"
          emissive="#3b82f6"
          emissiveIntensity={0.3}
          transparent
          opacity={0.2}
        />
      </mesh>
    </Float>
  );
}

// Scene with lighting
function Scene({ riskLevel = 'safe' }) {
  const color = useMemo(() => {
    switch (riskLevel) {
      case 'critical': return '#ef4444';
      case 'warning': return '#f59e0b';
      default: return '#3b82f6';
    }
  }, [riskLevel]);
  
  return (
    <>
      <ambientLight intensity={0.5} />
      <directionalLight position={[5, 5, 5]} intensity={1} />
      <pointLight position={[-3, -3, -3]} intensity={0.3} color="#60a5fa" />
      
      <Stars radius={50} depth={30} count={1000} factor={3} saturation={0} fade speed={0.5} />
      
      <Shield color={color} />
      
      <Environment preset="night" />
    </>
  );
}

// Loading fallback
function LoadingFallback() {
  return (
    <mesh>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color="#3b82f6" wireframe />
    </mesh>
  );
}

// Error Boundary Class
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('3D Shield Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          width: '100%',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'linear-gradient(135deg, #1a2332, #0a0e1a)',
          color: '#6b7280',
          fontSize: '0.875rem',
        }}>
          🛡️ 3D Visualization
        </div>
      );
    }

    return this.props.children;
  }
}

// Exported Component
export function ShieldHero3D({ riskLevel = 'safe', className = '' }) {
  return (
    <div className={`shield-hero-3d ${className}`} style={{ 
      width: '100%', 
      height: '100%',
      minHeight: '200px',
      background: 'transparent'
    }}>
      <ErrorBoundary>
        <Canvas
          camera={{ position: [0, 0, 4], fov: 50 }}
          dpr={[1, 1.5]}
          gl={{ 
            antialias: true, 
            alpha: true,
            powerPreference: 'default',
            failIfMajorPerformanceCaveat: false
          }}
        >
          <Suspense fallback={<LoadingFallback />}>
            <Scene riskLevel={riskLevel} />
          </Suspense>
        </Canvas>
      </ErrorBoundary>
    </div>
  );
}

export default ShieldHero3D;
