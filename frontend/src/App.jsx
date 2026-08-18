import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider, useAuth } from './context/AuthContext'
import { NotificationProvider } from './context/NotificationContext'
import MainLayout from './components/Layout/MainLayout'

// Import all pages
import Login from './pages/Auth/Login'
import Register from './pages/Auth/Register'
import ForgotPassword from './pages/Auth/ForgotPassword'
import Dashboard from './pages/Dashboard/Dashboard'
import BlockchainData from './pages/Blockchain/BlockchainData'
import Transactions from './pages/Transactions/Transactions'
import GraphVisualization from './pages/Graph/GraphVisualization'
import WalletFeatures from './pages/Features/WalletFeatures'
import FraudDetection from './pages/Fraud/FraudDetection'
import WalletAttribution from './pages/Attribution/WalletAttribution'
import ExplainableAI from './pages/Explainability/ExplainableAI'
import Blacklist from './pages/Blacklist/Blacklist'
import Investigations from './pages/Investigations/Investigations'
import Reports from './pages/Reports/Reports'
import NotificationsPage from './pages/Notifications/NotificationsPage'
import UserManagement from './pages/Admin/UserManagement'
import SystemStats from './pages/Admin/SystemStats'

import NotFound from './pages/NotFound'

function ProtectedRoute({ children, adminOnly = false }) {
  const { isAuthenticated, user, isLoading } = useAuth()
  if (isLoading) return <div className="flex items-center justify-center min-h-screen text-white"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div></div>
  return children
}

export default function App() {
  return (
    <AuthProvider>
      <NotificationProvider>
        <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <Toaster position="top-right" toastOptions={{ style: { background: '#1e293b', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' } }} />
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />

            <Route path="/" element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="analytics" element={<WalletFeatures />} />
              <Route path="features" element={<WalletFeatures />} />
              <Route path="blockchain" element={<BlockchainData />} />
              <Route path="blockchain-config" element={<BlockchainData />} />
              <Route path="transactions" element={<Transactions />} />
              <Route path="graph" element={<GraphVisualization />} />
              <Route path="fraud" element={<FraudDetection />} />
              <Route path="fraud-detection" element={<FraudDetection />} />
              <Route path="attribution" element={<WalletAttribution />} />
              <Route path="wallet-attribution" element={<WalletAttribution />} />
              <Route path="explainability" element={<ExplainableAI />} />
              <Route path="explainable-ai" element={<ExplainableAI />} />
              <Route path="blacklist" element={<Blacklist />} />
              <Route path="investigations" element={<Investigations />} />
              <Route path="reports" element={<Reports />} />
              <Route path="notifications" element={<NotificationsPage />} />
              <Route path="users" element={<UserManagement />} />
              <Route path="admin/users" element={<UserManagement />} />
              <Route path="system-stats" element={<SystemStats />} />
              <Route path="profile" element={<UserManagement />} />
            </Route>
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </NotificationProvider>
    </AuthProvider>
  )
}
