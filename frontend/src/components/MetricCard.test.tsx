import { render, screen } from '@testing-library/react';
import MetricCard from './MetricCard';

describe('MetricCard', () => {
  it('renders label and value', () => {
    render(<MetricCard label="Total Tickets" value={42} />);
    expect(screen.getByText('Total Tickets')).toBeInTheDocument();
    expect(screen.getByText('42')).toBeInTheDocument();
  });

  it('applies custom accent color', () => {
    render(<MetricCard label="Test" value="100" accent="#ff0000" />);
    const valueElement = screen.getByText('100');
    expect(valueElement).toHaveStyle({ color: 'rgb(255, 0, 0)' });
  });

  it('renders string values', () => {
    render(<MetricCard label="Status" value="Active" />);
    expect(screen.getByText('Active')).toBeInTheDocument();
  });
});