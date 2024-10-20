import React, { useState, useEffect, useRef } from 'react';
import { Gapless5 } from '@regosen/gapless-5';

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
  const playerRef = useRef<Gapless5 | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    playerRef.current = new Gapless5({ guiId: 'gapless5-player-id', loop: true });

    const fetchAndAddTrack = async () => {
      try {
        const response = await fetch('https://1524-195-242-23-83.ngrok-free.app/stream', {
          headers: {
            'Accept': 'audio/wav'
          }
        });
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        playerRef.current?.addTrack(url);
      } catch (error) {
        console.error('Error fetching audio:', error);
      }
    };

    fetchAndAddTrack();

    playerRef.current.onfinishedtrack = () => {
      console.log('onfinishedtrack');
      fetchAndAddTrack();
    };
  }, []);

  const handlePlay = () => {
    if (playerRef.current) {
      playerRef.current.play();
      setIsPlaying(true);
    }
  };

  return (
    <div>
      <div id="gapless5-player-id" />
      <button
        onClick={handlePlay}
        className="mt-4 px-6 py-3 bg-pink-500 text-white rounded-full hover:bg-pink-600 transition-colors duration-300"
        disabled={isPlaying}
      >
        {isPlaying ? 'Playing' : 'Start Play'}
      </button>
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
      {/* <StarBackground isPlaying={isPlaying} onClick={togglePlayPause} /> */}
      <Player />
      <div className="w-full bg-black p-4 relative z-10">
        {/* <span className="text-pink-400 text-xl font-bold animate-pulse">TBD</span> */}
      </div>
      <div className="flex-grow flex flex-col items-center justify-center p-4 relative z-10">
        <div className="w-full">
          <p className="text-3xl text-center text-pink-500 animate-pulse shadow-glow">
            ... an infinite collaborative AI DJ!
          </p>
        </div>
        <button
          onClick={togglePlayPause}
          className="mt-8 px-6 py-3 bg-pink-500 text-white rounded-full hover:bg-pink-600 transition-colors duration-300"
        >
          {isPlaying ? 'Pause' : 'Play'} Animation
        </button>
        <div className="absolute bottom-4 left-4 w-32 h-32">
          <img 
            src="/public/qrt.png" 
            alt="QR Code" 
            className="w-full h-full"
            style={{ filter: 'invert(48%) sepia(89%) saturate(2476%) hue-rotate(280deg) brightness(118%) contrast(119%)' }}
          />
        </div>
      </div>
    </div>
  )
}
