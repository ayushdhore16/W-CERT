import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { Shield, UserPlus, Mail, Lock, User, ArrowRight } from 'lucide-react';
import CyberButton from '../../components/UI/CyberButton';

const Register = () => {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: '',
        confirmPassword: ''
    });
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const { register } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        if (formData.password !== formData.confirmPassword) {
            setError("Passwords do not match");
            setIsLoading(false);
            return;
        }

        const result = await register(formData);

        if (result.success) {
            navigate('/login');
        } else {
            setError(result.error);
        }
        setIsLoading(false);
    };

    return (
        <div className="min-h-[85vh] flex items-center justify-center relative py-10">
            <div className="w-full max-w-md">

                <div className="text-center mb-8">
                    <Shield className="w-12 h-12 text-cyber-blue mx-auto mb-4" />
                    <h2 className="text-3xl font-bold text-white tracking-tight">Join W-CERT</h2>
                    <p className="text-gray-400 mt-2">Create secure credentials.</p>
                </div>

                <div className="cyber-card backdrop-blur-xl bg-cyber-gray/50 border border-white/10 shadow-[0_0_50px_rgba(0,0,0,0.5)]">
                    <form onSubmit={handleSubmit} className="space-y-5">

                        {error && (
                            <div className="bg-alert-red/10 border border-alert-red text-alert-red px-4 py-3 rounded text-sm text-center">
                                {error}
                            </div>
                        )}

                        <div>
                            <label className="block text-sm font-medium text-gray-400 mb-1">Display Name</label>
                            <div className="relative">
                                <User className="absolute left-3 top-3 w-5 h-5 text-gray-500" />
                                <input
                                    type="text"
                                    className="cyber-input pl-10 bg-black/40 border-gray-700 focus:border-cyber-blue"
                                    placeholder="Agent Name"
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                    required
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-400 mb-1">Email Identifier</label>
                            <div className="relative">
                                <Mail className="absolute left-3 top-3 w-5 h-5 text-gray-500" />
                                <input
                                    type="email"
                                    className="cyber-input pl-10 bg-black/40 border-gray-700 focus:border-cyber-blue"
                                    placeholder="agent@w-cert.org"
                                    value={formData.email}
                                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                    required
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-400 mb-1">Passcode</label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-3 w-5 h-5 text-gray-500" />
                                <input
                                    type="password"
                                    className="cyber-input pl-10 bg-black/40 border-gray-700 focus:border-cyber-blue"
                                    placeholder="••••••••"
                                    value={formData.password}
                                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                    required
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-400 mb-1">Confirm Passcode</label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-3 w-5 h-5 text-gray-500" />
                                <input
                                    type="password"
                                    className="cyber-input pl-10 bg-black/40 border-gray-700 focus:border-cyber-blue"
                                    placeholder="••••••••"
                                    value={formData.confirmPassword}
                                    onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                                    required
                                />
                            </div>
                        </div>

                        <div className="pt-2">
                            <CyberButton type="submit" variant="primary" className="w-full justify-center" isLoading={isLoading}>
                                Initialize Account <ArrowRight className="ml-2 w-4 h-4" />
                            </CyberButton>
                        </div>

                    </form>

                    <div className="mt-6 text-center text-sm">
                        <span className="text-gray-500">Already authorized? </span>
                        <Link to="/login" className="text-cyber-blue hover:text-white transition-colors">Access Login</Link>
                    </div>
                </div>

            </div>
        </div>
    );
};

export default Register;
