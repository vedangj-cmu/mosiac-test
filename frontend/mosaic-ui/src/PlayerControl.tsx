import { PauseIcon, PlayIcon } from '@heroicons/react/24/solid'

interface PlayerControlProps {
  rateAll: (rate: number) => void
  pauseAll: () => void
  playAll: () => void
}

const PlayerControl = ({ rateAll, pauseAll, playAll }: PlayerControlProps) => {
  return (
    <div className="flex items-center gap-3 p-4 bg-card border border-border rounded-xl shadow-soft">
      <button
        onClick={playAll}
        className="flex items-center gap-2 px-4 py-2 rounded-lg bg-background-secondary hover:bg-background-tertiary text-foreground border border-border font-medium transition-colors duration-200"
      >
        <PlayIcon className="w-5 h-5" />
        Play all
      </button>

      <button
        onClick={pauseAll}
        className="flex items-center gap-2 px-4 py-2 rounded-lg bg-background-secondary hover:bg-background-tertiary text-foreground border border-border font-medium transition-colors duration-200"
      >
        <PauseIcon className="w-5 h-5" />
        Pause all
      </button>

      <div className="flex gap-2">
        <button
          onClick={() => rateAll(0.5)}
          className="px-4 py-2 rounded-lg bg-background-secondary hover:bg-background-tertiary text-foreground border border-border font-medium transition-colors duration-200"
        >
          0.5X
        </button>
        <button
          onClick={() => rateAll(1)}
          className="px-4 py-2 rounded-lg bg-background-secondary hover:bg-background-tertiary text-foreground border border-border font-medium transition-colors duration-200"
        >
          1X
        </button>
        <button
          onClick={() => rateAll(2)}
          className="px-4 py-2 rounded-lg bg-background-secondary hover:bg-background-tertiary text-foreground border border-border font-medium transition-colors duration-200"
        >
          2X
        </button>
      </div>
    </div>
  )
}

export default PlayerControl
