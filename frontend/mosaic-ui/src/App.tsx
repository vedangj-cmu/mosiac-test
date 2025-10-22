import { useRef } from 'react'
import VideoPanel from './VideoPanel'
import RosbagSelector from './RosbagSelector'
import { PlayIcon, PauseIcon, ArrowPathIcon } from '@heroicons/react/24/solid'

const App = () => {
  const mockRosbags = [
    { id: '1', name: 'Run 2025-10-08', category: 'Experiments', path: '/bags/run1.bag' },
    { id: '2', name: 'Run 2025-10-09', category: 'Experiments', path: '/bags/run2.bag' },
    { id: '3', name: 'Debug Session', category: 'Tests', path: '/bags/debug.bag' },
  ]
  const handleSelect = (bag) => {
    console.log('Selected:', bag)
    // send to video player, etc.
  }
  return (
    <div class="flex gap-4">
      <RosbagSelector rosbags={mockRosbags} onSelect={handleSelect} />
      <VideoPanel />
    </div>
  )
}

export default App
