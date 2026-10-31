// Update these numbers from your own labeling runs. Do not round them up.
const NUMBERS = [
  ['9 / 9', 'covered claims answered with a cited article'],
  ['5 / 5', 'off-topic claims refused'],
  ['13 / 13', 'statements judged supported by their cited article (author-labeled)'],
  ['0 / 11', 'answers that presented a mismatched claim as confirmed'],
]
const FIXES = [
  ['Padding from old, undated headlines', 'Refuse when only undated items are found'],
  ['A wrong publisher named in a statement', 'Source and date fields are labeled in the prompt'],
  ['A claim with a different number was echoed back', 'The answer now says plainly that the claim differs'],
]
const LIMITS = [
  'Claims were written and labeled by one person, with AI-assisted guidance.',
  'The prompt and code were tuned on these same 20 claims, so the results are optimistic.',
  'Most articles are headline-length. A valid citation does not prove support.',
  'Retrieval quality has not been benchmarked yet. A held-out set is planned.',
]

export default function Evaluation() {
  return (
    <main className="max-w-4xl mx-auto px-4 sm:px-6 py-10">
      <h1 className="font-display uppercase text-5xl mb-2">How it was checked</h1>
      <p className="mb-8 text-lg max-w-2xl">A development check on 20 hand-written claims. It is not a benchmark.</p>

      <div className="grid sm:grid-cols-2 gap-6 mb-6">
        {NUMBERS.map(([n, label]) => (
          <div key={label} className="bg-cream border-t-[6px] border-teal p-6">
            <p className="font-display text-6xl leading-none">{n}</p>
            <p className="mt-2">{label}</p>
          </div>
        ))}
      </div>

      <section className="bg-cream border-t-[6px] border-teal p-6 mb-6">
        <h2 className="text-xl font-semibold mb-3">Problems found, then fixed</h2>
        <table className="w-full text-left">
          <thead><tr><th className="py-2 pr-4">Found</th><th className="py-2">Fix</th></tr></thead>
          <tbody>
            {FIXES.map(([a, b]) => (
              <tr key={a} className="border-t-2 border-teal"><td className="py-2 pr-4">{a}</td><td className="py-2">{b}</td></tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="bg-cream border-t-[6px] border-teal p-6">
        <h2 className="text-xl font-semibold mb-3">Limits</h2>
        <ul className="list-disc pl-5 space-y-1">{LIMITS.map((l) => <li key={l}>{l}</li>)}</ul>
      </section>
    </main>
  )
}