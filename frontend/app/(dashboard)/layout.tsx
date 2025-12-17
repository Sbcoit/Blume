import type { ReactNode } from "react";

// Streamlined layout: no sidebar/topbar, just a centered content column.
export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <main className="min-h-screen px-4 pt-16 pb-8 sm:px-6">
      <div className="mx-auto w-full max-w-3xl page-enter">
        {children}
      </div>
    </main>
  );
}



