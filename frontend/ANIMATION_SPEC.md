# Matrix Motion Specification

## Status

Saved for a future, step-by-step implementation. Do not install Motion or change the current UI until explicitly requested.

## Core constraints

- Use the latest `motion` package with `motion/react`.
- Keep the existing layout, functionality, and business logic unchanged.
- Use purposeful, subtle animations only: typically 200-500ms.
- Prefer springs for physical UI interactions where appropriate.
- Respect `prefers-reduced-motion`, preserve accessibility, and avoid unnecessary work.
- No continuous animation, flashing, excessive rotation, bouncing, or distracting effects.
- Use viewport-triggered chart animation once only.

## Architecture to add later

Create `src/animations/` (or `src/lib/motion/`) with reusable variants and helpers:

- `fadeUp`
- `fadeIn`
- `slideLeft`
- `slideRight`
- `slideUp`
- `staggerContainer`
- `staggerItem`
- `pageTransition`
- `modalAnimation`
- `drawerAnimation`
- `buttonHover`
- `cardHover`

Use `AnimatePresence` for route, modal, drawer, list-removal, and loading exits. Avoid duplicating animation objects in components.

## Planned animation coverage

### Global

- Page fade transitions and smooth route layout changes.
- Shared-layout transitions only where they clarify an interaction.
- Loading and skeleton fade states.

### Navbar and sidebar

- Navbar slide-down on its first load.
- Notification/profile dropdown and mobile-menu enter/exit.
- Search expansion.
- Sidebar slide-in on load, active-indicator movement, collapse/expand, icon hover feedback, and label fade.

### Dashboard

- Welcome card first appearance.
- Staggered statistic cards.
- Quick-action cards and recent-activity list entrance.
- No repeating dashboard motion.

### Career prediction (richest sequence)

1. Predict button feedback.
2. Loading state and AI-processing transition.
3. Prediction-card reveal.
4. Confidence-meter animation.
5. Placement-readiness animation.
6. Staggered skill-gap cards.
7. Roadmap timeline expansion.

### Profile and forms

- Edit mode, save-success confirmation, progress bar, and image-preview transitions.
- Input focus transition, validation shake, submit loading, and success state.

### Shared components

- Cards: fade-up on first view, minimal hover elevation, smooth shadow/layout transition.
- Buttons: hover/tap scale, CSS ripple-like feedback, loading state.
- Modals: fading backdrop, dialog scale, and smooth exit.
- Lists: staggered entrance, add/remove layout transitions, animated filtering.
- Charts: animate once when entering viewport.

## Implementation order

1. Install Motion and create the shared animation primitives plus reduced-motion support.
2. Add global route, loading, navbar, and sidebar motion.
3. Add dashboard-only entrance and interaction motion.
4. Add profile, forms, modals, and reusable list/card/button behavior.
5. Implement the career-prediction flow.
6. Verify keyboard access, reduced-motion behavior, mobile performance, and route transitions.
