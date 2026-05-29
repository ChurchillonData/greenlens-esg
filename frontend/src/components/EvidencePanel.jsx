import { useState, useMemo } from 'react'
import { HugeiconsIcon } from '@hugeicons/react'
import { LinkSquare01Icon, Sorting01Icon } from '@hugeicons/core-free-icons'

const SOURCE_TYPE = {
  'Guardian':         'Investigative journalism',
  'Carbon Tracker':   'NGO report',
  'InfluenceMap':     'NGO report',
  'ClientEarth':      'NGO report',
  'Global Witness':   'NGO report',
  'Reclaim Finance':  'NGO report',
  'TPI':              'NGO report',
}

function sourceType(sourceName) {
  for (const [key, label] of Object.entries(SOURCE_TYPE)) {
    if (sourceName?.includes(key)) return label
  }
  return null
}

function CredibilityPills({ score }) {
  const filled = Math.round(score * 5)
  return (
    <span className="flex items-center gap-0.5" title={`Credibility: ${score}`}>
      {[1, 2, 3, 4, 5].map(i => (
        <span
          key={i}
          className={`h-1.5 w-4 rounded-full ${i <= filled ? 'bg-emerald-600' : 'bg-gray-300'}`}
        />
      ))}
    </span>
  )
}

const VERDICT_BADGE = {
  supports:    'bg-emerald-700 text-white ring-emerald-800',
  neutral:     'bg-slate-600 text-white ring-slate-700',
  contradicts: 'bg-rose-700 text-white ring-rose-800',
}

function verdictForEvidence(decisionTrace, evidenceIdx) {
  // evidence_ref might be "1", "2,3", "[1]", etc.
  const num = String(evidenceIdx + 1)
  const steps = (decisionTrace ?? []).filter(step => {
    const ref = String(step.evidence_ref ?? '')
    return ref.replace(/[\[\]\s]/g, '').split(',').includes(num)
  })
  if (!steps.length) return null
  // If any step contradicts, show that; otherwise first verdict
  const contradicting = steps.find(s => s.verdict === 'contradicts')
  return contradicting ? contradicting.verdict : steps[0].verdict
}

const SORT_OPTIONS = [
  { value: 'index',       label: 'Evidence number' },
  { value: 'credibility', label: 'Credibility' },
  { value: 'date',        label: 'Date' },
]

export default function EvidencePanel({ evidence, decisionTrace }) {
  const [sortBy, setSortBy] = useState('index')

  const sorted = useMemo(() => {
    if (!evidence?.length) return []
    const indexed = evidence.map((ev, i) => ({ ...ev, _origIdx: i }))
    if (sortBy === 'credibility') {
      return [...indexed].sort((a, b) => b.source_credibility - a.source_credibility)
    }
    if (sortBy === 'date') {
      return [...indexed].sort((a, b) => {
        const da = a.date ? new Date(a.date) : new Date(0)
        const db = b.date ? new Date(b.date) : new Date(0)
        return db - da
      })
    }
    return indexed
  }, [evidence, sortBy])

  if (!evidence?.length) return null

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="font-display text-sm font-bold text-gray-700 uppercase tracking-widest">
          Evidence
          <span className="ml-2 text-xs font-normal normal-case text-gray-400">
            linked to decision steps above
          </span>
        </h3>
        <div className="flex items-center gap-1.5 text-xs text-gray-500">
          <HugeiconsIcon icon={Sorting01Icon} size={13} color="currentColor" strokeWidth={1.5} />
          <span>Sort by</span>
          <select
            value={sortBy}
            onChange={e => setSortBy(e.target.value)}
            className="text-xs border border-gray-200 rounded px-1.5 py-0.5 bg-white focus:outline-none focus:ring-1 focus:ring-green-dark"
          >
            {SORT_OPTIONS.map(o => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="divide-y divide-gray-100 border border-gray-200 rounded-lg overflow-hidden">
        {sorted.map((ev) => {
          const idx = ev._origIdx
          const verdict = verdictForEvidence(decisionTrace, idx)
          const type = sourceType(ev.source)

          return (
            <div key={idx} className="flex items-start gap-3 px-4 py-3 bg-white hover:bg-gray-50/50 transition-colors">
              {/* Index */}
              <span className="text-xs font-semibold text-gray-400 shrink-0 w-5 text-right mt-0.5">
                [{idx + 1}]
              </span>

              {/* Main content */}
              <div className="flex-1 min-w-0 space-y-1.5">
                {/* Source row */}
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-xs font-semibold text-white bg-green-dark px-2 py-0.5 rounded-full shrink-0">
                    {ev.source}
                  </span>
                  {type && (
                    <span className={`text-xs font-medium text-white px-2 py-0.5 rounded-full shrink-0 ${
                      type === 'Investigative journalism' ? 'bg-violet-700' : 'bg-sky-700'
                    }`}>
                      {type}
                    </span>
                  )}
                  {ev.source_credibility > 0 && (
                    <span className="flex items-center gap-1">
                      <span className="text-[10px] font-medium text-slate-500">Credibility</span>
                      <CredibilityPills score={ev.source_credibility} />
                    </span>
                  )}
                  {ev.date && (
                    <span className="text-xs font-medium text-slate-500">{ev.date}</span>
                  )}
                </div>

                {/* Snippet */}
                <p className="text-xs text-gray-600 leading-relaxed line-clamp-3">{ev.text}</p>
              </div>

              {/* Right column: verdict + link */}
              <div className="flex flex-col items-end gap-1.5 shrink-0">
                {verdict && (
                  <span className={`text-xs px-2 py-0.5 rounded-full ring-1 ${VERDICT_BADGE[verdict] ?? VERDICT_BADGE.neutral}`}>
                    {verdict}
                  </span>
                )}
                {ev.url && (
                  <a
                    href={ev.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-emerald-600 hover:text-emerald-800 transition-colors"
                    title="Open source"
                  >
                    <HugeiconsIcon icon={LinkSquare01Icon} size={14} color="currentColor" strokeWidth={1.5} />
                  </a>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
