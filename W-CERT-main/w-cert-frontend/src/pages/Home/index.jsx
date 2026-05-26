import { useState } from 'react';
import { Shield, Lock, Activity, EyeOff, FileText, AlertTriangle, ArrowRight, LayoutDashboard, Search, Loader2, CheckCircle, Clock } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import CyberButton from '../../components/UI/CyberButton';
import { useAuth } from '../../hooks/useAuth';
import api from '../../api/axios';

const Home = () => {
    const { user } = useAuth();
    const isStaff = user && (user.role === 'ANALYST' || user.role === 'ADMIN');

    // Status Check State
    const [searchId, setSearchId] = useState('');
    const [statusResult, setStatusResult] = useState(null);
    const [statusLoading, setStatusLoading] = useState(false);
    const [statusError, setStatusError] = useState('');

    const handleCheckStatus = async (e) => {
        e.preventDefault();
        if (!searchId.trim()) return;

        setStatusLoading(true);
        setStatusError('');
        setStatusResult(null);

        try {
            const res = await api.get(`/status/${searchId.trim().toUpperCase()}`);
            setStatusResult(res.data.incident);
        } catch (err) {
            setStatusError(err.response?.data?.error || "Incident ID not found in secure records.");
        } finally {
            setStatusLoading(false);
        }
    };

    return (
        <div className="relative">

            {/* Hero Section */}
            <section className="min-h-[85vh] flex flex-col items-center justify-center text-center relative z-10 px-4">

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                    className="mb-6 inline-flex items-center px-4 py-2 rounded-full bg-cyber-blue/10 border border-cyber-blue/30 text-cyber-blue text-sm font-mono tracking-widest"
                >
                    <span className="relative flex h-2 w-2 mr-3">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyber-blue opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-cyber-blue"></span>
                    </span>
                    SECURE & ENCRYPTED REPORTING CHANNEL
                </motion.div>

                <motion.h1
                    className="text-6xl md:text-8xl font-black mb-6 tracking-tighter text-transparent bg-clip-text bg-gradient-to-b from-white to-gray-500 drop-shadow-[0_0_15px_rgba(255,255,255,0.3)]"
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.8, delay: 0.2 }}
                >
                    W-CERT
                </motion.h1>

                <motion.p
                    className="text-xl md:text-2xl text-gray-400 max-w-2xl mb-10 font-light"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.8, delay: 0.4 }}
                >
                    Women-Centric Cyber Emergency Response Team.
                    <br />
                    <span className="text-cyber-blue/80 font-mono text-lg mt-2 block uppercase tracking-widest">Detect. Defend. Empower.</span>
                </motion.p>

                <motion.div
                    className="flex flex-col sm:flex-row gap-6 mb-16"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.6 }}
                >
                    <CyberButton to="/report" variant="danger" className="text-lg px-12 py-4">
                        <AlertTriangle className="w-5 h-5 mr-2" /> Report Incident
                    </CyberButton>

                    {isStaff ? (
                        <CyberButton to="/dashboard" variant="primary" className="text-lg px-8 py-4">
                            <LayoutDashboard className="w-5 h-5 mr-2" /> Go to Dashboard
                        </CyberButton>
                    ) : (
                        <div className="flex items-center text-gray-400 font-mono text-xs uppercase tracking-[0.2em] border border-white/5 bg-white/5 px-8 py-4 rounded-lg">
                            <Shield className="w-4 h-4 mr-2 text-cyber-blue animate-pulse" /> Victim Protection Active
                        </div>
                    )}
                </motion.div>

                {/* Status Check Section */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 1 }}
                    className="w-full max-w-md bg-black/40 backdrop-blur-md p-6 rounded-xl border border-white/10 shadow-2xl"
                >
                    <h3 className="text-white font-mono text-sm mb-4 uppercase tracking-widest flex items-center justify-center gap-2">
                        <Search className="w-4 h-4 text-cyber-blue" /> Check Incident Progress
                    </h3>

                    <form onSubmit={handleCheckStatus} className="flex gap-2 mb-4">
                        <input
                            type="text"
                            placeholder="Enter Incident ID (e.g. 4A8B2C)"
                            className="cyber-input text-center py-2 text-sm uppercase"
                            value={searchId}
                            onChange={(e) => setSearchId(e.target.value)}
                        />
                        <button
                            type="submit"
                            disabled={statusLoading}
                            className="bg-cyber-blue hover:bg-cyber-blue/80 text-black px-4 py-2 rounded font-bold transition-all disabled:opacity-50"
                        >
                            {statusLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'GO'}
                        </button>
                    </form>

                    <AnimatePresence>
                        {statusError && (
                            <motion.div
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: 'auto' }}
                                exit={{ opacity: 0, height: 0 }}
                                className="text-alert-red text-xs font-mono"
                            >
                                {statusError}
                            </motion.div>
                        )}

                        {statusResult && (
                            <motion.div
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: 'auto' }}
                                exit={{ opacity: 0, height: 0 }}
                                className="mt-4 p-4 bg-white/5 rounded border border-white/10 text-left"
                            >
                                <div className="flex justify-between items-start mb-2">
                                    <span className="text-[10px] text-gray-500 font-mono uppercase">Current Status</span>
                                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${statusResult.status === 'CLOSED' ? 'bg-gray-500/20 text-gray-400 border-gray-500/30' :
                                            statusResult.status === 'ESCALATED' ? 'bg-alert-red/20 text-alert-red border-alert-red/30' :
                                                'bg-cyber-blue/20 text-cyber-blue border-cyber-blue/30'
                                        }`}>
                                        {statusResult.status}
                                    </span>
                                </div>
                                <div className="flex items-center gap-2 text-white font-mono text-xs">
                                    {statusResult.status === 'OPEN' ? <Clock className="w-3 h-3 text-yellow-500" /> : <CheckCircle className="w-3 h-3 text-green-500" />}
                                    Inc-ID {statusResult.incident_id}
                                </div>
                                <div className="text-[9px] text-gray-600 mt-2 font-mono italic">
                                    Last Updated: {statusResult.updated_at}
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </motion.div>

            </section>

            {/* Grid Features */}
            <section className="grid grid-cols-1 md:grid-cols-3 gap-8 pb-20 px-4">
                <FeatureCard
                    icon={<EyeOff className="w-8 h-8 text-cyber-blue" />}
                    title="Anonymous Reporting"
                    desc="Submit incidents without revealing your identity. Encrypted storage ensures your privacy is never compromised."
                />
                <FeatureCard
                    icon={<Shield className="w-8 h-8 text-cyber-blue" />}
                    title="Professional Support"
                    desc="Our certified analysts investigate every report with sensitivity and provide direct guidance for recovery."
                />
                <FeatureCard
                    icon={<Lock className="w-8 h-8 text-cyber-blue" />}
                    title="Legal Admissibility"
                    desc="Evidence files are hashed (SHA-256) and stored with a strict chain of custody for official police reporting."
                />
            </section>

        </div>
    );
};

const FeatureCard = ({ icon, title, desc }) => (
    <motion.div
        whileHover={{ scale: 1.02 }}
        className="bg-cyber-gray/50 border border-white/5 p-8 rounded-xl backdrop-blur-sm hover:border-cyber-blue/30 transition-all group"
    >
        <div className="mb-4 p-4 bg-cyber-black rounded-lg inline-block border border-white/10 group-hover:border-cyber-blue/50 group-hover:shadow-[0_0_15px_rgba(0,240,255,0.2)] transition-all">
            {icon}
        </div>
        <h3 className="text-xl font-bold text-white mb-3 font-mono">{title}</h3>
        <p className="text-gray-400 leading-relaxed">{desc}</p>
    </motion.div>
);

export default Home;
