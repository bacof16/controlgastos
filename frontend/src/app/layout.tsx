import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ControlGastos Premium",
  description: "Gestión inteligente de finanzas",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body>
        <main className="container">
            {children}
        </main>
      </body>
    </html>
  );
}
