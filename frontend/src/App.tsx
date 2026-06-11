import { BrowserRouter, Route, Routes } from "react-router-dom";
import AppLayout from "./components/AppLayout";
import AccountPage from "./pages/AccountPage";
import AssistPage from "./pages/AssistPage";
import AuditPage from "./pages/AuditPage";
import ConnectorsPage from "./pages/ConnectorsPage";
import DashboardPage from "./pages/DashboardPage";
import EvalRunsPage from "./pages/EvalRunsPage";
import JobsPage from "./pages/JobsPage";
import KnowledgeBasePage from "./pages/KnowledgeBasePage";
import PiiPage from "./pages/PiiPage";
import PromptsPage from "./pages/PromptsPage";
import RagPlaygroundPage from "./pages/RagPlaygroundPage";
import ReliabilityPage from "./pages/ReliabilityPage";
import SettingsPage from "./pages/SettingsPage";
import SlaPage from "./pages/SlaPage";
import TicketDetailPage from "./pages/TicketDetailPage";
import TicketsPage from "./pages/TicketsPage";
import UploadPage from "./pages/UploadPage";
import WorkspacesPage from "./pages/WorkspacesPage";

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
          <Route path="/account" element={<AccountPage />} />
          <Route path="/workspaces" element={<WorkspacesPage />} />
          <Route path="/prompts" element={<PromptsPage />} />
          <Route path="/jobs" element={<JobsPage />} />
          <Route path="/pii" element={<PiiPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/audit" element={<AuditPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
