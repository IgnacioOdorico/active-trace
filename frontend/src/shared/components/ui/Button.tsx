import React from 'react'

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
}

export function Button({ 
  className = '', 
  variant = 'primary', 
  size = 'md', 
  ...props 
}: ButtonProps) {
  const baseStyles = "inline-flex items-center justify-center font-label-caps text-label-caps rounded transition-all duration-200 uppercase tracking-widest disabled:opacity-50 disabled:cursor-not-allowed"
  
  const variants = {
    primary: "bg-primary text-on-primary hover:bg-opacity-90",
    secondary: "bg-secondary-container text-on-secondary-container hover:bg-secondary hover:text-on-secondary",
    danger: "bg-error text-on-error hover:bg-opacity-90",
    ghost: "bg-transparent border border-outline text-primary hover:bg-surface-container"
  }

  const sizes = {
    sm: "px-3 py-1.5 text-[10px]",
    md: "px-4 py-2",
    lg: "px-6 py-3"
  }

  return (
    <button 
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
      {...props}
    />
  )
}
