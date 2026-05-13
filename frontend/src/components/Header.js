import React from 'react';
import { Link } from 'react-router-dom';
import './Header.css';

function Header() {
  return (
    <header className="header">
      <div className="header-container">
        <Link to="/" className="logo">
          <img src="/logo.png" alt="Saṃśodhakaḥ" className="logo-image" />
          <span className="logo-text">Saṃśodhakaḥ</span>
        </Link>
        <nav className="nav">
          <Link to="/" className="nav-link">Research</Link>
          <Link to="/library" className="nav-link">Library</Link>
          <Link to="/evidence" className="nav-link">Evidence</Link>
          <Link to="/draft" className="nav-link">Drafting</Link>
          <Link to="/citations" className="nav-link">Citations</Link>
          <Link to="/export" className="nav-link">Export</Link>
        </nav>
      </div>
    </header>
  );
}

export default Header;