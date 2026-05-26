import { useState, useEffect } from 'react';
import { Users as UsersIcon, UserPlus, Shield, MoreVertical, Loader2, UserCheck, UserX } from 'lucide-react';
import api from '../../api/axios';

const Users = () => {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [updating, setUpdating] = useState(null);

    useEffect(() => {
        const fetchUsers = async () => {
            try {
                const res = await api.get('/admin/users');
                setUsers(res.data.users);
            } catch (err) {
                console.error("Failed to fetch users", err);
                setError("Access Denied: Only administrators can view this page.");
            } finally {
                setLoading(false);
            }
        };
        fetchUsers();
    }, []);

    const handleRoleChange = async (userId, newRole) => {
        setUpdating(userId);
        try {
            await api.patch(`/admin/users/${userId}/role`, { role: newRole });
            setUsers(users.map(u => u.user_id === userId ? { ...u, role: newRole } : u));
        } catch (err) {
            alert("Failed to update role");
        } finally {
            setUpdating(null);
        }
    };

    if (loading) return <div className="p-10 text-center text-cyber-blue"><Loader2 className="w-10 h-10 animate-spin mx-auto" /> Loading Users...</div>;
    if (error) return <div className="p-10 text-center text-alert-red">{error}</div>;

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-white font-mono flex items-center gap-3">
                    <UsersIcon className="text-cyber-blue" /> User Management
                </h1>
                <div className="text-xs text-gray-500 font-mono uppercase tracking-widest bg-white/5 px-4 py-2 rounded border border-white/5">
                    {users.length} Registered Identities
                </div>
            </div>

            <div className="cyber-card overflow-hidden p-0 border-white/5">
                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr className="bg-cyber-black/50 border-b border-white/10 text-[10px] uppercase text-gray-500 tracking-[0.2em]">
                            <th className="p-4 font-mono font-bold">Identity ID</th>
                            <th className="p-4 font-mono font-bold">User Details</th>
                            <th className="p-4 font-mono font-bold">Access Level</th>
                            <th className="p-4 font-mono font-bold">Status</th>
                            <th className="p-4 font-mono font-bold text-right">Clearance Action</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5 text-sm">
                        {users.map((user) => (
                            <tr key={user.user_id} className="hover:bg-cyber-blue/5 transition-all group">
                                <td className="p-4 font-mono text-xs text-cyber-blue/70">{user.user_id}</td>
                                <td className="p-4">
                                    <div className="font-bold text-white group-hover:text-cyber-blue transition-colors">{user.display_name}</div>
                                    <div className="text-xs text-gray-500 font-mono">{user.email}</div>
                                </td>
                                <td className="p-4">
                                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold border font-mono tracking-tighter ${user.role === 'ADMIN' ? 'bg-alert-red/10 text-alert-red border-alert-red/30' :
                                        user.role === 'ANALYST' ? 'bg-cyber-blue/10 text-cyber-blue border-cyber-blue/30' :
                                            'bg-gray-700/20 text-gray-500 border-gray-600/30'
                                        }`}>
                                        {user.role}
                                    </span>
                                </td>
                                <td className="p-4">
                                    <span className="text-[10px] font-mono flex items-center gap-2 text-green-400">
                                        <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse shadow-[0_0_8px_#4ade80]"></span>
                                        AUTHORIZED
                                    </span>
                                </td>
                                <td className="p-4 text-right">
                                    <div className="flex justify-end gap-2">
                                        {user.role !== 'ADMIN' && (
                                            <button
                                                onClick={() => handleRoleChange(user.user_id, 'ADMIN')}
                                                disabled={updating === user.user_id}
                                                className="p-2 bg-alert-red/5 hover:bg-alert-red/20 text-alert-red rounded border border-alert-red/10 transition-all"
                                                title="Promote to Admin"
                                            >
                                                <Shield className="w-4 h-4" />
                                            </button>
                                        )}
                                        {user.role !== 'ANALYST' && (
                                            <button
                                                onClick={() => handleRoleChange(user.user_id, 'ANALYST')}
                                                disabled={updating === user.user_id}
                                                className="p-2 bg-cyber-blue/5 hover:bg-cyber-blue/20 text-cyber-blue rounded border border-cyber-blue/10 transition-all"
                                                title="Promote to Analyst"
                                            >
                                                <UserCheck className="w-4 h-4" />
                                            </button>
                                        )}
                                        {user.role !== 'USER' && (
                                            <button
                                                onClick={() => handleRoleChange(user.user_id, 'USER')}
                                                disabled={updating === user.user_id}
                                                className="p-2 bg-white/5 hover:bg-white/10 text-gray-400 rounded border border-white/5 transition-all"
                                                title="Demote to User"
                                            >
                                                <UserX className="w-4 h-4" />
                                            </button>
                                        )}
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <p className="text-[10px] text-gray-600 italic text-center font-mono">
                NOTICE: Administrative actions are logged to the Secure Audit Trail.
            </p>
        </div>
    );
};

export default Users;
