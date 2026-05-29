import { useState, useEffect, useRef } from 'react'
import { HugeiconsIcon } from '@hugeicons/react'
import {
  LinkSquare01Icon,
  Calendar01Icon,
  Target01Icon,
  ArrowLeft01Icon,
  FilterIcon,
  ArrowDown01Icon,
  CheckmarkCircle01Icon,
  Cancel01Icon,
  AlertCircleIcon,
  Clock01Icon,
} from '@hugeicons/core-free-icons'
import { COMPANY_LABELS, COMPANY_LOGOS } from '../utils/classStyles'

// ---------------------------------------------------------------------------
// Verdict config
// ---------------------------------------------------------------------------
const VERDICT = {
  fulfilled: {
    label: 'Fulfilled',
    badge: 'bg-emerald-700 text-white ring-emerald-800',
    bar:   'bg-emerald-600',
    dot:   'bg-emerald-500',
    text:  'text-emerald-700',
  },
  partially_fulfilled: {
    label: 'Partially fulfilled',
    badge: 'bg-amber-600 text-white ring-amber-700',
    bar:   'bg-amber-500',
    dot:   'bg-amber-500',
    text:  'text-amber-700',
  },
  reversed: {
    label: 'Reversed / Abandoned',
    badge: 'bg-rose-700 text-white ring-rose-800',
    bar:   'bg-rose-600',
    dot:   'bg-rose-500',
    text:  'text-rose-700',
  },
  too_early: {
    label: 'Too early to judge',
    badge: 'bg-sky-600 text-white ring-sky-700',
    bar:   'bg-sky-500',
    dot:   'bg-sky-400',
    text:  'text-sky-600',
  },
}

const CATEGORY_LABELS = {
  net_zero:             'Net Zero',
  emissions_reduction:  'Emissions Reduction',
  methane:              'Methane',
  renewables_investment:'Renewables Investment',
  scope_3:              'Scope 3',
  just_transition:      'Just Transition',
  biodiversity:         'Biodiversity',
  climate_lobbying:     'Climate Lobbying',
  other:                'Other',
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function AccountabilityBadge({ score }) {
  if (score == null) return null
  const pct = Math.round(score * 100)
  const { label, ring, bar, text } =
    score >= 0.6 ? { label: 'Good',     ring: 'ring-emerald-300', bar: 'bg-emerald-500', text: 'text-emerald-700' } :
    score >= 0.4 ? { label: 'Moderate', ring: 'ring-amber-300',   bar: 'bg-amber-500',   text: 'text-amber-700'   } :
    score >= 0.2 ? { label: 'Low',      ring: 'ring-rose-300',    bar: 'bg-rose-500',    text: 'text-rose-700'    } :
                   { label: 'Very Low', ring: 'ring-rose-400',    bar: 'bg-rose-600',    text: 'text-rose-800'    }
  return (
    <div className={`shrink-0 flex flex-col items-end gap-1 px-3 py-2 rounded-xl bg-white ring-1 ${ring}`}>
      <p className="text-[9px] font-bold text-gray-400 uppercase tracking-widest whitespace-nowrap">Pledge Accountability</p>
      <div className="flex items-baseline gap-1.5">
        <span className={`font-mono text-2xl font-black tabular-nums leading-none ${text}`}>{pct}%</span>
        <span className={`text-[10px] font-semibold ${text}`}>{label}</span>
      </div>
      <div className="flex items-center gap-0.5 w-24">
        {Array.from({ length: DASH_SEGMENTS }, (_, i) => (
          <div key={i} className={`h-1.5 flex-1 rounded-full ${i < Math.round(score * DASH_SEGMENTS) ? bar : 'bg-gray-100'}`} />
        ))}
      </div>
    </div>
  )
}

function VerdictBadge({ verdict }) {
  const cfg = VERDICT[verdict] ?? VERDICT.too_early
  return (
    <span className={`inline-flex items-center text-xs font-semibold px-2.5 py-0.5 rounded-full ring-1 ${cfg.badge}`}>
      {cfg.label}
    </span>
  )
}

const DASH_SEGMENTS = 10

function ConfidenceBar({ confidence, verdict }) {
  const cfg = VERDICT[verdict] ?? VERDICT.too_early
  const pct = Math.round((confidence ?? 0) * 100)
  const filled = Math.round((confidence ?? 0) * DASH_SEGMENTS)
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 flex items-center gap-0.5">
        {Array.from({ length: DASH_SEGMENTS }, (_, i) => (
          <div key={i} className={`h-1.5 flex-1 rounded-full ${i < filled ? cfg.bar : 'bg-gray-200'}`} />
        ))}
      </div>
      <span className="text-[10px] font-medium text-gray-400 tabular-nums w-8 text-right">{pct}%</span>
    </div>
  )
}

function EvidenceSnippet({ ev }) {
  return (
    <div className="flex items-start gap-2">
      <span className="shrink-0 mt-0.5 w-1.5 h-1.5 rounded-full bg-gray-300 mt-1.5" />
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap mb-0.5">
          <span className="text-[10px] font-semibold text-white bg-green-dark px-1.5 py-0.5 rounded-full">
            {ev.source}
          </span>
          {ev.date && (
            <span className="text-[10px] text-gray-400">{ev.date}</span>
          )}
          {ev.url && (
            <a
              href={ev.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-emerald-600 hover:text-emerald-800 transition-colors"
              title="Open source"
            >
              <HugeiconsIcon icon={LinkSquare01Icon} size={12} color="currentColor" strokeWidth={1.5} />
            </a>
          )}
        </div>
        <p className="text-[11px] text-gray-500 leading-relaxed line-clamp-3">{ev.text}</p>
      </div>
    </div>
  )
}

function PledgeCard({ pledge }) {
  const [expanded, setExpanded] = useState(false)
  const cfg = VERDICT[pledge.verdict] ?? VERDICT.too_early
  const category = CATEGORY_LABELS[pledge.category] ?? pledge.category

  const targetLine = [
    pledge.target_value != null ? `${pledge.target_value} ${pledge.target_unit ?? ''}`.trim() : null,
    pledge.scope ? `scope: ${pledge.scope}` : null,
  ].filter(Boolean).join(' · ')

  return (
    <article className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-shadow">
      {/* Coloured top bar */}
      <div className={`h-1 ${cfg.bar}`} />

      <div className="p-4 md:p-5 space-y-3">
        {/* Header row */}
        <div className="space-y-2">
          <div className="flex items-center gap-2 flex-wrap">
            <VerdictBadge verdict={pledge.verdict} />
            {pledge.deadline_year && (
              <span className="flex items-center gap-1 text-[10px] font-semibold text-white bg-gray-700 px-2 py-0.5 rounded-full shrink-0">
                <HugeiconsIcon icon={Calendar01Icon} size={10} color="currentColor" strokeWidth={1.5} />
                Deadline {pledge.deadline_year}
              </span>
            )}
            <span className="text-[10px] font-medium text-gray-500 uppercase tracking-wider">{category}</span>
          </div>
          <blockquote className="text-sm text-gray-800 leading-relaxed italic">
            "{pledge.claim_text}"
          </blockquote>
        </div>

        {/* Target line */}
        {targetLine && (
          <div className="flex items-center gap-1.5 text-xs text-gray-500">
            <HugeiconsIcon icon={Target01Icon} size={12} color="currentColor" strokeWidth={1.5} />
            <span>{targetLine}</span>
          </div>
        )}

        {/* Confidence */}
        <div>
          <p className="text-[10px] font-medium text-gray-400 uppercase tracking-wider mb-1">
            Assessment confidence
          </p>
          <ConfidenceBar confidence={pledge.confidence} verdict={pledge.verdict} />
        </div>

        {/* Rationale */}
        <p className="text-xs text-gray-600 leading-relaxed">{pledge.rationale}</p>

        {/* Evidence (expandable) */}
        {pledge.evidence?.length > 0 && (
          <div>
            <button
              onClick={() => setExpanded(e => !e)}
              className="text-[11px] font-medium text-green-dark hover:underline"
            >
              {expanded ? 'Hide evidence' : `Show evidence (${pledge.evidence.length})`}
            </button>
            {expanded && (
              <div className="mt-2 space-y-2.5 border-t border-gray-100 pt-2.5">
                {pledge.evidence.map((ev, i) => (
                  <EvidenceSnippet key={i} ev={ev} />
                ))}
              </div>
            )}
          </div>
        )}

        <p className="text-[10px] text-gray-400 italic">
          Source: {pledge.company_id.toUpperCase()} sustainability report {pledge.report_year ?? 2021}
        </p>
      </div>
    </article>
  )
}

// ---------------------------------------------------------------------------
// Verdict filter dropdown
// ---------------------------------------------------------------------------

const FILTER_OPTIONS = [
  { key: 'all',                  label: 'All pledges',         icon: FilterIcon,          cls: 'text-gray-500'    },
  { key: 'reversed',             label: 'Reversed',            icon: Cancel01Icon,          cls: 'text-rose-500'    },
  { key: 'partially_fulfilled',  label: 'Partially fulfilled', icon: AlertCircleIcon,       cls: 'text-amber-500'   },
  { key: 'fulfilled',            label: 'Fulfilled',           icon: CheckmarkCircle01Icon, cls: 'text-emerald-600' },
  { key: 'too_early',            label: 'Too early',           icon: Clock01Icon,           cls: 'text-sky-500'     },
]

function VerdictFilter({ value, onChange, verdictCounts, total }) {
  const [open, setOpen] = useState(false)
  const [pos, setPos] = useState(null)
  const buttonRef = useRef(null)

  useEffect(() => {
    function handleOutside(e) {
      if (buttonRef.current && !buttonRef.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener('mousedown', handleOutside)
    return () => document.removeEventListener('mousedown', handleOutside)
  }, [])

  function handleToggle() {
    if (!open && buttonRef.current) {
      const r = buttonRef.current.getBoundingClientRect()
      setPos({ top: r.bottom + 4, right: window.innerWidth - r.right, minWidth: r.width })
    }
    setOpen(o => !o)
  }

  const current = FILTER_OPTIONS.find(o => o.key === value) ?? FILTER_OPTIONS[0]

  return (
    <div className="w-full md:w-auto" ref={buttonRef}>
      <button
        onClick={handleToggle}
        className="w-full md:w-auto flex items-center gap-1.5 border border-gray-200 rounded-lg px-2.5 py-1.5 bg-white text-xs hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-green-dark transition-colors shadow-sm"
      >
        <HugeiconsIcon icon={current.icon} size={13} color="currentColor" strokeWidth={1.5} className={current.cls} />
        <span className="font-medium text-gray-700">{current.label}</span>
        {value !== 'all' && (verdictCounts[value] ?? 0) > 0 && (
          <span className="bg-gray-100 text-gray-500 text-[10px] font-bold px-1.5 py-0.5 rounded-full tabular-nums">
            {verdictCounts[value]}
          </span>
        )}
        <HugeiconsIcon icon={ArrowDown01Icon} size={11} color="currentColor" strokeWidth={2} className="text-gray-400 ml-auto md:ml-0.5" />
      </button>

      {open && pos && (
        <ul
          style={{ position: 'fixed', top: pos.top, right: pos.right, minWidth: pos.minWidth, zIndex: 9999 }}
          className="bg-white border border-gray-200 rounded-xl shadow-xl py-1"
        >
          {FILTER_OPTIONS.map(opt => {
            const count = opt.key === 'all' ? total : (verdictCounts[opt.key] ?? 0)
            const isActive = opt.key === value
            return (
              <li key={opt.key}>
                <button
                  onClick={() => { onChange(opt.key); setOpen(false) }}
                  className={`w-full flex items-center gap-2.5 px-3 py-2 text-xs transition-colors hover:bg-gray-50 ${
                    isActive ? 'bg-green-dark/5' : ''
                  }`}
                >
                  <HugeiconsIcon icon={opt.icon} size={13} color="currentColor" strokeWidth={1.5} className={opt.cls} />
                  <span className={`flex-1 text-left ${isActive ? 'font-semibold text-green-dark' : 'text-gray-700'}`}>
                    {opt.label}
                  </span>
                  <span className="text-[10px] text-gray-400 tabular-nums font-medium">{count}</span>
                </button>
              </li>
            )
          })}
        </ul>
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Summary strip for selected company
// ---------------------------------------------------------------------------

function VerdictSummary({ verdictCounts }) {
  const order = ['reversed', 'partially_fulfilled', 'fulfilled', 'too_early']
  return (
    <div className="flex items-center gap-3 flex-wrap">
      {order.filter(v => (verdictCounts?.[v] ?? 0) > 0).map(v => {
        const cfg = VERDICT[v]
        return (
          <span key={v} className="flex items-center gap-1.5">
            <span className={`w-2 h-2 rounded-full ${cfg.dot}`} />
            <span className="text-xs text-gray-600">{verdictCounts[v]} {cfg.label.toLowerCase()}</span>
          </span>
        )
      })}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Main export
// ---------------------------------------------------------------------------

export default function CommitmentTracker({ data, selectedId, onBack }) {
  const [filterVerdict, setFilterVerdict] = useState('all')

  useEffect(() => {
    setFilterVerdict('all')
  }, [selectedId])

  const company = data.find(c => c.company_id === selectedId)

  if (!data.length) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-400 text-sm">
        No tracker data — run <code className="font-mono text-xs mx-1">scripts/run_gap_scoring.py</code> first
      </div>
    )
  }

  return (
    <main className="flex-1 bg-paper flex flex-col min-h-0">
        {/* Panel header */}
        <div className="bg-white border-b border-gray-200 px-4 md:px-8 py-4 shrink-0">
          <button
            onClick={onBack}
            className="md:hidden flex items-center gap-1.5 text-sm text-green-dark font-medium mb-3"
          >
            <HugeiconsIcon icon={ArrowLeft01Icon} size={16} color="currentColor" strokeWidth={1.5} />
            All companies
          </button>
          {company && (
            <div className="space-y-2">
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-center gap-3">
                  {COMPANY_LOGOS[company.company_id] && (
                    <span className="w-10 h-10 rounded-xl shrink-0 flex items-center justify-center overflow-hidden border border-gray-200 bg-white">
                      <img
                        src={COMPANY_LOGOS[company.company_id]}
                        alt={company.company_label}
                        className="w-7 h-7 object-contain"
                        onError={e => { e.currentTarget.style.display = 'none' }}
                      />
                    </span>
                  )}
                  <div>
                    <h2 className="font-display text-lg font-black text-gray-900 leading-tight">
                      {company.company_label}
                    </h2>
                    <p className="text-xs text-gray-400">
                      {company.total_analyzed} pledges analysed · 2021 reports vs. 2023–2025 NGO evidence
                    </p>
                  </div>
                </div>
                <AccountabilityBadge score={company.accountability_score} />
              </div>
              <div className="flex items-center justify-between gap-3 flex-wrap">
                <VerdictSummary verdictCounts={company.verdict_counts} />
                <VerdictFilter
                  key={selectedId}
                  value={filterVerdict}
                  onChange={setFilterVerdict}
                  verdictCounts={company.verdict_counts ?? {}}
                  total={company.total_analyzed ?? company.pledges.length}
                />
              </div>
            </div>
          )}
        </div>

        {/* Pledge cards */}
        <div className="flex-1 p-4 md:p-8 overflow-y-auto">
          {company ? (() => {
            const visible = filterVerdict === 'all'
              ? company.pledges
              : company.pledges.filter(p => p.verdict === filterVerdict)
            return visible.length > 0 ? (
              <div className="space-y-4 max-w-4xl mx-auto w-full">
                {visible.map((pledge, i) => (
                  <PledgeCard key={i} pledge={pledge} />
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center h-40 gap-2 text-gray-400">
                <HugeiconsIcon icon={FilterIcon} size={28} color="currentColor" strokeWidth={1.5} className="text-gray-300" />
                <p className="text-sm">No pledges match this filter</p>
              </div>
            )
          })() : (
            <div className="flex items-center justify-center h-full text-gray-400 text-sm">
              Select a company
            </div>
          )}
        </div>
      </main>
  )
}
