import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';

const Layout = () => {
    return (
        <div className="min-h-screen bg-cyber-black text-white relative overflow-x-hidden">
            {/* Background Grid Effect */}
            <div className="absolute inset-0 z-0 opacity-10 pointer-events-none"
                style={{
                    backgroundImage: 'linear-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.05) 1px, transparent 1px)',
                    backgroundSize: '30px 30px'
                }}>
            </div>

            {/* Glow Orbs */}
            <div className="absolute top-0 left-0 w-96 h-96 bg-cyber-blue/20 rounded-full blur-[100px] -translate-x-1/2 -translate-y-1/2 pointer-events-none"></div>
            <div className="absolute bottom-0 right-0 w-96 h-96 bg-purple-500/10 rounded-full blur-[100px] translate-x-1/2 translate-y-1/2 pointer-events-none"></div>

            <Navbar />

            <main className="relative z-10 pt-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
                <Outlet />
            </main>

            <footer className="relative z-10 mt-20 border-t border-white/10 py-8 text-center text-gray-500 text-sm">
                <p>© {new Date().getFullYear()} W-CERT. Secure & Anonymous.</p>
            </footer>
        </div>
    );
};

export default Layout;
