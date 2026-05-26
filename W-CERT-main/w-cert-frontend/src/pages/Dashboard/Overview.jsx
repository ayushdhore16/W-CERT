import { useState, useEffect } from 'react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement } from 'chart.js';
import { Doughnut, Bar } from 'react-chartjs-2';
import { Shield, AlertCircle, CheckCircle, Clock, Loader2, TrendingUp } from 'lucide-react';
import api from '../../api/axios';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement);

const DashboardOverview = () => {
    const [stats, setStats] = useState(null);
    const [trends, setTrends] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchAll = async () => {
            try {
                const [statsRes, trendsRes] = await Promise.all([
                    api.get('/dashboard/stats'),
                    api.get('/dashboard/trends')
                ]);
                setStats(statsRes.data.stats);
                setTrends(trendsRes.data.trends);
            } catch (err) {
                console.error("Failed to fetch dashboard data", err);
            } finally {
                setLoading(false);
            }
        };
        fetchAll();
    }, []);

    if (loading) return <div className="p-10 text-center text-cyber-blue"><Loader2 className="w-10 h-10 animate-spin mx-auto" /> Loading Dashboard...</div>;

    // Severity doughnut
    const severityData = {
        labels: Object.keys(stats?.by_severity || {}),
        datasets: [{
            data: Object.values(stats?.by_severity || {}),
            backgroundColor: ['#00f0ff', '#f97316', '#ff003c', '#888888'],
            borderColor: ['#000'],
            borderWidth: 1,
        }],
    };

    // Attack type bar chart — from real trend data
    const attackTypes = trends?.by_attack_type || {};
    const sortedAttacks = Object.entries(attackTypes)
        .sort(([,a],[,b]) => b - a)
        .slice(0, 8);

    const attackBarData = {
        labels: sortedAttacks.map(([k]) => k.replace(/_/g, ' ')),
        datasets: [{
            label: 'Incidents',
            data: sortedAttacks.map(([,v]) => v),
            backgroundColor: [
                '#ff003c', '#f97316', '#facc15', '#00f0ff',
                '#a855f7', '#22c55e', '#ec4899', '#6366f1'
            ],
            borderRadius: 4,
            borderSkipped: false,
        }],
    };

    const doughnutOptions = {
        responsive: true,
        plugins: { legend: { position: 'bottom', labels: { color: '#fff', font: { size: 11 } } } },
    };

    const barOptions = {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
            y: { grid: { color: '#1f2937' }, ticks: { color: '#6b7280', precision: 0 } },
            x: { grid: { color: 'transparent' }, ticks: { color: '#9ca3af', font: { size: 10 } } },
        }
    };

    const escalated = stats?.by_status?.ESCALATED || 0;
    const critical = stats?.critical_incidents || 0;

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-white font-mono">Threat Intelligence Overview</h1>
                <div className="text-sm text-gray-500 font-mono flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse inline-block" />
                    LIVE MONITORING
                </div>
            </div>

            {/* KPI Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <KPICard title="Total Incidents" value={stats?.total_incidents || 0} icon={<AlertCircle className="text-alert-red" />} change="Live" />
                <KPICard title="Pending Review" value={stats?.by_status?.OPEN || 0} icon={<Clock className="text-yellow-500" />} change="Active" />
                <KPICard title="Escalated" value={escalated} icon={<TrendingUp className="text-orange-500" />} change={escalated > 0 ? 'Action' : 'Clear'} />
                <KPICard title="Critical" value={critical} icon={<Shield className="text-alert-red" />} change={critical > 0 ? 'Urgent' : 'Clear'} />
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="cyber-card">
                    <h3 className="text-lg font-bold text-white mb-4">Severity Distribution</h3>
                    <div className="h-64 flex justify-center">
                        {stats?.by_severity && Object.keys(stats.by_severity).length > 0 ? (
                            <Doughnut data={severityData} options={doughnutOptions} />
                        ) : (
                            <div className="flex items-center justify-center h-full text-gray-500">No data available</div>
                        )}
                    </div>
                </div>

                <div className="cyber-card">
                    <h3 className="text-lg font-bold text-white mb-4">Incidents by Attack Type</h3>
                    <div className="h-64">
                        {sortedAttacks.length > 0 ? (
                            <Bar data={attackBarData} options={barOptions} />
                        ) : (
                            <div className="flex items-center justify-center h-full text-gray-500">No trend data</div>
                        )}
                    </div>
                </div>
            </div>

            {/* Closed / resolved stat */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <KPICard title="Resolved" value={stats?.by_status?.RESOLVED || 0} icon={<CheckCircle className="text-green-500" />} change="Done" />
                <KPICard title="Closed" value={stats?.by_status?.CLOSED || 0} icon={<CheckCircle className="text-cyber-blue" />} change="Archived" />
                <KPICard title="System Status" value="ONLINE" icon={<Shield className="text-cyber-blue" />} change="Secure" />
            </div>
        </div>
    );
};

const KPICard = ({ title, value, icon, change }) => (
    <div className="bg-cyber-gray/40 border border-white/10 p-5 rounded-lg backdrop-blur-sm">
        <div className="flex justify-between items-start mb-2">
            <div className="text-gray-400 text-sm font-medium uppercase tracking-wider">{title}</div>
            {icon}
        </div>
        <div className="flex items-baseline gap-2">
            <div className="text-3xl font-bold text-white font-mono">{value}</div>
            <div className={`text-xs font-bold ${change === 'Live' || change === 'Urgent' || change === 'Action' ? 'text-alert-red animate-pulse' : 'text-cyber-blue'}`}>{change}</div>
        </div>
    </div>
);

export default DashboardOverview;

