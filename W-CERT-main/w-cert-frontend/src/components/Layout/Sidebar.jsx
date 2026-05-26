import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, FileText, AlertTriangle, Users, BookOpen, LogOut } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const Sidebar = () => {
    const location = useLocation();
    const { logout } = useAuth();

    const isActive = (path) => location.pathname === path ? "bg-cyber-blue/10 text-cyber-blue border-r-2 border-cyber-blue" : "text-gray-400 hover:text-white hover:bg-white/5";

    return (
        <div className="hidden md:flex flex-col w-64 bg-cyber-gray/50 border-r border-white/5 min-h-[calc(100vh-64px)] fixed left-0 top-16">
            <div className="flex-1 py-6 space-y-2">

                <div className="px-6 mb-6">
                    <h3 className="text-xs font-mono text-gray-500 uppercase tracking-widest">Analyst Console</h3>
                </div>

                <Link to="/dashboard" className={`flex items-center px-6 py-3 text-sm font-medium transition-colors ${isActive('/dashboard')}`}>
                    <LayoutDashboard className="w-5 h-5 mr-3" />
                    Overview
                </Link>

                <Link to="/dashboard/incidents" className={`flex items-center px-6 py-3 text-sm font-medium transition-colors ${isActive('/dashboard/incidents')}`}>
                    <FileText className="w-5 h-5 mr-3" />
                    Incidents
                </Link>

                <Link to="/dashboard/escalations" className={`flex items-center px-6 py-3 text-sm font-medium transition-colors ${isActive('/dashboard/escalations')}`}>
                    <AlertTriangle className="w-5 h-5 mr-3" />
                    Escalations
                </Link>

                <div className="px-6 mt-8 mb-2">
                    <h3 className="text-xs font-mono text-gray-500 uppercase tracking-widest">System</h3>
                </div>

                <Link to="/dashboard/users" className={`flex items-center px-6 py-3 text-sm font-medium transition-colors ${isActive('/dashboard/users')}`}>
                    <Users className="w-5 h-5 mr-3" />
                    User Management
                </Link>

                <Link to="/dashboard/audit" className={`flex items-center px-6 py-3 text-sm font-medium transition-colors ${isActive('/dashboard/audit')}`}>
                    <BookOpen className="w-5 h-5 mr-3" />
                    Audit Logs
                </Link>

            </div>

            <div className="p-4 border-t border-white/5">
                <button onClick={logout} className="flex items-center w-full px-4 py-2 text-sm text-alert-red hover:bg-alert-red/10 rounded transition-colors">
                    <LogOut className="w-4 h-4 mr-2" />
                    Sign Out
                </button>
            </div>
        </div>
    );
};

export default Sidebar;
