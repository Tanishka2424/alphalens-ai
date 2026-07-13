import ResultCard from './ResultCard'
import StampBadge from './StampBadge'

const COLOR_FOR_BUCKET = { 'Reliable': 'ledger', 'Needs Verification': 'amber', 'High Risk': 'red' }

export default function CredibilitySection({ status, error, data }) {
  return (
    <ResultCard eyebrow="Credibility Check" status={status} error={error}>
      {data && (
        <div>
          <div className="flex flex-wrap items-center gap-4 mb-5">
            <StampBadge label={data.action_bucket} color={COLOR_FOR_BUCKET[data.action_bucket]} />
            <span className="font-mono-data text-sm text-[var(--color-card-ink-soft)]">
              risk score {data.risk_score.toFixed(2)}
            </span>
          </div>

          <dl className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
            <div>
              <dt className="text-xs uppercase tracking-wide text-[var(--color-card-ink-soft)]">Classifier</dt>
              <dd className="font-mono-data mt-0.5 text-[var(--color-card-ink)]">{data.classifier.label} ({(data.classifier.confidence * 100).toFixed(0)}%)</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wide text-[var(--color-card-ink-soft)]">Clickbait</dt>
              <dd className="font-mono-data mt-0.5 text-[var(--color-card-ink)]">{data.clickbait.score.toFixed(2)}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wide text-[var(--color-card-ink-soft)]">Emotional language</dt>
              <dd className="font-mono-data mt-0.5 text-[var(--color-card-ink)]">{data.emotional_language.score.toFixed(2)}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wide text-[var(--color-card-ink-soft)]">Source</dt>
              <dd className="font-mono-data mt-0.5 text-[var(--color-card-ink)]">{data.source_reputation.tier}</dd>
            </div>
          </dl>

          <p className="mt-5 text-xs text-[var(--color-card-ink-soft)] italic font-display">
            {data.disclaimer}
          </p>
        </div>
      )}
    </ResultCard>
  )
}
