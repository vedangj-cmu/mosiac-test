import { PlayIcon, PauseIcon } from '@heroicons/react/24/solid'

const PlayerControl = ({ rateAll, pauseAll, playAll }) => {
  return (
    <div className="flex items-center gap-2 p-2 bg-slate-300 text-white rounded-xl shadow-md max-w-min">
      <button
        onClick={playAll}
        className="flex items-center gap-1 px-3 py-2 rounded-lg bg-green-600 hover:bg-green-700 whitespace-nowrap"
      >
        <PlayIcon className="w-5 h-5" />
        Play all
      </button>

      <button
        onClick={pauseAll}
        className="flex items-center gap-1 px-3 py-2 rounded-lg bg-red-600 hover:bg-red-700 whitespace-nowrap"
      >
        <PauseIcon className="w-5 h-5" />
        Pause all
      </button>

      <div className="flex gap-1">
        <button
          onClick={() => rateAll(0.5)}
          className="px-3 py-2 rounded-lg bg-gray-700 hover:bg-gray-600 whitespace-nowrap"
        >
          0.5X
        </button>
        <button
          onClick={() => rateAll(1)}
          className="px-3 py-2 rounded-lg bg-gray-700 hover:bg-gray-600 whitespace-nowrap"
        >
          1X
        </button>
        <button
          onClick={() => rateAll(2)}
          className="px-3 py-2 rounded-lg bg-gray-700 hover:bg-gray-600 whitespace-nowrap"
        >
          2X
        </button>
      </div>
    </div>
  )
}

export default PlayerControl
