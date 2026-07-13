import ResultCard from './ResultCard'
import StampBadge from './StampBadge'

const COLOR_FOR_LABEL = { Bullish: 'ledger', Bearish: 'red', Neutral: 'amber' }

export default function SentimentSection({ status, error, data }) {
  return (
    <ResultCard eyebrow="Sentiment Read" status={status} error={error}>
      {data && (
        <div className="flex flex-wrap items-center gap-4">
          <StampBadge label={data.label} color={COLOR_FOR_LABEL[data.label]} />
          <span className="font-mono-data text-sm text-[var(--color-card-ink-soft)]">
            {(data.confidence * 100).toFixed(1)}% confidence &middot; {data.inference_time_ms}ms
          </span>
        </div>
      )}
    </ResultCard>
  )
}
