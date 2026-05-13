import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles/base.css'; // New base styles
import './styles/variables.css'; // New design tokens
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);