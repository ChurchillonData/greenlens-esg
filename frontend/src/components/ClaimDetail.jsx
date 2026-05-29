import { HugeiconsIcon } from '@hugeicons/react'
import { Target01Icon, Calendar01Icon, EarthIcon, RulerIcon, ArrowLeft01Icon } from '@hugeicons/core-free-icons'
import { COMPANY_LABELS, COMPANY_LOGOS, COMPANY_REPORT_YEAR, CLASS_LABELS, badgeCls, scoreColor } from '../utils/classStyles'
import RationalePanel from './RationalePanel'
import DecisionTrace from './DecisionTrace'
import EvidencePanel from './EvidencePanel'

function formatCategory(cat) {
  return cat.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

function CompanyLogo({ companyId }) {
  const src = COMPANY_LOGOS[companyId]
  if (!src) return null
  return (
    <span className="w-14 h-14 md:w-20 md:h-20 rounded-2xl shrink-0 flex items-center justify-center overflow-hidden border-2 border-gray-100 bg-white shadow-lg">
      <img
        key={src}
        src={src}
        alt={COMPANY_LABELS[companyId] ?? companyId}
        className="w-10 h-10 md:w-14 md:h-14 object-contain"
        onError={e => { e.currentTarget.style.display = 'none' }}
      />
    </span>
  )
}

function AnatomySignal({ icon, label, value, present }) {
  return (
    <div className="flex items-center gap-3 bg-white border border-gray-200 rounded-xl px-3 py-2.5 shadow-sm">
      <span className={`shrink-0 ${present ? 'text-green-dark' : 'text-gray-300'}`}>{icon}</span>
      <div className="flex-1 min-w-0">
        <p className="text-xs font-bold text-gray-800 leading-none">{label}</p>
        <p className="text-[11px] text-gray-400 mt-0.5 leading-none truncate">
          {present ? value : 'Not stated'}
        </p>
      </div>
      {present ? (
        <span className="shrink-0 w-6 h-6 rounded-full bg-emerald-700 flex items-center justify-center">
          <svg className="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7"/>
          </svg>
        </span>
      ) : (
        <span className="shrink-0 w-6 h-6 rounded-full bg-gray-200 flex items-center justify-center">
          <svg className="w-3 h-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </span>
      )}
    </div>
  )
}

function ClaimAnatomy({ claim }) {
  const hasTarget   = claim.target_value != null
  const hasDeadline = claim.deadline_year != null
  const hasScope    = !!claim.scope
  const hasMeasure  = !!(claim.target_value && claim.target_unit)

  const targetLabel = hasTarget
    ? `${claim.target_value} ${claim.target_unit ?? ''}`.trim()
    : null

  return (
    <div className="grid grid-cols-2 gap-2 pt-1">
      <AnatomySignal
        icon={<HugeiconsIcon icon={Target01Icon} size={14} color="currentColor" strokeWidth={1.5} />}
        label="Target"
        value={targetLabel}
        present={hasTarget}
      />
      <AnatomySignal
        icon={<HugeiconsIcon icon={Calendar01Icon} size={14} color="currentColor" strokeWidth={1.5} />}
        label="Deadline"
        value={hasDeadline ? String(claim.deadline_year) : null}
        present={hasDeadline}
      />
      <AnatomySignal
        icon={<HugeiconsIcon icon={EarthIcon} size={14} color="currentColor" strokeWidth={1.5} />}
        label="Scope"
        value={claim.scope}
        present={hasScope}
      />
      <AnatomySignal
        icon={<HugeiconsIcon icon={RulerIcon} size={14} color="currentColor" strokeWidth={1.5} />}
        label="Measurable"
        value={hasMeasure ? `${claim.target_value} ${claim.target_unit}` : null}
        present={hasMeasure}
      />
    </div>
  )
}

const SEGMENTS = 10

function riskSegmentColor(score) {
  if (score <= 0.4) return 'bg-emerald-600'
  if (score <= 0.7) return 'bg-amber-600'
  return 'bg-rose-700'
}

function RiskMeter({ score }) {
  const filled = Math.round(score * SEGMENTS)
  const activeColor = riskSegmentColor(score)
  return (
    <div className="space-y-1.5">
      <div className="flex items-center gap-1">
        {Array.from({ length: SEGMENTS }, (_, i) => (
          <div
            key={i}
            className={`h-3 flex-1 rounded-full transition-colors ${i < filled ? activeColor : 'bg-gray-200'}`}
          />
        ))}
      </div>
      <div className="flex justify-between text-[10px] font-medium text-gray-400 px-0.5">
        <span>Low</span>
        <span>Moderate</span>
        <span>High</span>
      </div>
    </div>
  )
}

function ScoreBlock({ predictedClass, riskScore }) {
  const riskLabel =
    riskScore <= 0.4 ? 'Low greenwashing signal' :
    riskScore <= 0.7 ? 'Moderate greenwashing signal' :
    'Strong greenwashing signal'

  return (
    <div className="w-full md:shrink-0 md:min-w-[220px] md:w-auto space-y-3">
      <div>
        <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">GreenSignal</p>
        <p className={`font-mono text-6xl md:text-7xl font-black tabular-nums leading-none ${scoreColor(riskScore)}`}>
          {riskScore.toFixed(2)}
        </p>
        <p className={`font-display text-sm font-bold mt-1 ${scoreColor(riskScore)}`}>{riskLabel}</p>
      </div>
      <RiskMeter score={riskScore} />
      <span className={`inline-block text-xs px-3 py-1 rounded-full ring-1 font-semibold ${badgeCls(predictedClass)}`}>
        {CLASS_LABELS[predictedClass]}
      </span>
    </div>
  )
}

export default function ClaimDetail({ claim, onBack }) {
  if (!claim) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-400 text-sm">
        Select a claim to view details
      </div>
    )
  }

  const companyName = COMPANY_LABELS[claim.company_id] ?? claim.company_id
  const reportYear = COMPANY_REPORT_YEAR[claim.company_id] ?? 2024
  const sourceRef = claim.page
    ? `${companyName} Sustainability Report ${reportYear}, p.${claim.page}`
    : `${companyName} Sustainability Report ${reportYear}`

  return (
    <main className="flex-1 overflow-y-auto bg-paper">

      {/* Company identity bar */}
      <div className="bg-white border-b border-gray-200 px-4 md:px-8 py-4 md:py-5">
        {/* Mobile back button */}
        {onBack && (
          <button
            onClick={onBack}
            className="md:hidden flex items-center gap-1.5 text-sm text-green-dark font-medium mb-3"
          >
            <HugeiconsIcon icon={ArrowLeft01Icon} size={16} color="currentColor" strokeWidth={1.5} />
            All claims
          </button>
        )}
        <div className="flex items-center justify-between gap-3 flex-wrap">
          <div className="flex items-center gap-3 md:gap-5">
            <CompanyLogo companyId={claim.company_id} />
            <div>
              <h1 className="font-display text-xl md:text-2xl font-black text-gray-900 leading-tight">{companyName}</h1>
              <p className="text-xs md:text-sm text-gray-500 mt-0.5 uppercase tracking-wide font-medium">{formatCategory(claim.category)}</p>
            </div>
          </div>
          <div className="flex items-center gap-1.5 text-xs text-gray-500 border border-gray-200 rounded-md px-3 py-1.5 shrink-0">
            <HugeiconsIcon icon={Calendar01Icon} size={14} color="currentColor" strokeWidth={1.5} className="text-gray-400" />
            Report year: <span className="font-semibold text-gray-700 ml-1">{reportYear}</span>
          </div>
        </div>
      </div>

      <div className="p-4 md:p-8 space-y-6 md:space-y-8">

        {/* Claim + Score — stacked on mobile, side-by-side on desktop */}
        <div className="flex flex-col md:flex-row md:items-start gap-6 md:gap-10">
          <div className="flex-1 min-w-0 space-y-4">
            <blockquote className="text-gray-800 text-base leading-relaxed italic">
              "{claim.claim_text}"
            </blockquote>
            <p className="text-xs text-gray-400">
              Source: <span className="text-gray-600">{sourceRef}</span>
            </p>
            <ClaimAnatomy claim={claim} />
          </div>
          <ScoreBlock predictedClass={claim.predicted_class} riskScore={claim.risk_score} />
        </div>

        <div className="border-t border-gray-200" />

        <RationalePanel rationale={claim.rationale} keyFactors={claim.key_factors} />

        <div className="border-t border-gray-200" />

        <DecisionTrace steps={claim.decision_trace} />

        <div className="border-t border-gray-200" />

        <EvidencePanel evidence={claim.evidence} decisionTrace={claim.decision_trace} />

      </div>
    </main>
  )
}
