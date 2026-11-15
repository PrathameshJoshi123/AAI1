export type InsuranceStatus =
  | "DRAFT"
  | "IN_PROGRESS"
  | "QUALIFIED"
  | "QUOTED"
  | "PROPOSAL_SUBMITTED"
  | "UNDER_REVIEW"
  | "ESCALATED"
  | "APPROVED"
  | "ISSUED"
  | "REJECTED";

export interface BreadcrumbItem {
  label: string;
  href?: string;
}

export interface PaginationMeta {
  page: number;
  pageSize: number;
  totalItems: number;
  totalPages: number;
}

