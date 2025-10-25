import { MoonIcon, SunIcon } from '@heroicons/react/24/outline'
import { useTheme } from './ThemeContext'

export function ThemeToggle() {
    const { theme, toggleTheme } = useTheme()

    return (
        <button
            onClick={toggleTheme}
            className="flex items-center justify-center w-10 h-10 rounded-lg bg-background-secondary border border-border hover:bg-background-tertiary transition-colors duration-200"
            aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
            title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
        >
            {theme === 'light' ? (
                <MoonIcon className="w-5 h-5 text-foreground-secondary" />
            ) : (
                <SunIcon className="w-5 h-5 text-foreground-secondary" />
            )}
        </button>
    )
}
