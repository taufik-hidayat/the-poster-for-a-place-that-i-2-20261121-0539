# VELKARA — The City Above the Clouds

[![make.fun](https://img.shields.io/badge/make.fun-bounty-7C3AED)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539)
[![make.fun](https://img.shields.io/badge/make.fun-entry-00C853)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539)
[![make.fun](https://img.shields.io/badge/make.fun-VELKARA-FF6B35)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539)

A travel poster for a place that isn't there — **VELKARA, the city above the
clouds**. Floating islands with tiny tower cities drift over a sea of clouds
at golden dusk, under a ringed planet and a low sun. Drawn 100% procedurally
with Pillow: no input images, no network, fully deterministic.

- **Bounty:** [The Poster for a Place That Isn't There](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539)
- **Referral code:** `2z9vc20p`

## Run

```bash
python3 main.py
```

Writes exactly one file: `$MAKEFUN_OUTPUT_DIR/entry.png`
(1024×1024 PNG, under 1 MB). If `MAKEFUN_OUTPUT_DIR` is unset, output goes
to `output/` next to `main.py`.

## How it works

`main.py` draws the poster layer by layer:

1. Dusk gradient sky (indigo → violet → rose → gold)
2. Stars, a ringed planet, and a low glowing sun
3. Layered mountain ridges and a sea of clouds
4. Three floating islands carrying Velkara's tower city
5. Classic travel-poster title block: **VELKARA** — *THE CITY ABOVE THE CLOUDS* — "VISIT VELKARA • WHERE THE SKY BEGINS"

Fonts (DejaVu Sans / DejaVu Sans Bold) are bundled in `fonts/` with their
license (`fonts/LICENSE`), so the poster renders identically anywhere — no
system font paths are required.

## License

MIT — see [LICENSE](LICENSE).
