const VERDICT_STYLES = {
  supports:    'bg-emerald-700 text-white ring-emerald-800',
  neutral:     'bg-slate-600 text-white ring-slate-700',
  contradicts: 'bg-rose-700 text-white ring-rose-800',
}

export default function DecisionTrace({ steps }) {
  if (!steps?.length) return null

  return (
    <div className="space-y-3">
      <h3 className="font-display text-sm font-bold text-gray-700 uppercase tracking-widest">
        Decision trace
        <span className="ml-2 text-xs font-normal normal-case text-gray-400">
          system reasoning, each step grounded in evidence
        </span>
      </h3>
      <ol className="space-y-px">
        {steps.map((step) => (
          <li key={step.step} className="flex items-start gap-3 py-2.5 border-b border-gray-50 last:border-0">
            {/* Step number */}
            <span className="flex-shrink-0 w-5 h-5 rounded-full bg-green-dark text-white text-xs flex items-center justify-center font-medium mt-0.5">
              {step.step}
            </span>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <p className="text-sm text-gray-800 leading-snug">
                <span className="font-medium">{step.title}</span>
                {step.finding && (
                  <span className="text-gray-500 font-normal">: {step.finding}</span>
                )}
              </p>
              <p className="text-xs text-gray-400 mt-0.5 italic">{step.rule}</p>
              {step.evidence_ref && (
                <span className="inline-block mt-1 text-xs border border-gray-200 text-gray-500 rounded px-1.5 py-0.5">
                  Evidence [{step.evidence_ref}]
                </span>
              )}
            </div>

            {/* Verdict badge */}
            <div className="shrink-0">
              <span className={`text-xs px-2 py-0.5 rounded-full ring-1 ${VERDICT_STYLES[step.verdict] ?? VERDICT_STYLES.neutral}`}>
                {step.verdict}
              </span>
            </div>
          </li>
        ))}
      </ol>
    </div>
  )
}
