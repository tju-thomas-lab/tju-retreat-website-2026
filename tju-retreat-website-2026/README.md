# TJU Retreat 2026

Site for the 2026 Enterprise Medical Physics Retreat: Friday, November 13, 2026, 1:00 to 5:15 PM Eastern,
Bluemle Life Sciences Building, Room 105, Philadelphia.

`index.html` is the whole site: one file, images included. There is nothing to install or bundle.

## Deploy with GitHub Pages

Settings > Pages > Build and deployment > Source: **Deploy from a branch**, branch `main`, folder `/ (root)`.
The site will be at `https://tju-thomas-lab.github.io/tju-retreat-website-2026/`.

## Editing

The page is generated from `src/`. To change the agenda, speakers or wording:

1. Edit `src/build.py`:
   - `SESSIONS` holds each session's start and end (minutes after 1:00 PM) and its name.
   - `DETAILS` holds the text shown when someone points at a session. The two talks already have their titles;
     the other sessions are blank until you add something.
   - `VALDES` and `GODLEY` hold the speakers' names, credentials, talk titles and links.
2. Run `python3 src/build.py` (Python 3 only, no packages). This rewrites `index.html`.
3. Commit `index.html` and the files you changed.

The dial is a real clock face and the gantry turns with the hour hand, so 1:00 sits at the 1 o'clock position
and 5:00 at the 5. Session times can change freely **inside 1:00 to 5:15 PM**. If the day's overall start or end
moves, that is not a single setting: the dial span (`SPAN`, `A0`), the date lines in `src/template.html`, the
`START` time in its script, and the calendar times in `src/build.py` all need to change together.

To preview the "on the day" behaviour, add a time to the address, for example
`index.html?now=2026-11-13T14:10:00-05:00`.

## Notes

- The machine is a render of a Varian TrueBeam 3D model (CGMood). The source model file is **not** in this repository.
  The renders carry the model's own "trueBEAM" and "VARIAN" markings. Confirm the model licence and that the markings
  are acceptable before making the site public.
- Fonts (Libre Caslon, Public Sans) load from Google Fonts. The page falls back to Georgia if they can't load.
- `src/*.webp` are the three render layers (fixed stand, rotating gantry, couch). `src/*.jpg` are the toned portraits.
