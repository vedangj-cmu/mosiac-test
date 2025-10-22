import React, { useState } from 'react'

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
    <div className="space-y-4">
      {Object.entries(grouped).map(([category, items]) => (
        <div key={category}>
          <h3 className="text-sm font-semibold text-gray-400 mb-2">{category}</h3>
          <ul className="space-y-1">
            {items.map((r) => (
              <li key={r.id}>
                <button
                  onClick={() => {
                    setSelectedId(r.id)
                    onSelect(r)
                  }}
                  className={`w-full text-left px-3 py-2 rounded border ${
                    selectedId === r.id
                      ? 'bg-blue-600 text-white border-blue-600'
                      : 'bg-gray-800 text-gray-200 border-gray-700 hover:bg-gray-700'
                  }`}
                >
                  {r.name}
                </button>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  )
}
