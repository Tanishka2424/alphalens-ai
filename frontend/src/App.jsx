import { useEffect, useState } from 'react'
import Nav from './components/Nav'
import Analyze from './pages/Analyze'
import Evaluation from './pages/Evaluation'
import HowItWorks from './pages/HowItWorks'
import Landing from './pages/Landing'

const ROUTES = {
  '/': Landing,
  '/analyze': Analyze,
  '/evaluation': Evaluation,
  '/how-it-works': HowItWorks,
}

const currentRoute = () => window.location.hash.replace(/^#/, '') || '/'

export default function App() {
  const [route, setRoute] = useState(currentRoute())

  useEffect(() => {
    const onChange = () => {
      setRoute(currentRoute())
      window.scrollTo(0, 0)
    }
    window.addEventListener('hashchange', onChange)
    return () => window.removeEventListener('hashchange', onChange)
  }, [])

  const Page = ROUTES[route] || Landing

  return (
    <div className="min-h-screen bg-sage text-teal">
      <Nav route={route} />
      <Page />
    </div>
  )
}