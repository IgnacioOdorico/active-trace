import React from 'react'

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'info' | 'warning' | 'critical' | 'success' | 'neutral'
}

export function Badge({ 
  className = '', 
  variant = 'neutral',
  ...props 
}: BadgeProps) {
  const baseStyles = "inline-flex items-center font-label-caps text-[10px] px-2 py-0.5 tracking-wider rounded-sm uppercase whitespace-nowrap"
  
  const variants = {
    info: "bg-secondary-container text-on-secondary-container",
    warning: "bg-[#fff3cd] text-[#856404]", // Optional fallback if standard warning colors aren't defined
    critical: "bg-error-container text-on-error-container",
    success: "bg-[#d4edda] text-[#155724]",
    neutral: "bg-surface-container-high text-on-surface-variant"
  }

  // Adjust warning mapping to standard design tokens if needed
  if (variant === 'warning') {
    variants.warning = "bg-tertiary-container text-on-tertiary-container" // Using tertiary as a fallback for warning/guide
  }

  return (
    <span 
      className={`${baseStyles} ${variants[variant]} ${className}`}
      {...props}
    />
  )
}
