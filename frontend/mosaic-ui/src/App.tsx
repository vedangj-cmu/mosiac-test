import { useRef } from "react";
import VideoPlayer from "./VideoPlayer";
import type { VideoHandle } from "./VideoPlayer";
import { PlayIcon, PauseIcon, ArrowPathIcon } from "@heroicons/react/24/solid";


function App() {

    const refs = Array.from({ length: 6 }, () => useRef<VideoHandle>(null));
    const srcs = [
        "/video?filename=center_front_image_rect_compressed.mp4",
        "/video?filename=center_rear_image_rect_compressed.mp4",
        "/video?filename=driver_front_image_rect_compressed.mp4",
        "/video?filename=driver_rear_image_rect_compressed.mp4",
        "/video?filename=passenger_front_image_rect_compressed.mp4",
        "/video?filename=passenger_rear_image_rect_compressed.mp4"
    ];

    const playAll = () => refs.forEach(r => r.current?.play());
    const pauseAll = () => refs.forEach(r => r.current?.pause());
    const rateAll = (r: number) => refs.forEach(rf => rf.current?.setRate(r));

    return (
        <>
            <div className='m-8 border p-8 rounded'>
                <h1>Hello world</h1>
                <div className=" flex flex-wrap">
                    {srcs.map((src, i) => (
                        <VideoPlayer className=" m-1 rounded-md w-1/4" key={i} ref={refs[i]} src={"http://localhost:8000" + src} />
                    ))}
                </div>
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
            </div>
        </>
    )
}

export default App