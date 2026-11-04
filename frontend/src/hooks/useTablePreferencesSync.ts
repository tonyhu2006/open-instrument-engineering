import { useCallback, useEffect, useRef } from 'react'
import { preferencesApi } from '@/lib/api'

const STORAGE_PREFIX = 'openinstrument.adminTable.v1.cols.'
const DEBOUNCE_MS = 2_000

/**
 * Sync table column widths between localStorage (offline-first) and server
 * (cross-device persistence).
 *
 * Flow:
 *   1. On mount (once per session) fetch server preferences and seed any
 *      localStorage keys that are missing locally.
 *   2. On every `save(storageKey, widths)` call, write to localStorage
 *      immediately **and** debounce a PATCH to the server.
 *
 * Guarantees:
 *   - Offline / unauthenticated: degrades to localStorage-only — no errors.
 *   - Rapid column resizes coalesce into at most 1 PATCH per DEBOUNCE_MS.
 */
export function useTablePreferencesSync() {
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const pendingRef = useRef<Record<string, Record<string, number>>>({})
  const fetchedRef = useRef(false)

  // ── Pull server → localStorage (once) ──
  useEffect(() => {
    if (fetchedRef.current) return
    fetchedRef.current = true

    preferencesApi.get().then((prefs) => {
      const serverWidths = prefs.tableWidths as
        | Record<string, Record<string, number>>
        | undefined
      if (!serverWidths || typeof serverWidths !== 'object') return

      for (const [key, colWidths] of Object.entries(serverWidths)) {
        const lsKey = STORAGE_PREFIX + key
        const local = safeParseJson(localStorage.getItem(lsKey))
        if (!local) {
          // Server has data the client doesn't — seed it
          try {
            localStorage.setItem(lsKey, JSON.stringify(colWidths))
          } catch { /* quota */ }
        }
        // If local already exists, local wins (fresher edits)
      }
    }).catch(() => {
      /* offline / unauth — silent */
    })
  }, [])

  // ── Save: localStorage immediately, server debounced ──
  const save = useCallback((storageKey: string, widths: Record<string, number>) => {
    // 1) localStorage — instant
    try {
      localStorage.setItem(STORAGE_PREFIX + storageKey, JSON.stringify(widths))
    } catch { /* quota */ }

    // 2) Accumulate for server PATCH
    pendingRef.current[storageKey] = widths

    if (timerRef.current) clearTimeout(timerRef.current)
    timerRef.current = setTimeout(() => {
      const batch = { ...pendingRef.current }
      pendingRef.current = {}
      flushToServer(batch)
    }, DEBOUNCE_MS)
  }, [])

  // Flush on unmount so pending changes aren't lost
  useEffect(() => {
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current)
      const batch = { ...pendingRef.current }
      pendingRef.current = {}
      if (Object.keys(batch).length) flushToServer(batch)
    }
  }, [])

  return { save, STORAGE_PREFIX }
}

/** Load widths from localStorage (versioned key). */
export function loadStoredWidths(storageKey?: string): Record<string, number> | null {
  if (!storageKey || typeof window === 'undefined') return null
  try {
    const raw = window.localStorage.getItem(STORAGE_PREFIX + storageKey)
    if (!raw) return migrateV0(storageKey)
    return safeParseWidths(raw)
  } catch {
    return null
  }
}

// ── internal helpers ──

const LEGACY_PREFIX = 'openinstrument.adminTable.cols.'

/** One-time migration from v0 (no version) → v1. */
function migrateV0(storageKey: string): Record<string, number> | null {
  try {
    const raw = window.localStorage.getItem(LEGACY_PREFIX + storageKey)
    if (!raw) return null
    const parsed = safeParseWidths(raw)
    if (!parsed) return null
    // Write under v1 key, remove legacy key
    window.localStorage.setItem(STORAGE_PREFIX + storageKey, JSON.stringify(parsed))
    window.localStorage.removeItem(LEGACY_PREFIX + storageKey)
    return parsed
  } catch {
    return null
  }
}

function safeParseWidths(raw: string): Record<string, number> | null {
  try {
    const parsed = JSON.parse(raw)
    if (!parsed || typeof parsed !== 'object') return null
    const out: Record<string, number> = {}
    for (const [k, v] of Object.entries(parsed)) {
      if (typeof v === 'number' && Number.isFinite(v) && v > 0) out[k] = v
    }
    return Object.keys(out).length ? out : null
  } catch {
    return null
  }
}

function safeParseJson(raw: string | null): Record<string, number> | null {
  if (!raw) return null
  return safeParseWidths(raw)
}

function flushToServer(batch: Record<string, Record<string, number>>) {
  if (!Object.keys(batch).length) return
  preferencesApi.patch({ tableWidths: batch }).catch(() => {
    /* offline / unauth — silent */
  })
}
