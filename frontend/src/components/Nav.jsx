const LINKS = [
  ['#/analyze', '/analyze', 'Analyze'],
  ['#/evaluation', '/evaluation', 'Evaluation'],
  ['#/how-it-works', '/how-it-works', 'How it works'],
]

export default function Nav({ route }) {
  return (
    <header className="bg-teal text-cream">
      <nav className="flex items-center justify-between px-6 sm:px-14 py-4">
        <a href="#/" className="font-display text-2xl tracking-wide">ALPHALENS AI</a>
        <div className="flex gap-6 font-semibold">
          {LINKS.map(([href, path, label]) => (
            <a
              key={path}
              href={href}
              aria-current={route === path ? 'page' : undefined}
              className={`py-2 ${route === path ? 'border-b-2 border-cream' : 'opacity-80 hover:opacity-100'}`}
            >
              {label}
            </a>
          ))}
        </div>
      </nav>
    </header>
  )
}