/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],

  // Class-based dark mode — <html class="dark"> is toggled by themeStore.
  darkMode: 'class',

  theme: {
    extend: {
      colors: {
        // ── Theme-aware palette (auto-swaps between light & dark) ──
        // Values come from CSS variables defined in src/styles/globals.css.
        // Every existing `bg-bg`, `bg-surface`, `text-text`, `border-border`,
        // `text-textDim`, `bg-muted` class instantly becomes theme-aware.
        bg:       'rgb(var(--c-bg)       / <alpha-value>)',
        surface:  'rgb(var(--c-surface)  / <alpha-value>)',
        border:   'rgb(var(--c-border)   / <alpha-value>)',
        muted:    'rgb(var(--c-muted)    / <alpha-value>)',
        text:     'rgb(var(--c-text)     / <alpha-value>)',
        textDim:  'rgb(var(--c-text-dim) / <alpha-value>)',

        // ── Brand / status colours (unchanged across themes) ──
        accent:   '#00d9ff',
        success:  '#00ff88',
        error:    '#ff0055',
        warn:     '#ffaa00',

        // ── Settings-system semantic tokens (used by new components) ──
        app:           'rgb(var(--color-bg)        / <alpha-value>)',
        'app-fg':      'rgb(var(--color-fg)        / <alpha-value>)',
        card:          'rgb(var(--color-card)      / <alpha-value>)',
        'card-fg':     'rgb(var(--color-card-fg)   / <alpha-value>)',
        'border-app':  'rgb(var(--color-border)    / <alpha-value>)',
        primary:       'rgb(var(--color-primary)   / <alpha-value>)',
        'primary-fg':  'rgb(var(--color-primary-fg)/ <alpha-value>)',
        'muted-app':   'rgb(var(--color-muted)     / <alpha-value>)',
        'muted-fg':    'rgb(var(--color-muted-fg)  / <alpha-value>)',
      },

      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
        ui:   ['Inter', 'system-ui', 'sans-serif'],
      },

      keyframes: {
        pulse_glow: {
          '0%, 100%': { opacity: '1',   transform: 'scale(1)' },
          '50%':      { opacity: '0.6', transform: 'scale(1.06)' },
        },
        flow: {
          '0%':   { strokeDashoffset: '100' },
          '100%': { strokeDashoffset: '0' },
        },
        slide_up: {
          '0%':   { opacity: '0', transform: 'translateY(12px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slide_in_right: {
          '0%':   { opacity: '0', transform: 'translateX(100%)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
      },
      animation: {
        pulse_glow:     'pulse_glow 2s ease-in-out infinite',
        flow:           'flow 1.5s linear infinite',
        slide_up:       'slide_up 0.3s ease-out',
        slide_in_right: 'slide_in_right 0.3s ease-out',
      },
    },
  },
  plugins: [],
}
