import React, { useRef } from 'react';

function AudioPlayer({ audioUrl }) {
    const audioRef = useRef(null);

    const handlePlay = () => {
        if (audioRef.current) {
            audioRef.current.play();
        }
    };

    const handlePause = () => {
        if (audioRef.current) {
            audioRef.current.pause();
        }
    };

    return (
        <div>
            <audio ref={audioRef} src={audioUrl} controls />
            <button onClick={handlePlay}>Play</button>
            <button onClick={handlePause}>Pause</button>
        </div>
    );
}

export default AudioPlayer;