# Mosaic UI - Color Schema & Theme System

## Overview

This project implements a comprehensive color schema and dark mode system using Tailwind CSS v4 with custom CSS variables for consistent theming across all components.

## Color Schema

### Primary Colors
- **Primary**: Blue-based color palette (`primary-50` to `primary-950`)
- **Secondary**: Slate-based neutral palette (`secondary-50` to `secondary-950`)
- **Success**: Green-based palette (`success-50` to `success-950`)
- **Warning**: Amber-based palette (`warning-50` to `warning-950`)
- **Error**: Red-based palette (`error-50` to `error-950`)
- **Neutral**: Gray-based palette (`neutral-50` to `neutral-950`)

### Semantic Colors
The system uses CSS variables that automatically adapt to light/dark mode:

- `bg-background` - Main background color
- `bg-background-secondary` - Secondary background
- `bg-background-tertiary` - Tertiary background
- `text-foreground` - Main text color
- `text-foreground-secondary` - Secondary text
- `text-foreground-tertiary` - Tertiary text
- `border-border` - Main border color
- `border-border-secondary` - Secondary border
- `bg-card` - Card background
- `text-card-foreground` - Card text
- `bg-input` - Input background
- `text-input-foreground` - Input text
- `ring-ring` - Focus ring color

## Dark Mode

### Features
- **Automatic detection**: Respects system preference on first visit
- **Manual toggle**: Theme toggle button in header
- **Persistent storage**: Remembers user preference in localStorage
- **Smooth transitions**: 300ms transitions for all color changes
- **System sync**: Auto-switches when system preference changes (if no manual preference set)

### Usage

```tsx
import { useTheme } from './ThemeContext'

function MyComponent() {
  const { theme, toggleTheme, setTheme } = useTheme()
  
  return (
    <div className="bg-background text-foreground">
      <button onClick={toggleTheme}>
        Switch to {theme === 'light' ? 'dark' : 'light'} mode
      </button>
    </div>
  )
}
```

## Component Styling Guidelines

### Use Semantic Colors
```tsx
// ✅ Good - Uses semantic colors that adapt to theme
<div className="bg-card border border-border text-card-foreground">

// ❌ Bad - Hardcoded colors that don't adapt
<div className="bg-white border border-gray-200 text-black">
```

### Consistent Spacing & Shadows
- Use `shadow-soft`, `shadow-medium`, `shadow-strong` for consistent elevation
- Use `rounded-xl`, `rounded-2xl`, `rounded-3xl` for consistent border radius
- Use `gap-3`, `gap-4`, `gap-6` for consistent spacing

### Button Styles
```tsx
// Primary action
<button className="bg-primary-600 hover:bg-primary-700 text-white">

// Success action
<button className="bg-success-600 hover:bg-success-700 text-white">

// Error action
<button className="bg-error-600 hover:bg-error-700 text-white">

// Secondary action
<button className="bg-secondary-600 hover:bg-secondary-700 text-white">
```

## Configuration Files

- `tailwind.config.js` - Defines color palette and theme configuration
- `src/index.css` - CSS variables for light/dark mode
- `src/ThemeContext.tsx` - React context for theme management
- `src/ThemeToggle.tsx` - Theme toggle component

## Development

To add new components with consistent styling:

1. Use semantic color classes (`bg-background`, `text-foreground`, etc.)
2. Add proper TypeScript interfaces
3. Include hover states and transitions
4. Test in both light and dark modes
5. Use the theme toggle to verify color consistency
