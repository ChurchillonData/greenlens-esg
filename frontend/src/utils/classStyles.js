export const CLASS_LABELS = {
  well_substantiated: 'Well substantiated',
  weakly_substantiated: 'Weakly substantiated',
  contradicted: 'Contradicted',
}

export const COMPANY_LABELS = {
  bp: 'BP', chevron: 'Chevron', conoco: 'ConocoPhillips',
  eni: 'Eni', equinor: 'Equinor', exxon: 'ExxonMobil',
  occidental: 'Occidental', repsol: 'Repsol',
  shell: 'Shell', totalenergies: 'TotalEnergies',
}

export const COMPANY_REPORT_YEAR = {
  bp:            2025,
  chevron:       2024,
  conoco:        2025,
  eni:           2024,
  equinor:       2025,
  exxon:         2024,
  occidental:    2024,
  repsol:        2025,
  shell:         2025,
  totalenergies: 2025,
}

export const COMPANY_LOGOS = {
  bp:            '/logos/bp.png',
  chevron:       '/logos/chevron.png',
  conoco:        '/logos/conoco.png',
  eni:           '/logos/eni.png',
  equinor:       '/logos/equinor.png',
  exxon:         '/logos/exxon.png',
  occidental:    '/logos/occidental.png',
  repsol:        '/logos/repsol.png',
  shell:         '/logos/shell.svg',
  totalenergies: '/logos/totalenergies.png',
}

export function dotColor(cls) {
  return {
    well_substantiated: 'bg-emerald-600',
    weakly_substantiated: 'bg-amber-600',
    contradicted: 'bg-rose-700',
  }[cls] ?? 'bg-gray-500'
}

export function badgeCls(cls) {
  return {
    well_substantiated: 'bg-emerald-700 text-white ring-emerald-800',
    weakly_substantiated: 'bg-amber-700 text-white ring-amber-800',
    contradicted: 'bg-rose-700 text-white ring-rose-800',
  }[cls] ?? 'bg-slate-600 text-white ring-slate-700'
}

export function scoreColor(score) {
  if (score <= 0.4) return 'text-emerald-700'
  if (score <= 0.7) return 'text-amber-700'
  return 'text-rose-700'
}
