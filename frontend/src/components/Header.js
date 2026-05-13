import React from 'react';
import { NavLink } from 'react-router-dom';
import './Header.css';

function Header() {
  return (
    <aside className="header" aria-label="Primary workspace navigation">
      <div className="header-container">
        <NavLink to="/" className="logo">
          <img src="/logo.png" alt="Saṃśodhakaḥ" className="logo-image" />
          <span>
            <span className="logo-text">Saṃśodhakaḥ</span>
            <span className="logo-subtitle">semantic writing IDE</span>
          </span>
        </NavLink>
        <nav className="nav">
          <NavLink to="/" end className="nav-link">Research</NavLink>
          <NavLink to="/library" className="nav-link">Library</NavLink>
          <NavLink to="/evidence" className="nav-link">Evidence</NavLink>
          <NavLink to="/draft" className="nav-link">Drafting</NavLink>
          <NavLink to="/verify" className="nav-link">Verification</NavLink>
          <NavLink to="/citations" className="nav-link">Citations</NavLink>
          <NavLink to="/export" className="nav-link">Export</NavLink>
        </nav>
      </div>
    </aside>
  );
}

export default Header;