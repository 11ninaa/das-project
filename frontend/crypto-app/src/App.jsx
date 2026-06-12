
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import RouteWrapper from "./components/RouteWrapper";
import Home from "./pages/Home";
import CryptoSearch from "./pages/CryptoSearch";
import AssetHistory from "./pages/AssetHistory";
import TechnicalAnalysis from './pages/TechnicalAnalysis';
import AnalysisSelector from './pages/AnalysisSelector';
import LSTMPrediction from './pages/LSTMPrediction';
import OnChainSentiment from './pages/OnChainSentiment';
import Help from './pages/Help';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<RouteWrapper><Home /></RouteWrapper>} />
        <Route path="/search" element={<RouteWrapper><CryptoSearch /></RouteWrapper>} />
        <Route path="/history" element={<RouteWrapper><AssetHistory /></RouteWrapper>} />
        <Route path="/analysis" element={<RouteWrapper><AnalysisSelector /></RouteWrapper>} />
        <Route path="/analysis/:symbol" element={<RouteWrapper><TechnicalAnalysis /></RouteWrapper>} />
        <Route path="/lstm" element={<RouteWrapper><LSTMPrediction /></RouteWrapper>} />
        <Route path="/onchain-sentiment" element={<RouteWrapper><OnChainSentiment /></RouteWrapper>} />
        <Route path="/help" element={<RouteWrapper><Help /></RouteWrapper>} />
      </Routes>
    </Router>
  );
}

export default App;