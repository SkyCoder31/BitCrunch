import { render, screen } from '@testing-library/react';
import { Button } from '../button'; // Adjust path as necessary

describe('Button Component', () => {
  it('renders with default props', () => {
    render(<Button>Default Button</Button>);
    const buttonElement = screen.getByRole('button', { name: /Default Button/i });
    expect(buttonElement).toBeInTheDocument();
    expect(buttonElement).toHaveClass('bg-primary text-primary-foreground'); // Default variant
    expect(buttonElement).toHaveClass('h-10 px-4 py-2'); // Default size
  });

  // Test variants
  const variants = [
    { name: 'default', className: 'bg-primary' },
    { name: 'destructive', className: 'bg-destructive' },
    { name: 'outline', className: 'border border-input' },
    { name: 'secondary', className: 'bg-secondary' },
    { name: 'ghost', className: 'hover:bg-accent' },
    { name: 'link', className: 'text-primary underline-offset-4' },
  ] as const;

  variants.forEach(variant => {
    it(`renders with variant: ${variant.name}`, () => {
      render(<Button variant={variant.name}>Variant Button</Button>);
      const buttonElement = screen.getByRole('button', { name: /Variant Button/i });
      expect(buttonElement).toHaveClass(variant.className);
    });
  });

  // Test sizes
  const sizes = [
    { name: 'default', className: 'h-10 px-4 py-2' },
    { name: 'sm', className: 'h-9 rounded-md px-3' },
    { name: 'lg', className: 'h-11 rounded-md px-8' },
    { name: 'icon', className: 'h-10 w-10' },
  ] as const;

  sizes.forEach(size => {
    it(`renders with size: ${size.name}`, () => {
      render(<Button size={size.name}>Size Button</Button>);
      // For 'icon' size, the text might not be the best way to get it if it's only an icon
      const buttonElement = screen.getByRole('button');
      expect(buttonElement).toHaveClass(size.className);
    });
  });

  it('renders as child when asChild prop is true', () => {
    render(
      <Button asChild>
        <a href="/test">As Child Link</a>
      </Button>
    );
    // Check if it's an anchor tag now, not a button
    const linkElement = screen.getByRole('link', { name: /As Child Link/i });
    expect(linkElement).toBeInTheDocument();
    expect(linkElement.tagName).toBe('A');
    // It should still have button styling classes
    expect(linkElement).toHaveClass('bg-primary'); // Default variant
    expect(linkElement).toHaveClass('h-10'); // Default size part
  });

  it('renders as a div when asChild prop is true and child is a div', () => {
    render(
      <Button asChild>
        <div>As Child Div</div>
      </Button>
    );
    // Check if it's a div, not a button, and no role='button'
    const divElement = screen.getByText(/As Child Div/i);
    expect(divElement).toBeInTheDocument();
    expect(divElement.tagName).toBe('DIV');
    // Check it does not have role="button"
    expect(screen.queryByRole('button', { name: /As Child Div/i })).not.toBeInTheDocument();
    // It should still have button styling classes
    expect(divElement).toHaveClass('bg-primary');
    expect(divElement).toHaveClass('h-10');
  });


  it('passes other HTML button attributes like disabled', () => {
    render(<Button disabled>Disabled Button</Button>);
    const buttonElement = screen.getByRole('button', { name: /Disabled Button/i });
    expect(buttonElement).toBeDisabled();
  });

  it('passes other HTML button attributes like type', () => {
    render(<Button type="submit">Submit Button</Button>);
    const buttonElement = screen.getByRole('button', { name: /Submit Button/i });
    expect(buttonElement).toHaveAttribute('type', 'submit');
  });

  it('applies custom className', () => {
    render(<Button className="custom-class">Custom Class Button</Button>);
    const buttonElement = screen.getByRole('button', { name: /Custom Class Button/i });
    expect(buttonElement).toHaveClass('custom-class');
  });
});
