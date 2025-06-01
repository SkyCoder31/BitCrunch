# BitCrunch - Advanced File Compression Tool

A web-based file compression tool that uses Huffman Coding for efficient lossless compression of various file types. The tool is designed to provide real compression results while maintaining a user-friendly interface.

## Features

- Lossless compression using Huffman Coding
- Real file compression implementation
- Supports multiple file formats:
  - Text files (.txt, .html, .css, .js)
  - PDF documents (.pdf)
  - Word documents (.docx, .doc)
- Modern, responsive web interface built with Next.js
- Real-time compression status with progress indicators
- Automatic file extension preservation
- Error handling and user feedback

## Tech Stack

- Frontend: Next.js 14 with TypeScript
- Backend: Python 3.x with Huffman Coding implementation
- UI Components: Radix UI and Tailwind CSS
- Compression Algorithm: Huffman Coding with optimized implementations

## Installation

1. Clone the repository:
```bash
git clone https://github.com/SkyCoder31/BitCrunch.git
```

2. Install Node.js dependencies:
```bash
cd file-compressor-frontend
npm install
```

3. Start the development server:
```bash
npm run dev
```

## Next Steps

The current version of BitCrunch focuses on implementing the core compression functionality. In the next development round, we plan to enhance the frontend UI with the following improvements:

- Modern, responsive dashboard layout
- File upload progress bar with percentage
- Detailed compression statistics:
  - Original file size
  - Compressed file size
  - Compression ratio
  - Compression time
- Visual compression comparison chart
- Batch file compression support
- Drag and drop file upload
- File history and compression records
- Theme support (light/dark mode)
- Mobile-responsive design
- Improved error handling and user feedback
- File format specific compression options

## Usage

## Usage

1. Open your web browser and navigate to `http://localhost:3000`
2. Click "Choose File" to select a file to compress
3. The file will be automatically uploaded to the server
4. Wait for the compression process to complete (this may take a few seconds depending on file size)
5. Click "Download Compressed File" to save the compressed version
6. Verify the compression by comparing file sizes

## File Format Support

- Text files: .txt, .html, .css, .js
- Documents: .pdf, .docx, .doc
- Other formats: .json, .xml, .csv

## Compression Algorithm

The tool uses Huffman Coding for efficient lossless compression with several optimizations:
- Pattern recognition for common file sequences
- Sequence replacement with shorter markers
- Weighted frequency dictionary for common patterns
- Binary data optimization for non-text files
- File type specific optimizations

## Project Structure

```
file-compressor/
├── compressor.py          # Python compression script
├── file-compressor-frontend/
│   ├── app/              # Next.js frontend
│   │   ├── api/         # API routes
│   │   │   └── compress/ route.ts
│   │   └── page.tsx     # Main page component
│   └── package.json     # Frontend dependencies
└── README.md            # Project documentation
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
