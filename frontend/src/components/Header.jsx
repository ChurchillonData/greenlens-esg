import { HugeiconsIcon } from '@hugeicons/react'
import { Leaf01Icon, InformationCircleIcon } from '@hugeicons/core-free-icons'

export default function Header({ onShowSourceInfo }) {
  return (
    <header className="bg-white border-b border-gray-200 px-4 md:px-8 py-3 md:py-4 flex items-center justify-between shrink-0">
      <div className="flex items-center gap-3 md:gap-4 min-w-0">
        <div className="w-10 h-10 md:w-12 md:h-12 rounded-2xl bg-green-dark/8 border-2 border-yellow-400 flex items-center justify-center shrink-0">
          <HugeiconsIcon icon={Leaf01Icon} size={24} color="#1F3A2E" strokeWidth={1.5} />
        </div>
        <div className="min-w-0 h-10 md:h-12 flex flex-col justify-center">
          <p className="font-display font-black text-xl md:text-2xl tracking-tight text-green-dark leading-none">
            Claimify<span className="text-[10px] font-bold uppercase tracking-widest bg-green-dark text-white px-2 py-0.5 rounded-full align-sub ml-1.5">ESG</span>
          </p>
          <p className="hidden text-gray-500 text-xs font-medium mt-1 tracking-wide truncate">
            Explainable greenwashing detection &nbsp;·&nbsp; oil &amp; gas majors
          </p>
        </div>
      </div>

      <button
        onClick={onShowSourceInfo}
        className="flex items-center gap-2 text-sm font-medium text-gray-600 bg-gray-50 hover:bg-gray-100 border border-gray-200 hover:border-gray-300 rounded-lg px-3 md:px-4 py-2 transition-colors shrink-0 ml-3"
      >
        <HugeiconsIcon icon={InformationCircleIcon} size={16} color="currentColor" strokeWidth={1.5} />
        <span className="hidden sm:inline">How are sources weighted?</span>
      </button>
    </header>
  )
}
