import { render, screen, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import ReliabilityPage from './ReliabilityPage';

vi.mock('../api/client', () => ({
  getRetrievalMetrics: vi.fn().mockResolvedValue({
    total_queries: 10,
    average_confidence: 0.75,
    low_confidence_query_count: 2,
    average_latency_ms: 150,
    latency_p50_ms: 120,
    latency_p95_ms: 280,
    latency_p99_ms: 350,
    total_estimated_cost_usd: 0.125,
    citation_rate: 0.85,
    average_hallucination_risk: 0.15,
    average_citation_coverage: 0.82,
    average_retrieval_precision: 0.78,
    average_answer_completeness: 0.88,
    recent_queries: [
      {
        id: 'q1',
        question: 'How to fix billing error?',
        confidence: 0.85,
        latency_ms: 120,
        estimated_cost_usd: 0.012,
        created_at: '2026-01-01T00:00:00Z',
      },
    ],
  }),
  getCostMetrics: vi.fn().mockResolvedValue({
    total_estimated_cost_usd: 0.125,
    total_queries: 10,
    by_model: [
      {
        provider: 'mock',
        model: 'mock-llm',
        query_count: 10,
        total_cost_usd: 0.125,
      },
    ],
  }),
  getQualityByArea: vi.fn().mockResolvedValue({
    areas: [
      {
        product_area: 'Billing',
        query_count: 5,
        average_confidence: 0.8,
        average_hallucination_risk: 0.1,
        average_citation_coverage: 0.85,
        average_retrieval_precision: 0.82,
        average_answer_completeness: 0.9,
        citation_rate: 0.9,
      },
    ],
  }),
  getFailedQueries: vi.fn().mockResolvedValue({
    count: 1,
    items: [
      {
        id: 'fq1',
        question: 'What is quantum physics?',
        confidence: 0.15,
        reason: 'low_confidence',
        feedback: null,
        product_area: null,
        created_at: '2026-01-01T00:00:00Z',
      },
    ],
  }),
  compareEval: vi.fn().mockResolvedValue({
    name: 'test-compare',
    total_questions: 5,
    config_a: {
      label: 'Baseline',
      top_k: 3,
      threshold: 0.3,
      passed_count: 4,
      failed_count: 1,
      average_confidence: 0.7,
      average_latency_ms: 100,
      average_hallucination_risk: 0.2,
    },
    config_b: {
      label: 'Candidate',
      top_k: 5,
      threshold: 0.3,
      passed_count: 5,
      failed_count: 0,
      average_confidence: 0.8,
      average_latency_ms: 150,
      average_hallucination_risk: 0.15,
    },
    passed_delta: 1,
    confidence_delta: 0.1,
    latency_delta_ms: 50,
    hallucination_risk_delta: -0.05,
    per_question: [
      {
        question: 'Test question',
        confidence_a: 0.7,
        confidence_b: 0.8,
        confidence_delta: 0.1,
        passed_a: true,
        passed_b: true,
      },
    ],
  }),
}));

describe('ReliabilityPage', () => {
  it('renders loading state initially', () => {
    render(<ReliabilityPage />);
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('renders reliability page with metrics', async () => {
    render(<ReliabilityPage />);

    await waitFor(() => {
      expect(screen.getByText('Reliability')).toBeInTheDocument();
    });

    expect(screen.getByText('Answer Quality (averages)')).toBeInTheDocument();
    expect(screen.getByText('Latency Percentiles')).toBeInTheDocument();
    expect(screen.getByText('Cost by Provider / Model')).toBeInTheDocument();
    expect(screen.getByText('Quality by Product Area')).toBeInTheDocument();
    expect(screen.getByText(/Failed-Query Review Queue/)).toBeInTheDocument();
  });

  it('displays quality metrics correctly', async () => {
    render(<ReliabilityPage />);

    await waitFor(() => {
      expect(screen.getAllByText('15.0%').length).toBeGreaterThanOrEqual(1);
    });

    expect(screen.getByText('Hallucination Risk')).toBeInTheDocument();
    expect(screen.getByText('Citation Coverage')).toBeInTheDocument();
    expect(screen.getByText('Retrieval Precision')).toBeInTheDocument();
    expect(screen.getByText('Answer Completeness')).toBeInTheDocument();
  });

  it('displays latency percentiles', async () => {
    render(<ReliabilityPage />);

    await waitFor(() => {
      expect(screen.getByText('p50')).toBeInTheDocument();
    });

    expect(screen.getByText('p95')).toBeInTheDocument();
    expect(screen.getByText('p99')).toBeInTheDocument();
  });

  it('displays cost breakdown', async () => {
    render(<ReliabilityPage />);

    await waitFor(() => {
      expect(screen.getByText('mock')).toBeInTheDocument();
    });

    expect(screen.getByText('mock-llm')).toBeInTheDocument();
  });

  it('displays product area quality', async () => {
    render(<ReliabilityPage />);

    await waitFor(() => {
      expect(screen.getByText('Billing')).toBeInTheDocument();
    });
  });

  it('displays failed queries', async () => {
    render(<ReliabilityPage />);

    await waitFor(() => {
      expect(screen.getByText('What is quantum physics?')).toBeInTheDocument();
    });

    expect(screen.getByText('low_confidence')).toBeInTheDocument();
  });
});