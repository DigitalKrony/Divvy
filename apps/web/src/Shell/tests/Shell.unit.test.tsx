import { render, screen } from '@testing-library/react';

import {Shell} from './../Shell';

describe('Shell Component', () => {
  it('renders without crashing', () => {
    render(<Shell />);
    // Adjust thi1s text based on what is actually in your App.jsx!
    expect(screen.getByText(/New/i)).toBeInTheDocument(); 
  });
});