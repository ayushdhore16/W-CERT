import { useState, useEffect } from 'react';
import { BookOpen, Search, Filter, Loader2, Terminal, ShieldAlert } from 'lucide-react';
import api from '../../api/axios';

const Audit = () => {
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchLogs = async () => {
            try {
                const res = await api.get('/admin/audit-logs');
                setLogs(res.data.logs);
            } catch (err) {
                console.error("Failed to fetch audit logs", err);
                setError("Clearance Level Insufficient: Admin access required.");
            } finally {
                setLoading(false);
            }
        };
        fetchLogs();
    }, []);

    if (loading) return <div className="p-10 text-center text-cyber-blue"><Loader2 className="w-10 h-10 animate-spin mx-auto" /> Syncing Audit Stream...</div>;
    if (error) return <div className="p-10 text-center text-alert-red flex flex-col items-center gap-4">
        <ShieldAlert className="w-12 h-12" />
        {error}
    </div>;

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white font-mono flex items-center gap-3">
                        <Terminal className="text-cyber-blue" /> System Audit Trail
                    </h1>
                    <p className="text-xs text-gray-500 font-mono mt-1">REAL-TIME TAMPER-EVIDENT RECORDING ACTIVE</p>
                </div>
                <div className="flex gap-2">
                    <div className="px-3 py-1 bg-white/5 border border-white/5 rounded text-[10px] font-mono text-gray-500 uppercase">
                        {logs.length} Events Captured
                    </div>
                </div>
            </div>

            <div className="cyber-card font-mono text-[11px] h-[calc(100vh-220px)] overflow-y-auto custom-scrollbar bg-black/40 border-white/10 p-0">
                <div className="sticky top-0 bg-cyber-black border-b border-white/10 flex gap-4 py-2 px-6 text-gray-500 font-bold uppercase tracking-widest z-10">
                    <div className="w-40 shrink-0">Timestamp</div>
                    <div className="w-32 shrink-0">Action</div>
                    <div className="w-24 shrink-0">Identity</div>
                    <div>Event Details</div>
                </div>

                <div className="p-0">
                    {logs.map((log, idx) => (
                        <div key={idx} className="flex gap-4 py-3 px-6 border-b border-white/5 hover:bg-cyber-blue/5 transition-all group">
                            <div className="text-gray-500 w-40 shrink-0 font-mono whitespace-nowrap">{log.timestamp}</div>
                            <div className={`w-32 shrink-0 font-bold tracking-tight ${log.action.includes('ESCALATION') || log.action.includes('ERROR') ? 'text-alert-red' :
                                log.action.includes('LOGIN') || log.action.includes('SUCCESS') ? 'text-green-400' :
                                    'text-cyber-blue'
                                }`}>
                                [{log.action}]
                            </div>
                            <div className="text-gray-400 w-24 shrink-0 truncate font-bold text-white/50">{log.user_id}</div>
                            <div className="text-gray-300 italic group-hover:not-italic group-hover:text-white transition-all">
                                {log.details}
                                {log.resource_type && (
                                    <span className="ml-2 text-[9px] px-1 bg-white/5 rounded border border-white/10 text-gray-600">
                                        TARGET: {log.resource_type}@{log.resource_id}
                                    </span>
                                )}
                            </div>
                        </div>
                    ))}
                    <div className="py-8 text-center text-gray-700 font-mono text-[10px] uppercase tracking-[0.5em] bg-white/[0.02]">
                        -- End of Encrypted Audit Stream --
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Audit;
