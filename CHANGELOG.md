# Changelog

All notable changes to the **NEET PG Tools** project will be documented in this file.

## [Unreleased]

## [2.0.0] - 2025-12-06
### Added
- **Dark Mode Theme**: A comprehensive dark theme using Slate-900 backgrounds and high-contrast text.
- **Tailwind CSS Integration**: Replaced Bootstrap with Tailwind CSS for modern, utility-first styling.
- **Responsive Design**: Improved mobile responsiveness across all pages.
- **Versioned Assets**: Added cache-busting (?v=darkmode) to CSS links to ensure immediate updates.

### Changed
- **Home Page**: Refactored with a modern grid layout and gradient typography. Buttons now align perfectly at the bottom of equal-height cards.
- **Course Predictor**: 
    - Updated UI to a glassmorphism card design.
    - Improved feedback mechanism for "No courses found".
    - Fixed data handling to correctly display Course Names instead of failing object references.
- **Best Colleges**: 
    - Fixed table column keys to correctly map internal API data to the view.
    - Styled tables with dark mode compatible rows and hover effects.
- **Rank Predictor**: Centralized the design and added visual emphasis to the result.

### Fixed
- **Mobile Layout**: Fixed specific issues with horizontal scrolling on smaller screens.
- **Browser Caching**: Resolved issue where stubborn old CSS was being loaded by the browser.

## [1.0.0] - Initial Release
- Basic Flask application structure.
- Course Predictor, College Finder, and Rank Predictor tools.
- Bootstrap 5 based styling.
