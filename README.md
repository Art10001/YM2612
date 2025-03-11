Yamaha YM2612 emulation attempt in python/c++. This is so that i dont need to use actual m68k/z80 assembly to program a Sega Mega Drive. It would be, technically at least, more convenient.

2fm.py uses PyGame and renders to a wav. It processes how long you hold the key down for, making the note longer or shorter. The PyGame is a black screen, you basically play blind until i ask the ai to implement a piano roll or staff. Staff better in my opinion, but both may be helpful too.

fm.py writes to a wav based on what's hardcoded in it.
`ym2612_simulator.py` currently crashes and does not output. It was made with 4o.

The various wav files are output examples.

3fm.py is for 444 Hz. `4_639.py` is for 639 Hz.

speaker.py emits to your speaker. However, it sounds a bit screechy compared to the wav outputs.

Tools used: Aider, OpenRouter chat for fm2.py... mostly by Claude Sonnet 3.7, the jump from fm.py to fm2.py was achieved by DeepSeek R1 though, as well as speaker.py
