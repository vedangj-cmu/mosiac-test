import { useRef } from 'react'
import PlayerControl from './PlayerControl'
import type { VideoHandle } from './VideoPlayer'
import VideoPlayer from './VideoPlayer'

const VideoPanel = () => {
  const refs = Array.from({ length: 6 }, () => useRef<VideoHandle>(null))
  const srcs = [
    '/video?filename=center_front_image_rect_compressed.mp4',
    '/video?filename=center_rear_image_rect_compressed.mp4',
    '/video?filename=driver_front_image_rect_compressed.mp4',
    '/video?filename=driver_rear_image_rect_compressed.mp4',
    '/video?filename=passenger_front_image_rect_compressed.mp4',
    '/video?filename=passenger_rear_image_rect_compressed.mp4',
  ]

  const playAll = () => refs.forEach((r) => r.current?.play())
  const pauseAll = () => refs.forEach((r) => r.current?.pause())
  const rateAll = (r: number) => refs.forEach((rf) => rf.current?.setRate(r))

  return (
    <div className="bg-card border border-border rounded-xl p-6 shadow-soft">
      <h2 className="text-lg font-semibold text-card-foreground mb-6">Video Streams</h2>

      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        {srcs.map((src, i) => (
          <VideoPlayer
            className="rounded-lg border border-border shadow-medium"
            key={i}
            ref={refs[i]}
            src={'http://localhost:8000' + src}
          />
        ))}
      </div>

      <PlayerControl playAll={playAll} pauseAll={pauseAll} rateAll={rateAll} />
    </div>
  )
}

export default VideoPanel
