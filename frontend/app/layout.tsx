import type { Metadata } from "next";
import Link from "next/link";
import "./styles.css";

export const metadata: Metadata = {
  title: "Autonomous Detection Platform",
  description: "MVP frontend skeleton",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <header className="header">
          <h1>Autonomous Detection Platform</h1>
          <nav>
            <Link href="/">Overview</Link>
            <Link href="/coverage">Coverage</Link>
            <Link href="/runs">Runs</Link>
            <Link href="/alerts">Alerts</Link>
            <Link href="/rules">Rules</Link>
          </nav>
        </header>
        <main className="container">{children}</main>
      </body>
    </html>
  );
}
