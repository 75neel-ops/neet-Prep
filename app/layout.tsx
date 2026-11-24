import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'NEETPrep — NCERT Guided Preparation',
  description: 'AI-powered chapter practice and NCERT-guided exam preparation',
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
