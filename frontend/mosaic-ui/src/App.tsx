import RosbagSelector from './RosbagSelector'
import { ThemeProvider } from './ThemeContext'
import { ThemeToggle } from './ThemeToggle'
import VideoPanel from './VideoPanel'

type Rosbag = {
  id: string
  name: string
  category?: string
  path: string
}

const App = () => {
  const mockRosbags: Rosbag[] = [
    { id: '1', name: 'Run 2025-10-08', category: 'Experiments', path: '/bags/run1.bag' },
    { id: '2', name: 'Run 2025-10-09', category: 'Experiments', path: '/bags/run2.bag' },
    { id: '3', name: 'Debug Session', category: 'Tests', path: '/bags/debug.bag' },
  ]
  const handleSelect = (bag: Rosbag) => {
    console.log('Selected:', bag)
    // send to video player, etc.
  }
  return (
    <ThemeProvider>
      <div className="min-h-screen bg-background text-foreground">
        {/* Header with theme toggle */}
        <header className="flex items-center justify-between p-4 border-b border-border bg-card">
          <h1 className="text-2xl font-bold text-foreground">Mosaic UI New</h1>
          <ThemeToggle />
        </header>

        {/* Main content */}
        <main className="flex gap-6 p-6">
          <aside className="w-80">
            <RosbagSelector rosbags={mockRosbags} onSelect={handleSelect} />
          </aside>
          <section className="flex-1">
            <VideoPanel />
          </section>
        </main>
      </div>
    </ThemeProvider>
  )
}

export default App
