import { useState } from 'react';
import { AlertTriangle, Upload, FileText, ArrowRight, ShieldCheck } from 'lucide-react';
import CyberButton from '../../components/UI/CyberButton';
import { useNavigate } from 'react-router-dom';
import api from '../../api/axios';

const Report = () => {
    const navigate = useNavigate();
    const [step, setStep] = useState(1);
    const [formData, setFormData] = useState({
        description: '',
        files: [],
        contact: ''
    });
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [reportResult, setReportResult] = useState(null);
    const [error, setError] = useState('');

    // Handle file selection
    const handleFileChange = (e) => {
        setFormData({ ...formData, files: Array.from(e.target.files) });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsSubmitting(true);
        setError('');

        try {
            // 0. Silently grab Geo-IP state for routing
            let stateLocation = "Unknown";
            try {
                const geoRes = await fetch('https://ipapi.co/json/');
                const geoData = await geoRes.json();
                if (geoData.region) {
                    stateLocation = geoData.region;
                }
            } catch (err) {
                console.log("Geo-IP lookup skipped/failed");
            }

            // 1. Submit Incident Details
            const incidentPayload = {
                description: formData.description,
                contact_info: formData.contact || "Anonymous",
                state_location: stateLocation
            };

            const res = await api.post('/incidents', incidentPayload);
            const { incident } = res.data;

            // 2. Upload Evidence (if any)
            if (formData.files.length > 0) {
                // Backend expects a single file per request with the key 'file'
                for (const file of formData.files) {
                    const evidenceData = new FormData();
                    evidenceData.append('file', file);

                    await api.post(`/incidents/${incident.incident_id}/evidence`, evidenceData, {
                        headers: { 'Content-Type': 'multipart/form-data' }
                    });
                }
            }

            setReportResult(incident);
            setStep(3); // Success step

        } catch (err) {
            console.error("Submission failed", err);
            setError(err.response?.data?.error || "Failed to submit report. Please try again.");
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="min-h-[80vh] flex flex-col items-center justify-center py-10">

            <div className="w-full max-w-2xl">
                <div className="mb-8 text-center">
                    <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400 mb-2">
                        Secure Incident Reporting
                    </h1>
                    <p className="text-gray-400">
                        Submit evidence securely. Your data is encrypted and anonymized.
                    </p>
                </div>

                {/* Progress Steps */}
                <div className="flex justify-between mb-8 relative">
                    <div className="absolute top-1/2 left-0 w-full h-0.5 bg-gray-800 -z-10"></div>
                    {[1, 2, 3].map((s) => (
                        <div key={s} className={`w-10 h-10 rounded-full flex items-center justify-center font-mono font-bold border-2 transition-colors ${step >= s ? 'bg-cyber-blue border-cyber-blue text-black' : 'bg-black border-gray-700 text-gray-500'}`}>
                            {s}
                        </div>
                    ))}
                </div>

                <div className="cyber-card backdrop-blur-md bg-cyber-gray/30">

                    {error && (
                        <div className="mb-4 bg-alert-red/10 border border-alert-red text-alert-red px-4 py-3 rounded text-sm text-center">
                            {error}
                        </div>
                    )}

                    {step === 1 && (
                        <form onSubmit={() => setStep(2)} className="space-y-6">
                            <div>
                                <label className="block text-cyber-blue font-mono mb-2 flex items-center">
                                    <FileText className="w-4 h-4 mr-2" /> Incident Description
                                </label>
                                <textarea
                                    className="cyber-input min-h-[150px] resize-y"
                                    placeholder="Describe what happened... (e.g. 'I received a threatening email asking for money...')"
                                    value={formData.description}
                                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-cyber-blue font-mono mb-2 flex items-center">
                                    <Upload className="w-4 h-4 mr-2" /> Evidence Upload (Optional)
                                </label>
                                <div className="border-2 border-dashed border-gray-700 rounded-lg p-8 text-center hover:border-cyber-blue/50 transition-colors cursor-pointer bg-black/20 relative">
                                    <input
                                        type="file"
                                        multiple
                                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                        id="file-upload"
                                        onChange={handleFileChange}
                                    />
                                    <div>
                                        <Upload className="w-8 h-8 text-gray-500 mx-auto mb-2" />
                                        <p className="text-gray-400 text-sm">Drag files here or click to upload</p>
                                        <p className="text-xs text-gray-600 mt-2">Screenshots, Emails, PDFs (Max 10MB)</p>
                                        {formData.files.length > 0 && (
                                            <div className="mt-4 text-cyber-blue text-sm font-bold">
                                                {formData.files.length} file(s) selected
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>

                            <div className="flex justify-end pt-4">
                                <CyberButton onClick={() => setStep(2)} variant="primary">
                                    Next Step <ArrowRight className="ml-2 w-4 h-4" />
                                </CyberButton>
                            </div>
                        </form>
                    )}

                    {step === 2 && (
                        <div className="space-y-6">
                            <div>
                                <label className="block text-cyber-blue font-mono mb-2">
                                    Contact Information (Optional)
                                </label>
                                <p className="text-xs text-gray-500 mb-4">Leave blank for anonymous reporting.</p>
                                <input
                                    type="text"
                                    className="cyber-input"
                                    placeholder="Email or Phone Number"
                                    value={formData.contact}
                                    onChange={(e) => setFormData({ ...formData, contact: e.target.value })}
                                />
                            </div>

                            <div className="bg-cyber-blue/5 border border-cyber-blue/20 p-4 rounded text-sm text-gray-300">
                                <h4 className="text-cyber-blue font-bold mb-2 flex items-center"><ShieldCheck className="w-4 h-4 mr-2" /> Pre-Submission Checks</h4>
                                <ul className="list-disc list-inside space-y-1 text-xs">
                                    <li>Data will be encrypted with AES-256 before storage.</li>
                                    <li>Evidence integrity will be verified via SHA-256 hashing.</li>
                                    <li>Our AI engine will analyze this for immediate threat assessment.</li>
                                </ul>
                            </div>

                            <div className="flex justify-between pt-4">
                                <CyberButton onClick={() => setStep(1)} variant="ghost">
                                    Back
                                </CyberButton>
                                <CyberButton onClick={handleSubmit} variant="danger" isLoading={isSubmitting}>
                                    Submit Report
                                </CyberButton>
                            </div>
                        </div>
                    )}

                    {step === 3 && reportResult && (
                        <div className="text-center py-8">
                            <div className="w-20 h-20 bg-green-500/10 rounded-full flex items-center justify-center mx-auto mb-6 border border-green-500/50">
                                <ShieldCheck className="w-10 h-10 text-green-500" />
                            </div>
                            <h2 className="text-2xl font-bold text-white mb-2">Report Submitted Successfully</h2>
                            <p className="text-gray-400 mb-8">
                                Your Incident ID: <span className="font-mono text-cyber-blue">{reportResult.incident_id}</span>
                            </p>

                            <div className="bg-gray-900/50 p-6 rounded-lg text-left mb-8 border border-white/5">
                                <div className="flex justify-between items-center mb-4">
                                    <h4 className="text-white font-bold">AI Threat Analysis:</h4>
                                    <span className={`px-2 py-1 rounded text-xs font-bold border ${reportResult.severity === 'CRITICAL' ? 'bg-red-500/20 text-red-500 border-red-500' :
                                        reportResult.severity === 'HIGH' ? 'bg-orange-500/20 text-orange-500 border-orange-500' :
                                            'bg-green-500/20 text-green-500 border-green-500'
                                        }`}>
                                        {reportResult.severity}
                                    </span>
                                </div>

                                <p className="text-gray-300 text-sm mb-4 italic uppercase tracking-wider font-mono text-cyber-blue">
                                    {reportResult.attack_type.replace('_', ' ')} Detected
                                </p>

                                <h4 className="text-white font-bold mb-2 text-sm">Priority Recommendations:</h4>
                                <ul className="space-y-3 text-sm text-gray-300">
                                    {reportResult.recommendations && reportResult.recommendations.map((rec, i) => (
                                        <li key={i} className="flex items-start">
                                            <span className="text-cyber-blue mr-2">{i + 1}.</span> {rec}
                                        </li>
                                    ))}
                                    {(!reportResult.recommendations || reportResult.recommendations.length === 0) && (
                                        <>
                                            <li className="flex items-start"><span className="text-cyber-blue mr-2">1.</span> Do not delete original evidence from your device.</li>
                                            <li className="flex items-start"><span className="text-cyber-blue mr-2">2.</span> Block the sender/caller immediately.</li>
                                        </>
                                    )}
                                </ul>
                            </div>

                            <CyberButton to="/" variant="primary">
                                Return Home
                            </CyberButton>
                        </div>
                    )}

                </div>
            </div>
        </div>
    );
};

export default Report;
