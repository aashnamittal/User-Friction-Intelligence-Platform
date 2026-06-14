import React from 'react';
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import Home from './pages/Home';
import CustomerEmpathy from './pages/CustomerEmpathy';
import MLAnalytics from './pages/MLAnalytics';
import EngineControl from './pages/EngineControl';
import { Zap, Users, BarChart2, Settings } from 'lucide-react';
import './index.css';

function Sidebar() {
  return (
    <div className="sidebar">
      <h2 style={{ fontFamily: 'Outfit', marginBottom: '32px', display: 'flex', alignItems: 'center', gap: '8px' }}>
        <Zap size={24} color="var(--primary)" /> UFIP NAVIGATION
      </h2>
      <nav>
        <NavLink to="/" className={({isActive}) => isActive ? "nav-link active" : "nav-link"}>
          <div style={{display: 'flex', alignItems: 'center', gap: '12px'}}><Zap size={18}/> Live Telemetry</div>
        </NavLink>
        <NavLink to="/empathy" className={({isActive}) => isActive ? "nav-link active" : "nav-link"}>
          <div style={{display: 'flex', alignItems: 'center', gap: '12px'}}><Users size={18}/> Customer Empathy</div>
        </NavLink>
        <NavLink to="/ml-analytics" className={({isActive}) => isActive ? "nav-link active" : "nav-link"}>
          <div style={{display: 'flex', alignItems: 'center', gap: '12px'}}><BarChart2 size={18}/> ML Analytics</div>
        </NavLink>
        <NavLink to="/engine-control" className={({isActive}) => isActive ? "nav-link active" : "nav-link"}>
          <div style={{display: 'flex', alignItems: 'center', gap: '12px'}}><Settings size={18}/> Engine Control</div>
        </NavLink>
      </nav>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <div style={{ display: 'flex' }}>
        <Sidebar />
        <div className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/empathy" element={<CustomerEmpathy />} />
            <Route path="/ml-analytics" element={<MLAnalytics />} />
            <Route path="/engine-control" element={<EngineControl />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;
