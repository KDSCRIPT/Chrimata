// app/layout.tsx
"use client";

import { ClerkProvider } from "@clerk/nextjs";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import {
  SignedIn,
  SignedOut,
  SignInButton,
  SignUpButton,
  UserButton,
} from "@clerk/nextjs";
import { Zap } from "lucide-react";
import { usePathname } from "next/navigation";
import "./../../styles/globals.css";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  const showHeader = pathname !== "/";

  return (
    <ClerkProvider>
      <html lang="en">
        <body className="min-h-screen bg-background text-foreground">
          {showHeader && (
            <header className="flex justify-between items-center p-4 border-b bg-white dark:bg-sidebar-background dark:text-sidebar-foreground shadow-sm">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                  <Zap className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  Chrimata
                </span>
              </div>

              <nav className="flex items-center gap-4">
                <div className="flex items-center space-x-4">
                  <Link href="/">
                    <Button
                      size="lg"
                      className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white"
                    >
                      Home
                    </Button>
                  </Link>
                </div>
                <div className="flex items-center space-x-4">
                  <Link href="/dashboard">
                    <Button>Dashboard</Button>
                  </Link>
                </div>

                <SignedOut>
                  <SignInButton mode="modal" />
                  <SignUpButton mode="modal" />
                </SignedOut>

                <SignedIn>
                  <UserButton afterSignOutUrl="/" />
                </SignedIn>
              </nav>
            </header>
          )}

          {children}
        </body>
      </html>
    </ClerkProvider>
  );
}
