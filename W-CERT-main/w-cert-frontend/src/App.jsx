import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout/Layout';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Report from './pages/Report';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/Auth/ProtectedRoute';

import DashboardLayout from './pages/Dashboard/Layout';
import DashboardOverview from './pages/Dashboard/Overview';
import Incidents from './pages/Dashboard/Incidents';
import IncidentDetail from './pages/Dashboard/IncidentDetail';
import Escalations from './pages/Dashboard/Escalations';
import Users from './pages/Dashboard/Users';
import Audit from './pages/Dashboard/Audit';

function App() {
    return (
        <AuthProvider>
            <Routes>
                <Route path="/" element={<Layout />}>
                    <Route index element={<Home />} />
                    <Route path="report" element={<Report />} />
                    <Route path="login" element={<Login />} />
                    <Route path="register" element={<Register />} />

                    {/* Dashboard Routes - Protected for Analysts/Admins */}
                    <Route path="dashboard" element={
                        <ProtectedRoute roles={['ANALYST', 'ADMIN']}>
                            <DashboardLayout />
                        </ProtectedRoute>
                    }>
                        <Route index element={<DashboardOverview />} />
                        <Route path="incidents" element={<Incidents />} />
                        <Route path="incidents/:id" element={<IncidentDetail />} />
                        <Route path="escalations" element={<Escalations />} />
                        <Route path="users" element={<Users />} />
                        <Route path="audit" element={<Audit />} />
                    </Route>
                </Route>
            </Routes>
        </AuthProvider>
    )
}

export default App;
