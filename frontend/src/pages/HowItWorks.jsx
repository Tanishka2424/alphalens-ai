const STEPS = [
  ['1 Retrieve', 'Find similar articles. Drop copies of your own text.'],
  ['2 Explain', 'An LLM may only use those articles, and must cite them.'],
  ['3 Validate', 'Any statement that cites an unknown article is dropped.'],
  ['4 Show', 'Publisher, date and link sit beside each statement.'],
]
const SOURCES = [
  ['SEntFiN dataset', '10,686 India-market headlines. No dates or links, so they are treated as archive context.'],
  ['NewsAPI', 'Recent articles with publisher, date and link.'],
  ['SEBI RSS feed', 'Press releases and circulars from the regulator.'],
]

export default function HowItWorks() {
  return (
    <main className="max-w-4xl mx-auto px-4 sm:px-6 py-10">
      <h1 className="font-display uppercase text-5xl mb-2">How it works</h1>
      <p className="mb-8 text-lg max-w-2xl">Every explanation comes only from retrieved articles, and every statement cites them.</p>

      <div className="grid sm:grid-cols-2 gap-6 mb-6">
        {STEPS.map(([t, d]) => (
          <div key={t} className="bg-cream border-t-[6px] border-teal p-6">
            <h2 className="font-display uppercase text-3xl mb-1">{t}</h2>
            <p>{d}</p>
          </div>
        ))}
      </div>

      <section className="bg-cream border-t-[6px] border-teal p-6 mb-6">
        <h2 className="text-xl font-semibold mb-3">Sources</h2>
        <table className="w-full text-left">
          <tbody>
            {SOURCES.map(([a, b]) => (
              <tr key={a} className="border-t-2 border-teal first:border-t-0"><td className="py-2 pr-4 font-semibold">{a}</td><td className="py-2">{b}</td></tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="bg-cream border-t-[6px] border-teal p-6">
        <h2 className="text-xl font-semibold mb-2">What this is not</h2>
        <p>Not a fact-checker, not trading advice, and not an alert service. Related articles are context, not confirmation.</p>
      </section>
    </main>
  )
}