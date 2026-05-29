/**
 * useTheme — ergonomic hook to consume the global theme store.
 *
 * Example:
 *   const { theme, preference, setTheme, toggle, isDark } = useTheme()
 *
 *   <button onClick={toggle}>Flip theme</button>
 *   <p className={isDark ? 'text-white' : 'text-slate-900'}>…</p>
 */
import { useThemeStore, type EffectiveTheme, type ThemePreference } from '@/store/themeStore'

export interface UseThemeReturn {
  /** The currently applied concrete theme — 'light' | 'dark'. */
  theme:      EffectiveTheme
  /** The user's saved preference — 'light' | 'dark' | 'system'. */
  preference: ThemePreference
  /** Convenience boolean. */
  isDark:     boolean
  /** Change the saved preference (also re-applies the <html> class). */
  setTheme:   (pref: ThemePreference) => void
  /** Flip between light and dark (ignores 'system'). */
  toggle:     () => void
}

export function useTheme(): UseThemeReturn {
  const preference = useThemeStore(s => s.preference)
  const effective  = useThemeStore(s => s.effective)
  const setPref    = useThemeStore(s => s.setPreference)
  const toggle     = useThemeStore(s => s.toggle)

  return {
    theme:      effective,
    preference,
    isDark:     effective === 'dark',
    setTheme:   setPref,
    toggle,
  }
}

export default useTheme
