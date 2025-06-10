"use client"

import type React from "react"

import { useState, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Upload, Download, FileArchive, Loader2, CheckCircle } from "lucide-react"

type ProcessingState = "idle" | "uploading" | "processing" | "completed" | "error"

export default function Component() {
  const [state, setState] = useState<ProcessingState>("idle")
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [statusMessage, setStatusMessage] = useState("")
  const [compressedFileUrl, setCompressedFileUrl] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      setState("idle")
      setStatusMessage("")
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) return

    setState("uploading");
    setStatusMessage("Uploading file...");

    try {
      // Simulate a brief upload period before actual processing starts
      // This matches the spirit of the reference UI's separate "uploading" phase
      await new Promise(resolve => setTimeout(resolve, 500)); // Short delay

      setState("processing");
      setStatusMessage("Compressing file...");

      // Convert file to base64
      const fileReader = new FileReader();
      const base64Data = await new Promise<string>((resolve, reject) => {
        fileReader.onload = (e) => resolve(e.target?.result as string);
        fileReader.onerror = reject;
        fileReader.readAsDataURL(selectedFile);
      });

      // Upload to backend for compression
      const response = await fetch('/api/compress', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          fileName: selectedFile.name,
          content: base64Data,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: 'Failed to compress file' }));
        throw new Error(errorData.message || 'Failed to compress file');
      }

      const compressedData = await response.arrayBuffer();
      const compressedBlob = new Blob([compressedData], { type: 'application/octet-stream' });
      
      setState("completed");
      setStatusMessage("Compression completed successfully!");
      setCompressedFileUrl(URL.createObjectURL(compressedBlob));
    } catch (error: any) {
      setState("error");
      setStatusMessage(error.message || "An unknown error occurred during compression.");
      console.error('Error:', error);
    }
  }

  const handleDownload = () => {
    if (compressedFileUrl) {
      const link = document.createElement("a")
      link.href = compressedFileUrl
      link.download = `compressed_${selectedFile?.name || "file"}`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
  }

  const handleReset = () => {
    setState("idle")
    setSelectedFile(null)
    setStatusMessage("")
    setCompressedFileUrl(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  const getStatusIcon = () => {
    switch (state) {
      case "uploading":
      case "processing":
        return <Loader2 data-testid="loader-icon" className="w-5 h-5 animate-spin" />
      case "completed":
        return <CheckCircle data-testid="check-circle-icon" className="w-5 h-5 text-green-600" />
      case "error":
        return <FileArchive data-testid="error-icon" className="w-5 h-5 text-red-600" />
      default:
        return <FileArchive data-testid="default-status-icon" className="w-5 h-5" />
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50 p-4">
      <Card className="w-full max-w-md">
        <CardContent className="p-8 space-y-6">
          <div className="text-center">
            <FileArchive data-testid="main-file-archive-icon" className="w-12 h-12 mx-auto mb-4 text-gray-600" />
            <h1 className="text-2xl font-semibold text-gray-900 mb-2">File Compressor</h1>
            <p className="text-sm text-gray-600">Upload a file to compress it</p>
          </div>

          <div className="space-y-4">
            {/* File Selection */}
            {!selectedFile && state === "idle" && (
              <div>
                <input ref={fileInputRef} type="file" onChange={handleFileSelect} className="hidden" id="file-upload" />
                <label htmlFor="file-upload">
                  <Button asChild className="w-full cursor-pointer">
                    <span>
                      <Upload className="w-4 h-4 mr-2" />
                      Choose File
                    </span>
                  </Button>
                </label>
              </div>
            )}

            {/* Selected File Display */}
            {selectedFile && state === "idle" && (
              <div className="space-y-3">
                <div className="p-3 bg-gray-100 rounded-lg">
                  <p className="text-sm font-medium text-gray-900 truncate">{selectedFile.name}</p>
                  <p className="text-xs text-gray-600">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
                <div className="flex gap-2">
                  <Button onClick={handleUpload} className="flex-1">
                    <Upload className="w-4 h-4 mr-2" />
                    Compress File
                  </Button>
                  <Button variant="outline" onClick={handleReset}>
                    Cancel
                  </Button>
                </div>
              </div>
            )}

            {/* Status Message */}
            {statusMessage && (
              <div className="flex items-center justify-center p-4 bg-gray-100 rounded-lg">
                {getStatusIcon()}
                <span className="ml-2 text-sm font-medium text-gray-700">{statusMessage}</span>
              </div>
            )}

            {/* Download Button */}
            {state === "completed" && (
              <div className="space-y-3">
                <Button onClick={handleDownload} className="w-full">
                  <Download className="w-4 h-4 mr-2" />
                  Download Compressed File
                </Button>
                <Button variant="outline" onClick={handleReset} className="w-full">
                  Compress Another File
                </Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
