"use client";

import React from "react";

interface LogoProps {
  /** Size in pixels (standard: 32) */
  size?: number;
  /** Color variant: navy (standard), white (dark bg), green (accent) */
  variant?: "navy" | "white" | "green";
  /** Whether to show the "Nocturn AI" text brand mark */
  showText?: boolean;
  /** Additional CSS classes */
  className?: string;
}

/**
 * NOCTURN AI — Reusable Signature Logo
 * This component is pre-configured with the official Nocturn brand marks.
 */
export const Logo = ({
  size = 32,
  variant = "navy",
  showText = true,
  className = "",
}: LogoProps) => {
  // Brand color mapping
  const colors = {
    navy: "#0F172A",
    white: "#FFFFFF",
    green: "#22C55E",
  };

  const brandColor = colors[variant] || colors.navy;

  return (
    <div 
      className={`nocturn-logo ${className}`} 
      style={{ 
        display: "inline-flex", 
        alignItems: "center", 
        gap: `${size * 0.25}px`, // Proportional gap
        userSelect: "none"
      }}
    >
      <svg 
        width={size} 
        height={size} 
        viewBox="0 0 32 32" 
        fill="none" 
        aria-hidden="true"
      >
        <circle 
          cx="16" 
          cy="16" 
          r="14" 
          stroke={brandColor} 
          strokeWidth="2.5" 
          style={{ fill: "none" }} 
        />
        <path 
          d="M16 6C10.5 6 8 12 8 16c0 4 2.5 10 8 10 -3-2-4.5-5.5-4.5-10S13 8 16 6z" 
          fill={brandColor} 
        />
      </svg>
      
      {showText && (
        <span 
          style={{ 
            color: brandColor, 
            fontSize: `${size * 0.75}px`, // Proportional text size (24px at 32px)
            fontWeight: 700, 
            fontFamily: "'Instrument Serif', serif", 
            textTransform: "uppercase",
            lineHeight: 1,
            whiteSpace: "nowrap"
          }}
        >
          Nocturn AI
        </span>
      )}
    </div>
  );
};
