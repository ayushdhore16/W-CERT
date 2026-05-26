import { Link } from 'react-router-dom';
import { Loader2 } from 'lucide-react';

const CyberButton = ({
    children,
    variant = 'primary',
    isLoading = false,
    to,
    onClick,
    className = '',
    type = 'button'
}) => {

    const baseStyles = "relative inline-flex items-center justify-center font-mono font-bold tracking-wider uppercase text-sm transition-all duration-300 transform hover:-translate-y-1 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-cyber-black disabled:opacity-50 disabled:cursor-not-allowed";

    const variants = {
        primary: "bg-cyber-blue/10 border border-cyber-blue text-cyber-blue hover:bg-cyber-blue hover:text-black shadow-[0_0_10px_rgba(0,240,255,0.3)] hover:shadow-[0_0_20px_rgba(0,240,255,0.6)]",
        danger: "bg-alert-red/10 border border-alert-red text-alert-red hover:bg-alert-red hover:text-white shadow-[0_0_10px_rgba(255,0,60,0.3)] hover:shadow-[0_0_20px_rgba(255,0,60,0.6)]",
        ghost: "bg-transparent border border-white/20 text-gray-300 hover:border-white hover:text-white hover:bg-white/5",
    };

    const content = (
        <>
            {isLoading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
            {children}
            {/* Corner accents */}
            <span className="absolute top-0 left-0 w-2 h-2 border-t border-l border-current opacity-50"></span>
            <span className="absolute bottom-0 right-0 w-2 h-2 border-b border-r border-current opacity-50"></span>
        </>
    );

    if (to) {
        return (
            <Link to={to} className={`${baseStyles} ${variants[variant]} px-6 py-3 ${className}`}>
                {content}
            </Link>
        );
    }

    return (
        <button
            type={type}
            onClick={onClick}
            disabled={isLoading}
            className={`${baseStyles} ${variants[variant]} px-6 py-3 ${className}`}
        >
            {content}
        </button>
    );
};

export default CyberButton;
