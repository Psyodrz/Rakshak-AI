/**
 * Motion Components
 * =================
 * 
 * Reusable Framer Motion wrappers for consistent animations.
 * Import these instead of writing animation props everywhere.
 */
import React from 'react';
import { motion } from 'framer-motion';

/**
 * Animated Card with hover lift and entry animation
 */
export function MotionCard({ 
  children, 
  className = '', 
  delay = 0,
  ...props 
}) {
  return (
    <motion.div
      className={`card ${className}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ 
        duration: 0.4, 
        delay,
        ease: [0.4, 0, 0.2, 1]
      }}
      whileHover={{ 
        y: -4,
        transition: { duration: 0.2 }
      }}
      {...props}
    >
      {children}
    </motion.div>
  );
}

/**
 * Stagger container for animating children sequentially
 */
export function StaggerContainer({ 
  children, 
  className = '', 
  staggerDelay = 0.1,
  ...props 
}) {
  return (
    <motion.div
      className={className}
      initial="hidden"
      animate="visible"
      variants={{
        hidden: { opacity: 0 },
        visible: {
          opacity: 1,
          transition: {
            staggerChildren: staggerDelay
          }
        }
      }}
      {...props}
    >
      {children}
    </motion.div>
  );
}

/**
 * Stagger child item
 */
export function StaggerItem({ children, className = '', ...props }) {
  return (
    <motion.div
      className={className}
      variants={{
        hidden: { opacity: 0, y: 20 },
        visible: { 
          opacity: 1, 
          y: 0,
          transition: {
            duration: 0.4,
            ease: [0.4, 0, 0.2, 1]
          }
        }
      }}
      {...props}
    >
      {children}
    </motion.div>
  );
}

/**
 * Scale on hover component
 */
export function ScaleOnHover({ 
  children, 
  scale = 1.02,
  className = '',
  ...props 
}) {
  return (
    <motion.div
      className={className}
      whileHover={{ scale }}
      whileTap={{ scale: 0.98 }}
      transition={{ type: "spring", stiffness: 400, damping: 25 }}
      {...props}
    >
      {children}
    </motion.div>
  );
}

/**
 * Fade in on scroll (intersection observer)
 */
export function FadeInOnScroll({ 
  children, 
  className = '',
  ...props 
}) {
  return (
    <motion.div
      className={className}
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-50px" }}
      transition={{ duration: 0.5, ease: [0.4, 0, 0.2, 1] }}
      {...props}
    >
      {children}
    </motion.div>
  );
}

/**
 * Pulse animation for alerts/notifications
 */
export function PulseAnimation({ 
  active = false, 
  children, 
  className = '',
  color = 'rgba(239, 68, 68, 0.5)',
  ...props 
}) {
  return (
    <motion.div
      className={className}
      animate={active ? {
        boxShadow: [
          `0 0 0 0 ${color}`,
          `0 0 0 10px transparent`,
        ]
      } : {}}
      transition={active ? {
        duration: 1.5,
        repeat: Infinity,
        ease: "easeOut"
      } : {}}
      {...props}
    >
      {children}
    </motion.div>
  );
}

/**
 * Number counter animation
 */
export function AnimatedNumber({ 
  value, 
  duration = 0.8,
  className = '' 
}) {
  return (
    <motion.span
      className={className}
      key={value}
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {value}
    </motion.span>
  );
}

export default {
  MotionCard,
  StaggerContainer,
  StaggerItem,
  ScaleOnHover,
  FadeInOnScroll,
  PulseAnimation,
  AnimatedNumber
};
