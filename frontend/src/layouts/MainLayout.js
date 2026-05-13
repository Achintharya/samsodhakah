import React from 'react';
import { Outlet } from 'react-router-dom';
import Header from '../components/Header';
import './MainLayout.css';

function MainLayout() {
  return (
    <div className="app-container">
      <Header />
      <div className="workspace-shell">
        <main className="main-content">
          <Outlet />
        </main>
        <footer className="footer">
          <p>© 2025 Saṃśodhakaḥ. Built with ❤️ by Achintharya.</p>
        </footer>
      </div>
    </div>
  );
}

export default MainLayout;