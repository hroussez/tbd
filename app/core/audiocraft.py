
from concurrent.futures import ProcessPoolExecutor
import time
import os
from pathlib import Path
import subprocess as sp
from tempfile import NamedTemporaryFile
import time
import typing as tp
import warnings
import os
from einops import rearrange
import torch
import gradio as gr
from pydub import AudioSegment

from audiocraft.audiocraft.data.audio_utils import convert_audio
from audiocraft.audiocraft.data.audio import audio_write
from audiocraft.audiocraft.models.encodec import InterleaveStereoCompressionModel
from audiocraft.audiocraft.models import MusicGen, MultiBandDiffusion


MODEL = None  # Last used model
SPACE_ID = os.environ.get('SPACE_ID', '')
IS_BATCHED = "facebook/MusicGen" in SPACE_ID or 'musicgen-internal/musicgen_dev' in SPACE_ID
print(IS_BATCHED)
MAX_BATCH_SIZE = 12
BATCHED_DURATION = 15
INTERRUPTING = False
MBD = None
# We have to wrap subprocess call to clean a bit the log when using gr.make_waveform
_old_call = sp.call


def _call_nostderr(*args, **kwargs):
    # Avoid ffmpeg vomiting on the logs.
    kwargs['stderr'] = sp.DEVNULL
    kwargs['stdout'] = sp.DEVNULL
    _old_call(*args, **kwargs)


sp.call = _call_nostderr
# Preallocating the pool of processes.
pool = ProcessPoolExecutor(4)
pool.__enter__()

def interrupt():
    global INTERRUPTING
    INTERRUPTING = True

class FileCleaner:
    def __init__(self, file_lifetime: float = 3600):
        self.file_lifetime = file_lifetime
        self.files = []

    def add(self, path: tp.Union[str, Path]):
        self._cleanup()
        self.files.append((time.time(), Path(path)))

    def _cleanup(self):
        now = time.time()
        for time_added, path in list(self.files):
            if now - time_added > self.file_lifetime:
                if path.exists():
                    path.unlink()
                self.files.pop(0)
            else:
                break
                
file_cleaner = FileCleaner()


def make_waveform(*args, **kwargs):
    return ""
    # Further remove some warnings.
    be = time.time()
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        out = gr.make_waveform(*args, **kwargs)
        print("Make a video took", time.time() - be)
        return out


def load_model(version='facebook/musicgen-melody'):
    global MODEL
    print("Loading model", version)
    if MODEL is None or MODEL.name != version:
        # Clear PyTorch CUDA cache and delete model
        del MODEL
        torch.cuda.empty_cache()
        MODEL = None  # in case loading would crash
        MODEL = MusicGen.get_pretrained(version)


def load_diffusion():
    global MBD
    if MBD is None:
        print("loading MBD")
        MBD = MultiBandDiffusion.get_mbd_musicgen()


def _do_predictions(texts, melodies, duration, progress=False, gradio_progress=None, **gen_kwargs):
    MODEL.set_generation_params(duration=duration, **gen_kwargs)
    print("new batch", len(texts), texts, [None if m is None else (m[0], m[1].shape) for m in melodies])
    be = time.time()
    processed_melodies = []
    target_sr = 32000
    target_ac = 1
    for melody in melodies:
        if melody is None:
            processed_melodies.append(None)
        else:
            sr, melody = melody[0], torch.from_numpy(melody[1]).to(MODEL.device).float().t()
            if melody.dim() == 1:
                melody = melody[None]
            melody = melody[..., :int(sr * duration)]
            melody = convert_audio(melody, sr, target_sr, target_ac)
            processed_melodies.append(melody)

    try:
        if any(m is not None for m in processed_melodies):
            outputs = MODEL.generate_with_chroma(
                descriptions=texts,
                melody_wavs=processed_melodies,
                melody_sample_rate=target_sr,
                progress=progress,
                return_tokens=USE_DIFFUSION
            )
        else:
            outputs = MODEL.generate(texts, progress=progress, return_tokens=USE_DIFFUSION)
    except RuntimeError as e:
        raise gr.Error("Error while generating " + e.args[0])
    if USE_DIFFUSION:
        if gradio_progress is not None:
            gradio_progress(1, desc='Running MultiBandDiffusion...')
        tokens = outputs[1]
        if isinstance(MODEL.compression_model, InterleaveStereoCompressionModel):
            left, right = MODEL.compression_model.get_left_right_codes(tokens)
            tokens = torch.cat([left, right])
        outputs_diffusion = MBD.tokens_to_wav(tokens)
        if isinstance(MODEL.compression_model, InterleaveStereoCompressionModel):
            assert outputs_diffusion.shape[1] == 1  # output is mono
            outputs_diffusion = rearrange(outputs_diffusion, '(s b) c t -> b (s c) t', s=2)
        outputs = torch.cat([outputs[0], outputs_diffusion], dim=0)
    outputs = outputs.detach().cpu().float()
    pending_videos = []
    out_wavs = []
    for output in outputs:
        with NamedTemporaryFile("wb", suffix=".wav", delete=False) as file:
            audio_write(
                file.name, output, MODEL.sample_rate, strategy="loudness",
                loudness_headroom_db=16, loudness_compressor=True, add_suffix=False)
            pending_videos.append(pool.submit(make_waveform, file.name))
            out_wavs.append(file.name)
            file_cleaner.add(file.name)
    out_videos = [pending_video.result() for pending_video in pending_videos]
    for video in out_videos:
        file_cleaner.add(video)
    print("batch finished", len(texts), time.time() - be)
    print("Tempfiles currently stored: ", len(file_cleaner.files))
    return out_videos, out_wavs


def predict_batched(texts, melodies):
    max_text_length = 512
    texts = [text[:max_text_length] for text in texts]
    load_model('facebook/musicgen-stereo-melody')
    res = _do_predictions(texts, melodies, BATCHED_DURATION)
    return res

def predict_full(model, model_path, decoder, text, melody, duration, topk, topp, temperature, cfg_coef):
    global INTERRUPTING
    global USE_DIFFUSION
    INTERRUPTING = False
    model_path = model_path.strip()
    if model_path:
        if not Path(model_path).exists():
            raise gr.Error(f"Model path {model_path} doesn't exist.")
        if not Path(model_path).is_dir():
            raise gr.Error(f"Model path {model_path} must be a folder containing "
                           "state_dict.bin and compression_state_dict_.bin.")
        model = model_path
    if temperature < 0:
        raise gr.Error("Temperature must be >= 0.")
    if topk < 0:
        raise gr.Error("Topk must be non-negative.")
    if topp < 0:
        raise gr.Error("Topp must be non-negative.")

    topk = int(topk)
    if decoder == "MultiBand_Diffusion":
        USE_DIFFUSION = True
        load_diffusion()
    else:
        USE_DIFFUSION = False
    load_model(model)
    videos, wavs = _do_predictions( [text], [melody], duration, progress=True, top_k=topk, top_p=topp, temperature=temperature, cfg_coef=cfg_coef, )
    if USE_DIFFUSION:
        return videos[0], wavs[0], videos[1], wavs[1]
    return videos[0], wavs[0], None, None

def index2wav(index, output_dir):
    return f"{output_dir}/{str(index).zfill(3)}.wav"

def generate_audio(prompt, last_wav=None):
    model = "facebook/musicgen-small"
    model_path = ""
    decoder = "Default"
    melody = None
    duration = 10
    topk = 250
    topp = 0 
    temperature = 1
    cfg_coef = 3
    # Set the duration of the crossfade (in milliseconds)
    crossfade_duration = 4000

    if last_wav is not None:
        duration += crossfade_duration / 1000

    print("generating:", prompt)
    start_time = time.time()
    _, wav_file, _, _ = predict_full(model, model_path, decoder, prompt, melody, duration, topk, topp, temperature, cfg_coef)
    end_time = time.time()
    print("finished", duration, "in", round(end_time - start_time, 2), "seconds", wav_file)

    audio2 = AudioSegment.from_wav(wav_file)

    with NamedTemporaryFile("wb", suffix=".wav", delete=False) as file:
        audio2.export(file.name, format="wav")
        wav_file = file.name

    print("new wav", wav_file)
    
    if last_wav is None:
        print("no last wav")
        return wav_file
    
    wav1 = last_wav
    wav2 = wav_file

    # Load audio files
    audio1 = AudioSegment.from_wav(wav1)
    
    # Crossfade the two audio files
    output = audio1.append(audio2, crossfade=crossfade_duration)


    # Apply EQ fade to the second track during the crossfade
    # For example, progressively increasing treble
    def apply_eq_fade(audio_segment, start_time, end_time):
        """Apply EQ fade by increasing the high frequencies over time."""
        eq_faded_audio = audio_segment
        fade_duration = end_time - start_time

        # Break down the segment into small chunks to apply EQ progressively
        chunk_size = 100  # 100 milliseconds chunks
        for i in range(0, fade_duration, chunk_size):
            # Calculate the current volume boost for high frequencies
            factor = (i / fade_duration)  # A factor that increases over time
            
            # Apply EQ boost (increasing the dB gain for higher frequencies)
            eq_faded_audio = eq_faded_audio.overlay(
                audio_segment[start_time + i:start_time + i + chunk_size].high_pass_filter(5000).apply_gain(factor * 6),  # Adjust dB gain as needed
                position=i
            )
        return eq_faded_audio

    # Apply EQ fade to the second track starting at the crossfade duration
    eq_faded_audio2 = apply_eq_fade(audio2, start_time=0, end_time=crossfade_duration)

    # Crossfade again, but with EQ faded version of track 2
    output_with_eq_fade = audio1.append(eq_faded_audio2, crossfade=crossfade_duration)

    # Get the total duration of the output audio in milliseconds
    total_duration = len(output_with_eq_fade)

    # Calculate the midpoint to split the audio
    midpoint = total_duration // 2

    # Split the audio into two parts
    first_half = output_with_eq_fade[:midpoint]
    second_half = output_with_eq_fade[midpoint:]

    # Export the first and second halves as separate files
    first_half.export(wav1, format="wav")
    second_half.export(wav2, format="wav")

    # # Get the total duration of the output audio in milliseconds
    # total_duration = len(output)

    # # Calculate the midpoint to split the audio
    # midpoint = total_duration // 2
    # print(total_duration)

    # # Split the audio into two parts
    # first_half = output[:midpoint]
    # second_half = output[midpoint:]

    # first_half.export(wav1, format="wav")
    # second_half.export(wav2, format="wav")

    print("returning", wav2)

    return wav2