# Saṃśodhakaḥ — UI/UX Documentation

## Overview

The Saṃśodhakaḥ frontend provides a comprehensive research workspace for scholars to generate, verify, and export evidence-grounded scientific content. This document describes the user interface architecture, design principles, and component structure.

## Design Principles

1. **Researcher-Centric**: Designed for academic workflows with familiar terminology
2. **Evidence-First**: Always shows evidence support and verification status
3. **Minimalist**: Clean interface that doesn't distract from research content
4. **Responsive**: Works on desktop and mobile devices
5. **Accessible**: Follows WCAG guidelines for academic accessibility

## Architecture

### Frontend Stack

- **Framework**: React 18+
- **Routing**: React Router v6
- **Styling**: CSS Modules with responsive design
- **State Management**: React Context + localStorage for temporary persistence
- **API Communication**: Fetch API with proper error handling

### Component Structure

```
frontend/src/
├── components/          # Reusable UI components
├── features/            # Feature-specific modules
├── layouts/             # Layout templates
├── services/            # API services
├── styles/              # Global styles and variables
├── types/               # TypeScript types (future)
├── utils/               # Utility functions
└── App.js               # Main application entry
```

## Main Features

### 1. Research Workspace

**Location**: `/` (Home page)

**Component**: `ResearchWorkspace.js`

**Purpose**: Central hub for research paper generation and management

**Key UI Elements**:

- **Document Controls**: Input fields for document ID, section type, topic, and related work
- **Action Buttons**: Generate Outline, Generate Section, Verify Section
- **Feature Cards**: Quick access to all major features
- **Export Options**: Direct export to scholarly formats
- **Status Feedback**: Success/error alerts with clear messaging

**Workflow**:

1. User enters document ID and research parameters
2. System generates evidence-grounded content
3. User verifies claims and evidence support
4. User exports to desired format

### 2. Document Library

**Location**: `/library`

**Component**: `DocumentLibrary.js`

**Purpose**: Manage uploaded research documents

**Features**:

- Document upload and management
- Metadata display (title, authors, year)
- Status tracking (parsed, indexed, etc.)
- Search and filtering capabilities

### 3. Drafting Workspace

**Location**: `/draft`

**Component**: `DraftingWorkspace.js`

**Purpose**: Refine and edit generated research sections

**Features**:

- Rich text editing interface
- Evidence attachment and citation management
- Section structure organization
- Real-time preview

### 4. Evidence Explorer

**Location**: `/evidence`

**Component**: `EvidenceExplorer.js`

**Purpose**: Browse extracted semantic units and evidence graphs

**Features**:

- Semantic unit visualization
- Evidence graph navigation
- Claim- evidence relationship mapping
- Source document tracing

### 5. Verification Dashboard

**Location**: `/verification`

**Component**: `VerificationDashboard.js`

**Purpose**: Check claim support and evidence quality

**Features**:

- Claim verification results
- Evidence strength indicators
- Contradiction detection
- Confidence scoring
- Actionable recommendations

### 6. Export Center

**Location**: `/export`

**Component**: `ExportCenter.js`

**Purpose**: Export research content to scholarly formats

**Features**:

- Format selection (Markdown, LaTeX, BibTeX, DOCX)
- Export configuration options
- Batch export capabilities
- Format-specific preview

## UI Components

### Header Component

**File**: `components/Header.js`

**Features**:

- Application logo and branding
- Navigation menu with links to all features
- Responsive design for mobile devices

### Main Layout

**File**: `layouts/MainLayout.js`

**Structure**:

```html
<Header />
<MainContent>
  <Outlet />  <!-- Feature content -->
</MainContent>
<Footer />
```

## Styling System

### CSS Architecture

- **CSS Modules**: Scoped styles for each component
- **Global Styles**: Base styles and variables in `styles/base.css`
- **Design Tokens**: CSS variables for colors, spacing, typography
- **Responsive Breakpoints**: Mobile-first approach with media queries

### Color Palette

```css
:root {
  --primary-color: #3498db;
  --secondary-color: #2ecc71;
  --accent-color: #e74c3c;
  --text-color: #2c3e50;
  --background-color: #f8f9fa;
  --card-background: #ffffff;
  --border-color: #e0e0e0;
  --success-color: #27ae60;
  --warning-color: #f39c12;
  --error-color: #c0392b;
}
```

### Typography

- **Primary Font**: System sans-serif stack
- **Headings**: Bold, hierarchical typography
- **Body Text**: Readable line height and spacing
- **Code**: Monospace for technical content

## User Flows

### Research Paper Generation

1. **Start**: User lands on Research Workspace
2. **Input**: User enters document ID, selects section type, specifies topic
3. **Generate**: User clicks "Generate Section"
4. **Review**: System displays generated content in Drafting Workspace
5. **Verify**: User verifies claims in Verification Dashboard
6. **Export**: User exports final document in desired format

### Document Management

1. **Upload**: User uploads documents in Document Library
2. **Process**: System parses and indexes documents
3. **Browse**: User explores extracted content in Evidence Explorer
4. **Use**: User references documents in research generation

## API Integration

### Backend Endpoints Used

- **Drafting**: `/api/drafting/outline`, `/api/drafting/section`
- **Verification**: `/api/verification/section-claims`
- **Export**: `/api/export/paper`, `/api/export/formats`
- **Documents**: `/api/documents/` (various endpoints)

### Error Handling

- Network error detection and user notification
- Form validation with clear error messages
- Loading states during API operations
- Graceful degradation when features are unavailable

## Accessibility Features

- Semantic HTML structure
- Keyboard navigation support
- ARIA attributes for interactive elements
- Color contrast compliance
- Screen reader friendly content

## Future Enhancements

- Dark mode support
- Customizable workspace layouts
- Collaborative editing features
- Advanced search and filtering
- User preferences and settings
- Internationalization support

## Development Guidelines

1. **Component Structure**: Keep components small and focused
2. **State Management**: Use React state for local UI state
3. **API Calls**: Centralize API logic in services
4. **Error Handling**: Always provide user feedback
5. **Performance**: Optimize rendering and minimize re-renders
6. **Testing**: Write unit tests for critical components

This UI/UX system provides researchers with a comprehensive, evidence-grounded workspace for scientific research paper generation and management.