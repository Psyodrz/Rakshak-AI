/**
 * Smooth Scroll Provider using Lenis
 * -----------------------------------
 * Provides butter-smooth scrolling.
 * Wrapped in try-catch for graceful recovery.
 */
import React, { useEffect, useRef } from 'react';

export function SmoothScrollProvider({ children }) {
  const lenisRef = useRef(null);
  const rafRef = useRef(null);
  
  useEffect(() => {
    let lenis = null;
    
    // Dynamically import Lenis to prevent SSR/bundling issues
    const initLenis = async () => {
      try {
        const Lenis = (await import('lenis')).default;
        
        lenis = new Lenis({
          duration: 1.2,
          easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
          direction: 'vertical',
          smooth: true,
          smoothTouch: false,
        });
        
        lenisRef.current = lenis;
        
        function raf(time) {
          lenis?.raf(time);
          rafRef.current = requestAnimationFrame(raf);
        }
        
        rafRef.current = requestAnimationFrame(raf);
      } catch (error) {
        console.warn('Lenis initialization failed, using native scroll:', error);
      }
    };
    
    initLenis();
    
    return () => {
      if (rafRef.current) {
        cancelAnimationFrame(rafRef.current);
      }
      if (lenisRef.current) {
        lenisRef.current.destroy();
      }
    };
  }, []);
  
  return <>{children}</>;
}

export default SmoothScrollProvider;
