import * as React from "react";
import { SidebarProvider } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/navigation/app-sidebar";
import { TopNav } from "@/components/navigation/top-nav";

export default function AdvisorLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <SidebarProvider>
      <div className="flex min-h-screen w-full bg-white">
        <AppSidebar role="advisor" />
        <div className="flex flex-1 flex-col overflow-hidden">
          <TopNav roleTitle="Advisor & Underwriter Workbench" />
          <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 bg-slate-50/30">
            <div className="mx-auto max-w-7xl">{children}</div>
          </main>
        </div>
      </div>
    </SidebarProvider>
  );
}

