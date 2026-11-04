export default function ResultCard({ step, title, status, error, children }) {
  return (
    <section className="fade-up bg-cream text-teal border-t-[6px] border-teal p-6 mb-6">
      <h2 className="flex items-baseline gap-3 mb-4">
        {step && <span className="font-display text-5xl leading-none">{step}</span>}
        <span className="text-xl font-semibold">{title}</span>
      </h2>
      {status === 'loading' && <p className="text-teal-soft">Working on it...</p>}
      {status === 'error' && (
        <p role="alert" className="font-semibold">Couldn't complete this check: {error}</p>
      )}
      {status === 'done' && children}
    </section>
  )
}