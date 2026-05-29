import { useState, useRef, useEffect, useMemo } from 'react'
import { HugeiconsIcon } from '@hugeicons/react'
import { ArrowRight01Icon, ArrowDown01Icon, CheckmarkCircle01Icon, BalanceScaleIcon } from '@hugeicons/core-free-icons'
import { COMPANY_LABELS, COMPANY_LOGOS, scoreColor } from '../utils/classStyles'

const COMP_CATEGORIES = [
  { key: 'emissions_reduction',   label: 'Emissions reduction'  },
  { key: 'renewables_investment', label: 'Renewables investment' },
  { key: 'net_zero',              label: 'Net-zero commitments'  },
  { key: 'scope_3',               label: 'Scope 3 emissions'     },
  { key: 'biodiversity',          label: 'Biodiversity'          },
  { key: 'methane',               label: 'Methane reduction'     },
  { key: 'just_transition',       label: 'Just transition'       },
  { key: 'climate_lobbying',      label: 'Climate lobbying'      },
  { key: 'flaring',               label: 'Flaring'               },
  { key: 'carbon_capture',        label: 'Carbon capture'        },
  { key: 'other',                 label: 'Other'                 },
]

const SEGMENTS = 10

function riskSegmentColor(score) {
  if (score <= 0.4) return 'bg-emerald-600'
  if (score <= 0.7) return 'bg-amber-600'
  return 'bg-rose-700'
}

const VERDICT = {
  well_substantiated:   { label: 'supports',   cls: 'bg-emerald-700 text-white ring-emerald-800' },
  weakly_substantiated: { label: 'mixed',       cls: 'bg-amber-700 text-white ring-amber-800' },
  contradicted:         { label: 'contradicts', cls: 'bg-rose-700 text-white ring-rose-800' },
}

function CompanyLogo({ companyId, size = 'md' }) {
  const src = COMPANY_LOGOS[companyId]
  const dim = size === 'lg' ? 'w-10 h-10' : 'w-5 h-5'
  if (!src) return null
  return (
    <span className={`${dim} rounded-lg shrink-0 flex items-center justify-center overflow-hidden`}>
      <img
        src={src}
        alt={COMPANY_LABELS[companyId] ?? companyId}
        className="w-full h-full object-contain"
        onError={e => { e.currentTarget.style.display = 'none' }}
      />
    </span>
  )
}

function CompanyDropdown({ companies, value, onChange, className = '' }) {
  const [open, setOpen] = useState(false)
  const ref = useRef(null)

  useEffect(() => {
    function handleClick(e) {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [])

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen(o => !o)}
        className={`flex items-center gap-2 border border-gray-300 rounded-md px-3 py-2.5 bg-white text-sm hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-green-dark min-w-[160px] ${className}`}
      >
        <CompanyLogo companyId={value} />
        <span className="flex-1 text-left font-medium text-gray-800 truncate">
          {COMPANY_LABELS[value] ?? value}
        </span>
        <HugeiconsIcon icon={ArrowDown01Icon} size={13} color="currentColor" strokeWidth={1.5} className="text-gray-400 shrink-0" />
      </button>

      {open && (
        <ul className="absolute z-20 mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-lg py-1 max-h-64 overflow-y-auto">
          {companies.map(co => (
            <li key={co}>
              <button
                onClick={() => { onChange(co); setOpen(false) }}
                className={`w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-gray-50 transition-colors ${
                  co === value ? 'bg-green-dark/5 text-green-dark font-medium' : 'text-gray-700'
                }`}
              >
                <CompanyLogo companyId={co} />
                <span className="flex-1 text-left">{COMPANY_LABELS[co] ?? co}</span>
                {co === value && (
                  <HugeiconsIcon icon={CheckmarkCircle01Icon} size={13} color="currentColor" strokeWidth={1.5} className="text-green-dark" />
                )}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

function MiniRiskMeter({ score }) {
  const filled = Math.round(score * SEGMENTS)
  const color = riskSegmentColor(score)
  return (
    <div className="flex items-center gap-0.5 w-full">
      {Array.from({ length: SEGMENTS }, (_, i) => (
        <div key={i} className={`h-1.5 flex-1 rounded-full ${i < filled ? color : 'bg-gray-200'}`} />
      ))}
    </div>
  )
}

function ClaimCard({ claim, companyId, allCompanyClaims, onViewClaim }) {
  if (!claim) {
    return (
      <div className="flex-1 bg-white border border-paper-border rounded-xl p-6 flex items-center justify-center min-h-[260px]">
        <p className="text-sm text-gray-400 italic text-center">No claim in this category</p>
      </div>
    )
  }

  const topEvidence = claim.evidence
    ?.slice()
    .sort((a, b) => (b.source_credibility ?? 0) - (a.source_credibility ?? 0))[0]

  const verdict = VERDICT[claim.predicted_class]

  const catClaims = allCompanyClaims.filter(c => c.category === claim.category)
  const scores = catClaims.map(c => c.risk_score)
  const hasRange = scores.length > 1
  const lo = Math.min(...scores).toFixed(2)
  const hi = Math.max(...scores).toFixed(2)

  const evidenceSnippet = topEvidence?.text
    ? topEvidence.text.replace(/\n/g, ' ').trim().slice(0, 130)
    : null

  return (
    <div className="flex-1 bg-white border border-paper-border rounded-xl p-6 flex flex-col gap-5">
      {/* Company header */}
      <div className="flex items-center gap-3">
        <CompanyLogo companyId={companyId} size="lg" />
        <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
          {COMPANY_LABELS[companyId]} claim
        </p>
      </div>

      {/* Claim text */}
      <blockquote className="text-sm text-gray-800 italic leading-relaxed flex-1">
        "{claim.claim_text}"
      </blockquote>

      {/* GreenSignal + meter */}
      <div className="space-y-1.5">
        <div className="flex items-baseline gap-2">
          <span className="text-xs font-medium text-gray-500">Signal:</span>
          <span className={`font-mono text-2xl font-black tabular-nums leading-none ${scoreColor(claim.risk_score)}`}>
            {claim.risk_score.toFixed(2)}
          </span>
          {hasRange && (
            <span className="text-xs text-gray-400 font-mono">({lo}–{hi})</span>
          )}
        </div>
        <MiniRiskMeter score={claim.risk_score} />
      </div>

      {/* Top evidence */}
      {topEvidence && (
        <div className="border-t border-gray-100 pt-3 space-y-1.5">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs text-gray-500">Top evidence:</span>
            <span className="text-xs font-semibold text-gray-700">{topEvidence.source}</span>
            {verdict && (
              <span className={`text-[11px] px-2 py-0.5 rounded-full ring-1 font-medium ${verdict.cls}`}>
                {verdict.label}
              </span>
            )}
          </div>
          {evidenceSnippet && (
            <p className="text-xs text-gray-500 italic leading-relaxed line-clamp-2">
              "{evidenceSnippet}{evidenceSnippet.length >= 130 ? '…' : ''}"
            </p>
          )}
        </div>
      )}

      {/* View all evidence */}
      <button
        onClick={() => onViewClaim(companyId, claim)}
        className="flex items-center gap-1.5 text-xs font-semibold text-green-dark hover:opacity-75 transition-opacity"
      >
        View all evidence
        <HugeiconsIcon icon={ArrowRight01Icon} size={13} color="currentColor" strokeWidth={1.5} />
      </button>
    </div>
  )
}

export default function ClaimComparison({ data, companies, onViewClaim }) {
  const [compA, setCompA] = useState(companies[0])
  const [compB, setCompB] = useState(companies[1] ?? companies[0])
  const [category, setCategory] = useState('emissions_reduction')

  const claimsA = useMemo(() => data.filter(r => r.company_id === compA), [data, compA])
  const claimsB = useMemo(() => data.filter(r => r.company_id === compB), [data, compB])

  const catsA = useMemo(() => new Set(claimsA.map(r => r.category)), [claimsA])
  const catsB = useMemo(() => new Set(claimsB.map(r => r.category)), [claimsB])

  // When companies change, keep current category if either has data;
  // otherwise fall back to the first category both share, then first either has.
  useEffect(() => {
    if (catsA.has(category) || catsB.has(category)) return
    const shared = COMP_CATEGORIES.find(c => catsA.has(c.key) && catsB.has(c.key))
    const fallback = COMP_CATEGORIES.find(c => catsA.has(c.key) || catsB.has(c.key))
    const best = shared ?? fallback
    if (best) setCategory(best.key)
  }, [compA, compB])

  const claimA = claimsA
    .filter(c => c.category === category)
    .sort((a, b) => b.risk_score - a.risk_score)[0] ?? null

  const claimB = claimsB
    .filter(c => c.category === category)
    .sort((a, b) => b.risk_score - a.risk_score)[0] ?? null

  return (
    <section className="space-y-4">
      <h3 className="font-display text-sm font-bold text-gray-700 uppercase tracking-widest">
        Comparison mode
        <span className="ml-2 text-xs font-normal normal-case text-gray-400">
          head-to-head claim analysis
        </span>
      </h3>

      {/* Controls bar */}
      <div className="bg-white border border-paper-border rounded-xl p-5 flex flex-col sm:flex-row sm:items-end gap-4 sm:gap-5">
        <div className="flex flex-col gap-1.5 flex-1">
          <label className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">Company A</label>
          <CompanyDropdown companies={companies} value={compA} onChange={setCompA} className="w-full" />
        </div>
        <div className="flex flex-col gap-1.5 flex-1">
          <label className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">Company B</label>
          <CompanyDropdown companies={companies} value={compB} onChange={setCompB} className="w-full" />
        </div>
        <div className="flex flex-col gap-1.5 flex-1">
          <label className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">Category</label>
          <select
            value={category}
            onChange={e => setCategory(e.target.value)}
            className="w-full border border-gray-300 rounded-md px-3 py-2.5 text-sm bg-white text-gray-800 focus:outline-none focus:ring-2 focus:ring-green-dark hover:border-gray-400 cursor-pointer"
          >
            {COMP_CATEGORIES.map(c => {
              const hasA = catsA.has(c.key)
              const hasB = catsB.has(c.key)
              const empty = !hasA && !hasB
              return (
                <option key={c.key} value={c.key}>
                  {c.label}{empty ? ' (no data)' : !hasA || !hasB ? ' (partial)' : ''}
                </option>
              )
            })}
          </select>
        </div>
      </div>

      {/* Side-by-side cards with VS divider */}
      <div className="flex flex-col md:flex-row gap-0 items-stretch">
        <ClaimCard
          claim={claimA}
          companyId={compA}
          allCompanyClaims={claimsA}
          onViewClaim={onViewClaim}
        />

        {/* VS divider */}
        {/* VS divider */}
        <div className="flex md:flex-col items-center justify-center shrink-0 px-3 md:px-0 py-4 md:py-8 gap-3 md:gap-0">
          <div className="hidden md:block w-px flex-1 bg-paper-border" />
          <div className="flex flex-col items-center gap-2 md:py-5">
            <div className="w-14 h-14 rounded-full bg-green-dark flex items-center justify-center shadow-lg ring-4 ring-white">
              <HugeiconsIcon icon={BalanceScaleIcon} size={24} color="white" strokeWidth={1.5} />
            </div>
            <span className="text-[10px] font-black tracking-[0.2em] text-gray-400 uppercase">vs</span>
          </div>
          <div className="hidden md:block w-px flex-1 bg-paper-border" />
        </div>

        <ClaimCard
          claim={claimB}
          companyId={compB}
          allCompanyClaims={claimsB}
          onViewClaim={onViewClaim}
        />
      </div>
    </section>
  )
}
