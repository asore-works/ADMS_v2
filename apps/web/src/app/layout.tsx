import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "ADMS",
  description: "Advanced Drone Management System",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ja">
      <body>{children}</body>
    </html>
  );
}
