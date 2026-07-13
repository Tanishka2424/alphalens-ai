import { useState } from 'react'

export default function IntakeForm({ onSubmit, isLoading }) {
  const [text, setText] = useState('')
  const [sourceName, setSourceName] = useState('')
  const [url, setUrl] = useState('')
  const [showOptional, setShowOptional] = useState(false)

  const remaining = 10 - text.trim().length
  const isValid = remaining <= 0

  function handleSubmit(e) {
    e.preventDefault()
    if (!isValid) return
    onSubmit({ text: text.trim(), sourceName: sourceName.trim(), url: url.trim() })
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-[var(--color-card)] border border-[var(--color-card-line)] rounded-xl p-6 sm:p-8 shadow-lg shadow-black/20"
    >
      <label className="block font-mono-data text-xs uppercase tracking-widest text-[var(--color-card-ink-soft)] mb-2">
        Wire Intake
      </label>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Paste a financial news headline or article text here..."
        rows={5}
        className="w-full resize-none rounded-lg border border-[var(--color-card-line)] bg-white/70 px-4 py-3 text-[15px] leading-relaxed text-[var(--color-card-ink)] focus:outline-none focus:ring-2 focus:ring-[var(--color-brass)] focus:border-transparent"
      />

      {/* Clearer than a raw fraction: only says something when it's actually
          useful (still below the minimum), and confirms readiness once met. */}
      <p className="mt-1.5 text-xs font-mono-data text-[var(--color-card-ink-soft)]">
        {remaining > 0 ? `Add ${remaining} more character${remaining === 1 ? '' : 's'} to continue` : 'Ready to submit'}
      </p>

      <button
        type="button"
        onClick={() => setShowOptional((s) => !s)}
        className="mt-4 text-sm font-medium text-[var(--color-brass)] hover:underline"
      >
        {showOptional ? '- Hide source details' : '+ Add source name or URL (optional)'}
      </button>

      {showOptional && (
        <div className="mt-3 grid gap-3 sm:grid-cols-2">
          <input
            type="text"
            value={sourceName}
            onChange={(e) => setSourceName(e.target.value)}
            placeholder="Publisher name, e.g. Reuters"
            className="rounded-lg border border-[var(--color-card-line)] bg-white/70 px-3 py-2 text-sm text-[var(--color-card-ink)] focus:outline-none focus:ring-2 focus:ring-[var(--color-brass)]"
          />
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Article URL, if available"
            className="rounded-lg border border-[var(--color-card-line)] bg-white/70 px-3 py-2 text-sm text-[var(--color-card-ink)] focus:outline-none focus:ring-2 focus:ring-[var(--color-brass)]"
          />
        </div>
      )}

      <button
        type="submit"
        disabled={isLoading || !isValid}
        className="mt-6 w-full sm:w-auto rounded-lg bg-[var(--color-brass)] px-8 py-3 font-semibold text-[var(--color-brass-deep)] disabled:opacity-40 disabled:cursor-not-allowed hover:brightness-110 transition-all"
      >
        {isLoading ? 'Filing...' : 'Analyze this article'}
      </button>
    </form>
  )
}
