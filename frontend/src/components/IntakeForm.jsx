import { useState } from 'react'
import ResultCard from './ResultCard'

const EXAMPLES = [
  'Sensex jumps 500 points after the Fed holds rates',
  'SEBI cautions investors about WhatsApp stock tips',
  'Jupiter Wagons shares rally 20% on a Railway Board order',
]

export default function IntakeForm({ onSubmit, isLoading }) {
  const [text, setText] = useState('')
  const [sourceName, setSourceName] = useState('')
  const [url, setUrl] = useState('')
  const [showSource, setShowSource] = useState(false)

  const remaining = 10 - text.trim().length
  const isValid = remaining <= 0

  function handleSubmit(e) {
    e.preventDefault()
    if (!isValid || isLoading) return
    onSubmit({ text: text.trim(), sourceName: sourceName.trim(), url: url.trim() })
  }

  const input = 'w-full border-2 border-teal bg-white text-[#0A2425] px-3 py-2 text-base'

  return (
    <ResultCard step="1" title="Paste a headline or claim" status="done">
      <form onSubmit={handleSubmit}>
        <label htmlFor="claim" className="sr-only">Headline or claim</label>
        <textarea
          id="claim"
          rows={3}
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste a financial news headline or claim here..."
          className={`${input} text-lg resize-none`}
        />
        <p className="mt-1 text-sm text-teal-soft">
          {remaining > 0 ? `Add ${remaining} more character${remaining === 1 ? '' : 's'} to continue` : 'Ready to analyze'}
        </p>

        <div className="mt-3 flex flex-wrap items-center gap-2">
          <span className="text-sm font-semibold">Try an example:</span>
          {EXAMPLES.map((ex) => (
            <button
              key={ex}
              type="button"
              onClick={() => setText(ex)}
              className="border-2 border-teal px-3 py-1 text-sm font-semibold hover:bg-teal hover:text-cream"
            >
              {ex}
            </button>
          ))}
        </div>

        <button
          type="button"
          onClick={() => setShowSource((s) => !s)}
          className="mt-4 text-sm font-semibold underline"
        >
          {showSource ? 'Hide publisher details' : '+ Add the publisher or link (optional)'}
        </button>
        {showSource && (
          <div className="mt-3 grid sm:grid-cols-2 gap-3">
            <input className={input} value={sourceName} onChange={(e) => setSourceName(e.target.value)} placeholder="Publisher, e.g. Reuters" aria-label="Publisher name" />
            <input className={input} value={url} onChange={(e) => setUrl(e.target.value)} placeholder="Article link, if you have one" aria-label="Article link" />
          </div>
        )}

        <button
          type="submit"
          disabled={isLoading || !isValid}
          className="mt-6 bg-teal text-cream px-8 py-3 text-lg font-semibold disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Analyzing...' : 'Analyze'}
        </button>
      </form>
    </ResultCard>
  )
}