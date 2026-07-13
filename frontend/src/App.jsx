import { useState } from 'react'
import IntakeForm from './components/IntakeForm'
import SentimentSection from './components/SentimentSection'
import CredibilitySection from './components/CredibilitySection'
import RetrievalSection from './components/RetrievalSection'
import ConsensusSection from './components/ConsensusSection'
import { analyzeSentiment, analyzeCredibility, findSimilarArticles, analyzeConsensus } from './api'

const emptySection = { status: 'idle', error: null, data: null }

const FEATURES = [
  { label: 'Sentiment', desc: 'FinBERT reads the market tone: bullish, bearish, or neutral.' },
  { label: 'Credibility', desc: 'A fine-tuned classifier plus clickbait, tone, and source checks.' },
  { label: 'Related coverage', desc: 'Semantic search across 10,686 indexed financial headlines.' },
  { label: 'Consensus', desc: 'LLM-assisted reasoning on whether other sources agree.' },
]

export default function App() {
  const [sentiment, setSentiment] = useState(emptySection)
  const [credibility, setCredibility] = useState(emptySection)
  const [retrieval, setRetrieval] = useState(emptySection)
  const [consensus, setConsensus] = useState(emptySection)
  const [isSubmitting, setIsSubmitting] = useState(false)

  function scrollToAnalyzer() {
    document.getElementById('analyzer')?.scrollIntoView({ behavior: 'smooth' })
  }

  async function handleSubmit({ text, sourceName, url }) {
    setIsSubmitting(true)
    setSentiment({ status: 'loading', error: null, data: null })
    setCredibility({ status: 'loading', error: null, data: null })
    setRetrieval({ status: 'loading', error: null, data: null })
    setConsensus({ status: 'loading', error: null, data: null })

    const run = async (fn, setter) => {
      try {
        const data = await fn()
        setter({ status: 'done', error: null, data })
      } catch (e) {
        setter({ status: 'error', error: e.message, data: null })
      }
    }

    await Promise.all([
      run(() => analyzeSentiment(text), setSentiment),
      run(() => analyzeCredibility(text, sourceName, url), setCredibility),
      run(() => findSimilarArticles(text, 5), setRetrieval),
      run(() => analyzeConsensus(text, 5), setConsensus),
    ])

    setIsSubmitting(false)
  }

  return (
    <div>
      {/* HERO */}
      <section className="min-h-[90vh] flex items-center justify-center px-6 py-20">
        <div className="max-w-2xl text-center">
          <p className="font-mono-data text-xs uppercase tracking-widest text-[var(--color-brass)] mb-5">
            AlphaLens AI &middot; Financial News Intelligence
          </p>
          <h1 className="text-4xl sm:text-5xl font-semibold leading-tight text-[var(--color-ink)]">
            A second opinion for<br />every financial headline.
          </h1>
          <p className="mt-5 text-[var(--color-ink-soft)] leading-relaxed max-w-xl mx-auto">
            Sentiment, credibility, and cross-source consensus &mdash; checked against
            10,686 indexed articles before you trust it. A heuristic assistance tool,
            not a fact-verification system.
          </p>
          <button
            onClick={scrollToAnalyzer}
            className="mt-8 rounded-lg bg-[var(--color-brass)] px-8 py-3.5 font-semibold text-[var(--color-brass-deep)] hover:brightness-110 transition-all"
          >
            Analyze a headline &darr;
          </button>

          <div className="mt-14 grid grid-cols-2 sm:grid-cols-4 gap-px bg-[var(--color-panel-line)] rounded-lg overflow-hidden max-w-xl mx-auto">
            {[
              ['Sentiment', 'Bullish'],
              ['Credibility', '72.4'],
              ['Consensus', '4/5'],
              ['Corpus', '10,686'],
            ].map(([label, value]) => (
              <div key={label} className="bg-[var(--color-card)] px-4 py-3 text-left">
                <div className="text-[10px] uppercase tracking-wide text-[var(--color-card-ink-soft)]">{label}</div>
                <div className="font-mono-data text-sm text-[var(--color-card-ink)] mt-0.5">{value}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FEATURES */}
      <section className="px-6 py-16 border-t border-[var(--color-panel-line)]">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-center text-2xl font-semibold text-[var(--color-ink)] mb-10">
            Four checks, run together
          </h2>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {FEATURES.map((f) => (
              <div key={f.label} className="bg-[var(--color-panel)] border border-[var(--color-panel-line)] rounded-xl p-5">
                <div className="text-sm font-semibold text-[var(--color-brass)] mb-2">{f.label}</div>
                <p className="text-sm text-[var(--color-ink-soft)] leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ANALYZER */}
      <section id="analyzer" className="px-6 py-20 border-t border-[var(--color-panel-line)]">
        <div className="max-w-2xl mx-auto">
          <h2 className="text-center text-2xl sm:text-3xl font-semibold text-[var(--color-ink)] mb-2">
            Try it on a real headline
          </h2>
          <p className="text-center text-sm text-[var(--color-ink-soft)] mb-8">
            Paste any financial news text below and see all four checks run at once.
          </p>

          <div className="space-y-6">
            <IntakeForm onSubmit={handleSubmit} isLoading={isSubmitting} />

            {sentiment.status !== 'idle' && (
              <>
                <SentimentSection {...sentiment} />
                <CredibilitySection {...credibility} />
                <RetrievalSection {...retrieval} />
                <ConsensusSection {...consensus} />
              </>
            )}
          </div>
        </div>
      </section>
    </div>
  )
}
