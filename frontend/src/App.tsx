import { BrowserRouter, Route, Routes } from "react-router-dom";
import AppLayout from "./components/AppLayout";
import DashboardPage from "./pages/DashboardPage";
import EvalRunsPage from "./pages/EvalRunsPage";
import RagPlaygroundPage from "./pages/RagPlaygroundPage";
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
          <Route path="/eval" element={<EvalRunsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
