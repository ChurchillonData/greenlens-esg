import { useState, useRef, useEffect } from 'react'
import { HugeiconsIcon } from '@hugeicons/react'
import { CheckListIcon, Analytics01Icon, Clock01Icon, ArrowRight01Icon, ArrowUp01Icon, ArrowDown01Icon, CheckmarkCircle01Icon } from '@hugeicons/core-free-icons'
import { CLASS_LABELS, COMPANY_LABELS, COMPANY_LOGOS, dotColor, badgeCls, scoreColor } from '../utils/classStyles'

function formatCategory(cat) {
  return cat.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

function CompanyLogo({ companyId, size = 'md' }) {
  const src = COMPANY_LOGOS[companyId]
  const dim = size === 'lg' ? 'w-6 h-6' : size === 'sm' ? 'w-4 h-4' : 'w-5 h-5'

  if (!src) return null

  return (
    <span className={`${dim} rounded shrink-0 flex items-center justify-center overflow-hidden`}>
      <img
        key={src}
        src={src}
        alt={COMPANY_LABELS[companyId] ?? companyId}
        className="w-full h-full object-contain"
        onError={e => { e.currentTarget.style.display = 'none' }}
      />
    </span>
  )
}

function CompanySelect({ companies, value, onChange }) {
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
        className="w-full flex items-center gap-2 border border-gray-300 rounded-md px-3 py-2 bg-white text-sm hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-green-dark"
      >
        <CompanyLogo companyId={value} size="lg" />
        <span className="flex-1 text-left font-medium text-gray-800">{COMPANY_LABELS[value] ?? value}</span>
        <HugeiconsIcon icon={ArrowDown01Icon} size={14} color="currentColor" strokeWidth={1.5} className="text-gray-400 shrink-0" />
      </button>

      {open && (
        <ul className="absolute z-20 mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-lg py-1 max-h-64 overflow-y-auto">
          {companies.map(co => (
            <li key={co}>
              <button
                onClick={() => { onChange(co); setOpen(false) }}
                className={`w-full flex items-center gap-2.5 px-3 py-2 text-sm hover:bg-gray-50 transition-colors ${
                  co === value ? 'bg-green-dark/5 text-green-dark font-medium' : 'text-gray-700'
                }`}
              >
                <CompanyLogo companyId={co} />
                <span>{COMPANY_LABELS[co] ?? co}</span>
                {co === value && (
                  <HugeiconsIcon icon={CheckmarkCircle01Icon} size={14} color="currentColor" strokeWidth={1.5} className="ml-auto text-green-dark" />
                )}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

const PAGE_SIZE = 20

export default function ClaimList({
  activeTab, onTabChange,
  companies, selectedCompany, onSelectCompany,
  claims, selectedIdx, onSelect,
  mobileVisible,
  trackerData = [], trackerSelectedId, onTrackerSelect,
}) {
  const [page, setPage] = useState(0)
  const start = page * PAGE_SIZE
  const paginated = claims.slice(start, start + PAGE_SIZE)
  const totalPages = Math.ceil(claims.length / PAGE_SIZE)

  function handleSelectCompany(co) {
    setPage(0)
    onSelectCompany(co)
  }

  return (
    <aside className={`${mobileVisible ? 'flex' : 'hidden'} md:flex w-full md:w-72 shrink-0 border-r border-paper-border flex-col h-full overflow-hidden bg-white`}>
      {/* Claims / Compare / Tracker tabs */}
      <div className="flex border-b border-gray-200 shrink-0">
        <button
          onClick={() => onTabChange('claims')}
          className={`flex-1 flex items-center justify-center gap-1.5 text-xs font-medium py-2.5 border-b-2 transition-colors ${
            activeTab === 'claims'
              ? 'border-green-dark text-green-dark'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <HugeiconsIcon icon={CheckListIcon} size={15} color="currentColor" strokeWidth={1.5} />
          Claims
        </button>
        <button
          onClick={() => onTabChange('compare')}
          className={`flex-1 flex items-center justify-center gap-1.5 text-xs font-medium py-2.5 border-b-2 transition-colors ${
            activeTab === 'compare'
              ? 'border-green-dark text-green-dark'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <HugeiconsIcon icon={Analytics01Icon} size={15} color="currentColor" strokeWidth={1.5} />
          Compare
        </button>
        <button
          onClick={() => onTabChange('tracker')}
          className={`flex-1 flex items-center justify-center gap-1.5 text-xs font-medium py-2.5 border-b-2 transition-colors ${
            activeTab === 'tracker'
              ? 'border-green-dark text-green-dark'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <HugeiconsIcon icon={Clock01Icon} size={15} color="currentColor" strokeWidth={1.5} />
          Tracker
        </button>
      </div>

      {activeTab === 'tracker' ? (
        <>
          {/* Tracker company list */}
          <div className="px-4 py-2 border-b border-gray-200 shrink-0">
            <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Companies</p>
          </div>
          <ul className="overflow-y-auto flex-1 divide-y divide-gray-50">
            {trackerData.map(co => {
              const label = COMPANY_LABELS[co.company_id] ?? co.company_id
              const logoSrc = COMPANY_LOGOS[co.company_id]
              const isSelected = co.company_id === trackerSelectedId
              const vc = co.verdict_counts ?? {}
              const reversed  = vc.reversed             ?? 0
              const partial   = vc.partially_fulfilled   ?? 0
              const fulfilled = vc.fulfilled             ?? 0
              const tooEarly  = vc.too_early             ?? 0
              return (
                <li key={co.company_id}>
                  <button
                    onClick={() => onTrackerSelect(co.company_id)}
                    className={`w-full flex items-center gap-3 px-4 py-3 text-left transition-all group ${
                      isSelected
                        ? 'bg-emerald-500/10 ring-1 ring-inset ring-emerald-400/25 shadow-sm'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    {logoSrc && (
                      <span className="w-7 h-7 rounded-full shrink-0 flex items-center justify-center overflow-hidden border border-gray-200 bg-white">
                        <img src={logoSrc} alt={label} className="w-5 h-5 object-contain"
                          onError={e => { e.currentTarget.style.display = 'none' }} />
                      </span>
                    )}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between gap-1">
                        <p className={`text-xs font-semibold truncate ${isSelected ? 'text-green-dark' : 'text-gray-800'}`}>
                          {label}
                        </p>
                        <span className="text-[9px] text-gray-400 shrink-0">{co.total_analyzed}</span>
                      </div>
                      <div className="flex items-center gap-1 mt-0.5 flex-wrap">
                        {reversed  > 0 && <span className="text-[9px] font-bold text-rose-400">{reversed} rev</span>}
                        {partial   > 0 && <span className="text-[9px] font-bold text-amber-400">{partial} part</span>}
                        {fulfilled > 0 && <span className="text-[9px] font-bold text-emerald-500">{fulfilled} ful</span>}
                        {tooEarly  > 0 && <span className="text-[9px] font-bold text-sky-400">{tooEarly} early</span>}
                      </div>
                    </div>
                    <HugeiconsIcon icon={ArrowRight01Icon} size={14} color="currentColor" strokeWidth={1.5} className={`shrink-0 transition-colors ${isSelected ? 'text-green-dark' : 'text-gray-300 group-hover:text-gray-400'}`} />
                  </button>
                </li>
              )
            })}
          </ul>
        </>
      ) : (
        <>
          {/* Company selector */}
          <div className="px-4 py-3 border-b border-gray-200 shrink-0">
            <label className="block text-xs font-medium text-gray-500 mb-1">Company</label>
            <CompanySelect
              companies={companies}
              value={selectedCompany}
              onChange={handleSelectCompany}
            />
          </div>

          {/* Claim list */}
          <ul className="overflow-y-auto flex-1 divide-y divide-gray-100">
            {paginated.map((claim, i) => {
              const globalIdx = start + i
              return (
                <li key={globalIdx}>
                  <button
                    onClick={() => onSelect(globalIdx)}
                    className={`w-full text-left px-4 py-3 transition-colors group ${
                      selectedIdx === globalIdx
                        ? 'bg-emerald-50 border-l-4 border-emerald-700'
                        : 'border-l-4 border-transparent hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-1">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1 flex-wrap">
                          <span className={`w-2 h-2 rounded-full shrink-0 ${dotColor(claim.predicted_class)}`} />
                          <span className="text-xs font-medium text-gray-700 truncate">
                            {formatCategory(claim.category)}
                          </span>
                          <span className={`inline-block text-xs px-2 py-0.5 rounded-full ring-1 ${badgeCls(claim.predicted_class)}`}>
                            {CLASS_LABELS[claim.predicted_class]}
                          </span>
                        </div>
                        <p className="text-xs text-gray-500 line-clamp-2 leading-relaxed mb-1">
                          "{claim.claim_text}"
                        </p>
                        <p className="text-xs text-gray-400">
                          GreenSignal: <span className={`font-mono font-bold ${scoreColor(claim.risk_score)}`}>{claim.risk_score.toFixed(2)}</span>
                        </p>
                      </div>
                      <HugeiconsIcon icon={ArrowRight01Icon} size={16} color="currentColor" strokeWidth={1.5} className="text-gray-300 group-hover:text-gray-400 shrink-0 mt-1 transition-colors" />
                    </div>
                  </button>
                </li>
              )
            })}
          </ul>

          {/* Pagination footer */}
          <div className="px-4 py-2 border-t border-gray-100 flex items-center justify-between shrink-0">
            <span className="text-xs text-gray-400">
              {totalPages > 1
                ? `${start + 1}-${Math.min(start + PAGE_SIZE, claims.length)} of ${claims.length} claims`
                : `${claims.length} claims`}
            </span>
            <div className="flex gap-1">
              <button
                onClick={() => setPage(p => Math.max(0, p - 1))}
                disabled={page === 0}
                className="p-1 rounded text-gray-400 hover:text-gray-600 disabled:opacity-30 disabled:cursor-not-allowed"
              >
                <HugeiconsIcon icon={ArrowUp01Icon} size={14} color="currentColor" strokeWidth={1.5} />
              </button>
              <button
                onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))}
                disabled={page >= totalPages - 1}
                className="p-1 rounded text-gray-400 hover:text-gray-600 disabled:opacity-30 disabled:cursor-not-allowed"
              >
                <HugeiconsIcon icon={ArrowDown01Icon} size={14} color="currentColor" strokeWidth={1.5} />
              </button>
            </div>
          </div>
        </>
      )}
    </aside>
  )
}
