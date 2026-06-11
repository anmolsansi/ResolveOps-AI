import { render, screen } from '@testing-library/react';
import ErrorState from './ErrorState';

describe('ErrorState', () => {
  it('renders error message', () => {
    render(<ErrorState message="Something went wrong" />);
    const errorDiv = screen.getByText('Something went wrong');
    expect(errorDiv).toBeInTheDocument();
    expect(screen.getByText('Error:')).toBeInTheDocument();
  });

  it('applies error styling', () => {
    const { container } = render(<ErrorState message="Test error" />);
    const errorDiv = container.firstChild as HTMLElement;
    expect(errorDiv).toHaveStyle({ backgroundColor: expect.stringContaining('08') });
    expect(errorDiv.style.border).toContain('0.19');
    expect(errorDiv.style.color).toContain('rgb(239, 68, 68)');
  });
});