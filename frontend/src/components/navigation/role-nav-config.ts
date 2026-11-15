import {
  LayoutDashboard,
  Compass,
  BotMessageSquare,
  FileText,
  ClipboardList,
  FolderOpen,
  User,
  Users,
  Briefcase,
  ShieldAlert,
  Sliders,
  History,
  Settings,
  Scale,
  CheckCircle2,
  UserCheck,
  Calculator,
  ListChecks,
  Sparkles,
  ShieldCheck,
  MessageSquare,
  FolderKanban,
  CalendarClock,
  Bell,
} from "lucide-react";
import { NavSection } from "@/types/nav";

export const CUSTOMER_NAV: NavSection[] = [
  {
    title: "Insurance Journey",
    items: [
      {
        title: "Overview",
        href: "/customer",
        icon: LayoutDashboard,
        description: "Your insurance portfolio summary",
      },
      {
        title: "Explore Plans",
        href: "/customer/explore",
        icon: Compass,
        description: "Health, life, and motor insurance products",
      },
      {
        title: "AI Insurance Assistant",
        href: "/customer/chat",
        icon: BotMessageSquare,
        description: "Need discovery & personalized recommendations",
      },
      {
        title: "Needs Assessment",
        href: "/customer/needs-assessment",
        icon: ListChecks,
        description: "Structured family, financial & health intake",
      },
      {
        title: "Coverage Calculator",
        href: "/customer/calculator",
        icon: Calculator,
        description: "Actuarial Human Life Value (HLV) math",
      },
      {
        title: "Recommendations",
        href: "/customer/recommendations",
        icon: Sparkles,
        description: "Tailored policy matches & rationales",
      },
      {
        title: "Indicative Quotes",
        href: "/customer/quotes",
        icon: FileText,
        description: "View and compare your indicative premium quotes",
      },
    ],
  },
  {
    title: "Onboarding & Policy",
    items: [
      {
        title: "Applications",
        href: "/customer/applications",
        icon: ClipboardList,
        description: "Active proposal submissions & onboarding tracker",
      },
      {
        title: "Document Vault",
        href: "/customer/documents",
        icon: FolderOpen,
        description: "Secure KYC and medical record uploads",
      },
      {
        title: "Profile & Preferences",
        href: "/customer/profile",
        icon: User,
        description: "Demographics, address & language preferences",
      },
      {
        title: "Privacy & Consents",
        href: "/customer/consent",
        icon: ShieldCheck,
        description: "DPDP / IRDAI transparency and permissions",
      },
    ],
  },
];

export const ADMIN_NAV: NavSection[] = [
  {
    title: "Executive & Pipeline",
    items: [
      {
        title: "Business Overview",
        href: "/admin",
        icon: LayoutDashboard,
      },
      {
        title: "Lead Management",
        href: "/admin/leads",
        icon: Users,
      },
      {
        title: "Customer Directory",
        href: "/admin/customers",
        icon: UserCheck,
      },
      {
        title: "Application Pipeline",
        href: "/admin/applications",
        icon: ClipboardList,
      },
    ],
  },
  {
    title: "Operations & Intelligence",
    items: [
      {
        title: "Agent Control Centre",
        href: "/admin/agents",
        icon: BotMessageSquare,
      },
      {
        title: "Product Catalog",
        href: "/admin/products",
        icon: Briefcase,
      },
      {
        title: "Employee Management",
        href: "/admin/employees",
        icon: User,
      },
      {
        title: "Business Analytics",
        href: "/admin/analytics",
        icon: Calculator,
      },
      {
        title: "Conversion Funnel",
        href: "/admin/funnel",
        icon: Sparkles,
      },
    ],
  },
  {
    title: "Governance & Systems",
    items: [
      {
        title: "Compliance & Audit",
        href: "/admin/audit",
        icon: History,
      },
      {
        title: "Integrations Console",
        href: "/admin/integrations",
        icon: ShieldAlert,
      },
      {
        title: "System Settings",
        href: "/admin/settings",
        icon: Settings,
      },
    ],
  },
];

export const ADVISOR_NAV: NavSection[] = [
  {
    title: "Advisor Workbench",
    items: [
      {
        title: "My Workspace",
        href: "/advisor",
        icon: LayoutDashboard,
        description: "Executive cockpit, caseload, and SLA alerts",
      },
      {
        title: "Assigned Leads",
        href: "/advisor/leads",
        icon: UserCheck,
        description: "Prospect pipeline & engagement",
      },
      {
        title: "Customer Conversations",
        href: "/advisor/conversations",
        icon: MessageSquare,
        description: "AI chat transcripts & advisor notes",
      },
      {
        title: "Follow-up Management",
        href: "/advisor/follow-ups",
        icon: CalendarClock,
        description: "Scheduled calls, emails & tasks",
      },
    ],
  },
  {
    title: "Underwriting & Governance",
    items: [
      {
        title: "Underwriting Cases",
        href: "/advisor/underwriting",
        icon: Scale,
        description: "Risk triage, loadings & decisions",
      },
      {
        title: "Application Pipeline",
        href: "/advisor/applications",
        icon: ClipboardList,
        description: "Proposals across onboarding steps",
      },
      {
        title: "Document Verification",
        href: "/advisor/documents",
        icon: CheckCircle2,
        description: "KYC inspection, OCR match & sign-off",
      },
      {
        title: "Activity Timeline",
        href: "/advisor/timeline",
        icon: History,
        description: "Cross-domain audit event feed",
      },
      {
        title: "Notifications",
        href: "/advisor/notifications",
        icon: Bell,
        description: "Real-time alerts & SLA countdowns",
      },
    ],
  },
];

