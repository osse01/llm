import asyncio
import numpy as np
from google import genai
from google.genai import types
import sounddevice as sd
from aioconsole import ainput

songDescription = "A Live Performance from 80s with Banjo, Bagpipes and Kalimba in the style of Funk Metal."

client = genai.Client(http_options={'api_version': 'v1alpha'})

# Correct audio configuration based on actual format
SAMPLE_RATE = 48000  # 48kHz
CHANNELS = 2         # Stereo
DTYPE = 'int16'      # 16-bit PCM
BLOCKSIZE = 2048     # Adjust based on your latency needs

async def audio_player(audio_queue):
    """Task to play audio from the queue with correct format."""
    try:
        with sd.OutputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype=DTYPE,
            blocksize=BLOCKSIZE
        ) as stream:
            print(f"Audio player ready at {SAMPLE_RATE}Hz, {CHANNELS} channels")
            while True:
                audio_data = await audio_queue.get()
                if audio_data:
                    try:
                        # Convert bytes to numpy array with correct shape
                        audio_array = np.frombuffer(audio_data, dtype=np.int16)
                        
                        # Reshape for stereo (2 columns)
                        audio_array = audio_array.reshape(-1, 2)
                        
                        stream.write(audio_array)
                    except Exception as e:
                        print(f"Audio processing error: {e}")
    except Exception as e:
        print(f"Stream error: {e}")

async def receive_audio(session, audio_queue):
    """Process incoming audio messages with format verification."""
    try:
        async for message in session.receive():
            if hasattr(message.server_content, 'audio_chunks') and message.server_content.audio_chunks:
                audio_data = message.server_content.audio_chunks[0].data
                #print(f"Received {len(audio_data)} bytes ({len(audio_data)/4:,} stereo samples)")
                await audio_queue.put(audio_data)
    except Exception as e:
        print(f"Error receiving audio: {e}")

async def newPrompt() -> str:
    """Async version: Waits for user input and updates only when Enter is pressed"""
    global songDescription
    while True:
        user_input = await ainput("New prompt for the music (press Enter when done):\n")
        songDescription= user_input.strip() if user_input.strip() else songDescription
        
        


async def main():
    
    # Now run main program
    audio_queue = asyncio.Queue()
    
    async with (
        client.aio.live.music.connect(model='models/lyria-realtime-exp') as session,
        asyncio.TaskGroup() as tg,
    ):
        tg.create_task(audio_player(audio_queue))
        tg.create_task(receive_audio(session, audio_queue))
        tg.create_task(newPrompt())
        
        await session.set_weighted_prompts(
            prompts=[
                {"text": songDescription, "weight": 2.0},
                ]
        )
        await session.set_music_generation_config(
            config=types.LiveMusicGenerationConfig(bpm=90, temperature=3.0)
        )

        await session.play()
        
        while True:
            await asyncio.sleep(1)
    

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")