import React, { useState, useEffect } from 'react'
import PageWrapper from '../../components/Layout/PageWrapper'
import { Server, Database, Share2, Brain, Activity, Zap, Play } from 'lucide-react'
import Spinner from '../../components/UI/Spinner'
import toast from 'react-hot-toast'

export default function SystemStats() {
  const [loading, setLoading] = useState(false)
  const [training, setTraining] = useState(false)

  const handleTrain = () => {
    setTraining(true)
    toast.success('Started model training')
    setTimeout(() => {
      setTraining(false)
      toast.success('Model training completed')
    }, 5000)
  }

  return (
    <PageWrapper title="System Status & ML Ops">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        
        {/* System Health */}
        <div className="bg-dark-300 border border-white/10 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-6">System Health</h3>
          <div className="space-y-4">
            {[
              { name: 'Core API Server', status: 'Healthy', ping: '24ms', icon: Server, color: 'emerald' },
              { name: 'PostgreSQL Database', status: 'Healthy', ping: '12ms', icon: Database, color: 'emerald' },
              { name: 'Neo4j Graph DB', status: 'Healthy', ping: '45ms', icon: Share2, color: 'emerald' },
              { name: 'Python ML Service', status: 'Healthy', ping: '110ms', icon: Brain, color: 'emerald' }
            ].map((service, i) => (
              <div key={i} className="flex items-center justify-between p-4 bg-dark-400 rounded-lg border border-white/5">
                <div className="flex items-center gap-3">
                  <div className={`p-2 bg-${service.color}-500/10 text-${service.color}-400 rounded-lg`}>
                    <service.icon size={20} />
                  </div>
                  <div>
                    <h4 className="text-white font-medium">{service.name}</h4>
                    <p className="text-xs text-white/50">{service.ping} response time</p>
                  </div>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium bg-${service.color}-500/10 text-${service.color}-400`}>
                  {service.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* AI Model Status */}
        <div className="bg-dark-300 border border-white/10 rounded-xl p-6 flex flex-col">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h3 className="text-lg font-semibold text-white mb-1">AI Model Status</h3>
              <p className="text-sm text-white/60">Version: v2.4.1-ensemble (Active)</p>
            </div>
            <button onClick={handleTrain} disabled={training} className="flex items-center gap-2 bg-primary-600 hover:bg-primary-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg transition-colors text-sm">
              {training ? <Spinner size="sm" /> : <Play size={16} />} 
              {training ? 'Training...' : 'Trigger Retrain'}
            </button>
          </div>
          
          <div className="flex-1 bg-dark-400 rounded-lg border border-white/5 p-4 mb-4">
            <h4 className="text-sm font-medium text-white/80 mb-4">Current Performance Metrics</h4>
            <div className="space-y-4">
              {[
                { label: 'Accuracy', value: 0.942 },
                { label: 'Precision', value: 0.915 },
                { label: 'Recall', value: 0.898 },
                { label: 'F1 Score', value: 0.906 },
                { label: 'AUC-ROC', value: 0.965 }
              ].map((metric, i) => (
                <div key={i}>
                  <div className="flex justify-between text-sm mb-1.5">
                    <span className="text-white/70">{metric.label}</span>
                    <span className="text-white font-mono">{(metric.value * 100).toFixed(1)}%</span>
                  </div>
                  <div className="h-2 w-full bg-dark-200 rounded-full overflow-hidden">
                    <div className="h-full bg-primary-500 rounded-full" style={{ width: `${metric.value * 100}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[
          { label: 'CPU Usage', value: 35, color: 'blue' },
          { label: 'Memory Usage', value: 62, color: 'purple' },
          { label: 'Storage', value: 41, color: 'orange' }
        ].map((res, i) => (
          <div key={i} className="bg-dark-300 border border-white/10 rounded-xl p-6">
            <div className="flex justify-between items-center mb-4">
              <h4 className="text-white/60 font-medium">{res.label}</h4>
              <Activity size={18} className={`text-${res.color}-400`} />
            </div>
            <div className="flex items-end gap-2 mb-2">
              <span className="text-3xl font-bold text-white">{res.value}%</span>
            </div>
            <div className="h-1.5 w-full bg-dark-200 rounded-full overflow-hidden mt-4">
              <div className={`h-full bg-${res.color}-500 rounded-full`} style={{ width: `${res.value}%` }} />
            </div>
          </div>
        ))}
      </div>
    </PageWrapper>
  )
}
