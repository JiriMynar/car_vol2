import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from '@/hooks/useAuth.jsx';
import Layout from '@/components/Layout';
import ProtectedRoute from '@/components/ProtectedRoute';
import Login from '@/pages/Login';
import Dashboard from '@/pages/Dashboard';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <Layout>
                  <Routes>
                    <Route path="/" element={<Dashboard />} />
                    {/* Placeholder routes - will be implemented in next iterations */}
                    <Route path="/calendar" element={<div className="p-8 text-center text-gray-500">Kalendář - bude implementován</div>} />
                    <Route path="/vehicles" element={<div className="p-8 text-center text-gray-500">Vozidla - bude implementován</div>} />
                    <Route path="/my-reservations" element={<div className="p-8 text-center text-gray-500">Moje rezervace - bude implementován</div>} />
                    <Route 
                      path="/admin/*" 
                      element={
                        <ProtectedRoute adminOnly>
                          <Routes>
                            <Route path="/reservations" element={<div className="p-8 text-center text-gray-500">Admin rezervace - bude implementován</div>} />
                            <Route path="/users" element={<div className="p-8 text-center text-gray-500">Správa uživatelů - bude implementován</div>} />
                            <Route path="/service-records" element={<div className="p-8 text-center text-gray-500">Servisní záznamy - bude implementován</div>} />
                            <Route path="/damage-records" element={<div className="p-8 text-center text-gray-500">Záznamy o poškození - bude implementován</div>} />
                          </Routes>
                        </ProtectedRoute>
                      } 
                    />
                  </Routes>
                </Layout>
              </ProtectedRoute>
            }
          />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;

