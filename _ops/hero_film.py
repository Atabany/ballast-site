#!/usr/bin/env python3
"""Cut the home page's hero film from real recordings of Ballast (no drawn interface, no sound).

    python3 _ops/hero_film.py ~/indie/quitPorn/marketing/app-preview-2026-11-v2/captures

Writes assets/ballast-panic-hero-film.mp4 and its poster. The captures are screen recordings of
Ballast 1.4 on an iPhone simulator with sample data. The film is the panic flow: Home, the tap,
Breathe, the plan, the ride, "It passed", and back to Home, so the last frame meets the first.
The recordings carry a P3 tag but hold sRGB values, so they're retagged, not converted.
Needs ffmpeg (on PATH, or the imageio-ffmpeg package). Nothing here runs in the site build.
"""
from pathlib import Path
import shutil, subprocess, sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/ballast-panic-hero-film.mp4'
POSTER = ROOT / 'assets/ballast-panic-hero-poster.jpg'
SIZE = '600:1304'
FADE = 0.4
# (capture, start, end) in seconds of the recording. Consecutive clips dissolve into each other,
# except where both sides are the same still screen: there the cut can't be seen.
CLIPS = [
    ('urge', 1.6, 10.3, 'fade'),
    ('urge', 15.4, 18.3, 'cut'),
    ('urge', 22.0, 25.1, 'fade'),
    ('outcome', 3.1, 7.7, 'fade'),
    ('urge', 1.2, 1.6, 'end'),   # Back to the frame the film opens on.
]


def ffmpeg():
    if shutil.which('ffmpeg'):
        return 'ffmpeg'
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def main():
    src = Path(sys.argv[1]).expanduser()
    inputs, chains = [], []
    for i, (name, start, end, _) in enumerate(CLIPS):
        inputs += ['-ss', str(start), '-t', f'{end - start:.3f}', '-i', str(src / f'{name}.mp4')]
        chains.append(f'[{i}:v]fps=30,scale={SIZE}:flags=lanczos,setparams=color_primaries=bt709:color_trc=iec61966-2-1:colorspace=bt709,format=yuv420p,setpts=PTS-STARTPTS,fps=30,settb=1/30[v{i}]')
    label, length = 'v0', CLIPS[0][2] - CLIPS[0][1]
    for i in range(1, len(CLIPS)):
        d = CLIPS[i][2] - CLIPS[i][1]
        if CLIPS[i - 1][3] == 'cut':
            chains.append(f'[{label}][v{i}]concat=n=2:v=1,fps=30,settb=1/30[x{i}]')
            length += d
        else:
            chains.append(f'[{label}][v{i}]xfade=transition=fade:duration={FADE}:offset={length - FADE:.3f},fps=30,settb=1/30[x{i}]')
            length += d - FADE
        label = f'x{i}'
    subprocess.run([ffmpeg(), '-y', '-loglevel', 'error', *inputs, '-filter_complex', ';'.join(chains), '-map', f'[{label}]', '-an',
                    '-c:v', 'libx264', '-profile:v', 'high', '-preset', 'veryslow', '-crf', '25', '-aq-mode', '3', '-pix_fmt', 'yuv420p',
                    '-color_primaries', 'bt709', '-color_trc', 'iec61966-2-1', '-colorspace', 'bt709', '-movflags', '+faststart', str(OUT)], check=True)
    subprocess.run([ffmpeg(), '-y', '-loglevel', 'error', '-i', str(OUT), '-frames:v', '1', '-q:v', '3', str(POSTER)], check=True)
    print(f'{OUT.name} {OUT.stat().st_size / 1024:.0f} KB, {length:.1f} s; {POSTER.name} {POSTER.stat().st_size / 1024:.0f} KB')


if __name__ == '__main__':
    main()
