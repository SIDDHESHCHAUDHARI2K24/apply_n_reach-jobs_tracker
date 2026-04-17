import { Suspense, lazy } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from '@core/auth/context'
import { ProtectedRoute } from '@core/auth/guards'
import { AppLayout } from '@app/layout/AppLayout'

const LoginPage = lazy(() => import('@app/auth/LoginPage'))
const RegisterPage = lazy(() => import('@app/auth/RegisterPage'))
const ResetPage = lazy(() => import('@app/auth/ResetPage'))
const ProfilePage = lazy(() => import('@app/profile/ProfilePage'))
const JobProfilesPage = lazy(() => import('@app/job-profiles/JobProfilesPage'))
const JobTrackerPage = lazy(() => import('@app/job-tracker/JobTrackerPage'))
const OpeningResumePage = lazy(() => import('@app/opening-resume/OpeningResumePage'))
const SettingsPage = lazy(() => import('@app/settings/SettingsPage'))

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Suspense fallback={<div>Loading...</div>}>
          <Routes>
            {/* Public auth routes */}
            <Route path="/auth/login" element={<LoginPage />} />
            <Route path="/auth/register" element={<RegisterPage />} />
            <Route path="/auth/reset" element={<ResetPage />} />

            {/* Protected routes with layout */}
            <Route element={<AppLayout />}>
              <Route path="/profile/*" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
              <Route path="/job-profiles/*" element={<ProtectedRoute><JobProfilesPage /></ProtectedRoute>} />
              <Route path="/job-tracker" element={<ProtectedRoute><JobTrackerPage /></ProtectedRoute>} />
              <Route path="/job-openings/:openingId/resume/*" element={<ProtectedRoute><OpeningResumePage /></ProtectedRoute>} />
              <Route path="/settings" element={<ProtectedRoute><SettingsPage /></ProtectedRoute>} />
              <Route path="/" element={<Navigate to="/job-profiles" replace />} />
            </Route>
          </Routes>
        </Suspense>
      </AuthProvider>
    </BrowserRouter>
  )
}
