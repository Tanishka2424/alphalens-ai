import { useState } from 'react'
import CredibilitySection from '../components/CredibilitySection'
import EvidenceSection from '../components/EvidenceSection'
import ExplanationSection from '../components/ExplanationSection'
import IntakeForm from '../components/IntakeForm'
import RetrievalSection from '../components/RetrievalSection'
import SentimentSection from '../components/SentimentSection'
import { analyzeCredibility, analyzeSentiment, explainClaim, findSimilarArticles } from '../api'

const empty = { status: 'idle', error: null, data: null }
const loading = { status: 'loading', error: null, data: null }

export default function Analyze() {
  const [explain, setExplain] = useState(empty)
  const [sentiment, setSentiment] = useState(empty)
  const [credibility, setCredibility] = useState(empty)
  const [retrieval, setRetrieval] = useState(empty)
  const [asked, setAsked] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit({ text, sourceName, url }) {
    setIsSubmitting(true)
    setAsked(true)
    setExplain(loading)
    setSentiment(loading)
    setCredibility(loading)
    setRetrieval(loading)

    const run = async (fn, setter) => {
      try {
        setter({ status: 'done', error: null, data: await fn() })
      } catch (e) {
        setter({ status: 'error', error: e.message, data: null })
      }
    }

    await Promise.all([
      run(() => explainClaim(text, 5), setExplain),
      run(() => analyzeSentiment(text), setSentiment),
      run(() => analyzeCredibility(text, sourceName, url), setCredibility),
      run(() => findSimilarArticles(text, 5), setRetrieval),
    ])
    setIsSubmitting(false)
  }

  return (
    <main className="max-w-3xl mx-auto px-4 sm:px-6 py-10">
      <h1 className="font-display uppercase text-5xl mb-2">Analyze a headline</h1>
      <p className="mb-8 text-lg">
        Paste a financial headline or claim. You get an explanation based on real articles, the market tone, and how the text is written.
      </p>

      <IntakeForm onSubmit={handleSubmit} isLoading={isSubmitting} />

      {asked && (
        <>
          <ExplanationSection {...explain} />
          <EvidenceSection {...explain} />
          <div className="grid md:grid-cols-2 gap-x-6">
            <SentimentSection {...sentiment} />
            <CredibilitySection {...credibility} />
          </div>
          <RetrievalSection
            {...retrieval}
            excludeIds={explain.data?.evidence.map((e) => e.article_id) ?? []}
          />
        </>
      )}
    </main>
  )
}