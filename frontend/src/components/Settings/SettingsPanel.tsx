/**
 * SettingsPanel — right-side drawer for application settings.
 *
 * Features
 *   • Slides in from the right (Framer Motion, 300ms ease-out)
 *   • Semi-transparent backdrop with its own fade animation
 *   • Closes on: Escape key, backdrop click, or the ✕ button
 *   • Focus is moved into the drawer on open and restored to the trigger on close
 *   • Scrolling of the underlying page is locked while open
 *   • Fully labelled for screen readers (role=dialog, aria-modal, aria-labelledby)
 *
 * Currently exposes:
 *   – Appearance (theme)
 *   – Placeholder "Notifications" and "Account" sections (disabled, for scale)
 */
import { useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Palette, Bell, UserCircle2 } from 'lucide-react'
import { useTheme } from '@/hooks/useTheme'
import ThemeToggle from './ThemeToggle'

interface SettingsPanelProps {
  open:    boolean
  onClose: () => void
}

export default function SettingsPanel({ open, onClose }: SettingsPanelProps) {
  const drawerRef = useRef<HTMLDivElement>(null)
  const titleId   = 'settings-panel-title'

  const { preference, theme } = useTheme()

  // ── Escape-to-close + focus management + body scroll lock ──────────────
  useEffect(() => {
    if (!open) return

    const previouslyFocused = document.activeElement as HTMLElement | null

    // Lock background scroll (page is already overflow:hidden, but be safe).
    const prevOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'

    // Move focus inside the drawer for keyboard users
    // Delay by a tick so the animation doesn't interrupt the focus.
    const t = window.setTimeout(() => {
      drawerRef.current?.querySelector<HTMLElement>('[data-autofocus]')?.focus()
    }, 50)

    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault()
        onClose()
      }
    }
    window.addEventListener('keydown', onKey)

    return () => {
      window.clearTimeout(t)
      window.removeEventListener('keydown', onKey)
      document.body.style.overflow = prevOverflow
      // Restore focus to the button that opened the drawer
      previouslyFocused?.focus?.()
    }
  }, [open, onClose])

  return (
    <AnimatePresence>
      {open && (
        <>
          {/* ── Backdrop ─────────────────────────────────────────────── */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{    opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={onClose}
            className="fixed inset-0 z-40"
            style={{ background: 'rgba(0, 0, 0, 0.45)', backdropFilter: 'blur(2px)' }}
            aria-hidden="true"
          />

          {/* ── Drawer ──────────────────────────────────────────────── */}
          <motion.aside
            ref={drawerRef}
            role="dialog"
            aria-modal="true"
            aria-labelledby={titleId}
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{    x: '100%' }}
            transition={{ type: 'tween', ease: [0.25, 1, 0.5, 1], duration: 0.3 }}
            className="fixed top-0 right-0 bottom-0 z-50 w-full max-w-[400px]
                       flex flex-col shadow-2xl"
            style={{
              background: 'rgb(var(--color-bg))',
              color:      'rgb(var(--color-fg))',
              borderLeft: '1px solid rgb(var(--color-border))',
            }}
          >
            {/* ── Header ─────────────────────────────────────────────── */}
            <header
              className="flex items-center justify-between px-5 py-4 shrink-0"
              style={{ borderBottom: '1px solid rgb(var(--color-border))' }}
            >
              <div>
                <h2 id={titleId} className="text-base font-semibold tracking-tight">
                  Settings
                </h2>
                <p className="text-xs mt-0.5" style={{ color: 'rgb(var(--color-muted-fg))' }}>
                  Customize your workspace
                </p>
              </div>
              <button
                data-autofocus
                onClick={onClose}
                aria-label="Close settings"
                className="icon-btn"
              >
                <X size={18} />
              </button>
            </header>

            {/* ── Body (scrollable) ──────────────────────────────────── */}
            <div className="flex-1 overflow-y-auto px-5 py-5 space-y-5">
              {/* Appearance */}
              <Section
                Icon={Palette}
                title="Appearance"
                description="Choose how the interface looks to you."
              >
                <div className="flex flex-col gap-3">
                  <ThemeToggle />
                  <p
                    className="text-[0.7rem]"
                    style={{ color: 'rgb(var(--color-muted-fg))' }}
                    aria-live="polite"
                  >
                    {preference === 'system'
                      ? `Following your system preference (currently ${theme}).`
                      : `Using ${preference} theme.`}
                  </p>
                </div>
              </Section>

              {/* Notifications (placeholder) */}
              <Section
                Icon={Bell}
                title="Notifications"
                description="Control alerts and desktop notifications."
                disabled
              >
                <ComingSoon />
              </Section>

              {/* Account (placeholder) */}
              <Section
                Icon={UserCircle2}
                title="Account"
                description="Manage your profile, billing, and team."
                disabled
              >
                <ComingSoon />
              </Section>
            </div>

            {/* ── Footer ─────────────────────────────────────────────── */}
            <footer
              className="px-5 py-3 text-[0.65rem] shrink-0"
              style={{
                borderTop: '1px solid rgb(var(--color-border))',
                color:     'rgb(var(--color-muted-fg))',
              }}
            >
              Agent Factory · Settings
            </footer>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  )
}

// ──────────────────────────────────────────────────────────────────────────
//  Local helpers
// ──────────────────────────────────────────────────────────────────────────

function Section({
  Icon,
  title,
  description,
  disabled = false,
  children,
}: {
  Icon:         React.ElementType
  title:        string
  description:  string
  disabled?:    boolean
  children:     React.ReactNode
}) {
  return (
    <section
      aria-disabled={disabled || undefined}
      className="settings-card p-4"
      style={{ opacity: disabled ? 0.55 : 1 }}
    >
      <header className="flex items-start gap-3 mb-3">
        <span
          className="flex items-center justify-center w-8 h-8 rounded-lg shrink-0"
          style={{
            background: 'rgb(var(--color-primary) / 0.12)',
            color:      'rgb(var(--color-primary))',
          }}
        >
          <Icon size={16} />
        </span>
        <div className="flex-1">
          <h3 className="text-sm font-semibold leading-tight">{title}</h3>
          <p className="text-xs mt-0.5" style={{ color: 'rgb(var(--color-muted-fg))' }}>
            {description}
          </p>
        </div>
      </header>
      <div>{children}</div>
    </section>
  )
}

function ComingSoon() {
  return (
    <span
      className="inline-flex items-center px-2 py-0.5 rounded-md text-[0.6rem]
                 font-medium uppercase tracking-wider"
      style={{
        background: 'rgb(var(--color-muted) / 0.8)',
        color:      'rgb(var(--color-muted-fg))',
        border:     '1px solid rgb(var(--color-border))',
      }}
    >
      Coming soon
    </span>
  )
}
