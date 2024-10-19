import React, { useRef } from 'react';

function AudioPlayer({ audioUrl }) {
    const audioRef = useRef(null);

    const handlePlay = () => {
        audioRef.current.play();
    };

    const handlePause = () => {
        audioRef.current.pause();
    };

    return (
        <div>
            <audio ref={audioRef} src={audioUrl} />
            <button onClick={handlePlay}>Play</button>
            <button onClick={handlePause}>Pause</button>
        </div>
    );
}

export default AudioPlayer;