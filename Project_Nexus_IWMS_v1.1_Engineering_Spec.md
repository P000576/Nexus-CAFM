Project Nexus IWMS (v1.1) — Engineering Specification
=====================================================

Author: Gollapudi Umamaheswara Dattu

Version: 1.1

Date: October 7, 2025

Status: For Development

Overview
--------
This document provides the detailed functional and non-functional requirements for Project Nexus, a cloud-native, enterprise-grade Integrated Workplace Management System (IWMS). It expands upon the product-level requirements and serves as the primary technical guide for engineering, QA, and DevOps for the MVP delivery.

Vision
------
To build a unified, scalable, and user-centric IWMS that combines comprehensive functionality with a modern, intuitive user experience, addressing the well-documented usability gaps in the current market.

1. Introduction
---------------
This engineering specification translates the Product Requirements Document (v1.0) into a granular, actionable blueprint for development. It contains functional epics, acceptance criteria, and non-functional requirements (NFRs) to guide implementation and verification.

2. Scope
---------
2.1 In Scope (Minimum Viable Product - MVP)

- Core Modules: Space & Occupancy Management, Corrective & Preventive Maintenance, Asset Management, Real Estate & Lease Management (ASC 842/IFRS 16 compliant), Foundational Capital Project Management.
- User Experience: Mobile-first Employee Experience (WEX) app for desk/room booking and service requests.
- Analytics: Role-based dashboards for operational metrics.
- Integrations: Bi-directional Autodesk Revit sync and open REST APIs for core objects.
- Deployment: Multi-tenant SaaS on AWS.

2.2 Out of Scope (Future Releases)

- On-premise deployment option.
- Advanced Capital Project Management features (procurement, bid management).
- Full Sustainability & Energy Management (only basic consumption tracking in MVP).
- Advanced AI/ML features (predictive maintenance deferred; MVP to collect data for future models).
- Pre-built ERP/HRIS connectors (e.g., SAP, Workday) — post-MVP.

3. Functional Requirements
--------------------------
The system will be implemented as modular services with clear APIs and shared data models. Following epics and user stories specify MVP functionality and acceptance criteria.

Epic 1: Core Platform & System Administration
---------------------------------------------

ADM-01 — RBAC and Roles

User story: As a System Administrator, I want to configure user roles and permissions so that I can enforce role-based access control (RBAC) and ensure data security.

Acceptance criteria:
- Support custom roles (Facility Manager, Technician, Employee, etc.).
- Permissions assignable at module, record, and field level.
- Provide at least four default license levels: Self-Service, Work Process, Analysis, Process Owner.

ADM-02 — User Accounts & Authentication

User story: As a System Administrator, I want to manage user accounts and authentication so that I can securely onboard and offboard users.

Acceptance criteria:
- Manual user creation and bulk import via CSV.
- Design for future identity provider integration (LDAP, SAML, OIDC).
- Users may be assigned multiple security roles.

ADM-03 — System Settings & Terminology

User story: As a System Administrator, I want to configure system-wide settings and terminology so that the platform aligns with our organization's branding and language.

Acceptance criteria:
- Upload company logo and basic theming.
- Terminology customization (e.g., rename "Building" to "Site").
- Configurable approval workflows and notifications.

ADM-04 — Developer API

User story: As a Developer, I need a well-documented REST API for core data objects so that I can build integrations with other enterprise systems.

Acceptance criteria:
- CRUD endpoints for Buildings, Floors, Rooms, Employees, Assets, Work Orders.
- OpenAPI (Swagger) specification and auth details.
- Example payloads and error codes documented.

Epic 2: Space & Occupancy Management
------------------------------------

SP-01 — Revit Synchronization

User story: As a Space Planner, I want to import and synchronize floor plan data from Autodesk Revit so that our space inventory is accurate.

Acceptance criteria:
- Provide a Smart Client Extension for Revit supporting bi-directional synchronization.
- Sync room boundaries, numbers, and areas from Revit to Nexus.
- Allow Nexus data (e.g., department allocation) to be visualized thematically in Revit.

SP-02 — Hierarchical Inventory

User story: As a Space Planner, I want to view and manage our space inventory in a hierarchical structure (Portfolio > Building > Floor > Room).

Acceptance criteria:
- Tree-like navigation for real estate objects.
- Each object stores key attributes (address, gross area, room capacity, etc.).
- Support space chargeback calculations based on area allocation.

SP-03 — Interactive Floor Plans

User story: As a Department Manager, I want to view our department's space allocation on an interactive floor plan.

Acceptance criteria:
- Web viewer that renders floor plans with departmental color highlights.
- Clickable room details (room name, occupant, department).
- Support standard CAD/BIM formats for import and rendering.

SP-04 — Employee Occupancy

User story: As a Facility Manager, I want to manage employee occupancy data (desk/office assignments).

Acceptance criteria:
- Assign employees to rooms or desks; bulk CSV import/update.
- Integration with WEX to show colleague locations.

Epic 3: Asset & Maintenance Management
-------------------------------------

AM-01 — Asset Registry

User story: As a Facility Manager, I want a centralized asset registry.

Acceptance criteria:
- Asset records with standard fields (ID, name, location, manufacturer, serial, warranty date).
- Link assets to locations on floor plans.
- QR code generation per asset for mobile scanning.

AM-02 — Mobile Service Requests

User story: As an Employee, I want to submit corrective maintenance requests from mobile with photos.

Acceptance criteria:
- WEX app supports "Request Service" with issue type, location (list or QR scan), and photo uploads.
- Push notifications for status changes (Created, In Progress, Completed).

AM-03 — Work Order Lifecycle

User story: As a Maintenance Manager, I want to manage full work order lifecycle.

Acceptance criteria:
- Service requests convert to work orders automatically.
- Assignable to technicians/teams; track creation date, assigned tech, status, completion date, labor and parts costs.

AM-04 — Preventive Maintenance

User story: As a Maintenance Manager, I want PM schedules for critical assets.

Acceptance criteria:
- PM schedules by fixed intervals (monthly, quarterly, etc.).
- Automatic generation of PM work orders on schedule.
- PM work orders include checklists.

Epic 4: Real Estate & Lease Management
-------------------------------------

RE-01 — Lease Repository

User story: As a Lease Administrator, I want a central repository for lease contracts.

Acceptance criteria:
- Store lease metadata (landlord/tenant, dates, financial terms).
- Attach lease documents (PDF) to records.
- Dashboard for critical dates within 90 days.

RE-02 — Lease Accounting

User story: As a Lease Accountant, I want ASC 842 / IFRS 16 lease accounting.

Acceptance criteria:
- Generate amortization schedules and journal entries.
- Support operating and finance lease calculations.
- Export financial reports (CSV) for balance sheet and P&L impact.

RE-03 — Portfolio Map View

User story: As a Real Estate Manager, I want to view the property portfolio on a map.

Acceptance criteria:
- Map visualization (Mapbox/Google Maps) plotting properties.
- Click pins for summary details.

Epic 5: Capital Project Management (Foundational)
-------------------------------------------------

CP-01 — Project Records

User story: As a Project Manager, I want to create/manage project records.

Acceptance criteria:
- Project records with name, type, budget, schedule, status.
- Link projects to buildings/properties.
- Dashboard summarizing active project status.

CP-02 — Budget Tracking

User story: As a Project Manager, I want to track project budgets and costs.

Acceptance criteria:
- Track Original Budget, Approved Changes, Commitments, Actual Spend.
- Manually log costs against projects.
- Dashboard with budget vs actual variance.

CP-03 — Milestones

User story: As a Project Manager, I want to define and track project milestones.

Acceptance criteria:
- Create milestone lists with target dates.
- Mark milestones complete.
- Dashboard shows upcoming/overdue milestones.

Epic 6: Workplace Experience (WEX)
---------------------------------

WEX-01 — Desk Booking

User story: As a Hybrid Employee, I want to book a desk for a specific day using mobile.

Acceptance criteria:
- Interactive floor plan shows real-time desk availability.
- Filter by date/area, one-tap booking, confirmation.

WEX-02 — Room Booking & Calendar Integration

User story: As an Employee, I want to book meeting rooms and invite attendees.

Acceptance criteria:
- Integrate with Microsoft 365 / Google Calendar for availability.
- Search rooms by capacity, time, amenities.
- Booking creates calendar event in corporate calendar.

WEX-03 — Find a Colleague

User story: As an Employee, I want to find a colleague's location on a floor plan.

Acceptance criteria:
- Search employee directory; highlight booked desk for the day if available.

4. Non-Functional Requirements (NFRs)
-----------------------------------

Performance

- Page load: user-facing pages/dashboards <= 3s under normal load.
- API Response: 99% calls < 500ms.

Scalability

- Support >= 10,000 concurrent users and portfolios > 1,000 properties.
- DB schema designed to handle millions of assets and work orders.

Availability

- 99.9% uptime SLA (excluding scheduled maintenance).
- Scheduled maintenance communicated 48 hours ahead.

Security

- Encryption at rest (AES-256) and in transit (TLS 1.2+).
- Platform designed for SOC 2 Type 2 and ISO 27001 compliance.
- Annual third-party penetration testing.

Integration

- RESTful APIs that follow OpenAPI and use OAuth 2.0.
- Multi-tier web architecture for future ERP/HRIS integrations.

Data Migration

- Provide CSV templates and a data mapping UI with validation and error reporting.

Usability

- Intuitive, responsive UI targeting WCAG 2.1 AA accessibility.

Deployment

- Deploy to AWS using scalable services (EC2, RDS, S3). Architect to minimize provider lock-in where feasible.

5. Assumptions
--------------
- Development team will have access to Autodesk Revit licenses and sample models.
- Initial launch: English only. Localization planned for future releases.
- Test accounts for Microsoft 365 and Google Workspace will be provided for calendar integration testing.

Engineering "Contract" (small)
------------------------------
Purpose: Short, actionable contract for implementation teams mapping inputs, outputs and success criteria for MVP features.

- Inputs: Revit models (BIM), CSV data exports from legacy systems (assets, employees, leases), OAuth credentials for calendar integration, and user stories/acceptance criteria defined above.
- Outputs: Multi-tenant SaaS services, OpenAPI specs, mobile WEX app binaries (iOS/Android builds or PWAs), data migration utilities, automated test suites, and deployment manifests (Terraform/CloudFormation).
- Success criteria: All stated acceptance criteria satisfied for each epic; CI pipeline green; basic load test showing API latency within NFRs for a representative workload; security scan and basic penetration test checklist completed.

Edge cases & considerations
--------------------------
- Empty or malformed CSV imports — provide validation reports and a rollback path.
- Large BIM models causing sync timeouts — implement chunked sync and idempotent updates.
- Calendar provider rate limits — implement exponential backoff and caching strategies.
- Concurrent edits to space/asset data — optimistic concurrency control and audit trails.

Quality Gates & Verification
----------------------------
- Build: Automated builds for backend services and WEX app on each PR.
- Lint/Typecheck: Enforce language-specific linters and static typing (TypeScript/Python rules as applicable).
- Unit tests: ≥ 80% coverage for core domain logic.
- Integration tests: Revit sync happy-path and calendar integration smoke tests.
- Security checks: SAST and dependency vulnerability scans in CI.

Deliverables (MVP)
------------------
- Source code repos for backend microservices and frontend WEX app.
- OpenAPI specs and API developer portal documentation.
- Data migration templates and a small CLI or web UI for loading CSVs.
- A minimal deployment automation (Terraform/CloudFormation + CI pipeline) to provision dev/staging environments on AWS.

Next Steps (recommended)
------------------------
1. Break this spec into prioritized backlog items (Epics -> Features -> Stories) in the team's issue tracker.
2. Create a high-level system architecture diagram showing services, data stores, and integration points (Revit, Calendar, Auth).
3. Produce an initial API contract (OpenAPI) for Buildings/Floors/Rooms/Employees/Assets/WorkOrders and scaffold a developer portal.
4. Provision a shared AWS sandbox and CI/CD pipeline templates.

Notes & references
------------------
References are the numbered placeholders embedded in acceptance criteria where industry or third-party references were noted in the product-level document.

---

File purpose: This file is the engineering-specification artifact for Project Nexus v1.1 (MVP) and is intended to live in the repository root for visibility by product, engineering, QA, and DevOps teams.
