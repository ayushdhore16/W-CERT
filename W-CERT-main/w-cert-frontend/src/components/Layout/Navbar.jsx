import { Link, useLocation } from 'react-router-dom';
import { Shield, LayoutDashboard, FileText, Menu, X, LogIn, UserPlus, LogOut, User } from 'lucide-react';
import { useState } from 'react';
import { useAuth } from '../../hooks/useAuth';

const Navbar = () => {
    const [isOpen, setIsOpen] = useState(false);
    const { user, logout } = useAuth();
    const location = useLocation();

    // Highlight active link
    const isActive = (path) => location.pathname === path ? "text-cyber-blue border-b-2 border-cyber-blue" : "text-gray-400 hover:text-white";

    const isStaff = user && (user.role === 'ANALYST' || user.role === 'ADMIN');

    return (
        <nav className="fixed w-full z-50 bg-cyber-black/90 backdrop-blur-lg border-b border-white/10">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    <div className="flex items-center">
                        <Link to="/" className="flex-shrink-0 flex items-center gap-2 group">
                            <Shield className="h-8 w-8 text-cyber-blue group-hover:shadow-neon transition-all" />
                            <span className="font-mono font-bold text-xl tracking-wider text-white">W-CERT</span>
                        </Link>
                    </div>

                    <div className="hidden md:block">
                        <div className="ml-10 flex items-baseline space-x-8">
                            <Link to="/" className={`${isActive('/')} px-3 py-2 rounded-md text-sm font-medium transition-all`}>Home</Link>
                            <Link to="/report" className={`${isActive('/report')} px-3 py-2 rounded-md text-sm font-medium transition-all`}>Report Incident</Link>

                            {isStaff && (
                                <Link to="/dashboard" className={`${isActive('/dashboard')} px-3 py-2 rounded-md text-sm font-medium transition-all`}>
                                    Dashboard
                                </Link>
                            )}

                            {!user ? (
                                <>
                                    <Link to="/login" className="flex items-center gap-2 text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium">
                                        <LogIn className="w-4 h-4" /> Login
                                    </Link>
                                    <Link to="/register" className="cyber-button text-xs py-1 px-4">
                                        Register
                                    </Link>
                                </>
                            ) : (
                                <div className="flex items-center gap-6 ml-4 border-l border-white/10 pl-6">
                                    <div className="flex flex-col items-end">
                                        <span className="text-white text-sm font-medium font-mono">{user.display_name}</span>
                                        <span className="text-cyber-blue text-[10px] font-bold uppercase tracking-widest">{user.role}</span>
                                    </div>
                                    <button
                                        onClick={logout}
                                        className="text-gray-400 hover:text-alert-red transition-colors group"
                                        title="Logout"
                                    >
                                        <LogOut className="w-5 h-5 group-hover:drop-shadow-[0_0_8px_rgba(255,0,60,0.5)]" />
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="-mr-2 flex md:hidden">
                        <button
                            onClick={() => setIsOpen(!isOpen)}
                            className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-white hover:bg-gray-700 focus:outline-none"
                        >
                            {isOpen ? <X className="block h-6 w-6" /> : <Menu className="block h-6 w-6" />}
                        </button>
                    </div>
                </div>
            </div>

            {/* Mobile menu */}
            {isOpen && (
                <div className="md:hidden bg-cyber-gray border-b border-white/10">
                    <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
                        <Link to="/" className="block px-3 py-2 rounded-md text-base font-medium text-white hover:bg-white/5">Home</Link>
                        <Link to="/report" className="block px-3 py-2 rounded-md text-base font-medium text-white hover:bg-white/5">Report Incident</Link>

                        {isStaff && (
                            <Link to="/dashboard" className="block px-3 py-2 rounded-md text-base font-medium text-white hover:bg-white/5">Dashboard</Link>
                        )}

                        {!user ? (
                            <>
                                <Link to="/login" className="block px-3 py-2 rounded-md text-base font-medium text-gray-400 hover:text-white">Login</Link>
                                <Link to="/register" className="block px-3 py-2 rounded-md text-base font-medium text-cyber-blue">Register</Link>
                            </>
                        ) : (
                            <div className="border-t border-white/5 mt-2 pt-2 px-3 pb-3">
                                <div className="flex items-center gap-3 mb-3">
                                    <div className="w-8 h-8 rounded-full bg-cyber-blue/10 flex items-center justify-center text-cyber-blue">
                                        <User className="w-4 h-4" />
                                    </div>
                                    <div>
                                        <div className="text-white text-sm font-bold">{user.display_name}</div>
                                        <div className="text-cyber-blue text-[10px] font-bold uppercase">{user.role}</div>
                                    </div>
                                </div>
                                <button
                                    onClick={logout}
                                    className="w-full text-left flex items-center gap-2 px-3 py-2 rounded-md text-base font-medium text-alert-red hover:bg-alert-red/10"
                                >
                                    <LogOut className="w-4 h-4" /> Logout
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </nav>
    );
};

export default Navbar;
