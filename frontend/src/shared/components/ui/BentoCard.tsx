import React from 'react'

export interface BentoCardProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string
  action?: React.ReactNode
}

export function BentoCard({ 
  className = '', 
  title,
  action,
  children,
  ...props 
}: BentoCardProps) {
  return (
    <div 
      className={`bg-surface-container-lowest neo-latex-border rounded overflow-hidden flex flex-col ${className}`}
      {...props}
    >
      {(title || action) && (
        <div className="flex items-center justify-between px-4 py-3 border-b border-outline-variant bg-surface">
          {title && (
            <h3 className="font-label-caps text-label-caps text-on-surface uppercase tracking-wide">
              {title}
            </h3>
          )}
          {action && <div>{action}</div>}
        </div>
      )}
      <div className="p-4 flex-1">
        {children}
      </div>
    </div>
  )
}
