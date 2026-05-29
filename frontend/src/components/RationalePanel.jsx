export default function RationalePanel({ rationale, keyFactors, reasoning }) {
  return (
    <div className="space-y-3">
      <h3 className="font-display text-sm font-bold text-gray-700 uppercase tracking-widest">Rationale</h3>
      <p className="text-sm text-gray-700 leading-relaxed">{rationale}</p>
      {keyFactors?.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {keyFactors.map((f, i) => (
            <span key={i} className="text-xs bg-green-dark text-white rounded-full px-3 py-1 font-medium">
              {f}
            </span>
          ))}
        </div>
      )}
    </div>
  )
}
