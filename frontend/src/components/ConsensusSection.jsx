import ResultCard from './ResultCard'
import StampBadge from './StampBadge'

const COLOR_FOR_VERDICT = {
  'Consensus': 'ledger',
  'Partial Agreement': 'amber',
  'Conflict': 'red',
  'Insufficient Coverage': 'brass',
}

export default function ConsensusSection({ status, error, data }) {
  return (
    <ResultCard eyebrow="Cross-Source Consensus" status={status} error={error}>
      {data && (
        <div>
          <div className="flex flex-wrap items-center gap-4 mb-4">
            <StampBadge label={data.verdict} color={COLOR_FOR_VERDICT[data.verdict]} />
            <span className="font-mono-data text-xs text-[var(--color-card-ink-soft)] uppercase tracking-wide">
              {data.method === 'llm_assisted' ? 'LLM-assisted' : 'Rule-based'}
            </span>
          </div>
          <p className="text-sm leading-relaxed text-[var(--color-card-ink)]">{data.explanation}</p>
          {data.exaggeration_flag && (
            <p className="mt-3 text-xs text-[var(--color-risk-red)]">
              Note: this text uses notably more emotionally loaded language than the related coverage.
            </p>
          )}
        </div>
      )}
    </ResultCard>
  )
}
