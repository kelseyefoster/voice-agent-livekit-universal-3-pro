# LiveKit voice agent with AssemblyAI Universal-3 Pro Streaming

Build a production-ready real-time voice agent using **LiveKit Agents** and the **AssemblyAI Universal-3 Pro Streaming model** (`u3-rt-pro`). This is the fastest path from zero to a deployed Voice AI agent — and the combination that gives you the best speech-to-text latency available today.

## Why Universal-3 Pro Streaming?

307ms P50 latency. That's what separates a voice agent that feels natural from one that feels broken.

| Metric | AssemblyAI Universal-3 Pro | Deepgram Nova-3 |
|--------|---------------------------|-----------------|
| P50 latency | **307 ms** | 516 ms |
| P99 latency | **1,012 ms** | 1,907 ms |
| Word Error Rate | **8.14%** | 9.87% |
| Neural turn detection | ✅ | ❌ (VAD only) |
| Mid-session prompting | ✅ | ❌ |
| Anti-hallucination | ✅ | ❌ |
| Alphanumeric accuracy | **+21% fewer errors** | baseline |

*Benchmarks from Hamming.ai across 4M+ production calls.*

The turn detection difference is significant. Instead of silence-based VAD, Universal-3 Pro uses acoustic and linguistic signals together — so it knows the difference between a pause mid-sentence and an actual end-of-turn. Fewer false triggers, snappier response.

## Architecture

```
Browser / Phone
      │  WebRTC (LiveKit room)
      ▼
LiveKit Cloud ──► AssemblyAI Universal-3 Pro Streaming (speech-to-text)
                        │ transcript + neural turn signal
                        ▼
                   OpenAI GPT-4o (LLM)
                        │ text response
                        ▼
                   Cartesia Sonic (TTS)
                        │ audio
                        ▼
               Back to LiveKit room
```

## Prerequisites

- Python 3.11+
- [AssemblyAI API key](https://app.assemblyai.com) — free tier available
- [LiveKit Cloud account](https://cloud.livekit.io) — free tier available
- [OpenAI API key](https://platform.openai.com/api-keys)
- [Cartesia API key](https://play.cartesia.ai)

## Quick start

### 1. Clone and install

```bash
git clone https://github.com/AssemblyAI/voice-agent-livekit-universal-3-pro
cd voice-agent-livekit-universal-3-pro

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Download plugin models

```bash
python agent.py download-files
```

### 4. Run locally

```bash
# Console mode — speak directly from your terminal
python agent.py console

# Dev mode — connects to LiveKit Cloud, open agents-playground.livekit.io
python agent.py dev
```

Open [agents-playground.livekit.io](https://agents-playground.livekit.io), enter your LiveKit URL and API key, and start talking.

## Tuning Universal-3 Pro Streaming

The three turn detection parameters give you a lot of control over how responsive vs. patient the agent feels:

```python
stt=assemblyai.STT(
    model="u3-rt-pro",

    # How confident the model needs to be before declaring turn end (0.0–1.0)
    # Lower = faster response; higher = fewer false triggers on noisy lines
    end_of_turn_confidence_threshold=0.4,

    # Silence (ms) before the speculative end-of-turn check fires
    min_turn_silence=300,

    # Hard ceiling — force turn end after this much silence regardless
    max_turn_silence=1200,
)
```

**For noisy environments** (call centers, mobile): raise `end_of_turn_confidence_threshold` to `0.6`

**For fast-paced conversation**: lower `min_turn_silence` to `200`

**For healthcare or deliberate speech**: raise `max_turn_silence` to `2000`

## Enabling keyterm prompting

Boost recognition accuracy for domain-specific vocabulary mid-session — no restart required:

```python
# After session.start():
await session.stt.update_options(
    keyterms_prompt=["YourBrandName", "SpecialProduct", "TechnicalTerm"]
)
```

Up to 1,000 terms, each up to 50 characters. This is especially useful for medical terminology, product names, and financial jargon.

## Enabling real-time speaker diarization

```python
stt=assemblyai.STT(
    model="u3-rt-pro",
    speaker_labels=True,
    max_speakers=2,  # e.g., interviewer + candidate, agent + customer
)
```

## Swapping components

The LiveKit Agents plugin system makes it straightforward to swap any component:

```python
# Different LLM
from livekit.plugins import anthropic
llm=anthropic.LLM(model="claude-opus-4-6")

# Different TTS
from livekit.plugins import elevenlabs
tts=elevenlabs.TTS(voice_id="your_voice_id")

# Groq for ultra-low-latency LLM inference
llm=openai.LLM.with_groq(model="llama-3.3-70b-versatile")
```

## Deploy to Fly.io

```bash
fly launch --no-deploy
fly secrets set \
  ASSEMBLYAI_API_KEY=your_key \
  OPENAI_API_KEY=your_key \
  CARTESIA_API_KEY=your_key \
  LIVEKIT_URL=wss://... \
  LIVEKIT_API_KEY=your_key \
  LIVEKIT_API_SECRET=your_secret
fly deploy
```

## Related tutorials

- [Tutorial 02: Pipecat + Universal-3 Pro Streaming](../02-pipecat-universal-3-pro) — modular pipeline framework built on Daily.co WebRTC
- [Tutorial 05: raw WebSocket voice agent](../05-websocket-universal-3-pro) — understand exactly what LiveKit abstracts away
- [Tutorial 08: Node.js voice agent](../08-nodejs-assemblyai) — same Universal-3 Pro Streaming model, JavaScript stack

## Resources

- [AssemblyAI Universal Streaming docs](https://www.assemblyai.com/docs/speech-to-text/universal-streaming)
- [Universal-3 Pro Streaming announcement](https://www.assemblyai.com/blog/universal-3-pro-streaming)
- [LiveKit Agents docs](https://docs.livekit.io/agents/)
- [AssemblyAI LiveKit integration guide](https://www.assemblyai.com/docs/integrations/livekit)

---

<div class="blog-cta_component">
  <div class="blog-cta_title">Build your first LiveKit voice agent</div>
  <div class="blog-cta_rt w-richtext">
    <p>Sign up for a free AssemblyAI account and start building with Universal-3 Pro Streaming today. No credit card required.</p>
  </div>
  <a href="https://www.assemblyai.com/dashboard/signup" class="button w-button">Start building</a>
</div>

<div class="blog-cta_component">
  <div class="blog-cta_title">Experiment with real-time turn detection</div>
  <div class="blog-cta_rt w-richtext">
    <p>Try streaming transcription in our Playground and observe how punctuation and silence handling shape turn boundaries in real time. Compare behaviors across Universal-3 Pro Streaming and Universal-streaming models.</p>
  </div>
  <a href="https://www.assemblyai.com/playground" class="button w-button">Open playground</a>
</div>
