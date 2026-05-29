import { HugeiconsIcon } from '@hugeicons/react'
import { ArrowLeft01Icon, Target01Icon, Calendar01Icon } from '@hugeicons/core-free-icons'
import { COMPANY_LABELS, COMPANY_LOGOS, scoreColor, badgeCls, CLASS_LABELS } from '../utils/classStyles'
import ClaimComparison from './ClaimComparison'

const CATEGORIES = [
  { key: 'emissions_reduction',   short: 'Emissions'   },
  { key: 'renewables_investment', short: 'Renewables'  },
  { key: 'net_zero',              short: 'Net Zero'    },
  { key: 'scope_3',               short: 'Scope 3'     },
  { key: 'biodiversity',          short: 'Biodiversity'},
  { key: 'methane',               short: 'Methane'     },
  { key: 'just_transition',       short: 'Just Trans.' },
  { key: 'climate_lobbying',      short: 'Lobbying'    },
  { key: 'flaring',               short: 'Flaring'     },
  { key: 'carbon_capture',        short: 'Carbon Cap.' },
  { key: 'other',                 short: 'Other'       },
]

const DOT_COLOR = {
  well_substantiated:   'bg-emerald-600',
  weakly_substantiated: 'bg-amber-600',
  contradicted:         'bg-rose-700',
}

function riskTrackColor(score) {
  if (score <= 0.4) return 'bg-emerald-600'
  if (score <= 0.7) return 'bg-amber-600'
  return 'bg-rose-700'
}

function accColor(score) {
  if (score == null) return 'text-gray-300'
  if (score >= 0.6) return 'text-emerald-700'
  if (score >= 0.4) return 'text-amber-600'
  if (score >= 0.2) return 'text-rose-600'
  return 'text-rose-800'
}

function accTrackColor(score) {
  if (score == null) return 'bg-gray-200'
  if (score >= 0.6) return 'bg-emerald-500'
  if (score >= 0.4) return 'bg-amber-500'
  return 'bg-rose-600'
}

function cellCls(n) {
  if (n === 0) return 'text-gray-300 bg-transparent'
  if (n === 1) return 'text-emerald-700 bg-emerald-50 border border-emerald-200'
  if (n === 2) return 'text-emerald-800 bg-emerald-100 border border-emerald-300'
  if (n === 3) return 'text-white bg-emerald-600 border border-emerald-700'
  return 'text-white bg-emerald-800 border border-emerald-900'
}

function CompanyLogo({ companyId }) {
  const src = COMPANY_LOGOS[companyId]
  if (!src) return null
  return (
    <span className="w-5 h-5 rounded shrink-0 flex items-center justify-center overflow-hidden">
      <img key={src} src={src} alt="" className="w-full h-full object-contain"
        onError={e => { e.currentTarget.style.display = 'none' }} />
    </span>
  )
}

export default function CompareView({ data, trackerData = [], onBack, onViewClaim }) {
  const companies = [...new Set(data.map(r => r.company_id))].sort()
  const accByCompany = Object.fromEntries(
    trackerData.map(c => [c.company_id, c.accountability_score ?? null])
  )

  const rows = companies.map(co => {
    const claims = data.filter(r => r.company_id === co)
    const avgScore = claims.reduce((s, c) => s + c.risk_score, 0) / claims.length
    const dist = { well_substantiated: 0, weakly_substantiated: 0, contradicted: 0 }
    claims.forEach(c => { dist[c.predicted_class] = (dist[c.predicted_class] || 0) + 1 })
    const targets   = claims.filter(c => c.target_value  != null).length
    const deadlines = claims.filter(c => c.deadline_year != null).length
    const catCounts = {}
    CATEGORIES.forEach(cat => { catCounts[cat.key] = claims.filter(c => c.category === cat.key).length })
    return { co, claims, avgScore, dist, targets, deadlines, catCounts }
  }).sort((a, b) => b.avgScore - a.avgScore)

  const maxScore   = Math.max(...rows.map(r => r.avgScore))
  const overallAvg = data.reduce((s, c) => s + c.risk_score, 0) / data.length

  return (
    <main className="flex-1 overflow-y-auto bg-paper">
      <div className="p-4 md:p-8 space-y-8">

        {/* Mobile back */}
        {onBack && (
          <button onClick={onBack} className="md:hidden flex items-center gap-1.5 text-sm text-green-dark font-medium">
            <HugeiconsIcon icon={ArrowLeft01Icon} size={16} color="currentColor" strokeWidth={1.5} />
            Back to claims
          </button>
        )}

        {/* Page heading — no KPI cards, just clear typographic context */}
        <div className="border-b border-paper-border pb-5">
          <h2 className="font-display text-xl md:text-2xl font-black text-gray-900">
            Company Comparison
          </h2>
          <p className="text-sm text-gray-500 mt-1">
            10 oil &amp; gas majors &nbsp;·&nbsp; 191 ESG claims &nbsp;·&nbsp;
            portfolio avg GreenSignal{' '}
            <span className={`font-mono font-bold ${scoreColor(overallAvg)}`}>
              {overallAvg.toFixed(2)}
            </span>
          </p>
        </div>

        {/* ── Risk ranking table ── */}
        <section className="space-y-3">
          <h3 className="font-display text-sm font-bold text-gray-700 uppercase tracking-widest">
            GreenSignal ranking
            <span className="ml-2 text-xs font-normal normal-case text-gray-400">
              strongest greenwashing signal first
            </span>
          </h3>

          <div className="bg-white border border-paper-border rounded-xl overflow-hidden">
            {/* Table header */}
            <div className="grid grid-cols-[2rem_1fr_6rem] md:grid-cols-[2rem_1fr_6rem_10rem_7rem] items-center gap-x-4 px-4 py-2 bg-paper border-b border-paper-border text-[11px] font-semibold text-gray-400 uppercase tracking-wider">
              <span>#</span>
              <span>Company</span>
              <span className="text-right">GreenSignal</span>
              <span className="hidden md:block">Classification</span>
              <span className="hidden md:block text-right">Commitment</span>
            </div>

            {/* Rows */}
            {rows.map((row, i) => {
              const barPct = (row.avgScore / maxScore) * 100
              const total  = row.claims.length
              return (
                <div
                  key={row.co}
                  className="grid grid-cols-[2rem_1fr_6rem] md:grid-cols-[2rem_1fr_6rem_10rem_7rem] items-center gap-x-4 px-4 py-3.5 border-b border-paper-border last:border-0 hover:bg-paper/50 transition-colors"
                >
                  {/* Rank */}
                  <span className="font-display font-black text-gray-300 text-base leading-none">
                    {i + 1}
                  </span>

                  {/* Company + bar */}
                  <div className="min-w-0">
                    <div className="flex items-center gap-2 mb-1.5">
                      <CompanyLogo companyId={row.co} />
                      <span className="text-sm font-semibold text-gray-800 truncate">
                        {COMPANY_LABELS[row.co]}
                      </span>
                    </div>
                    <div className="flex items-center gap-0.5 w-full">
                      {Array.from({ length: 10 }, (_, i) => (
                        <div key={i} className={`h-1.5 flex-1 rounded-full ${i < Math.round(row.avgScore * 10) ? riskTrackColor(row.avgScore) : 'bg-paper-border'}`} />
                      ))}
                    </div>
                    {/* Mobile-only: classification + commitment */}
                    <div className="flex md:hidden items-center gap-2.5 mt-1.5 flex-wrap">
                      <div className="flex items-center gap-1.5 flex-wrap">
                        {Object.entries(row.dist).filter(([, n]) => n > 0).map(([cls, n]) => (
                          <span key={cls} className="flex items-center gap-1 text-[10px] text-gray-600">
                            <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${DOT_COLOR[cls]}`} />
                            {n}
                          </span>
                        ))}
                        <span className="text-[10px] text-gray-400">/{total}</span>
                      </div>
                      <span className="text-gray-200 text-[10px]">|</span>
                      <span className="flex items-center gap-1 text-[10px] text-gray-400">
                        <HugeiconsIcon icon={Target01Icon} size={10} color="currentColor" strokeWidth={1.5} />
                        {row.targets}/{total}
                      </span>
                      <span className="flex items-center gap-1 text-[10px] text-gray-400">
                        <HugeiconsIcon icon={Calendar01Icon} size={10} color="currentColor" strokeWidth={1.5} />
                        {row.deadlines}/{total}
                      </span>
                    </div>
                  </div>

                  {/* Score */}
                  <div className="text-right">
                    <span className={`font-mono text-lg font-bold tabular-nums ${scoreColor(row.avgScore)}`}>
                      {row.avgScore.toFixed(2)}
                    </span>
                  </div>

                  {/* Classification — desktop only */}
                  <div className="hidden md:flex items-center gap-2 flex-wrap">
                    {Object.entries(row.dist)
                      .filter(([, n]) => n > 0)
                      .map(([cls, n]) => (
                        <span key={cls} className="flex items-center gap-1 text-xs text-gray-600">
                          <span className={`w-2 h-2 rounded-full shrink-0 ${DOT_COLOR[cls]}`} />
                          {n}
                        </span>
                      ))}
                    <span className="text-xs text-gray-400 font-medium">
                      /{total}
                    </span>
                  </div>

                  {/* Commitment — desktop only */}
                  <div className="hidden md:flex items-center justify-end gap-3 text-xs text-gray-400">
                    <span className="flex items-center gap-1" title="Claims with quantified targets">
                      <HugeiconsIcon icon={Target01Icon} size={11} color="currentColor" strokeWidth={1.5} />
                      {row.targets}/{total}
                    </span>
                    <span className="flex items-center gap-1" title="Claims with stated deadlines">
                      <HugeiconsIcon icon={Calendar01Icon} size={11} color="currentColor" strokeWidth={1.5} />
                      {row.deadlines}/{total}
                    </span>
                  </div>
                </div>
              )
            })}
          </div>

          {/* Legend */}
          <div className="flex items-center gap-4 flex-wrap text-xs text-gray-400 pt-0.5 pl-1">
            {Object.entries(DOT_COLOR).map(([cls, dot]) => (
              <span key={cls} className="flex items-center gap-1.5">
                <span className={`w-2 h-2 rounded-full shrink-0 ${dot}`} />
                {CLASS_LABELS[cls]}
              </span>
            ))}
            <span className="flex items-center gap-1 ml-2">
              <HugeiconsIcon icon={Target01Icon} size={11} color="currentColor" strokeWidth={1.5} />
              = quantified target
            </span>
            <span className="flex items-center gap-1">
              <HugeiconsIcon icon={Calendar01Icon} size={11} color="currentColor" strokeWidth={1.5} />
              = stated deadline
            </span>
          </div>
        </section>

        {/* ── Pledge Accountability ranking ── */}
        {trackerData.length > 0 && (
          <section className="space-y-3">
            <h3 className="font-display text-sm font-bold text-gray-700 uppercase tracking-widest">
              Pledge Accountability
              <span className="ml-2 text-xs font-normal normal-case text-gray-400">
                how well 2021 pledges held up against 2023–2025 evidence · weighted by claim materiality
              </span>
            </h3>

            <div className="bg-white border border-paper-border rounded-xl overflow-hidden">
              <div className="grid grid-cols-[2rem_1fr_5rem] md:grid-cols-[2rem_1fr_5rem_8rem] items-center gap-x-4 px-4 py-2 bg-paper border-b border-paper-border text-[11px] font-semibold text-gray-400 uppercase tracking-wider">
                <span>#</span>
                <span>Company</span>
                <span className="text-right">Score</span>
                <span className="hidden md:block text-right">Pledges</span>
              </div>

              {[...trackerData]
                .sort((a, b) => (b.accountability_score ?? -1) - (a.accountability_score ?? -1))
                .map((co, i) => {
                  const acc   = co.accountability_score
                  const pct   = acc != null ? Math.round(acc * 100) : null
                  const vc    = co.verdict_counts ?? {}
                  return (
                    <div
                      key={co.company_id}
                      className="grid grid-cols-[2rem_1fr_5rem] md:grid-cols-[2rem_1fr_5rem_8rem] items-center gap-x-4 px-4 py-3 border-b border-paper-border last:border-0"
                    >
                      <span className="font-display font-black text-gray-300 text-base leading-none">{i + 1}</span>

                      <div className="min-w-0">
                        <div className="flex items-center gap-2 mb-1.5">
                          <CompanyLogo companyId={co.company_id} />
                          <span className="text-sm font-semibold text-gray-800 truncate">{co.company_label}</span>
                        </div>
                        <div className="flex items-center gap-0.5 w-full">
                          {Array.from({ length: 10 }, (_, i) => (
                            <div key={i} className={`h-1.5 flex-1 rounded-full ${i < Math.round((acc ?? 0) * 10) ? accTrackColor(acc) : 'bg-paper-border'}`} />
                          ))}
                        </div>
                        {/* Mobile-only: pledge breakdown */}
                        <div className="flex md:hidden items-center gap-2 mt-1.5 flex-wrap">
                          {(vc.reversed ?? 0) > 0 && <span className="text-[10px] text-rose-400 font-semibold">{vc.reversed} rev</span>}
                          {(vc.partially_fulfilled ?? 0) > 0 && <span className="text-[10px] text-amber-500 font-semibold">{vc.partially_fulfilled} part</span>}
                          {(vc.fulfilled ?? 0) > 0 && <span className="text-[10px] text-emerald-600 font-semibold">{vc.fulfilled} ful</span>}
                          {(vc.too_early ?? 0) > 0 && <span className="text-[10px] text-sky-400 font-semibold">{vc.too_early} early</span>}
                        </div>
                      </div>

                      <div className="text-right">
                        <span className={`font-mono text-lg font-bold tabular-nums ${accColor(acc)}`}>
                          {pct != null ? `${pct}%` : '—'}
                        </span>
                      </div>

                      <div className="hidden md:flex items-center justify-end gap-2 text-[10px] text-gray-400 flex-wrap">
                        {(vc.reversed ?? 0) > 0 && <span className="text-rose-400 font-semibold">{vc.reversed} rev</span>}
                        {(vc.partially_fulfilled ?? 0) > 0 && <span className="text-amber-500 font-semibold">{vc.partially_fulfilled} part</span>}
                        {(vc.fulfilled ?? 0) > 0 && <span className="text-emerald-600 font-semibold">{vc.fulfilled} ful</span>}
                      </div>
                    </div>
                  )
                })}
            </div>

            <p className="text-[11px] text-gray-400 pl-1">
              Score = 1 − weighted reversal rate. Net-zero and scope 3 pledges carry higher weight than operational claims.
              Too-early pledges (not yet due) are excluded from the calculation.
            </p>
          </section>
        )}

        {/* ── Comparison mode ── */}
        <ClaimComparison
          data={data}
          companies={companies}
          onViewClaim={onViewClaim}
        />

        {/* ── Category coverage ── */}
        <section className="space-y-3">
          <h3 className="font-display text-sm font-bold text-gray-700 uppercase tracking-widest">
            Category coverage
            <span className="ml-2 text-xs font-normal normal-case text-gray-400">
              claims per topic area
            </span>
          </h3>

          <div className="bg-white border border-paper-border rounded-xl overflow-hidden flex">

            {/* Fixed company column — never scrolls */}
            <div className="relative shrink-0">
              {/* Header */}
              <div className="h-10 flex items-center bg-paper border-b border-paper-border px-4">
                <span className="text-[11px] font-semibold text-gray-400 uppercase tracking-wide whitespace-nowrap">
                  Company
                </span>
              </div>
              {/* Rows */}
              {rows.map((row, i) => (
                <div
                  key={row.co}
                  className={`h-11 flex items-center gap-2 bg-white px-4 ${i < rows.length - 1 ? 'border-b border-paper-border' : ''}`}
                >
                  <CompanyLogo companyId={row.co} />
                  <span className="text-xs font-medium text-gray-700 whitespace-nowrap">
                    {COMPANY_LABELS[row.co]}
                  </span>
                </div>
              ))}
            </div>

              {/* Fade — softens where scrolling content disappears behind this column */}
              <div className="pointer-events-none absolute inset-y-0 right-0 w-4 bg-gradient-to-l from-white to-transparent" />

            {/* Scrollable category columns */}
            <div className="relative flex-1 min-w-0">
              {/* Right-edge fade — signals scrollable content */}
              <div className="pointer-events-none absolute inset-y-0 right-0 w-10 bg-gradient-to-l from-white to-transparent z-10" />
            <div className="overflow-x-auto h-full">
              {/* Header */}
              <div className="h-10 flex items-center bg-paper border-b border-paper-border w-full">
                {CATEGORIES.map(cat => (
                  <div key={cat.key} className="h-full flex flex-1 items-center justify-center px-2 text-[11px] font-semibold text-gray-400 uppercase tracking-wide whitespace-nowrap min-w-[72px]">
                    {cat.short}
                  </div>
                ))}
              </div>
              {/* Rows */}
              {rows.map((row, i) => (
                <div
                  key={row.co}
                  className={`h-11 flex items-center w-full hover:bg-paper/40 transition-colors ${i < rows.length - 1 ? 'border-b border-paper-border' : ''}`}
                >
                  {CATEGORIES.map(cat => (
                    <div key={cat.key} className="h-full flex flex-1 items-center justify-center px-2 min-w-[72px]">
                      <span className={`inline-flex items-center justify-center w-7 h-7 rounded-lg text-xs font-bold ${cellCls(row.catCounts[cat.key])}`}>
                        {row.catCounts[cat.key] || '·'}
                      </span>
                    </div>
                  ))}
                </div>
              ))}
            </div>
            </div>

          </div>
          <p className="md:hidden text-[10px] text-gray-400 text-right pt-1 pr-1">
            ← swipe to see all categories →
          </p>
        </section>

      </div>
    </main>
  )
}
