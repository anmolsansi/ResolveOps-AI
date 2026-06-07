import { BrowserRouter, Route, Routes } from "react-router-dom";
import AppLayout from "./components/AppLayout";
import AssistPage from "./pages/AssistPage";
import ConnectorsPage from "./pages/ConnectorsPage";
import DashboardPage from "./pages/DashboardPage";
import EvalRunsPage from "./pages/EvalRunsPage";
import KnowledgeBasePage from "./pages/KnowledgeBasePage";
import RagPlaygroundPage from "./pages/RagPlaygroundPage";
import ReliabilityPage from "./pages/ReliabilityPage";
import SlaPage from "./pages/SlaPage";
import TicketDetailPage from "./pages/TicketDetailPage";
import TicketsPage from "./pages/TicketsPage";
import UploadPage from "./pages/UploadPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/tickets" element={<TicketsPage />} />
          <Route path="/tickets/:id" element={<TicketDetailPage />} />
          <Route path="/rag" element={<RagPlaygroundPage />} />
          <Route path="/reliability" element={<ReliabilityPage />} />
          <Route path="/eval" element={<EvalRunsPage />} />
          <Route path="/connectors" element={<ConnectorsPage />} />
          <Route path="/assist" element={<AssistPage />} />
          <Route path="/kb" element={<KnowledgeBasePage />} />
          <Route path="/sla" element={<SlaPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
