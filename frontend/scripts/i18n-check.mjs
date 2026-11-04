#!/usr/bin/env node
/**
 * i18n key completeness check.
 *
 * Compares all locale bundles under src/i18n/locales/*.json against the
 * primary locale (en-US) and reports:
 *   - Missing keys (present in primary, absent in other locale)
 *   - Extra keys (present in other locale, absent in primary)
 *   - Type mismatches (leaf vs object at same path)
 *   - Empty string values
 *
 * Exits with code 1 if any issues are found, making it safe for CI / pre-commit.
 *
 * Usage: npm run i18n:check
 */
import { readFileSync, readdirSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import path from 'node:path'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const LOCALES_DIR = path.resolve(__dirname, '../src/i18n/locales')
const PRIMARY_LOCALE = 'en-US'

const CLR = {
  red: (s) => `\u001b[31m${s}\u001b[0m`,
  yellow: (s) => `\u001b[33m${s}\u001b[0m`,
  green: (s) => `\u001b[32m${s}\u001b[0m`,
  cyan: (s) => `\u001b[36m${s}\u001b[0m`,
  bold: (s) => `\u001b[1m${s}\u001b[0m`,
}

/** Recursively flatten { a: { b: 'x' } } -> { 'a.b': { type: 'string', value: 'x' } } */
function flatten(obj, prefix = '', out = {}) {
  for (const [k, v] of Object.entries(obj)) {
    const key = prefix ? `${prefix}.${k}` : k
    if (v && typeof v === 'object' && !Array.isArray(v)) {
      out[key] = { type: 'object' }
      flatten(v, key, out)
    } else if (Array.isArray(v)) {
      out[key] = { type: 'array', value: v }
    } else {
      out[key] = { type: typeof v, value: v }
    }
  }
  return out
}

function loadLocale(file) {
  const raw = readFileSync(path.join(LOCALES_DIR, file), 'utf8')
  try {
    return JSON.parse(raw)
  } catch (e) {
    console.error(CLR.red(`[ERROR] Failed to parse ${file}: ${e.message}`))
    process.exit(2)
  }
}

function main() {
  const files = readdirSync(LOCALES_DIR).filter((f) => f.endsWith('.json'))
  const primaryFile = `${PRIMARY_LOCALE}.json`
  if (!files.includes(primaryFile)) {
    console.error(CLR.red(`[ERROR] Primary locale ${primaryFile} not found in ${LOCALES_DIR}`))
    process.exit(2)
  }

  const primaryFlat = flatten(loadLocale(primaryFile))
  const primaryLeafKeys = Object.keys(primaryFlat).filter(
    (k) => primaryFlat[k].type !== 'object',
  )

  console.log(
    CLR.bold(`\ni18n key-completeness check (primary = ${PRIMARY_LOCALE})`),
  )
  console.log(
    CLR.cyan(`  Primary locale leaf keys: ${primaryLeafKeys.length}`),
  )

  let totalIssues = 0

  for (const file of files) {
    if (file === primaryFile) continue
    const localeName = file.replace(/\.json$/, '')
    const localeFlat = flatten(loadLocale(file))
    const localeLeafKeys = Object.keys(localeFlat).filter(
      (k) => localeFlat[k].type !== 'object',
    )

    const missing = primaryLeafKeys.filter((k) => !(k in localeFlat))
    const extra = localeLeafKeys.filter((k) => !(k in primaryFlat))
    const typeMismatches = primaryLeafKeys
      .filter((k) => k in localeFlat)
      .filter((k) => primaryFlat[k].type !== localeFlat[k].type)
    const emptyValues = localeLeafKeys.filter(
      (k) => localeFlat[k].type === 'string' && localeFlat[k].value.trim() === '',
    )

    const issues =
      missing.length + extra.length + typeMismatches.length + emptyValues.length
    totalIssues += issues

    console.log(CLR.bold(`\n  ${localeName}: ${localeLeafKeys.length} keys`))
    if (issues === 0) {
      console.log(CLR.green('    ✓ perfectly in sync'))
      continue
    }

    if (missing.length) {
      console.log(CLR.red(`    ✗ ${missing.length} missing key(s):`))
      for (const k of missing.slice(0, 20)) console.log(`        - ${k}`)
      if (missing.length > 20) console.log(`        ... (+${missing.length - 20} more)`)
    }
    if (extra.length) {
      console.log(CLR.yellow(`    ! ${extra.length} extra key(s) (not in primary):`))
      for (const k of extra.slice(0, 20)) console.log(`        + ${k}`)
      if (extra.length > 20) console.log(`        ... (+${extra.length - 20} more)`)
    }
    if (typeMismatches.length) {
      console.log(CLR.red(`    ✗ ${typeMismatches.length} type mismatch(es):`))
      for (const k of typeMismatches) {
        console.log(
          `        ~ ${k} (primary=${primaryFlat[k].type}, ${localeName}=${localeFlat[k].type})`,
        )
      }
    }
    if (emptyValues.length) {
      console.log(CLR.yellow(`    ! ${emptyValues.length} empty string value(s):`))
      for (const k of emptyValues.slice(0, 20)) console.log(`        ␣ ${k}`)
      if (emptyValues.length > 20) console.log(`        ... (+${emptyValues.length - 20} more)`)
    }
  }

  console.log('')
  if (totalIssues === 0) {
    console.log(CLR.green(CLR.bold('✓ All locales in sync.')))
    process.exit(0)
  } else {
    console.log(
      CLR.red(CLR.bold(`✗ ${totalIssues} issue(s) across all locales.`)),
    )
    process.exit(1)
  }
}

main()
