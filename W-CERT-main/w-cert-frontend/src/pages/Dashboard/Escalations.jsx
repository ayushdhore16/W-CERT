import { useState, useEffect } from 'react';
import { AlertTriangle, ExternalLink, ShieldAlert, Loader2 } from 'lucide-react';
import api from '../../api/axios';

const Escalations = () => {
    const [escalations, setEscalations] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchEscalations = async () => {
            try {
                // Ensure backend has this route, otherwise this will fail gracefully
                const res = await api.get('/escalations');
                setEscalations(res.data.escalations || []);
            } catch (err) {
                console.error("Failed to load escalations", err);
                // Fallback for demo if route is restricted or fails
                setError("Authorized personnel only. Contact Admin for access.");
            } finally {
                setLoading(false);
            }
        };
        fetchEscalations();
    }, []);

    if (loading) return <div className="p-10 text-center text-cyber-blue"><Loader2 className="w-10 h-10 animate-spin mx-auto" /> Loading Escalations...</div>;

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-white font-mono">Escalation Protocol</h1>
                <div className="text-sm text-alert-red font-mono flex items-center gap-2">
                    <ShieldAlert className="w-4 h-4" /> LEVEL 3 ACCESS
                </div>
            </div>

            {error ? (
                <div className="cyber-card border-alert-red/50 bg-alert-red/5 text-center py-10">
                    <AlertTriangle className="w-12 h-12 text-alert-red mx-auto mb-4" />
                    <h3 className="text-xl font-bold text-white">Access Restricted</h3>
                    <p className="text-alert-red mt-2">{error}</p>
                </div>
            ) : (
                <div className="cyber-card overflow-hidden p-0">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="bg-cyber-black/50 border-b border-white/10 text-xs uppercase text-gray-500 tracking-wider">
                                <th className="p-4 font-mono">Escalation ID</th>
                                <th className="p-4 font-mono">Incident ID</th>
                                <th className="p-4 font-mono">Location</th>
                                <th className="p-4 font-mono">Target Authority</th>
                                <th className="p-4 font-mono">Reason</th>
                                <th className="p-4 font-mono">Status</th>
                                <th className="p-4 font-mono">Date</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5 text-sm">
                            {escalations.length === 0 ? (
                                <tr>
                                    <td colSpan="7" className="p-8 text-center text-gray-500">No active escalations.</td>
                                </tr>
                            ) : (
                                escalations.map((esc) => (
                                    <tr key={esc.escalation_id} className="hover:bg-white/5 transition-colors">
                                        <td className="p-4 font-mono text-cyber-blue">{esc.escalation_id}</td>
                                        <td className="p-4 font-mono text-gray-300">{esc.incident_id}</td>
                                        <td className="p-4 font-mono text-cyber-blue">{esc.location || 'Unknown'}</td>
                                        <td className="p-4 font-bold text-white flex items-center gap-2">
                                            {esc.target_info?.name || esc.escalated_to}
                                            <ExternalLink className="w-3 h-3 text-gray-500" />
                                        </td>
                                        <td className="p-4 text-gray-400">{esc.reason}</td>
                                        <td className="p-4">
                                            <span className="px-2 py-1 rounded text-xs bg-alert-red/10 text-alert-red border border-alert-red/20 animate-pulse">
                                                {esc.status}
                                            </span>
                                        </td>
                                        <td className="p-4 text-gray-500">{new Date(esc.created_at).toLocaleDateString()}</td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};

export default Escalations;
