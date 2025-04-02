import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Box } from '@mui/material';
import Dashboard from './pages/Dashboard';
import StockMarket from './pages/StockMarket';
import AISettings from './pages/AISettings';
import MockInvestment from './pages/MockInvestment';
import Reports from './pages/Reports';
import Settings from './pages/Settings';
import Layout from './components/Layout';
import './styles/App.css';

function App() {
  return (
    <Box sx={{ display: 'flex' }}>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/market" element={<StockMarket />} />
          <Route path="/ai-settings" element={<AISettings />} />
          <Route path="/investment" element={<MockInvestment />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Layout>
    </Box>
  );
}

export default App;
