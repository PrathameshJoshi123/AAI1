import { type LucideIcon } from "lucide-react";

export interface NavItem {
  title: string;
  href: string;
  icon: LucideIcon;
  badge?: string | number;
  description?: string;
}

export interface NavSection {
  title: string;
  items: NavItem[];
}

export type UserRole = "customer" | "admin" | "owner" | "advisor" | "underwriter";

export interface UserSession {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  avatarUrl?: string;
}

