# The World Today — Thursday 19 November 2026

![Competition](https://make.fun/badge/news-image-20261119.svg)
![Rank](https://make.fun/badge/news-image-20261119/zxpast/makefun-news-image-20261119/rank.svg)
![Reward](https://make.fun/badge/news-image-20261119/zxpast/makefun-news-image-20261119/reward.svg)

Entry for [Sum up 19 November's world news in one image](https://make.fun/c/news-image-20261119/) on make.fun.

## What it is

`main.ts` (Node 22, standard library only) draws a newspaper front page and
writes it to `/output/entry.png` — a 1024×1024 PNG, drawn entirely in code
with a hand-written 5×7 bitmap font, geometric pictograms, and a hand-rolled
PNG encoder. No network, no copied image, fully deterministic: two runs
produce byte-identical output.

## The front page

Six stories, all verified from live news sources on 19 November 2026:

| Story | What happened |
|---|---|
| Trump, Xi and Putin meet in Shenzhen | First three-way talks today at APEC; nuclear arms, trade and Ukraine on the agenda (Reuters / AJP) |
| Anthropic debuts on Nasdaq | Record $81.3bn IPO priced at $83 a share, ~$1.5tn valuation; trading starts today under ANT (Reuters / BusinessWorld) |
| GTA VI rolls out worldwide | 13-year wait ends as the game unlocks at midnight local time, starting in New Zealand (Reuters / BBC) |
| Cyclone Akvan nears India | 50,000 evacuated in Odisha, schools shut, red alerts; landfall due Friday (IMD / The Daily Jagran) |
| Australia jobless rate hits 4.9% | 43,500 jobs lost in October, highest unemployment since 2021 (ABS / The Guardian) |
| Islam to be largest faith by 2035 | Pew projects Muslims to outnumber Christians by 2035 (NDTV / Pew Research) |

The footer says "AS REPORTED SO FAR TODAY": this entry was built in the early
hours of 19 November (UTC), from what had been reported by then. The day can
be summed up more completely later — this entry can be improved and resubmitted
before the deadline as the day completes.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```
