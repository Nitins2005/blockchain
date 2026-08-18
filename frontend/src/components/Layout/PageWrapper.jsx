import React from 'react'

export default function PageWrapper({ title, subtitle, actions, children }) {
  return (
    <div className="flex-1 p-6 min-h-screen">
      <div className="mb-6 flex items-start justify-between">
        <div>
          <h1 className="page-title">{title}</h1>
          {subtitle && <p className="page-subtitle">{subtitle}</p>}
        </div>
        {actions && <div className="flex items-center gap-3">{actions}</div>}
      </div>
      {children}
    </div>
  )
}
