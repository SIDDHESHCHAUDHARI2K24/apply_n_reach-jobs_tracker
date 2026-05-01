# UI Consistency Checklist

Use this checklist while validating each frontend route after styling updates or framework migrations.

## Global

- Global CSS is loaded and Tailwind utilities resolve.
- Sidebar tokens (`--sidebar-*`) and content tokens (`--content-bg`, `--surface`) render correctly.
- Heading/body typography uses design tokens (`--font-heading`, `--font-ui`).
- No unstyled controls (default browser button/input styles) on core pages.
- Focus states are visible for keyboard users.

## Auth

- Login/Register/Reset pages render card layout and brand styling.
- Input, label, helper/error states are consistent across all forms.
- Primary/secondary button styles match token system.

## Profile

- `ProfileShell` tab navigation shows active state and hover state.
- All section pages (personal, education, experience, projects, research, certifications, skills) share spacing and card patterns.
- Form rows and list cards use consistent borders/radius/typography.

## Job Profiles

- List page filters, cards, and status badges are styled consistently.
- Editor section navigation, content panel, and render panel use shared visual tokens.
- Loading and empty states match global style language.

## Job Tracker

- Table headers/rows/status badges are legible and consistent.
- Drawer/panel surfaces and borders match tokenized styling.
- Ingestion panel controls and actions use the same button/input primitives.

## Opening Resume

- Shell navigation and section pages match profile module styling.
- Read-only content cards and editable controls follow shared spacing and typography.

## Settings

- Account/session cards render with consistent panel styles.
- Destructive action style for sign-out is distinct and accessible.

