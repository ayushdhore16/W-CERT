import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Shield, FileText, Download, User, Calendar, Activity, Loader2, Flag, AlertTriangle, Printer, Scale, AlertCircle, TrendingUp, ShieldAlert } from 'lucide-react';
import CyberButton from '../../components/UI/CyberButton';
import api from '../../api/axios';

const IncidentDetail = () => {
    const { id } = useParams();
    const [incident, setIncident] = useState(null);
    const [evidenceList, setEvidenceList] = useState([]);
    const [similarCases, setSimilarCases] = useState([]);
    const [escalationData, setEscalationData] = useState({ targets: null, stateAuthorities: null });
    const [showEscalateModal, setShowEscalateModal] = useState(false);
    const [loading, setLoading] = useState(true);
    const [updating, setUpdating] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchData = async () => {
            try {
                const incRes = await api.get(`/incidents/${id}`);
                const inc = incRes.data.incident;

                // Parse score_breakdown if stored as string (Sheets serialisation)
                if (inc.score_breakdown && typeof inc.score_breakdown === 'string') {
                    try {
                        inc.score_breakdown = JSON.parse(
                            inc.score_breakdown.replace(/'/g, '"')
                        );
                    } catch { inc.score_breakdown = {}; }
                }
                setIncident(inc);

                const evRes = await api.get(`/incidents/${id}/evidence`);
                setEvidenceList(evRes.data.evidence || []);

                try {
                    const simRes = await api.get(`/incidents/${id}/similar`);
                    setSimilarCases(simRes.data.similar_cases || []);
                } catch (err) {
                    console.log("No similar cases found or RAG disabled.");
                }

                try {
                    const escRes = await api.get('/escalation-targets');
                    setEscalationData({
                        targets: escRes.data.targets,
                        stateAuthorities: escRes.data.state_authorities
                    });
                } catch (err) {
                    console.log("Failed to load escalation targets");
                }

            } catch (err) {
                console.error("Failed to load incident detail", err);
                setError("Failed to load incident details. Incident might not exist or access denied.");
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [id]);

    const handleUpdateStatus = async (newStatus) => {
        setUpdating(true);
        try {
            await api.patch(`/incidents/${id}/status`, { status: newStatus });
            setIncident({ ...incident, status: newStatus });
        } catch (err) {
            alert("Failed to update status: " + (err.response?.data?.error || "Unknown error"));
        } finally {
            setUpdating(false);
        }
    };

    const triggerEscalationModal = () => {
        setShowEscalateModal(true);
    };

    const confirmEscalation = async () => {
        setUpdating(true);
        setShowEscalateModal(false);
        
        let targetName = null;
        if (incident.state_location && escalationData.stateAuthorities?.[incident.state_location]) {
            targetName = escalationData.stateAuthorities[incident.state_location].cyber_cell.name;
        }
        
        try {
            const res = await api.post(`/incidents/${id}/escalate`, {
                escalate_to: "CYBER_CRIME_CELL",
                target_name: targetName,
                reason: `Manual escalation by analyst. Severity: ${incident.severity}`
            });
            alert(res.data.message);
            setIncident({ ...incident, status: 'ESCALATED' });
        } catch (err) {
            alert("Escalation failed: " + (err.response?.data?.error || "Unknown error"));
        } finally {
            setUpdating(false);
        }
    };

    const handlePrintDocket = async () => {
        try {
            const res = await api.get(`/incidents/${id}/docket`, {
                responseType: 'blob',
                headers: { 'Accept': 'text/html' }
            });
            const blob = new Blob([res.data], { type: 'text/html' });
            const url = URL.createObjectURL(blob);
            const win = window.open(url, '_blank');
            if (win) win.focus();
        } catch (err) {
            alert('Failed to generate docket: ' + (err.response?.data?.error || err.message));
        }
    };

    const handleDownload = async (evidenceId, originalName) => {
        try {
            const res = await api.get(`/evidence/${evidenceId}/download`, {
                responseType: 'blob'
            });
            const url = window.URL.createObjectURL(new Blob([res.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', originalName);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (err) {
            alert("Download failed");
        }
    };

    if (loading) return <div className="p-10 text-center text-cyber-blue"><Loader2 className="w-10 h-10 animate-spin mx-auto" /> Loading Detail...</div>;
    if (error) return <div className="p-10 text-center text-alert-red">{error}</div>;
    if (!incident) return <div className="p-10 text-center">Incident not found</div>;

    const score = parseInt(incident.threat_score) || 0;

    // Fix for older incidents that lack a score breakdown (or fallback engine hits)
    let breakdown = incident.score_breakdown || {};
    if (Object.keys(breakdown).length === 0 && score > 0) {
        breakdown = {
            evidence_match: Math.round(score * 0.4),
            threat_indicators: Math.round(score * 0.3),
            urgency_signals: Math.round(score * 0.2),
            victim_vulnerability: Math.round(score * 0.1)
        };
    }

    return (
        <div className="space-y-6">

            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex items-center space-x-4">
                    <Link to="/dashboard/incidents" className="text-gray-400 hover:text-white transition-colors">
                        <ArrowLeft className="w-6 h-6" />
                    </Link>
                    <div>
                        <h1 className="text-2xl font-bold text-white font-mono flex items-center gap-3">
                            {incident.incident_id}
                            <span className={`text-sm px-3 py-1 rounded border ${incident.severity === 'CRITICAL' ? 'bg-alert-red/20 text-alert-red border-alert-red/50' :
                                incident.severity === 'HIGH' ? 'bg-orange-500/20 text-orange-500 border-orange-500' :
                                    'bg-green-500/20 text-green-500 border-green-500'
                                }`}>
                                {incident.severity}
                            </span>
                        </h1>
                        <p className="text-gray-500 text-sm mt-1 flex flex-wrap items-center gap-4">
                            <span className="flex items-center gap-1"><Calendar className="w-3 h-3" /> {incident.created_at}</span>
                            <span className="flex items-center gap-1 italic text-cyber-blue uppercase font-bold tracking-widest text-[10px]">
                                {incident.attack_type.replace('_', ' ')}
                            </span>
                            <span className="flex items-center gap-1 font-mono text-xs px-2 py-0.5 bg-white/5 rounded">
                                <Activity className="w-3 h-3" /> {incident.status}
                            </span>
                        </p>
                    </div>
                </div>

                <div className="flex flex-wrap gap-3">
                    {incident.status === 'OPEN' && (
                        <CyberButton
                            variant="default"
                            className="bg-yellow-500/10 text-yellow-500 border-yellow-500 hover:bg-yellow-500 hover:text-black"
                            onClick={() => handleUpdateStatus('INVESTIGATING')}
                            isLoading={updating}
                        >
                            <Flag className="w-4 h-4 mr-2" /> Start Investigation
                        </CyberButton>
                    )}

                    {incident.status !== 'ESCALATED' && incident.status !== 'CLOSED' && (
                        <CyberButton variant="danger" onClick={triggerEscalationModal} isLoading={updating}>
                            <AlertTriangle className="w-4 h-4 mr-2" /> Escalate to Authorities
                        </CyberButton>
                    )}

                    <CyberButton
                        variant="default"
                        className="bg-purple-500/10 text-purple-400 border-purple-500/50 hover:bg-purple-500 hover:text-white"
                        onClick={handlePrintDocket}
                    >
                        <Printer className="w-4 h-4 mr-2" /> Print Docket
                    </CyberButton>

                    {incident.status !== 'CLOSED' && (
                        <button
                            className="bg-white/5 hover:bg-white/10 text-white px-4 py2 rounded text-sm transition-colors border border-white/10"
                            onClick={() => handleUpdateStatus('CLOSED')}
                            disabled={updating}
                        >
                            Close Case
                        </button>
                    )}
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                {/* Main Content */}
                <div className="lg:col-span-2 space-y-6">

                    {/* Description Card */}
                    <div className="cyber-card">
                        <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                            <FileText className="w-5 h-5 text-cyber-blue" /> Original Statement
                        </h3>
                        <p className="text-gray-300 leading-relaxed whitespace-pre-wrap bg-black/20 p-6 rounded border border-white/5 font-mono text-sm">
                            {incident.description}
                        </p>
                    </div>

                    {/* Evidence Card */}
                    <div className="cyber-card">
                        <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                            Physical/Digital Evidence
                        </h3>
                        {evidenceList.length === 0 ? (
                            <div className="text-gray-500 italic py-4 text-center border-2 border-dashed border-white/5 rounded">
                                No evidence files uploaded by reporter.
                            </div>
                        ) : (
                            <div className="space-y-3">
                                {evidenceList.map((file, idx) => (
                                    <div key={idx} className="flex items-center justify-between p-4 bg-black/40 rounded border border-white/5 hover:border-cyber-blue/30 transition-all group">
                                        <div className="flex items-center gap-4">
                                            <div className="w-12 h-12 bg-gray-800 rounded flex items-center justify-center text-gray-400 group-hover:bg-cyber-blue/10 group-hover:text-cyber-blue transition-colors">
                                                <FileText className="w-6 h-6" />
                                            </div>
                                            <div>
                                                <div className="text-white font-medium">{file.original_filename}</div>
                                                <div className="text-[10px] font-mono text-gray-500 mt-1 uppercase">
                                                    {file.mime_type} • {Math.round(file.file_size / 1024)} KB
                                                </div>
                                            </div>
                                        </div>
                                        <button
                                            onClick={() => handleDownload(file.evidence_id, file.original_filename)}
                                            className="text-cyber-blue hover:text-white p-2 bg-cyber-blue/5 rounded hover:bg-cyber-blue/20 transition-all"
                                            title="Secure Download"
                                        >
                                            <Download className="w-5 h-5" />
                                        </button>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                </div>

                {/* Sidebar Analysis */}
                <div className="space-y-6">

                    {/* AI Threat Score Card */}
                    <div className="cyber-card border-cyber-blue/50 shadow-[0_0_15px_rgba(0,240,255,0.05)]">
                        <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                            <Shield className="w-5 h-5 text-cyber-blue" /> AI Threat Intelligence
                        </h3>

                        <div className="flex items-center justify-center py-4">
                            <div className="relative w-32 h-32 flex items-center justify-center">
                                <svg className="w-full h-full transform -rotate-90">
                                    <circle cx="64" cy="64" r="60" stroke="#11131a" strokeWidth="8" fill="transparent" />
                                    <circle cx="64" cy="64" r="60"
                                        stroke={incident.severity === 'CRITICAL' ? '#ff003c' : incident.severity === 'HIGH' ? '#f97316' : '#00f0ff'}
                                        strokeWidth="8" fill="transparent" strokeDasharray="377"
                                        strokeDashoffset={377 - (377 * score) / 100}
                                        className="transition-all duration-1000" />
                                </svg>
                                <div className="absolute text-center">
                                    <div className="text-3xl font-bold text-white">{score}</div>
                                    <div className="text-[10px] text-gray-500 font-bold uppercase tracking-widest">Threat</div>
                                </div>
                            </div>
                        </div>

                        {/* Score Breakdown */}
                        <div className="mt-2 space-y-2">
                            <div className="text-[10px] text-gray-500 font-bold uppercase tracking-widest mb-2">Score Breakdown</div>
                            {[{label:'Evidence Match', key:'evidence_match', max:40, color:'#00f0ff'},
                              {label:'Threat Indicators', key:'threat_indicators', max:30, color:'#f97316'},
                              {label:'Urgency Signals', key:'urgency_signals', max:20, color:'#facc15'},
                              {label:'Victim Vulnerability', key:'victim_vulnerability', max:10, color:'#a855f7'}
                            ].map(({label, key, max, color}) => {
                                const val = breakdown?.[key] ?? 0;
                                return (
                                    <div key={key}>
                                        <div className="flex justify-between text-[10px] mb-1">
                                            <span className="text-gray-400">{label}</span>
                                            <span className="font-mono" style={{color}}>{val}/{max}</span>
                                        </div>
                                        <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                                            <div className="h-full rounded-full transition-all duration-700"
                                                style={{width:`${(val/max)*100}%`, background:color}} />
                                        </div>
                                    </div>
                                );
                            })}
                        </div>

                        {/* Victim Risk Level */}
                        <div className="mt-4 pt-4 border-t border-white/5">
                            <div className="text-[10px] text-gray-500 font-bold uppercase tracking-widest mb-2">Victim Risk Level</div>
                            <span className={`text-xs font-bold px-3 py-1 rounded border ${
                                incident.victim_risk_level === 'IMMEDIATE' ? 'bg-red-500/20 text-red-400 border-red-500/50' :
                                incident.victim_risk_level === 'ACTIVE' ? 'bg-orange-500/20 text-orange-400 border-orange-500/50' :
                                incident.victim_risk_level === 'SUBSIDED' ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50' :
                                'bg-gray-500/20 text-gray-400 border-gray-500/50'
                            }`}>{incident.victim_risk_level || 'ACTIVE'}</span>
                        </div>

                        {/* Integrity Hash */}
                        <div className="pt-4 border-t border-white/5 mt-4">
                            <div className="text-[10px] text-gray-500 font-bold uppercase tracking-widest mb-2">Integrity Hash</div>
                            <div className="font-mono text-[10px] text-gray-600 break-all bg-black/40 p-2 rounded">
                                {incident.content_hash}
                            </div>
                        </div>
                    </div>

                    {/* Verification Analysis */}
                    <div className="cyber-card border-yellow-500/30">
                        <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                            <Activity className="w-5 h-5 text-yellow-500" /> Verification Analysis
                        </h3>
                        <div className="space-y-4">
                            <div className="flex items-center justify-between p-3 bg-white/5 rounded">
                                <span className="text-gray-400 text-sm">Authenticity Score</span>
                                <span className={`font-mono font-bold ${
                                    incident.authenticity_score >= 80 ? 'text-green-500' :
                                    incident.authenticity_score < 40 ? 'text-alert-red' : 'text-yellow-500'
                                }`}>{incident.authenticity_score}%</span>
                            </div>

                            <div className="space-y-2">
                                <div className="text-[10px] text-gray-500 font-bold uppercase tracking-widest">AI Forensic Deductions</div>
                                {incident.verification_insights?.length > 0 ? (
                                    incident.verification_insights.map((insight, i) => (
                                        <div key={i} className="flex items-start gap-2 bg-black/40 p-2 rounded border border-white/5 text-xs text-gray-300">
                                            <div className="mt-1 w-1.5 h-1.5 rounded-full bg-yellow-500 shrink-0" />
                                            {insight}
                                        </div>
                                    ))
                                ) : <div className="text-xs text-gray-600 italic">No flags.</div>}
                            </div>

                            {incident.ai_reasoning && (
                                <div className="pt-3 border-t border-white/5">
                                    <div className="text-[10px] text-gray-500 font-bold uppercase tracking-widest mb-2">AI Forensic Reasoning</div>
                                    <div className="text-xs text-gray-400 italic bg-black/20 p-3 rounded border border-white/5 leading-relaxed">
                                        &ldquo;{incident.ai_reasoning}&rdquo;
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* IPC Legal Sections */}
                    {incident.ipc_sections?.length > 0 && (
                        <div className="cyber-card border-purple-500/30">
                            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                                <Scale className="w-5 h-5 text-purple-400" /> Applicable Legal Sections
                            </h3>
                            <div className="space-y-2">
                                {incident.ipc_sections.map((sec, i) => (
                                    <div key={i} className="text-xs bg-purple-500/5 border border-purple-500/20 text-purple-300 px-3 py-2 rounded font-mono">
                                        {sec}
                                    </div>
                                ))}
                            </div>
                            <p className="text-[10px] text-gray-600 mt-3 italic">AI-suggested sections. Confirm with legal counsel.</p>
                        </div>
                    )}

                    {/* Evidence Gaps */}
                    {incident.evidence_gaps?.length > 0 && (
                        <div className="cyber-card border-orange-500/30">
                            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                                <AlertCircle className="w-5 h-5 text-orange-400" /> Evidence Gaps
                            </h3>
                            <div className="space-y-2">
                                {incident.evidence_gaps.map((gap, i) => (
                                    <div key={i} className="flex items-start gap-2 text-xs text-orange-300 bg-orange-500/5 border border-orange-500/20 px-3 py-2 rounded">
                                        <TrendingUp className="w-3 h-3 mt-0.5 shrink-0" />{gap}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Similar Past Cases (RAG) */}
                    {similarCases.length > 0 && (
                        <div className="cyber-card border-green-500/30">
                            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                                <Activity className="w-5 h-5 text-green-400" /> Similar Past Cases
                            </h3>
                            <div className="space-y-3">
                                {similarCases.map((sim, i) => (
                                    <Link key={i} to={`/dashboard/incidents/${sim.incident_id}`} className="block bg-green-500/5 hover:bg-green-500/10 border border-green-500/20 p-3 rounded transition-colors group">
                                        <div className="flex justify-between items-start mb-1">
                                            <div className="text-sm font-bold text-green-300 font-mono group-hover:text-green-400">
                                                ID: {sim.incident_id}
                                            </div>
                                            <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                                                sim.severity === 'CRITICAL' ? 'bg-red-500/20 text-red-400' :
                                                sim.severity === 'HIGH' ? 'bg-orange-500/20 text-orange-400' :
                                                'bg-yellow-500/20 text-yellow-400'
                                            }`}>
                                                {sim.severity}
                                            </span>
                                        </div>
                                        <div className="text-xs text-gray-400 mb-2 truncate">
                                            {sim.attack_type}
                                        </div>
                                        <div className="text-[10px] text-gray-500">
                                            <span className="text-green-500 font-bold">{sim.similarity_score}% Match:</span> {sim.match_reason}
                                        </div>
                                    </Link>
                                ))}
                            </div>
                            <p className="text-[10px] text-gray-600 mt-3 italic">Retrieved via RAG similarity engine.</p>
                        </div>
                    )}

                    {/* Chain of Custody */}
                    <div className="cyber-card">
                        <h3 className="text-[10px] font-bold text-gray-500 uppercase tracking-[0.2em] mb-4">Chain of Custody</h3>
                        <div className="flex items-center gap-3 mb-4">
                            <div className="w-10 h-10 rounded bg-cyber-blue/5 border border-cyber-blue/20 flex items-center justify-center">
                                <User className="w-5 h-5 text-cyber-blue" />
                            </div>
                            <div>
                                <div className="text-gray-400 text-xs font-mono uppercase tracking-wider">Reporter ID</div>
                                <div className="text-white text-sm font-bold font-mono">{incident.reporter_id}</div>
                            </div>
                        </div>
                        <div className="space-y-3">
                            <div className="p-3 bg-white/5 rounded border border-white/5">
                                <div className="text-gray-500 text-[10px] uppercase font-bold mb-1">Encrypted Name</div>
                                <div className="text-xs text-gray-300 break-all font-mono">{incident.encrypted_name || 'NULL'}</div>
                            </div>
                            <div className="p-3 bg-white/5 rounded border border-white/5">
                                <div className="text-gray-500 text-[10px] uppercase font-bold mb-1">Encrypted Contact</div>
                                <div className="text-xs text-gray-300 break-all font-mono">{incident.encrypted_contact || 'NULL'}</div>
                            </div>
                        </div>
                        <p className="text-[10px] text-gray-600 mt-4 leading-tight italic">
                            * PII encrypted at rest using AES-256 GCM.
                        </p>
                    </div>

                </div>
            </div>

            {/* Escalation Modal */}
            {showEscalateModal && (
                <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                    <div className="bg-[#0a0a0f] border border-cyber-blue/30 rounded-xl max-w-lg w-full p-6 shadow-[0_0_30px_rgba(0,240,255,0.1)]">
                        <div className="flex items-center gap-3 text-alert-red mb-4">
                            <ShieldAlert className="w-8 h-8" />
                            <h2 className="text-xl font-bold uppercase tracking-widest">Confirm Escalation</h2>
                        </div>
                        
                        <div className="space-y-4 mb-6">
                            <p className="text-gray-300 text-sm">
                                You are about to officially escalate this case to law enforcement. Based on the victim's detected location, the docket will be routed to the following authorities:
                            </p>
                            
                            <div className="bg-black/40 border border-white/10 rounded p-4">
                                <div className="text-xs text-gray-500 uppercase font-bold mb-1">Detected Jurisdiction</div>
                                <div className="text-lg text-white font-mono mb-4">{incident.state_location || 'Unknown'}</div>
                                
                                {incident.state_location && escalationData.stateAuthorities?.[incident.state_location] ? (
                                    <div className="space-y-3">
                                        <div className="border-l-2 border-cyber-blue pl-3">
                                            <div className="font-bold text-cyber-blue text-sm">
                                                {escalationData.stateAuthorities[incident.state_location].cyber_cell.name}
                                            </div>
                                            <div className="text-xs text-gray-400 font-mono mt-1">
                                                Email: {escalationData.stateAuthorities[incident.state_location].cyber_cell.email}<br/>
                                                Helpline: {escalationData.stateAuthorities[incident.state_location].cyber_cell.phone}
                                            </div>
                                        </div>
                                        <div className="border-l-2 border-purple-500 pl-3">
                                            <div className="font-bold text-purple-400 text-sm">
                                                {escalationData.stateAuthorities[incident.state_location].women_cell.name}
                                            </div>
                                            <div className="text-xs text-gray-400 font-mono mt-1">
                                                Email: {escalationData.stateAuthorities[incident.state_location].women_cell.email}<br/>
                                                Helpline: {escalationData.stateAuthorities[incident.state_location].women_cell.phone}
                                            </div>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="border-l-2 border-yellow-500 pl-3">
                                        <div className="font-bold text-yellow-500 text-sm">National Cyber Crime Reporting Portal</div>
                                        <div className="text-xs text-gray-400 font-mono mt-1">
                                            Portal: cybercrime.gov.in<br/>
                                            Helpline: 1930
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className="flex justify-end gap-3">
                            <button 
                                onClick={() => setShowEscalateModal(false)}
                                className="px-4 py-2 rounded text-sm text-gray-400 hover:text-white transition-colors"
                            >
                                Cancel
                            </button>
                            <CyberButton variant="danger" onClick={confirmEscalation}>
                                Confirm & Escalate
                            </CyberButton>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default IncidentDetail;
