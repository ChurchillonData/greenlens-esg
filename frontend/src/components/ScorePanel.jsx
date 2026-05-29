import { CLASS_LABELS, badgeCls, scoreColor } from '../utils/classStyles'

const SEGMENTS = 10

export default function ScorePanel({ predictedClass, riskScore }) {
  const filled = Math.round(riskScore * SEGMENTS)
  const trackColor = riskScore <= 0.4
    ? 'bg-green-accent'
    : riskScore <= 0.7 ? 'bg-amber-400' : 'bg-red-500'

  return (
    <div className="bg-gray-50 rounded-lg p-4 flex items-start gap-6">
      <div className="text-center shrink-0">
        <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">GreenSignal</p>
        <p className={`text-4xl font-bold tabular-nums ${scoreColor(riskScore)}`}>
          {riskScore.toFixed(2)}
        </p>
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-2">
          <span className={`text-xs px-2 py-0.5 rounded-full ring-1 ${badgeCls(predictedClass)}`}>
            {CLASS_LABELS[predictedClass]}
          </span>
        </div>
        <div className="flex items-center gap-0.5 w-full">
          {Array.from({ length: SEGMENTS }, (_, i) => (
            <div key={i} className={`h-1.5 flex-1 rounded-full ${i < filled ? trackColor : 'bg-gray-200'}`} />
          ))}
        </div>
        <div className="flex justify-between text-xs text-gray-400 mt-1">
          <span>Low signal</span>
          <span>Strong signal</span>
        </div>
      </div>
    </div>
  )
}
