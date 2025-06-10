import { render, screen } from '@testing-library/react';
import {
  Card,
  CardHeader,
  CardFooter,
  CardTitle,
  CardDescription,
  CardContent,
} from '../card'; // Adjust path as necessary

describe('Card Component and its parts', () => {
  describe('Card', () => {
    it('renders with children and default class names', () => {
      render(<Card data-testid="my-card">Card Content</Card>);
      const cardElement = screen.getByTestId('my-card');
      expect(cardElement).toBeInTheDocument();
      expect(cardElement).toHaveTextContent('Card Content');
      expect(cardElement).toHaveClass('rounded-lg border bg-card text-card-foreground shadow-sm');
    });

    it('applies custom className', () => {
      render(<Card className="custom-card-class">Custom Card</Card>);
      const cardElement = screen.getByText('Custom Card');
      expect(cardElement).toHaveClass('custom-card-class');
    });
  });

  describe('CardHeader', () => {
    it('renders with children and default class names', () => {
      render(<CardHeader data-testid="my-card-header">Header Content</CardHeader>);
      const headerElement = screen.getByTestId('my-card-header');
      expect(headerElement).toBeInTheDocument();
      expect(headerElement).toHaveTextContent('Header Content');
      expect(headerElement).toHaveClass('flex flex-col space-y-1.5 p-6');
    });

    it('applies custom className to CardHeader', () => {
      render(<CardHeader className="custom-header-class">Custom Header</CardHeader>);
      const headerElement = screen.getByText('Custom Header');
      expect(headerElement).toHaveClass('custom-header-class');
    });
  });

  describe('CardTitle', () => {
    it('renders with children and default class names', () => {
      render(<CardTitle data-testid="my-card-title">Title Content</CardTitle>);
      const titleElement = screen.getByTestId('my-card-title');
      expect(titleElement).toBeInTheDocument();
      expect(titleElement).toHaveTextContent('Title Content');
      expect(titleElement).toHaveClass('text-2xl font-semibold leading-none tracking-tight');
      expect(titleElement.tagName).toBe('H3'); // Default tag for CardTitle
    });

    it('renders as specified component via "as" prop (though CardTitle does not directly support it, this is a general pattern if it did)', () => {
      // Note: Shadcn CardTitle doesn't have 'as' prop by default. This test is illustrative.
      // If it did, it would be: render(<CardTitle as="h1">Title</CardTitle>);
      // For current CardTitle, we check its default tag.
      render(<CardTitle>Specific Tag Title</CardTitle>);
      const titleElement = screen.getByText('Specific Tag Title');
      expect(titleElement.tagName).toBe('H3');
    });
  });

  describe('CardDescription', () => {
    it('renders with children and default class names', () => {
      render(<CardDescription data-testid="my-card-desc">Description Content</CardDescription>);
      const descElement = screen.getByTestId('my-card-desc');
      expect(descElement).toBeInTheDocument();
      expect(descElement).toHaveTextContent('Description Content');
      expect(descElement).toHaveClass('text-sm text-muted-foreground');
      expect(descElement.tagName).toBe('P'); // Default tag
    });
  });

  describe('CardContent', () => {
    it('renders with children and default class names', () => {
      render(<CardContent data-testid="my-card-content">Main Content</CardContent>);
      const contentElement = screen.getByTestId('my-card-content');
      expect(contentElement).toBeInTheDocument();
      expect(contentElement).toHaveTextContent('Main Content');
      expect(contentElement).toHaveClass('p-6 pt-0');
    });
  });

  describe('CardFooter', () => {
    it('renders with children and default class names', () => {
      render(<CardFooter data-testid="my-card-footer">Footer Content</CardFooter>);
      const footerElement = screen.getByTestId('my-card-footer');
      expect(footerElement).toBeInTheDocument();
      expect(footerElement).toHaveTextContent('Footer Content');
      expect(footerElement).toHaveClass('flex items-center p-6 pt-0');
    });
  });

  // Integration test: Rendering a full card
  it('renders a full card structure', () => {
    render(
      <Card>
        <CardHeader>
          <CardTitle>Full Card Title</CardTitle>
          <CardDescription>Full Card Description</CardDescription>
        </CardHeader>
        <CardContent>
          <p>Full Card Main Content</p>
        </CardContent>
        <CardFooter>
          <p>Full Card Footer Content</p>
        </CardFooter>
      </Card>
    );

    expect(screen.getByText('Full Card Title')).toBeInTheDocument();
    expect(screen.getByText('Full Card Description')).toBeInTheDocument();
    expect(screen.getByText('Full Card Main Content')).toBeInTheDocument();
    expect(screen.getByText('Full Card Footer Content')).toBeInTheDocument();
  });
});
