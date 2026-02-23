import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { onAuthStateChanged } from 'firebase/auth';
import { auth } from './config/firebase';

// Pages
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import MonitorDetails from './pages/MonitorDetails';
import Monitors from './pages/Monitors';
import Alerts from './pages/Alerts';

// Components
import Layout from './components/Layout';
import LoadingSpinner from './components/LoadingSpinner';

// Context
import { AuthProvider, useAuth } from './context/AuthContext';

function PrivateRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return <LoadingSpinner />;
  }

  return user ? children : <Navigate to="/login" />;
}

function AppRoutes() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
          element={
            <PrivateRoute>
              <Layout>
                <Dashboard />
              </Layout>
            </PrivateRoute>
          }
        />
        <Route
          path="/monitors"
          element={
            <PrivateRoute>
              <Layout>
                <Monitors />
              </Layout>
            </PrivateRoute>
          }
        />
        <Route
          path="/monitors/:id"
          element={
            <PrivateRoute>
              <Layout>
                <MonitorDetails />
              </Layout>
            </PrivateRoute>
          }
        />
        <Route
          path="/alerts"
          element={
            <PrivateRoute>
              <Layout>
                <Alerts />
              </Layout>
            </PrivateRoute>
          }
        />
      </Routes>
    </Router>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppRoutes />
      <Toaster position="top-right" />
    </AuthProvider>
  );
}

export default App;
