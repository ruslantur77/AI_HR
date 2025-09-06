import './Header.css';
import logo from '/src/assets/logo.svg';
import { useNavigate } from 'react-router-dom';

export default function Header() {
    const navigate = useNavigate();

    const handleLogoClick = () => {
        navigate('/');
    };

    return (
        <header className="header">
            <h1>
                AI HR
            </h1>
            <div className="logo">
                <img
                    className="logo-image"
                    src={logo}
                    alt="Logo"
                />
            </div>
        </header>
    );
}