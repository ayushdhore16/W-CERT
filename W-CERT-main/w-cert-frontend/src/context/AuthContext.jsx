import { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/axios';

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check if token is valid on mount via real backend endpoint
        const verifyToken = async () => {
            if (!token) {
                setLoading(false);
                return;
            }
            try {
                // Correct endpoint is /auth/me
                const res = await api.get('/auth/me');
                setUser(res.data.user);
            } catch (error) {
                console.error("Token verification failed", error);
                logout();
            } finally {
                setLoading(false);
            }
        };

        verifyToken();
    }, [token]);

    const login = async (email, password) => {
        try {
            const res = await api.post('/auth/login', { email, password });

            // Backend returns: { status, message, user: {...}, access_token, refresh_token }
            const { access_token, user } = res.data;

            setToken(access_token);
            localStorage.setItem('token', access_token);
            setUser(user);

            return { success: true };
        } catch (error) {
            console.error("Login failed", error);
            return { success: false, error: error.response?.data?.error || "Login failed. Check credentials." };
        }
    };

    const register = async (userData) => {
        try {
            await api.post('/auth/register', {
                email: userData.email,
                password: userData.password,
                display_name: userData.name // Backend expects 'display_name'
            });
            return { success: true };
        } catch (error) {
            console.error("Registration failed", error);
            return { success: false, error: error.response?.data?.error || "Registration failed" };
        }
    };

    const logout = () => {
        setUser(null);
        setToken(null);
        localStorage.removeItem('token');
        window.location.href = '/login';
    };

    return (
        <AuthContext.Provider value={{ user, token, login, register, logout, loading }}>
            {!loading && children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
