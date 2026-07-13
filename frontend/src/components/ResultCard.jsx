export default function ResultCard({ eyebrow, status, error, children }) {
  return (
    <div className="fade-up bg-[var(--color-card)] border border-[var(--color-card-line)] rounded-xl p-6 sm:p-8 shadow-lg shadow-black/20">
      <h3 className="font-mono-data text-xs uppercase tracking-widest text-[var(--color-card-ink-soft)] mb-4">
        {eyebrow}
      </h3>

      {status === 'idle' && (
        <p className="text-sm text-[var(--color-card-ink-soft)] italic">Waiting for an article to analyze.</p>
      )}
      {status === 'loading' && (
        <div className="flex items-center gap-2 text-sm text-[var(--color-card-ink-soft)]">
          <span className="inline-block h-2 w-2 rounded-full bg-[var(--color-brass)] animate-pulse" />
          Running...
        </div>
      )}
      {status === 'error' && (
        <p className="text-sm text-[var(--color-risk-red)]">Couldn't complete this check: {error}</p>
      )}
      {status === 'done' && children}
    </div>
  )
}
