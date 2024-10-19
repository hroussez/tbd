import React, { useState } from 'react';
import Chat from './Chat';
import AudioPlayer from './AudioPlayer';

function App() {
    const [audioUrl, setAudioUrl] = useState(null);

    const handleNewMessage = async (message) => {
        try {
            const response = await fetch('http://localhost:8080/gen', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ prompt: message }),
            });

            if (response.ok) {
                const blob = await response.blob();
                const audioUrl = URL.createObjectURL(blob);
                setAudioUrl(audioUrl);
            }
        } catch (error) {
            console.error("Error fetching audio:", error);
        }
    };

    return (
        <div id="root">
            <div className="chat-container">
                <Chat onNewMessage={handleNewMessage} />
            </div>
            <div className="audio-container">
                {audioUrl && <AudioPlayer audioUrl={audioUrl} />}
            </div>
        </div>
    );
}

export default App;