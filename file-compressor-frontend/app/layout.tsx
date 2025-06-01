
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "File Compressor",
  description: "Compress and decompress files using lossless compression",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
