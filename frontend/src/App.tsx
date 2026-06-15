import { BrowserRouter, Route, Routes } from "react-router-dom";
import AppLayout from "./components/AppLayout";
import AccountPage from "./pages/AccountPage";
import ActionLogsPage from "./pages/ActionLogsPage";
import AssistPage from "./pages/AssistPage";
import AuditPage from "./pages/AuditPage";
import ConnectorsPage from "./pages/ConnectorsPage";
import ConversationDetailPage from "./pages/ConversationDetailPage";
import ConversationsPage from "./pages/ConversationsPage";
import CopilotPage from "./pages/CopilotPage";
import CustomerProfilePage from "./pages/CustomerProfilePage";
import CustomersPage from "./pages/CustomersPage";
import DashboardPage from "./pages/DashboardPage";
import EvalRunsPage from "./pages/EvalRunsPage";
import HandoffsPage from "./pages/HandoffsPage";
import IntelligencePage from "./pages/IntelligencePage";
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
import ToolDetailPage from "./pages/ToolDetailPage";
import ToolsPage from "./pages/ToolsPage";
import UploadPage from "./pages/UploadPage";
import WidgetHost from "./pages/WidgetHost";
import WorkspacesPage from "./pages/WorkspacesPage";
import RoutingPage from "./pages/RoutingPage";
import CannedResponsesPage from "./pages/CannedResponsesPage";
import PortalPage from "./pages/PortalPage";

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
          <Route path="/conversations" element={<ConversationsPage />} />
          <Route path="/conversations/:id" element={<ConversationDetailPage />} />
          <Route path="/customers" element={<CustomersPage />} />
          <Route path="/customers/:id" element={<CustomerProfilePage />} />
          <Route path="/handoffs" element={<HandoffsPage />} />
          <Route path="/tools" element={<ToolsPage />} />
          <Route path="/tools/:id" element={<ToolDetailPage />} />
          <Route path="/action-logs" element={<ActionLogsPage />} />
          <Route path="/intelligence" element={<IntelligencePage />} />
          <Route path="/copilot" element={<CopilotPage />} />
          <Route path="/routing" element={<RoutingPage />} />
          <Route path="/canned-responses" element={<CannedResponsesPage />} />
          <Route path="/portal" element={<PortalPage />} />
          <Route path="/widget" element={<WidgetHost />} />
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
