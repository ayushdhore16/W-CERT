import { useState, useEffect } from 'react';
import { Eye, ShieldAlert, MoreVertical, Loader2, Filter, ChevronDown, ChevronUp } from 'lucide-react';
import { Link } from 'react-router-dom';
import api from '../../api/axios';

const Incidents = () => {
    const [incidents, setIncidents] = useState([]);
    const [sortBy, setSortBy] = useState('date'); // 'date' or 'severity'
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchIncidents = async () => {
            try {
                const res = await api.get('/incidents');
                setIncidents(res.data.incidents || []);
            } catch (err) {
                console.error("Failed to fetch incidents", err);
                setError("Failed to load incidents");
            } finally {
                setLoading(false);
            }
        };

        fetchIncidents();
    }, []);

    const getSeverityScore = (sev) => {
        switch (sev) {
            case 'CRITICAL': return 4;
            case 'HIGH': return 3;
            case 'MEDIUM': return 2;
            case 'LOW': return 1;
            default: return 0;
        }
    };

    const sortedIncidents = [...incidents].sort((a, b) => {
        if (sortBy === 'severity') {
            const scoreA = getSeverityScore(a.severity);
            const scoreB = getSeverityScore(b.severity);
            if (scoreA !== scoreB) return scoreB - scoreA;
            // Fallback to date if severity is same
            return new Date(b.created_at || 0) - new Date(a.created_at || 0);
        } else {
            // Default: Data (Newest first)
            const dateA = new Date(a.created_at || 0);
            const dateB = new Date(b.created_at || 0);
            return dateB - dateA;
        }
    });

    const formatDate = (dateStr) => {
        if (!dateStr || dateStr === 'NULL' || dateStr === '') return 'N/A';
        const d = new Date(dateStr);
        return isNaN(d.getTime()) ? 'N/A' : d.toLocaleDateString();
    };

    const getSeverityColor = (sev) => {
        switch (sev) {
            case 'CRITICAL': return 'text-alert-red font-bold animate-pulse';
            case 'HIGH': return 'text-orange-500 font-bold';
            case 'MEDIUM': return 'text-yellow-400';
            default: return 'text-gray-300';
        }
    };

    if (loading) return <div className="p-10 text-center text-cyber-blue"><Loader2 className="w-10 h-10 animate-spin mx-auto" /> Loading Incidents...</div>;
    if (error) return <div className="p-10 text-center text-alert-red">{error}</div>;

    return (
        <div className="space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <h1 className="text-2xl font-bold text-white font-mono tracking-tight uppercase">
                    Incident Management
                </h1>

                <div className="flex items-center gap-3 bg-white/5 p-1 rounded-lg border border-white/10">
                    <span className="text-[10px] text-gray-500 font-bold uppercase pl-3 flex items-center gap-2">
                        <Filter className="w-3 h-3" /> Sort By
                    </span>
                    <select
                        value={sortBy}
                        onChange={(e) => setSortBy(e.target.value)}
                        className="bg-black/40 text-cyber-blue text-xs font-mono font-bold px-3 py-1.5 rounded outline-none border-l border-white/10 hover:text-white transition-colors cursor-pointer"
                    >
                        <option value="date">NEWEST FIRST</option>
                        <option value="severity">HIGHEST SEVERITY</option>
                    </select>
                </div>
            </div>

            <div className="cyber-card overflow-hidden p-0">
                {sortedIncidents.length === 0 ? (
                    <div className="p-10 text-center text-gray-500">No active incidents found.</div>
                ) : (
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="bg-cyber-black/50 border-b border-white/10 text-xs uppercase text-gray-500 tracking-wider">
                                <th className="p-4 font-mono">ID</th>
                                <th className="p-4 font-mono">Threat Type</th>
                                <th className="p-4 font-mono">Severity</th>
                                <th className="p-4 font-mono">Authenticity</th>
                                <th className="p-4 font-mono">Status</th>
                                <th className="p-4 font-mono">Date</th>
                                <th className="p-4 font-mono text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5 text-sm">
                            {sortedIncidents.map((inc) => (
                                <tr key={inc.incident_id} className="hover:bg-white/5 transition-colors group">
                                    <td className="p-4 font-mono text-cyber-blue">{inc.incident_id}</td>
                                    <td className="p-4 font-medium text-white group-hover:text-cyber-blue transition-colors">
                                        {inc.attack_type?.replace(/_/g, ' ')}
                                    </td>
                                    <td className={`p-4 ${getSeverityColor(inc.severity)}`}>{inc.severity}</td>
                                    <td className="p-4">
                                        <span className={`px-2 py-1 rounded text-[10px] font-bold border uppercase tracking-tighter ${inc.authenticity_status === 'HIGHLY_AUTHENTIC' ? 'bg-green-500/10 text-green-500 border-green-500/30' :
                                            inc.authenticity_status === 'LOW_AUTHENTICITY' ? 'bg-alert-red/10 text-alert-red border-alert-red/30' :
                                                'bg-yellow-500/10 text-yellow-500 border-yellow-500/30'
                                            }`}>
                                            {inc.authenticity_status?.replace(/_/g, ' ')} ({inc.authenticity_score}%)
                                        </span>
                                    </td>
                                    <td className="p-4">
                                        <span className="px-2 py-1 rounded text-[10px] bg-white/5 text-gray-400 border border-white/10 uppercase font-mono group-hover:border-white/20">
                                            {inc.status}
                                        </span>
                                    </td>
                                    <td className="p-4 text-gray-400 font-mono text-xs">{formatDate(inc.created_at)}</td>
                                    <td className="p-4 text-right">
                                        <Link to={`/dashboard/incidents/${inc.incident_id}`} className="inline-flex items-center text-cyber-blue hover:text-white transition-colors bg-cyber-blue/5 px-3 py-1.5 rounded hover:bg-cyber-blue/20">
                                            <Eye className="w-4 h-4 mr-2" /> View
                                        </Link>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
};

export default Incidents;
