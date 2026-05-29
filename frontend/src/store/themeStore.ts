/**
 * themeStore — global theme state.
 *
 * Zustand is used (not React Context) for consistency with the rest of the
 * Agent Factory frontend which already uses Zustand for every other store.
 *
 * Responsibilities:
 *   • Hold the user's preference   — 'light' | 'dark' | 'system'
 *   • Hold the effective theme     — 'light' | 'dark'  (what's actually applied)
 *   • Persist the preference to   localStorage under THEME_KEY
 *   • Apply the `dark` class to  <html>  whenever the effective theme changes
 *   • Listen to prefers-color-scheme and react when 'system' is active
 *
 * The anti-flicker inline <script> in index.html already sets the correct class
 * on <html> *before* React mounts, so the initial paint is never wrong.
 */
import { create } from 'zustand'

// ── constants ────────────────────────────────────────────────────────────────

export const THEME_KEY = 'theme-preference'

export type ThemePreference = 'light' | 'dark' | 'system'
export type EffectiveTheme  = 'light' | 'dark'

// ── utilities ────────────────────────────────────────────────────────────────

/** Safely read the stored preference, falling back to 'system'. */
function readStoredPreference(): ThemePreference {
  if (typeof window === 'undefined') return 'system'
  try {
    const raw = window.localStorage.getItem(THEME_KEY)
    if (raw === 'light' || raw === 'dark' || raw === 'system') return raw
  } catch {
    /* private mode / storage disabled — fall through */
  }
  return 'system'
}

/** Detect whether the OS currently prefers dark mode. */
function systemPrefersDark(): boolean {
  if (typeof window === 'undefined' || !window.matchMedia) return false
  return window.matchMedia('(prefers-color-scheme: dark)').matches
}

/** Resolve a preference into a concrete 'light' | 'dark' value. */
function resolveEffective(pref: ThemePreference): EffectiveTheme {
  if (pref === 'system') return systemPrefersDark() ? 'dark' : 'light'
  return pref
}

/** Apply the theme to <html> by toggling the `dark` class. */
function applyTheme(effective: EffectiveTheme): void {
  if (typeof document === 'undefined') return
  const root = document.documentElement
  root.classList.toggle('dark', effective === 'dark')
  root.dataset.theme = effective  // also expose data-theme="dark|light"
  root.style.colorScheme = effective
}

// ── store ────────────────────────────────────────────────────────────────────

interface ThemeStore {
  preference: ThemePreference
  effective:  EffectiveTheme
  // actions
  setPreference: (pref: ThemePreference) => void
  toggle:        () => void
  /** Must be called once on boot (from App.tsx) to attach the OS listener. */
  initSystemSync: () => () => void
}

const initialPref = readStoredPreference()

export const useThemeStore = create<ThemeStore>((set, get) => ({
  preference: initialPref,
  effective:  resolveEffective(initialPref),

  setPreference: (pref) => {
    try {
      window.localStorage.setItem(THEME_KEY, pref)
    } catch {
      /* storage unavailable — preference lives only for this session */
    }
    const effective = resolveEffective(pref)
    applyTheme(effective)
    set({ preference: pref, effective })
  },

  /** Plain light ↔ dark flip (ignores 'system' — flips to the opposite). */
  toggle: () => {
    const next: ThemePreference = get().effective === 'dark' ? 'light' : 'dark'
    get().setPreference(next)
  },

  initSystemSync: () => {
    if (typeof window === 'undefined' || !window.matchMedia) return () => {}

    const mql = window.matchMedia('(prefers-color-scheme: dark)')
    const handler = () => {
      if (get().preference === 'system') {
        const effective = resolveEffective('system')
        applyTheme(effective)
        set({ effective })
      }
    }

    // addEventListener is the modern API; fall back to addListener for old Safari
    if (mql.addEventListener) mql.addEventListener('change', handler)
    else                      mql.addListener(handler)

    return () => {
      if (mql.removeEventListener) mql.removeEventListener('change', handler)
      else                         mql.removeListener(handler)
    }
  },
}))

// ── one-time boot: guarantee <html> reflects the correct class ───────────────
// The anti-flicker script in index.html normally does this before React mounts,
// but we re-apply here in case the app is embedded or the script was missed.

if (typeof document !== 'undefined') {
  applyTheme(useThemeStore.getState().effective)
}
