---
name: Active-Trace
colors:
  surface: '#f9f9f9'
  surface-dim: '#dadada'
  surface-bright: '#f9f9f9'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f3f3'
  surface-container: '#eeeeee'
  surface-container-high: '#e8e8e8'
  surface-container-highest: '#e2e2e2'
  on-surface: '#1a1c1c'
  on-surface-variant: '#43474e'
  inverse-surface: '#2f3131'
  inverse-on-surface: '#f0f1f1'
  outline: '#74777f'
  outline-variant: '#c4c6cf'
  surface-tint: '#455f88'
  primary: '#002045'
  on-primary: '#ffffff'
  primary-container: '#1a365d'
  on-primary-container: '#86a0cd'
  inverse-primary: '#adc7f7'
  secondary: '#545f72'
  on-secondary: '#ffffff'
  secondary-container: '#d5e0f7'
  on-secondary-container: '#586377'
  tertiary: '#002141'
  on-tertiary: '#ffffff'
  tertiary-container: '#003765'
  on-tertiary-container: '#68a2e9'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d6e3ff'
  primary-fixed-dim: '#adc7f7'
  on-primary-fixed: '#001b3c'
  on-primary-fixed-variant: '#2d476f'
  secondary-fixed: '#d8e3fa'
  secondary-fixed-dim: '#bcc7dd'
  on-secondary-fixed: '#111c2c'
  on-secondary-fixed-variant: '#3c475a'
  tertiary-fixed: '#d3e4ff'
  tertiary-fixed-dim: '#a2c9ff'
  on-tertiary-fixed: '#001c38'
  on-tertiary-fixed-variant: '#004881'
  background: '#f9f9f9'
  on-background: '#1a1c1c'
  surface-variant: '#e2e2e2'
typography:
  display-lg:
    fontFamily: Source Serif 4
    fontSize: 42px
    fontWeight: '600'
    lineHeight: 52px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Source Serif 4
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
  headline-sm:
    fontFamily: Source Serif 4
    fontSize: 20px
    fontWeight: '500'
    lineHeight: 28px
  body-lg:
    fontFamily: IBM Plex Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: IBM Plex Sans
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-caps:
    fontFamily: IBM Plex Sans
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
  mono-data:
    fontFamily: IBM Plex Mono
    fontSize: 13px
    fontWeight: '450'
    lineHeight: 18px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base: 4px
  gutter: 16px
  margin-mobile: 16px
  margin-desktop: 32px
  bento-gap: 12px
---

## Brand & Style
The design system is engineered for the rigors of high-dimensional data annotation, where precision and long-term focus are paramount. The personality is authoritative, methodical, and academic—echoing the clarity of a peer-reviewed journal while maintaining the efficiency of a high-performance developer tool.

The "Neo-Latex" aesthetic leverages substantial whitespace, purposeful horizontal rules, and a restrained color palette to minimize cognitive load. It utilizes a **Bento Grid** layout to modularize complex datasets, ensuring that statistics, visualization windows, and annotation controls remain distinct and navigable. The style leans toward a **Minimalist-Professional** hybrid, prioritizing legibility and information density over decorative elements.

## Colors
The palette is rooted in academic tradition. The background utilizes a subtle off-white (`#fcfcfc`) to mitigate the harsh glare of pure white during extended research sessions. 

- **Primary:** Deep Academic Blue (`#1a365d`) for headers, primary actions, and structural grounding.
- **Secondary:** Slate Greys for metadata and supportive text.
- **Data Signals:** A Viridis-inspired color-blind-safe scale is used for heatmaps, density plots, and importance weights. This ensures that quantitative gradients are perceivable by all users regardless of color vision deficiency.

## Typography
The typographic system pairs a literary serif with a systematic sans-serif to bridge the gap between "Research Paper" and "Interactive Tool."

- **Headings:** Source Serif 4 provides a formal, trustworthy tone. Use it for page titles, section headers, and modal titles.
- **Interface:** IBM Plex Sans is the workhorse for labels, inputs, and navigation. Its high x-height and clear terminals ensure legibility in data-dense grids.
- **Data Display:** For coordinate values, indices, and timestamps, a monospaced variant (IBM Plex Mono) is used to maintain vertical alignment in lists and tables.

## Layout & Spacing
The design system employs a **Fixed-Fluid Hybrid** model. While the outer container respects a maximum width of 1600px for readability, the internal **Bento Grid** modules are fluid within their allocated column spans.

- **Bento Modules:** Use a 12-column grid. Visualization windows should typically span 8 columns, while control panels and metadata sidebars span 4.
- **Information Density:** Vertical rhythm is tight (using a 4px baseline) to allow more data on-screen without scrolling. 
- **Borders:** Modules are separated by 1px borders in a light grey tint rather than heavy shadows, maintaining the "Latex" document feel.

## Elevation & Depth
In line with the Neo-Latex aesthetic, depth is conveyed through **Tonal Layering** and **Fine Outlines** rather than traditional shadows.

- **Level 0 (Surface):** The `#fcfcfc` background.
- **Level 1 (Modules):** Bento cards use a white background with a 1px solid border (`#e2e8f0`). No shadow is applied to standard modules.
- **Level 2 (Overlays):** Modals and dropdowns use a very slight ambient shadow (4px blur, 5% opacity) and a distinct border to separate them from the underlying content.
- **Active State:** Selected data points or active modules are indicated by a 2px primary blue left-border accent.

## Shapes
To maintain a formal and clinical appearance, the design system uses a "Soft" roundedness profile.

- **General Elements:** Buttons, input fields, and bento modules use a 4px (`0.25rem`) corner radius. This provides a modern touch without sacrificing the structural, rectangular integrity of an academic layout.
- **Data Points:** In scatter plots or clusters, points should be crisp circles to ensure precision.

## Components
- **Buttons:** Primary buttons are solid `#1a365d` with white text. Secondary buttons use a "Ghost" style: 1px border with primary color text.
- **Data Bento Cards:** Each card must have a header with a `label-caps` title and an optional 1px bottom border.
- **Input Fields:** Minimalist design with a bottom-border only or a light 4-sided stroke. Focus states are marked by a transition to the primary blue border.
- **Chips / Labels:** Small, rectangular tags with light grey backgrounds (`#edf2f7`) for category tagging and status indicators.
- **Annotation Tooltip:** A high-contrast dark overlay that appears on data-point hover, displaying precise coordinate values in `mono-data` typography.
- **Progress Bars:** Thin 4px bars using the Viridis scale to indicate annotation completion or model confidence levels.