const FEATURES = [
  ['Cited, not guessed', 'Every statement points to the article it came from.'],
  ['Dated and linked', 'Publisher, date and a link to the original, or a clear note when there is none.'],
  ['Honest about limits', 'It says when evidence is missing. It never calls a claim true or false.'],
]

export default function Landing() {
  return (
    <main>
      <section className="relative overflow-hidden px-6 sm:px-14 pb-20">
        <div
          aria-hidden="true"
          className="hidden md:block absolute top-0 bottom-0 right-[-40px] w-[420px] bg-teal"
          style={{ transform: 'skewX(-16deg)' }}
        />
        <div className="relative grid md:grid-cols-[minmax(0,1.35fr)_minmax(0,1fr)] gap-10 items-center pt-14">
          <div>
            <h1 className="font-display uppercase text-6xl sm:text-8xl leading-[1.05]">
            Understand<br />any headline.
            <span className="mt-3 block w-fit bg-cream px-3 pt-2 pb-1 leading-none">With sources.</span>
            </h1>
            <p className="mt-6 text-xl max-w-xl">
              Paste a financial headline. Get a plain explanation based on real articles, the market tone, and how the text is written.
            </p>
            <div className="mt-8 flex flex-wrap items-center gap-6">
              <a href="#/analyze" className="bg-teal text-cream px-8 py-4 text-lg font-semibold">Analyze a headline</a>
              <a href="#/how-it-works" className="font-semibold underline">How it works</a>
            </div>
          </div>
          <div className="bg-cream text-teal p-6 shadow-[10px_10px_0_var(--color-sage)]">
            <p className="text-xs font-semibold uppercase tracking-widest">Example</p>
            <p className="my-3 text-xl">
              The claim says 20%, but The Times of India reports over 8%.{' '}
              <span className="border-2 border-teal px-2 text-sm font-semibold">1</span>
            </p>
            <p className="text-sm text-teal-soft">1 · The Times of India · 29 Oct 2026 · Read the original</p>
          </div>
        </div>
      </section>

      <section className="grid sm:grid-cols-3 gap-6 px-6 sm:px-14 pb-12 max-w-6xl mx-auto">
        {FEATURES.map(([title, text]) => (
          <div key={title} className="bg-cream border-t-[6px] border-teal p-6">
            <h2 className="font-display uppercase text-3xl mb-2">{title}</h2>
            <p>{text}</p>
          </div>
        ))}
      </section>
      <p className="text-center font-semibold pb-12">Not a fact-checker. Not trading advice.</p>
    </main>
  )
}