import { useRef } from 'react'
import VideoPlayer from './VideoPlayer'
import PlayerControl from './PlayerControl'
import type { VideoHandle } from './VideoPlayer'

const VideoPanel = () => {
  const refs = useRef<(VideoHandle | null)[]>([])
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
    <>
      <div className="m-8 border p-8 rounded">
        <div className=" flex flex-wrap">
          {srcs.map((src, i) => (
            <VideoPlayer
              className=" m-1 rounded-md w-1/4"
              key={i}
              ref={refs[i]}
              src={'http://localhost:8000' + src}
            />
          ))}
        </div>
        <PlayerControl playAll={playAll} pauseAll={pauseAll} rateAll={rateAll} />
      </div>
    </>
  )
}

export default VideoPanel
