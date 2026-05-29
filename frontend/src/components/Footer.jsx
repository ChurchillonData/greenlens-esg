import { HugeiconsIcon } from '@hugeicons/react'
import { Audit01Icon } from '@hugeicons/core-free-icons'

export default function Footer() {
  return (
    <footer className="shrink-0 border-t border-gray-100 bg-white px-4 md:px-6 py-3 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1 sm:gap-0">
      <p className="text-xs text-gray-400 leading-relaxed flex items-center gap-1.5">
        <HugeiconsIcon icon={Audit01Icon} size={13} color="#991b1b" strokeWidth={1.5} className="shrink-0" />
        <span className="font-medium text-gray-500">Design principle:</span>{' '}
        Every claim, evidence, rationale, and weight is auditable.
      </p>
      <p className="text-xs text-gray-400 sm:shrink-0 sm:ml-4">
        All times UTC · Data as of 14 May 2026
      </p>
    </footer>
  )
}
