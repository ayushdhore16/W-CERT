import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { Shield, Lock, Mail, ArrowRight } from 'lucide-react';
import CyberButton from '../../components/UI/CyberButton';

const Login = () => {
    const [formData, setFormData] = useState({ email: '', password: '' });
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        const result = await login(formData.email, formData.password);

        if (result.success) {
            navigate('/dashboard');
        } else {
            setError(result.error);
        }
        setIsLoading(false);
    };

    return (
        <div className="min-h-[80vh] flex items-center justify-center relative">
            <div className="w-full max-w-md">

                <div className="text-center mb-8">
                    <Shield className="w-12 h-12 text-cyber-blue mx-auto mb-4" />
                    <h2 className="text-3xl font-bold text-white tracking-tight">Access Control</h2>
                    <p className="text-gray-400 mt-2">Identify yourself to proceed.</p>
                </div>

                <div className="cyber-card backdrop-blur-xl bg-cyber-gray/50 border border-white/10 shadow-[0_0_50px_rgba(0,0,0,0.5)]">
                    <form onSubmit={handleSubmit} className="space-y-6">

                        {error && (
                            <div className="bg-alert-red/10 border border-alert-red text-alert-red px-4 py-3 rounded text-sm text-center">
                                {error}
                            </div>
                        )}

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

                        <div className="pt-2">
                            <CyberButton type="submit" variant="primary" className="w-full justify-center" isLoading={isLoading}>
                                Authenticate <ArrowRight className="ml-2 w-4 h-4" />
                            </CyberButton>
                        </div>

                    </form>

                    <div className="mt-6 text-center text-sm">
                        <span className="text-gray-500">Need credentials? </span>
                        <Link to="/register" className="text-cyber-blue hover:text-white transition-colors">Register Access</Link>
                    </div>
                </div>

            </div>
        </div>
    );
};

export default Login;
