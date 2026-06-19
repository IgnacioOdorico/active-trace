import React, { forwardRef } from 'react'

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className = '', label, error, id, ...props }, ref) => {
    const generatedId = id || React.useId()
    
    return (
      <div className={`flex flex-col gap-1 ${className}`}>
        {label && (
          <label 
            htmlFor={generatedId} 
            className="font-label-caps text-label-caps text-on-surface-variant uppercase"
          >
            {label}
          </label>
        )}
        <input
          id={generatedId}
          ref={ref}
          className={`
            block w-full neo-latex-border rounded bg-surface-container-lowest 
            px-3 py-2 font-body-md text-on-surface 
            placeholder:text-outline 
            focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary
            disabled:cursor-not-allowed disabled:bg-surface-container
            ${error ? 'border-error focus:border-error focus:ring-error' : ''}
          `}
          {...props}
        />
        {error && (
          <span className="font-body-md text-[12px] text-error">
            {error}
          </span>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'
