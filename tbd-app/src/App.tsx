import React, { useState, useEffect, useRef } from 'react';



const Prompt: React.FC = () => {
  const [prompt, setPrompt] = useState<string>('');

  const fetchPrompt = async () => {
    try {
      const response = await fetch('https://1524-195-242-23-83.ngrok-free.app/prompt', {
        headers: {
          'ngrok-skip-browser-warning': '69420'
        }
      });
      const data = await response.json();
      console.log(data)
      setPrompt(data || 'No prompt available');
    } catch (error) {
      console.error('Error fetching prompt:', error);
      setPrompt('Error fetching prompt');
    }
  };

  useEffect(() => {
    fetchPrompt();
    const interval = setInterval(fetchPrompt, 10000);
    return () => clearInterval(interval);
  }, []);
  return (
    <div className="flex justify-center items-center">
      <div className="w-1/2 p-4 rounded-lg">
        <p className="text-center text-white text-3xl">{prompt}</p>
      </div>
    </div>
  );
};

interface HistoryItem {
  timestamp: string;
  content: string;
  from: string;
}
const History: React.FC = () => {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [isCollapsed, setIsCollapsed] = useState<boolean>(false);

  const fetchHistory = async () => {
    try {
      const response = await fetch('https://1524-195-242-23-83.ngrok-free.app/history', {
        headers: {
          'ngrok-skip-browser-warning': '69420'
        }
      });
      const data = await response.json();
      setHistory(data.reverse());
      console.log(data)
    } catch (error) {
      console.error('Error fetching history:', error);
    }
  };

  useEffect(() => {
    fetchHistory();
    const interval = setInterval(fetchHistory, 10000);
    return () => clearInterval(interval);
  }, []);

  const colors = ['#ff00ff', '#00ffff', '#8a2be2', '#ff69b4', '#9370db', '#4169e1', '#9932cc', '#1e90ff'];
  return (
    <div className={`fixed right-0 top-1/2 transform -translate-y-1/2 ${isCollapsed ? 'w-12' : 'w-96'} h-1/2 overflow-y-auto bg-gray-900 bg-opacity-50 text-white p-2 z-50 rounded-l-lg shadow-lg transition-all duration-300`}>
      <button 
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="absolute top-2 left-2 bg-gray-700 hover:bg-gray-600 rounded-full p-1"
      >
        {isCollapsed ? '💗' : '💗'}
      </button>
      {!isCollapsed && (
        <>
          <h2 className="text-lg font-bold mb-2 text-center">Back2Back</h2>
          {history.map((item, index) => (
            <div key={index} className="mb-2 p-1 rounded" style={{ backgroundColor: `${colors[index % colors.length]}40` }}>
              <div className="flex justify-between items-center">
                <p className="text-xs opacity-70">{item.timestamp.substring(0, 10)}</p>
                <p className="font-semibold">📞 {item.from}</p>
              </div>
              <p className="text-sm">{item.content}</p>
            </div>
          ))}
        </>
      )}
    </div>
  );
};


const StarBackground: React.FC<{ isPlaying: boolean; onClick: () => void }> = ({ isPlaying, onClick }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const stars: { x: number; y: number; size: number; speed: number }[] = [];

    // Create stars
    for (let i = 0; i < 200; i++) {
      stars.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        size: Math.random() * 2,
        speed: Math.random() * 0.5 + 0.1
      });
    }

    let animationFrameId: number;
    let time = 0;

    const retrowaveColors = ['#ff00ff', '#00ffff', '#8a2be2', '#ff69b4', '#9370db', '#4169e1', '#9932cc', '#1e90ff'];
    const waveThicknesses = [2, 3, 1.5, 2.5, 2, 2.5, 1.8, 2.2];
    const amplitudes = [90, 80, 70, 60, 50, 40, 30, 20];
    const phases = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7];

    const animate = () => {
      time += 0.05;
      ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Draw stars
      stars.forEach(star => {
        ctx.fillStyle = 'white';
        ctx.beginPath();
        ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2);
        ctx.fill();

        star.y += star.speed;
        if (star.y > canvas.height) {
          star.y = 0;
          star.x = Math.random() * canvas.width;
        }
      });

      // Draw waveform
      const indices = [...Array(retrowaveColors.length).keys()];
      for (let i of indices.sort(() => Math.random() - 0.5)) {
        ctx.beginPath();
        ctx.moveTo(0, canvas.height / 2);

        for (let x = 0; x < canvas.width; x++) {
          const frequency = 0.02 + i * 0.005;
          const amplitude = amplitudes[i] - i * 2;
          const y = Math.sin(x * frequency + time * (1 + i * phases[i])) * amplitude + canvas.height / 2;
          ctx.lineTo(x, y);
        }

        ctx.strokeStyle = retrowaveColors[i];
        ctx.lineWidth = waveThicknesses[i];
        ctx.stroke();
      }

      if (isPlaying) {
        animationFrameId = requestAnimationFrame(animate);
      }
    };

    if (isPlaying) {
      animate();
    } else {
      ctx.fillStyle = 'black';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
    }

    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [isPlaying]);

  return (
    <canvas
      ref={canvasRef}
      className="fixed top-0 left-0 w-full h-full"
      width={window.innerWidth}
      height={window.innerHeight}
      onClick={onClick}
      style={{ cursor: 'pointer' }}
    />
  );
};
const Player: React.FC = () => {
  const audioRef1 = useRef<HTMLAudioElement>(null);
  const audioRef2 = useRef<HTMLAudioElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentPlayer, setCurrentPlayer] = useState<1 | 2>(1);
  const [nextTrackUrl, setNextTrackUrl] = useState<string | null>(null);

  useEffect(() => {
    if (audioRef1.current && audioRef2.current) {
      audioRef1.current.src = 'https://1524-195-242-23-83.ngrok-free.app/stream';
      audioRef1.current.load();
    }
  }, []);

  useEffect(() => {
    const currentAudio = currentPlayer === 1 ? audioRef1.current : audioRef2.current;
    const nextAudio = currentPlayer === 1 ? audioRef2.current : audioRef1.current;
    if (!currentAudio || !nextAudio) return;

    const handleTimeUpdate = () => {
      if (currentAudio.currentTime >= 5 && !nextTrackUrl) {
        const url = 'https://1524-195-242-23-83.ngrok-free.app/stream';
        setNextTrackUrl(url);
        nextAudio.src = url;
        nextAudio.load();
        console.log('New track ready to play');
      }
    };

    const handleEnded = () => {
      console.log('Current track ended');
      if (nextTrackUrl) {
        console.log('Has next track track ended');
        currentAudio.pause();
        currentAudio.currentTime = 0;
        nextAudio.play();
        setCurrentPlayer(currentPlayer === 1 ? 2 : 1);
        setNextTrackUrl(null);
      }
    };

    currentAudio.addEventListener('timeupdate', handleTimeUpdate);
    currentAudio.addEventListener('ended', handleEnded);

    return () => {
      currentAudio.removeEventListener('timeupdate', handleTimeUpdate);
      currentAudio.removeEventListener('ended', handleEnded);
    };
  }, [currentPlayer, nextTrackUrl]);

  const handlePlay = () => {
    const currentAudio = currentPlayer === 1 ? audioRef1.current : audioRef2.current;
    if (currentAudio) {
      currentAudio.play();
      setIsPlaying(true);
    }
  };

  return (
    <div className="fixed top-0 left-0 z-50">
      <audio ref={audioRef1} />
      <audio ref={audioRef2} />
      {!isPlaying && <button
        onClick={handlePlay}
        className="mt-4 px-6 py-3 bg-pink-500 text-white rounded-full hover:bg-pink-600 transition-colors duration-300"
        disabled={isPlaying}
      >
        {isPlaying ? '' : 'Start Play'}
      </button>}
    </div>
  );
};

export default function App() {
  const [isPlaying, setIsPlaying] = useState(true);

  const togglePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  return (
    <div className="min-h-screen bg-black flex flex-col relative">
      <Player />
      <StarBackground isPlaying={isPlaying} onClick={togglePlayPause} />
      <History />
      <div className="w-full bg-black p-4 relative z-10">
        {/* <span className="text-pink-400 text-xl font-bold animate-pulse">TBD</span> */}
      </div>
      <div className="flex-grow flex flex-col items-center justify-center p-4 relative z-10">
        <div className="w-full">
         
         <Prompt />
         
        </div>
       

        {/* <button
          onClick={togglePlayPause}
          className="mt-8 px-6 py-3 bg-pink-500 text-white rounded-full hover:bg-pink-600 transition-colors duration-300"
        >
          {isPlaying ? 'Pause' : 'Play'} Animation
        </button> */}
        <div className="absolute bottom-4 left-4 w-32 h-32">
          <img 
            src="/public/qrt.png" 
            alt="QR Code" 
            className="w-full h-full"
            style={{ filter: 'invert(48%) sepia(89%) saturate(2476%) hue-rotate(240deg) brightness(118%) contrast(119%)' }}
          />
        </div>
      </div>
    </div>
  )
}
