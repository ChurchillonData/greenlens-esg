import { useState, useMemo } from 'react'
import { HugeiconsIcon } from '@hugeicons/react'
import { Cancel01Icon } from '@hugeicons/core-free-icons'
import data from './data/rationales.json'
import trackerData from './data/tracker.json'
import Header from './components/Header'
import ClaimList from './components/ClaimList'
import ClaimDetail from './components/ClaimDetail'
import CompareView from './components/CompareView'
import CommitmentTracker from './components/CommitmentTracker'
import Footer from './components/Footer'

const companies = [...new Set(data.map(r => r.company_id))].sort()

const SOURCE_WEIGHTS = [
  { source: 'Carbon Tracker',  weight: '0.95', type: 'NGO report' },
  { source: 'InfluenceMap',    weight: '0.95', type: 'NGO report' },
  { source: 'TPI',             weight: '0.92', type: 'NGO report' },
  { source: 'ClientEarth',     weight: '0.90', type: 'NGO report' },
  { source: 'Reclaim Finance', weight: '0.88', type: 'NGO report' },
  { source: 'Global Witness',  weight: '0.85', type: 'NGO report' },
  { source: 'The Guardian',    weight: '0.75', type: 'Investigative journalism' },
]

function SourceInfoModal({ onClose }) {
  return (
    <div
      className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-xl shadow-xl w-full max-w-md p-6"
        onClick={e => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold text-gray-800">Methodology</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 p-0.5 rounded transition-colors">
            <HugeiconsIcon icon={Cancel01Icon} size={16} color="currentColor" strokeWidth={1.5} />
          </button>
        </div>

        <div className="space-y-3 mb-4">
          <div>
            <p className="text-[11px] font-bold text-gray-700 uppercase tracking-wider mb-0.5">GreenSignal (0–1)</p>
            <p className="text-xs text-gray-500 leading-relaxed">
              Claim-level greenwashing signal. GPT-4o-mini scores each ESG claim against retrieved NGO
              evidence. Scores are then scaled by a <em>materiality multiplier</em> — net-zero and scope 3
              claims receive up to 1.35× weight because they are more material to a company's climate
              commitment than operational disclosures. Higher = stronger greenwashing signal.
            </p>
          </div>
          <div>
            <p className="text-[11px] font-bold text-gray-700 uppercase tracking-wider mb-0.5">Pledge Accountability (0–100%)</p>
            <p className="text-xs text-gray-500 leading-relaxed">
              Company-level pledge-keeping score derived from the Commitment Tracker. Measures how well
              2021 sustainability pledges held up against 2023–2025 NGO evidence. Formula: 1 − weighted
              reversal rate, where high-materiality pledges (net-zero, scope 3) carry more weight than
              operational claims. Too-early pledges are excluded. Lower = more broken promises.
            </p>
          </div>
        </div>

        <p className="text-[11px] font-semibold text-gray-500 mb-2 uppercase tracking-wider">Source credibility weights</p>
        <p className="text-xs text-gray-400 mb-3 leading-relaxed">
          Source weights control retrieval priority. The GreenSignal is assigned by the model from
          evidence <em>content</em>, not by a weighted formula. Physical risk (asset-level climate exposure)
          is not modelled — it requires geographic data outside this pipeline's scope.
        </p>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-gray-100">
                <th className="text-left pb-2 text-gray-500 font-medium">Source</th>
                <th className="text-left pb-2 text-gray-500 font-medium">Type</th>
                <th className="text-right pb-2 text-gray-500 font-medium">Weight</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {SOURCE_WEIGHTS.map(row => (
                <tr key={row.source}>
                  <td className="py-2 text-gray-700 font-medium">{row.source}</td>
                  <td className="py-2 text-gray-400 italic">{row.type}</td>
                  <td className="py-2 text-right font-semibold text-green-dark">{row.weight}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-gray-400 mt-4">
          Weights are static for this prototype. A production system would feed them into a
          deterministic post-processing formula, replacing the LLM's implicit judgment with
          explicit, auditable weighted aggregation.
        </p>
      </div>
    </div>
  )
}

export default function App() {
  const [activeTab, setActiveTab] = useState('claims')
  const [selectedCompany, setSelectedCompany] = useState(companies[0])
  const [selectedIdx, setSelectedIdx] = useState(0)
  const [showSourceInfo, setShowSourceInfo] = useState(false)
  const [trackerSelectedId, setTrackerSelectedId] = useState(trackerData[0]?.company_id ?? null)
  // mobile: 'list' shows the sidebar, 'detail' shows the main panel
  const [mobileView, setMobileView] = useState('list')

  const claims = useMemo(
    () => data.filter(r => r.company_id === selectedCompany),
    [selectedCompany]
  )

  function handleTabChange(tab) {
    setActiveTab(tab)
    if (tab === 'compare') setMobileView('detail')
    else setMobileView('list')
  }

  function handleSelectClaim(idx) {
    setSelectedIdx(idx)
    setMobileView('detail')
  }

  function handleSelectCompany(co) {
    setSelectedCompany(co)
    setSelectedIdx(0)
  }

  function handleTrackerSelect(id) {
    setTrackerSelectedId(id)
    setMobileView('detail')
  }

  function handleBack() {
    setMobileView('list')
    if (activeTab === 'compare') setActiveTab('claims')
  }

  function handleViewClaim(companyId, claim) {
    const companyClaims = data.filter(r => r.company_id === companyId)
    const idx = Math.max(0, companyClaims.indexOf(claim))
    setSelectedCompany(companyId)
    setSelectedIdx(idx)
    setActiveTab('claims')
    setMobileView('detail')
  }

  return (
    <div className="flex flex-col h-dvh bg-paper">
      <Header onShowSourceInfo={() => setShowSourceInfo(true)} />
      <div className="flex flex-1 overflow-hidden">
        <ClaimList
            activeTab={activeTab}
            onTabChange={handleTabChange}
            companies={companies}
            selectedCompany={selectedCompany}
            onSelectCompany={handleSelectCompany}
            claims={claims}
            selectedIdx={selectedIdx}
            onSelect={handleSelectClaim}
            mobileVisible={mobileView === 'list'}
            trackerData={trackerData}
            trackerSelectedId={trackerSelectedId}
            onTrackerSelect={handleTrackerSelect}
          />
        <div className={`min-h-0 overflow-hidden flex-1 ${mobileView === 'detail' ? 'flex' : 'hidden'} md:flex`}>
          {activeTab === 'tracker'
            ? <CommitmentTracker data={trackerData} selectedId={trackerSelectedId} onBack={handleBack} />
            : activeTab === 'compare'
              ? <CompareView data={data} trackerData={trackerData} onBack={handleBack} onViewClaim={handleViewClaim} />
              : <ClaimDetail claim={claims[selectedIdx] ?? null} onBack={handleBack} />
          }
        </div>
      </div>
      <Footer />
      {showSourceInfo && <SourceInfoModal onClose={() => setShowSourceInfo(false)} />}
    </div>
  )
}
