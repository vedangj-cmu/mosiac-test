import { useRef, useImperativeHandle, forwardRef } from 'react'

export type VideoHandle = {
  play: () => void
  pause: () => void
  seek: (t: number) => void // seconds
  setRate: (r: number) => void
  getTime: () => number
}

type Props = { src: string; className?: string }

const VideoPlayer = forwardRef<VideoHandle, Props>(({ src, className }, ref) => {
  const el = useRef<HTMLVideoElement>(null)

  useImperativeHandle(
    ref,
    () => ({
      play: () => el.current?.play(),
      pause: () => el.current?.pause(),
      seek: (t: number) => {
        if (el.current) el.current.currentTime = t
      },
      setRate: (r: number) => {
        if (el.current) el.current.playbackRate = r
      },
      getTime: () => el.current?.currentTime ?? 0,
    }),
    [],
  )

  const onError = () => {
    const err = el.current?.error
    console.error('Video error:', err?.code, err?.message, err)
  }

  const onLoadedMetadata = () => {
    console.log('Loaded metadata:', {
      duration: el.current?.duration,
      readyState: el.current?.readyState,
    })
  }

  return (
    <video
      ref={el}
      className={className}
      src={src}
      playsInline
      preload="metadata"
      onError={onError}
      onLoadedMetadata={onLoadedMetadata}
    />
  )
})

export default VideoPlayer
