"""
Voice agent using LiveKit Agents + AssemblyAI Universal-3 Pro Streaming.

Stack:
  STT  — AssemblyAI Universal-3 Pro Streaming (u3-rt-pro)
  LLM  — OpenAI GPT-4o
  TTS  — Cartesia Sonic
  VAD  — Silero
  Turn — AssemblyAI neural turn detection
"""

import os
from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import openai, cartesia, assemblyai, silero

load_dotenv()

SYSTEM_PROMPT = """
You are a helpful, concise voice assistant. You are having a real-time spoken
conversation — keep every response under 2–3 sentences unless the user asks
for detail. Never use bullet points, markdown, or lists; speak in natural prose.
""".strip()


class VoiceAssistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=SYSTEM_PROMPT)


async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()

    session = AgentSession(
        # ── STT: AssemblyAI Universal-3 Pro Streaming ──────────────────────
        # Requires livekit-agents >= 1.0.0 and livekit-plugins-assemblyai
        # u3-rt-pro delivers 307 ms P50 latency with neural turn detection,
        # real-time speaker diarization, and mid-session keyterm prompting.
        stt=assemblyai.STT(
            # Universal-3 Pro Streaming: 307 ms P50 latency, neural turn detection,
            # real-time diarization, anti-hallucination, mid-session prompting.
            model="u3-rt-pro",
            # Neural turn detection: emit turn when confidence >= threshold.
            # Lower values (0.3–0.4) respond faster; raise to 0.6 for noisy lines.
            end_of_turn_confidence_threshold=0.4,
            # Silence (ms) before speculative end-of-turn check fires.
            min_turn_silence=300,
            # Hard ceiling: force end-of-turn after this much silence.
            max_turn_silence=1200,
        ),

        # ── LLM ────────────────────────────────────────────────────────────
        llm=openai.LLM(model="gpt-4o"),

        # ── TTS ────────────────────────────────────────────────────────────
        tts=cartesia.TTS(
            model="sonic-2",
            voice="79a125e8-cd45-4c13-8a67-188112f4dd22",  # British Lady
        ),

        # ── VAD ────────────────────────────────────────────────────────────
        vad=silero.VAD.load(),

        # Use AssemblyAI's own turn detection model instead of LiveKit default.
        # This leverages acoustic + linguistic signals for more accurate endpointing.
        turn_detection="stt",
    )

    await session.start(
        room=ctx.room,
        agent=VoiceAssistant(),
        room_input_options=RoomInputOptions(),
    )

    await session.generate_reply(
        instructions="Greet the user warmly and ask how you can help them today."
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
