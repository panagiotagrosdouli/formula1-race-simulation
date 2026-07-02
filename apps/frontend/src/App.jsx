import { QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { queryClientInstance } from '@/lib/query-client';
import { ModeProvider } from '@/lib/ModeContext';
import Layout from '@/components/Layout';
import Home from '@/pages/Home';
import Predictor from '@/pages/Predictor';
import Strategy from '@/pages/Strategy';
import Telemetry from '@/pages/Telemetry';
import Live from '@/pages/Live';
import Championship from '@/pages/Championship';
import Engineer from '@/pages/Engineer';
import Reports from '@/pages/Reports';

function App() {
  return (
    <QueryClientProvider client={queryClientInstance}>
      <ModeProvider>
        <Router>
          <Routes>
            <Route element={<Layout />}>
              <Route path="/" element={<Home />} />
              <Route path="/predictor" element={<Predictor />} />
              <Route path="/strategy" element={<Strategy />} />
              <Route path="/telemetry" element={<Telemetry />} />
              <Route path="/live" element={<Live />} />
              <Route path="/championship" element={<Championship />} />
              <Route path="/engineer" element={<Engineer />} />
              <Route path="/reports" element={<Reports />} />
            </Route>
          </Routes>
        </Router>
      </ModeProvider>
    </QueryClientProvider>
  );
}

export default App;
