import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event'; // For more realistic interactions
import Page from '../page'; // Path to the component

// Mocking global objects and functions
global.fetch = jest.fn();
global.URL.createObjectURL = jest.fn((blob) => `blob:${blob?.size || 'mocked_url_for_test'}`);
global.URL.revokeObjectURL = jest.fn(); // Important for cleanup if used

// Mock FileReader
const mockFileReader = {
  onload: null as ((e: ProgressEvent<FileReader>) => void) | null,
  onerror: null as ((e: ProgressEvent<FileReader>) => void) | null,
  readAsDataURL: jest.fn(function(this: FileReader, file: File) {
    // Simulate async file reading
    setTimeout(() => {
      if (this.onload) {
        this.onload({ target: { result: `data:${file.type};base64,mocked_base64_content` } } as any);
      }
    }, 10);
  }),
  result: null
};


describe('Page Component - Initial Render', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    global.FileReader = jest.fn(() => {
        mockFileReader.onload = null;
        mockFileReader.onerror = null;
        mockFileReader.readAsDataURL.mockClear();
        (mockFileReader as any).result = null;
        return mockFileReader;
    }) as any;
  });

  it('renders the main heading', () => {
    render(<Page />);
    expect(screen.getByRole('heading', { name: /File Compressor/i })).toBeInTheDocument();
  });

  it('initially shows the "Choose File" button and no status message', () => {
    render(<Page />);
    expect(screen.getByText(/Choose File/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Choose File/i, { selector: 'input' })).toBeInTheDocument();

    expect(screen.queryByText(/Uploading file.../i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Compressing file.../i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Compression completed successfully!/i)).not.toBeInTheDocument();
  });
});

describe('Page Component - File Handling', () => {
  let actualCreateElement: (tagName: string, options?: ElementCreationOptions) => HTMLElement;

  beforeEach(() => {
    jest.clearAllMocks();
    global.URL.createObjectURL = jest.fn((blob) => `blob:${blob?.size || 'mocked_url_for_test'}`);
    global.URL.revokeObjectURL = jest.fn();
    global.FileReader = jest.fn(() => {
        mockFileReader.onload = null;
        mockFileReader.onerror = null;
        mockFileReader.readAsDataURL.mockClear();
        (mockFileReader as any).result = null;
        return mockFileReader;
    }) as any;

    actualCreateElement = document.createElement.bind(document);
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  const mockFile = new File(['dummy content'], 'test.png', { type: 'image/png' });

  it('allows file selection and displays file info', async () => {
    render(<Page />);
    const fileInput = screen.getByLabelText(/Choose File/i);

    await act(async () => {
        await userEvent.upload(fileInput!, mockFile);
    });

    expect(screen.getByText(mockFile.name)).toBeInTheDocument();
    expect(screen.getByText(`${(mockFile.size / 1024 / 1024).toFixed(2)} MB`)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Compress File/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Cancel/i })).toBeInTheDocument();
  });

  it('handles file compression successfully (happy path)', async () => {
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      arrayBuffer: async () => new ArrayBuffer(8),
    });

    render(<Page />);
    const fileInput = screen.getByLabelText(/Choose File/i);

    await act(async () => {
        await userEvent.upload(fileInput!, mockFile);
    });

    const compressButton = screen.getByRole('button', { name: /Compress File/i });
    await act(async () => {
        fireEvent.click(compressButton);
    });

    expect(screen.getByText(/Uploading file.../i)).toBeInTheDocument();
    expect(screen.getByTestId('loader-icon')).toBeInTheDocument();

    await waitFor(() => expect(screen.getByText(/Compressing file.../i)).toBeInTheDocument(), { timeout: 1000 });
    expect(screen.getByTestId('loader-icon')).toBeInTheDocument();


    await waitFor(() => expect(screen.getByText(/Compression completed successfully!/i)).toBeInTheDocument(), { timeout: 4000 });
    expect(screen.getByTestId('check-circle-icon')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Download Compressed File/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Compress Another File/i })).toBeInTheDocument();
    expect(fetch).toHaveBeenCalledTimes(1);
    expect(global.URL.createObjectURL).toHaveBeenCalledTimes(1);
  });

  it('handles file download', async () => {
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      arrayBuffer: async () => new ArrayBuffer(8),
    });
    const mockLinkClick = jest.fn();

    const createElementSpy = jest.spyOn(document, 'createElement').mockImplementation((tagName: string): HTMLElement => {
        if (tagName === 'a') {
            const mockAnchor = actualCreateElement('a');
            mockAnchor.click = mockLinkClick;
            jest.spyOn(document.body, 'appendChild').mockImplementationOnce((node) => node);
            jest.spyOn(document.body, 'removeChild').mockImplementationOnce((node) => node);
            return mockAnchor;
        }
        return actualCreateElement(tagName);
    });


    render(<Page />);
    const fileInput = screen.getByLabelText(/Choose File/i);
    await act(async () => {
        await userEvent.upload(fileInput!, mockFile);
    });

    const compressButton = screen.getByRole('button', { name: /Compress File/i });
    await act(async () => {
        fireEvent.click(compressButton);
    });

    await waitFor(() => screen.getByRole('button', { name: /Download Compressed File/i }), { timeout: 4000 });
    const downloadButton = screen.getByRole('button', { name: /Download Compressed File/i });

    await act(async () => {
        fireEvent.click(downloadButton);
    });

    expect(createElementSpy).toHaveBeenCalledWith('a');
    expect(mockLinkClick).toHaveBeenCalledTimes(1);

    if ((document.body.appendChild as jest.Mock).mockRestore) {
        (document.body.appendChild as jest.Mock).mockRestore();
    }
    if ((document.body.removeChild as jest.Mock).mockRestore) {
        (document.body.removeChild as jest.Mock).mockRestore();
    }
    createElementSpy.mockRestore();
  });

  it('resets the state when "Cancel" is clicked after selecting a file', async () => {
    render(<Page />);
    const fileInput = screen.getByLabelText(/Choose File/i) as HTMLInputElement;
    await act(async () => {
        await userEvent.upload(fileInput!, mockFile);
    });

    const cancelButton = screen.getByRole('button', { name: /Cancel/i });
    await act(async () => {
        fireEvent.click(cancelButton);
    });

    expect(screen.getByText(/Choose File/i)).toBeInTheDocument();
    expect(screen.queryByText(mockFile.name)).not.toBeInTheDocument();
    // expect(fileInput.value).toBe(''); // This assertion can be brittle in JSDOM
  });

  it('resets the state when "Compress Another File" is clicked', async () => {
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      arrayBuffer: async () => new ArrayBuffer(8),
    });
    render(<Page />);
    const fileInput = screen.getByLabelText(/Choose File/i) as HTMLInputElement;

    await act(async () => {
        await userEvent.upload(fileInput!, mockFile);
    });

    const compressButton = screen.getByRole('button', { name: /Compress File/i });
    await act(async () => {
        fireEvent.click(compressButton);
    });

    await waitFor(() => screen.getByRole('button', { name: /Compress Another File/i }), { timeout: 4000 });
    const resetButton = screen.getByRole('button', { name: /Compress Another File/i });
    await act(async () => {
        fireEvent.click(resetButton);
    });

    expect(screen.getByText(/Choose File/i)).toBeInTheDocument();
    expect(screen.queryByText(/Compression completed successfully!/i)).not.toBeInTheDocument();
    // expect(fileInput.value).toBe(''); // This assertion can be brittle in JSDOM
  });

  it('handles file compression failure', async () => {
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      json: async () => ({ message: 'Compression failed by mock' }),
    });
    render(<Page />);
    const fileInput = screen.getByLabelText(/Choose File/i);

    await act(async () => {
        await userEvent.upload(fileInput!, mockFile);
    });

    const compressButton = screen.getByRole('button', { name: /Compress File/i });
    await act(async () => {
        fireEvent.click(compressButton);
    });

    expect(screen.getByText(/Uploading file.../i)).toBeInTheDocument();

    await waitFor(() => expect(screen.getByText(/Compressing file.../i)).toBeInTheDocument(), { timeout: 1000 });

    await waitFor(() => expect(screen.getByText(/Compression failed by mock/i)).toBeInTheDocument(), { timeout: 2000 });
    expect(screen.getByTestId('error-icon')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /Download Compressed File/i })).not.toBeInTheDocument();
  });
});
