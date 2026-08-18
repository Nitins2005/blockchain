import { useEffect, useRef, useState } from 'react'
import { ZoomIn, ZoomOut, Maximize2, RefreshCw } from 'lucide-react'

export default function CytoscapeGraph({ nodes = [], edges = [], onNodeClick, height = 500 }) {
  const containerRef = useRef(null)
  const cyRef = useRef(null)
  const [selectedNode, setSelectedNode] = useState(null)

  useEffect(() => {
    if (!containerRef.current || nodes.length === 0) return

    let cy
    import('cytoscape').then(({ default: cytoscape }) => {
      cy = cytoscape({
        container: containerRef.current,
        elements: { nodes, edges },
        style: [
          {
            selector: 'node',
            style: {
              'background-color': 'data(color)',
              'label': 'data(label)',
              'color': '#ffffff',
              'font-size': '10px',
              'text-valign': 'bottom',
              'text-margin-y': 4,
              'width': (ele) => ele.data('is_center') ? 40 : 24,
              'height': (ele) => ele.data('is_center') ? 40 : 24,
              'border-width': (ele) => ele.data('is_center') ? 3 : 1,
              'border-color': (ele) => ele.data('is_center') ? '#6366f1' : 'rgba(255,255,255,0.2)',
              'overlay-padding': 4,
            }
          },
          {
            selector: 'node:selected',
            style: {
              'border-width': 3,
              'border-color': '#6366f1',
              'box-shadow': '0 0 20px #6366f1',
            }
          },
          {
            selector: 'edge',
            style: {
              'width': 1.5,
              'line-color': 'rgba(255,255,255,0.15)',
              'target-arrow-color': 'rgba(255,255,255,0.3)',
              'target-arrow-shape': 'triangle',
              'curve-style': 'bezier',
              'arrow-scale': 0.8,
            }
          },
          {
            selector: 'edge:selected',
            style: {
              'line-color': '#6366f1',
              'target-arrow-color': '#6366f1',
              'width': 2.5,
            }
          }
        ],
        layout: { name: 'cose', padding: 30, animate: true, animationDuration: 800 },
        userZoomingEnabled: true,
        userPanningEnabled: true,
        boxSelectionEnabled: false,
      })

      cy.on('tap', 'node', (evt) => {
        const node = evt.target
        const data = node.data()
        setSelectedNode(data)
        if (onNodeClick) onNodeClick(data)
      })

      cy.on('tap', (evt) => {
        if (evt.target === cy) setSelectedNode(null)
      })

      cyRef.current = cy
    })

    return () => {
      if (cy) cy.destroy()
    }
  }, [nodes, edges])

  const handleZoomIn = () => cyRef.current?.zoom(cyRef.current.zoom() * 1.3)
  const handleZoomOut = () => cyRef.current?.zoom(cyRef.current.zoom() * 0.7)
  const handleFit = () => cyRef.current?.fit(30)
  const handleReset = () => cyRef.current?.layout({ name: 'cose', animate: true }).run()

  return (
    <div className="relative rounded-xl overflow-hidden border border-white/10 bg-dark-300" style={{ height }}>
      <div ref={containerRef} style={{ width: '100%', height: '100%', background: 'transparent' }} />

      {/* Controls */}
      <div className="absolute top-3 right-3 flex flex-col gap-1">
        {[{ icon: ZoomIn, fn: handleZoomIn }, { icon: ZoomOut, fn: handleZoomOut },
          { icon: Maximize2, fn: handleFit }, { icon: RefreshCw, fn: handleReset }].map(({ icon: Icon, fn }, i) => (
          <button key={i} onClick={fn}
            className="p-2 rounded-lg bg-dark-200/90 backdrop-blur-sm text-white/60 hover:text-white border border-white/10 hover:border-primary-500/40 transition-colors">
            <Icon size={14} />
          </button>
        ))}
      </div>

      {/* Legend */}
      <div className="absolute bottom-3 left-3 flex gap-3">
        {[['#10b981', 'Low'], ['#f59e0b', 'Medium'], ['#f97316', 'High'], ['#ef4444', 'Critical']].map(([color, label]) => (
          <div key={label} className="flex items-center gap-1.5 text-xs text-white/50">
            <span className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />{label}
          </div>
        ))}
      </div>

      {/* Node detail */}
      {selectedNode && (
        <div className="absolute top-3 left-3 bg-dark-200/95 backdrop-blur-md border border-white/10 rounded-xl p-3 w-64 text-xs">
          <p className="font-mono text-primary-300 truncate mb-2">{selectedNode.address}</p>
          <div className="space-y-1">
            <div className="flex justify-between"><span className="text-white/40">Blockchain</span><span className="text-white capitalize">{selectedNode.blockchain}</span></div>
            <div className="flex justify-between"><span className="text-white/40">Fraud Score</span>
              <span className="font-mono" style={{ color: selectedNode.color }}>{(selectedNode.fraud_score * 100).toFixed(1)}%</span></div>
            <div className="flex justify-between"><span className="text-white/40">Transactions</span><span className="text-white">{selectedNode.tx_count?.toLocaleString()}</span></div>
            <div className="flex justify-between"><span className="text-white/40">Risk Level</span>
              <span className="capitalize" style={{ color: selectedNode.color }}>{selectedNode.risk_level}</span></div>
          </div>
        </div>
      )}

      {nodes.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center">
          <p className="text-white/30">Enter a wallet address to visualize the transaction graph</p>
        </div>
      )}
    </div>
  )
}
