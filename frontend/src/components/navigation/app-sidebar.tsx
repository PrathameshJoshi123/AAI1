"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ShieldCheck, LogOut, ArrowRightLeft } from "lucide-react";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { NavSection, UserRole } from "@/types/nav";
import {
  CUSTOMER_NAV,
  ADMIN_NAV,
  ADVISOR_NAV,
} from "@/components/navigation/role-nav-config";

interface AppSidebarProps {
  role: UserRole;
  userName?: string;
  userEmail?: string;
}

export function AppSidebar({
  role,
  userName = "Prathamesh Joshi",
  userEmail = "prathamesh@example.com",
}: AppSidebarProps) {
  const pathname = usePathname();
  const { state } = useSidebar();
  const isCollapsed = state === "collapsed";

  const navSections: NavSection[] = React.useMemo(() => {
    switch (role) {
      case "customer":
        return CUSTOMER_NAV;
      case "admin":
      case "owner":
        return ADMIN_NAV;
      case "advisor":
      case "underwriter":
        return ADVISOR_NAV;
      default:
        return CUSTOMER_NAV;
    }
  }, [role]);

  const roleLabel = React.useMemo(() => {
    switch (role) {
      case "customer":
        return "Customer Portal";
      case "admin":
        return "Admin Portal";
      case "advisor":
        return "Advisor Workbench";
      default:
        return "Insurance Portal";
    }
  }, [role]);

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader>
        <div className={`flex items-center gap-3 px-2 py-1.5 ${isCollapsed ? "justify-center px-0" : ""}`}>
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground shadow-xs">
            <ShieldCheck className="h-5 w-5" />
          </div>
          {!isCollapsed && (
            <div className="flex flex-col truncate">
              <span className="text-sm font-bold tracking-tight text-slate-900">
                PS-21 Insure
              </span>
              <span className="text-[11px] font-medium text-slate-400 capitalize">
                {roleLabel}
              </span>
            </div>
          )}
        </div>
      </SidebarHeader>

      <SidebarContent>
        {navSections.map((section) => (
          <SidebarGroup key={section.title}>
            <SidebarGroupLabel>{section.title}</SidebarGroupLabel>
            <SidebarMenu>
              {section.items.map((item) => {
                const isActive =
                  pathname === item.href ||
                  (item.href !== `/${role}` && pathname.startsWith(item.href));
                const Icon = item.icon;

                return (
                  <SidebarMenuItem key={item.href}>
                    <SidebarMenuButton asChild isActive={isActive} tooltip={item.title}>
                      <Link href={item.href} title={isCollapsed ? item.title : undefined} className={isCollapsed ? "justify-center px-0" : ""}>
                        <Icon className="h-4 w-4 shrink-0" />
                        {!isCollapsed && <span>{item.title}</span>}
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroup>
        ))}
      </SidebarContent>

      <SidebarFooter>
        <SidebarMenu>
          <SidebarMenuItem>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className={`flex w-full items-center gap-3 rounded-lg p-2 text-left hover:bg-slate-100 transition-colors ${isCollapsed ? "justify-center p-1" : ""}`}>
                  <Avatar className="h-8 w-8 shrink-0">
                    <AvatarFallback className="bg-primary/10 text-primary text-xs font-semibold">
                      {userName.slice(0, 2).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  {!isCollapsed && (
                    <div className="flex flex-1 flex-col truncate text-xs">
                      <span className="font-semibold text-slate-900 truncate">
                        {userName}
                      </span>
                      <span className="text-slate-400 truncate">{userEmail}</span>
                    </div>
                  )}
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel className="font-normal">
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium text-slate-900 leading-none">
                      {userName}
                    </p>
                    <p className="text-xs text-slate-500 leading-none">
                      {userEmail}
                    </p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuLabel className="text-xs text-slate-400 font-semibold uppercase tracking-wider">
                  Switch Portal (Demo)
                </DropdownMenuLabel>
                <DropdownMenuItem asChild>
                  <Link href="/customer" className="cursor-pointer">
                    <ArrowRightLeft className="mr-2 h-4 w-4" />
                    Customer Portal
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link href="/admin" className="cursor-pointer">
                    <ArrowRightLeft className="mr-2 h-4 w-4" />
                    Admin Dashboard
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link href="/advisor" className="cursor-pointer">
                    <ArrowRightLeft className="mr-2 h-4 w-4" />
                    Advisor Workbench
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem asChild>
                  <Link href="/login" className="cursor-pointer text-red-600 focus:text-red-600">
                    <LogOut className="mr-2 h-4 w-4" />
                    Sign out
                  </Link>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  );
}

