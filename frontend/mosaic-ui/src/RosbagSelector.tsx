import { useState } from 'react'

type Rosbag = {
  id: string
  name: string
  category?: string
  path: string // filesystem or URL
}

type Props = {
  rosbags: Rosbag[]
  onSelect: (rosbag: Rosbag) => void
}

export default function RosbagSelector({ rosbags, onSelect }: Props) {
  const [selectedId, setSelectedId] = useState<string | null>(null)

  // Group by category (optional)
  const grouped = rosbags.reduce<Record<string, Rosbag[]>>((acc, r) => {
    const key = r.category ?? 'Uncategorized'
    acc[key] = acc[key] || []
    acc[key].push(r)
    return acc
  }, {})

  return (
    <div className="bg-card border border-border rounded-xl p-6 shadow-soft">
      <h2 className="text-lg font-semibold text-card-foreground mb-4">Rosbag Files</h2>
      <div className="space-y-6">
        {Object.entries(grouped).map(([category, items]) => (
          <div key={category}>
            <h3 className="text-sm font-medium text-foreground-secondary mb-3 uppercase tracking-wide">
              {category}
            </h3>
            <ul className="space-y-2">
              {items.map((r) => (
                <li key={r.id}>
                  <button
                    onClick={() => {
                      setSelectedId(r.id)
                      onSelect(r)
                    }}
                    className={`w-full text-left px-4 py-3 rounded-lg border transition-all duration-200 ${
                      selectedId === r.id
                        ? 'bg-blue-200 text-blue-900 border-blue-600 shadow-lg'
                        : 'bg-background-secondary text-foreground border-border hover:bg-background-tertiary hover:border-border-secondary'
                    }`}
                    style={selectedId === r.id ? {
                      backgroundColor: '#dbeafe',
                      color: '#1e3a8a',
                      borderColor: '#2563eb',
                      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                    } : {}}
                  >
                    <div className="font-medium">{r.name}</div>
                    <div className={`text-xs mt-1 ${
                      selectedId === r.id ? 'text-blue-700' : 'text-foreground-tertiary'
                    }`}>{r.path}</div>
                  </button>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  )
}
