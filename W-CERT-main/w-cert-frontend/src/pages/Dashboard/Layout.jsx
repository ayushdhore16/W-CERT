import { Outlet } from 'react-router-dom';
import Sidebar from '../../components/Layout/Sidebar';

const DashboardLayout = () => {
    return (
        <div className="flex pt-16 min-h-screen">
            <Sidebar />
            <div className="flex-1 md:ml-64 p-6 overflow-y-auto">
                <Outlet />
            </div>
        </div>
    );
};

export default DashboardLayout;
