import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import path from 'path';

export async function POST(request: Request) {
  try {
    const { fileName, content } = await request.json();
    
    // Create temporary file
    const tempFilePath = path.join(process.cwd(), 'temp', fileName);
    
    // Write base64 content to file
    const buffer = Buffer.from(content.split(',')[1], 'base64');
    
    // Create temp directory if it doesn't exist
    try {
      const fs = require('fs');
      const tempDir = path.join(process.cwd(), 'temp');
      if (!fs.existsSync(tempDir)) {
        fs.mkdirSync(tempDir);
      }
    } catch (error) {
      console.error('Error creating temp directory:', error);
      throw error;
    }
    
    // Write file
    await new Promise((resolve, reject) => {
      require('fs').writeFile(tempFilePath, buffer, (error: NodeJS.ErrnoException | null) => {
        if (error) reject(error);
        else resolve(true);
      });
    });

    // Compress the file using our Python script
    const compressedFilePath = path.join(process.cwd(), 'temp', `${fileName}.compressed`);
    
    await new Promise((resolve, reject) => {
      exec(`python "${path.join('..', 'compressor.py')}" compress "${tempFilePath}" "${compressedFilePath}"`, (error: Error | null) => {
        if (error) {
          console.error('Error executing Python script:', error);
          reject(new Error('Error compressing file: ' + error.message));
        } else {
          resolve(true);
        }
      });
    });

    // Read the compressed file
    const compressedBuffer = await new Promise<Buffer>((resolve, reject) => {
      require('fs').readFile(compressedFilePath, (error: NodeJS.ErrnoException | null, data: Buffer) => {
        if (error) reject(error);
        else resolve(data);
      });
    });

    // Clean up temporary files
    try {
      const fs = require('fs');
      const path = require('path');
      
      // Delete temporary files safely
      const deleteFile = (filePath: string) => {
        try {
          // First try to close any open handles
          if (fs.existsSync(filePath)) {
            // Try to rename the file first to break any locks
            const tempRename = path.join(path.dirname(filePath), `temp_${path.basename(filePath)}`);
            fs.renameSync(filePath, tempRename);
            // Then try to delete it
            fs.unlinkSync(tempRename);
          }
        } catch (error) {
          console.error(`Error deleting file ${filePath}:`, error);
        }
      };

      // Delete both files
      deleteFile(tempFilePath);
      deleteFile(compressedFilePath);
    } catch (error) {
      console.error('Error cleaning up temporary files:', error);
      // Don't throw error here as it's not critical for the main functionality
    }

    // Get the file extension
    const fileExtension = fileName.split('.').pop() || 'txt';
    const compressedFileName = `${fileName.replace('.' + fileExtension, '')}.compressed.${fileExtension}`;

    // Return the compressed file data directly
    return new NextResponse(compressedBuffer, {
      headers: {
        'Content-Type': 'application/octet-stream',
        'Content-Disposition': `attachment; filename="${compressedFileName}"`
      }
    });

    // Clean up temporary files after sending response
    try {
      const fs = require('fs');
      const path = require('path');
      
      // Delete temporary files safely
      const deleteFile = (filePath: string) => {
        try {
          // First try to close any open handles
          if (fs.existsSync(filePath)) {
            // Try to rename the file first to break any locks
            const tempRename = path.join(path.dirname(filePath), `temp_${path.basename(filePath)}`);
            fs.renameSync(filePath, tempRename);
            // Then try to delete it
            fs.unlinkSync(tempRename);
          }
        } catch (error) {
          console.error(`Error deleting file ${filePath}:`, error);
        }
      };

      // Delete both files
      deleteFile(tempFilePath);
      deleteFile(compressedFilePath);
    } catch (error) {
      console.error('Error cleaning up temporary files:', error);
    }

  } catch (error) {
    console.error('Error compressing file:', error);
    return NextResponse.json(
      { error: 'Failed to compress file' },
      { status: 500 }
    );
  }
}
