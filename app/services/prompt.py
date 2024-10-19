from openai import OpenAI

examples = [
    # "ambiant tribal house",
    "80s driving pop song with heavy drums and synth pads in the background",
    "cheerful country song with acoustic guitars",
    "rock song with electric guitar and heavy drums",
    "light and cheerly EDM track, with syncopated drums, aery pads, and strong emotions bpm: 130",
    "lofi slow bpm electro chill with organic samples",
    "smooth jazz track with a soothing saxophone melody and gentle piano chords",
    "fast-paced techno track with pulsating bass and crisp hi-hats",
    "melancholic orchestral piece with slow strings and a somber piano",
    "futuristic synthwave track with retro arpeggios and punchy electronic drums",
    "high-energy punk rock anthem with distorted guitars and aggressive vocals",
    "soulful R&B ballad with soft vocals and mellow keyboard backing",
    "tropical house track with upbeat rhythms, steel drums, and vocal chops",
    "atmospheric ambient piece with evolving textures and soft drones",
    "gritty trap beat with deep 808s, snappy snares, and vocal ad-libs",
    "funky disco tune with groovy basslines, brass sections, and catchy hooks",
    "dark cinematic score with heavy strings, deep percussion, and suspenseful brass",
    "upbeat reggae track with syncopated guitar strumming and smooth vocals",
    "dreamy synth-pop song with lush synths and reverbed vocals",
    "high-tempo drum and bass track with rolling basslines and fast-paced drums",
    "smooth R&B groove with laid-back beats, silky vocals, and jazzy chords",
    " epic orchestral track with powerful brass, intense strings, and choir vocals",
    "gritty industrial track with mechanical sounds, heavy distortion, and dark ambience",
    "chillwave track with nostalgic synths, lo-fi beats, and hazy melodies",
    "funky electro-swing tune with brass instruments and modern dance beats",
    "folktronica track with acoustic instruments and glitchy electronic elements",
    "dynamic progressive rock track with complex rhythms and powerful guitar solos",
    "vibrant Afrobeat song with rhythmic percussion and catchy vocal hooks",
    "moody downtempo track with deep bass and atmospheric textures",
    "fast-paced ska track with punchy brass, off-beat guitar rhythms, and lively vocals",
    "soulful gospel choir piece with rich harmonies and uplifting piano",
    "minimal techno track with repetitive beats and hypnotic synth sequences",
    "emotional piano ballad with delicate melodies and a soft string accompaniment",
    "groovy funk track with tight basslines, wah-wah guitar, and funky horns",
    "psychedelic rock song with swirling guitars, spacey effects, and a laid-back groove",
    "high-energy Latin dance track with fast percussion, brass accents, and vibrant rhythms",
]

system_prompt = f"""
You are a DJ who is using an audio generation model to create music.

Your goal is to generate a prompt that will be used to generate the next song in the sequence.

As part of your job, you receive a list of instructions and examples of music you should create coming from your audience.
Consider the transition between the current song and the next one, and use the instructions and examples to generate a prompt that will be used to generate the next song in the sequence.

Return only the prompt, nothing else.
"""

client = OpenAI()

def generate_prompt(history: list[dict]):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system_prompt}, *history]
    )

    return response.choices[0].message.content
