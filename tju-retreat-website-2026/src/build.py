"""Builds index.html from template.html and the images in this folder.

    python3 src/build.py

Edit SESSIONS (names and times) and DETAILS (text shown when someone points at a session) below.
No packages needed beyond Python 3."""
import base64, datetime, html, math, os, sys
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'index.html')
esc = lambda s: html.escape(s, quote=True)
data = lambda path, mime: f'data:{mime};base64,' + base64.b64encode(open(os.path.join(HERE, path), 'rb').read()).decode()

TITLE = '2026 Enterprise Medical Physics Retreat'
LOCATION = 'Bluemle Life Sciences Building, Room 105, 233 S. 10th Street, Philadelphia, PA 19107'
MAPS = 'https://www.google.com/maps/search/?api=1&query=' + quote('Bluemle Life Sciences Building, 233 S 10th St, Philadelphia, PA 19107', safe='')

VALDES = dict(role='Keynote speaker', tone='cool', photo=data('valdes.jpg', 'image/jpeg'), w=512, h=512, name='Gilmer Valdes', cred='PhD, DABR',
              talk='The First Ever Oncology-Wide Treatment Planning System and Its Implications for Medical Physicists',
              links=[('LinkedIn', 'https://www.linkedin.com/in/gilmer-valdes-02066725'), ('OncoBrain.ai', 'https://oncobrain.ai')])
GODLEY = dict(role='Featured speaker', tone='warm', photo=data('godley.jpg', 'image/jpeg'), w=760, h=760, name='Lyn Godley', cred='MFA',
              talk='A Deep Dive into Calm at Ravenhill Chapel',
              links=[('LinkedIn', 'https://www.linkedin.com/in/lyn-godley-7bb96629'), ('lyngodley.com', 'https://lyngodley.com'),
                     ('Jefferson', 'https://www.jefferson.edu/academics/colleges-schools-institutes/architecture-design-engineering/'
                                   'research-centers/jefferson-center-of-immersive-arts-for-health/about/godley.html')])

# minutes after 1:00 PM Eastern. The afternoon is 255 minutes and half a turn of the dial.
SESSIONS = [
    (0, 15, 'Welcome and overview', None),
    (15, 60, VALDES['name'], VALDES),
    (60, 90, 'Hackathon presentations', None),
    (90, 105, 'Coffee break', 'quiet'),
    (105, 150, GODLEY['name'], GODLEY),
    (150, 180, 'Point / Counterpoint', None),
    (180, 210, 'Unknown unknowns panel', None),
    (210, 240, 'Pub quiz', None),
    (240, 255, 'Awards and closing remarks', None),
]
SPAN = 255
A0 = 30                 # 1:00 sits at the 1 o'clock position; the hand moves 0.5 degrees a minute, like a real hour hand
DEG = 0.5

def clock(m):
    return f'{1 + m // 60}:{m % 60:02d}'
def iso(m):
    return f'2026-11-13T{13 + m // 60:02d}:{m % 60:02d}-05:00'

def icon(paths, cls='icon'):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true" focusable="false">{paths}</svg>'
ICON_EXT = icon('<path d="M14 4h6v6M20 4l-8.5 8.5M18 14v4.5a1.5 1.5 0 0 1-1.5 1.5h-11A1.5 1.5 0 0 1 4 18.5v-11A1.5 1.5 0 0 1 5.5 6H10"/>')
ICON_CHEV = icon('<path d="M6 9l6 6 6-6"/>', 'icon cal__chev')
FAVICON = 'data:image/svg+xml,' + quote('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><rect width="24" height="24" fill="#F1ECE3"/>'
    '<path d="M12 3A9 9 0 0 1 12 21" fill="none" stroke="#1E2B38" stroke-width="2"/><path d="M12 12L17.5 6" stroke="#7FA1BC" stroke-width="3" stroke-linecap="round"/></svg>', safe='')

# ---------- calendar ----------
details = '\n'.join(['Jefferson Medical Physics division retreat.', LOCATION, '', 'Agenda (Eastern time)'] +
    [f"{clock(a)} " + (f"{t['name']}, {t['cred']}. {t['talk']}" if isinstance(t, dict) else n) for (a, b, n, t) in SESSIONS])
qs = lambda d: '&'.join(f'{k}={quote(v, safe="")}' for k, v in d.items())
GOOGLE = 'https://calendar.google.com/calendar/render?' + qs({'action': 'TEMPLATE', 'text': TITLE, 'dates': '20261113T180000Z/20261113T221500Z', 'details': details, 'location': LOCATION})
OUTLOOK = 'https://outlook.office.com/calendar/0/deeplink/compose?' + qs({'path': '/calendar/action/compose', 'rru': 'addevent', 'subject': TITLE,
    'startdt': '2026-11-13T18:00:00Z', 'enddt': '2026-11-13T22:15:00Z', 'location': LOCATION, 'body': details})
def ics_escape(s): return s.replace('\\', '\\\\').replace(';', '\\;').replace(',', '\\,').replace('\n', '\\n')
def fold(line, limit=75):
    out, cur, n = [], '', 0
    for ch in line:
        w = len(ch.encode('utf-8'))
        if n + w > limit: out.append(cur); cur, n = ' ' + ch, 1 + w
        else: cur += ch; n += w
    out.append(cur); return '\r\n'.join(out)
stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
ics = '\r\n'.join(fold(l) for l in ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Jefferson Medical Physics//2026 Retreat//EN', 'CALSCALE:GREGORIAN', 'METHOD:PUBLISH',
    'BEGIN:VEVENT', 'UID:2026-enterprise-medical-physics-retreat@jefferson-medical-physics', f'DTSTAMP:{stamp}', 'DTSTART:20261113T180000Z', 'DTEND:20261113T221500Z',
    'SUMMARY:' + ics_escape(TITLE), 'LOCATION:' + ics_escape(LOCATION), 'DESCRIPTION:' + ics_escape(details), 'END:VEVENT', 'END:VCALENDAR']) + '\r\n'
ICS = 'data:text/calendar;charset=utf-8,' + quote(ics, safe='')
CAL = (f'<details class="cal" data-cal><summary class="util">Add to calendar{ICON_CHEV}</summary><div class="cal__menu">'
       f'<a class="cal__item" href="{esc(OUTLOOK)}" target="_blank" rel="noopener noreferrer">Outlook<span class="cal__hint">Microsoft 365</span></a>'
       f'<a class="cal__item" href="{esc(GOOGLE)}" target="_blank" rel="noopener noreferrer">Google Calendar<span class="cal__hint">Google account</span></a>'
       f'<a class="cal__item" href="{esc(ICS)}" download="enterprise-medical-physics-retreat-2026.ics" data-ics hidden>Apple Calendar and others<span class="cal__hint">.ics file</span></a></div></details>')

# ---------- the half clock (stage units are pixels of the 1200px render) ----------
CX, CY, R = 600, 600, 431
VX, VY, VW, VH = 190, 110, 900, 950
def pol(a, r):
    t = math.radians(a); return CX + r * math.sin(t), CY - r * math.cos(t)
def arc(a0, a1, r):
    p0, p1 = pol(a0, r), pol(a1, r)
    return f'M{p0[0]:.2f} {p0[1]:.2f}A{r} {r} 0 0 1 {p1[0]:.2f} {p1[1]:.2f}'

minor, major = [], []
for a in range(0, 181, 6):                        # a tick every minute-mark of the clock face, 12 to 6
    hour = a % 30 == 0
    p0, p1 = pol(a, R - (34 if hour else 14)), pol(a, R)
    (major if hour else minor).append(f'M{p0[0]:.1f} {p0[1]:.1f}L{p1[0]:.1f} {p1[1]:.1f}')
numerals = ''.join(f'<text class="num" x="{pol(a, R - 74)[0]:.1f}" y="{pol(a, R - 74)[1]:.1f}">{n}</text>'
                   for a, n in zip(range(0, 181, 30), ['12', '1', '2', '3', '4', '5', '6']))
arcs = ''
for (a, b, n, t) in SESSIONS:
    tone = 'quiet' if t == 'quiet' else ('cool' if isinstance(t, dict) and t['tone'] == 'cool' else 'warm' if isinstance(t, dict) else 'plain')
    arcs += f'<path class="arc arc--{tone}" d="{arc(A0 + a * DEG + 0.35, A0 + b * DEG - 0.35, R + 20)}"/>'

STAGE = f"""          <svg viewBox="{VX} {VY} {VW} {VH}" focusable="false" role="presentation">
            <image href="{data('back.webp', 'image/webp')}" x="0" y="0" width="1200" height="1200"/>
            <path class="ring ring--ghost" d="M{CX} {CY - R}A{R} {R} 0 0 0 {CX} {CY + R}"/>
            <path class="ring" d="M{CX} {CY - R}A{R} {R} 0 0 1 {CX} {CY + R}"/>
            <path class="tick" d="{''.join(minor)}"/><path class="tick tick--hour" d="{''.join(major)}"/>
            {arcs}
            <path class="elapsed" d=""/>
            <g class="hand" transform="rotate(0 {CX} {CY})"><image href="{data('rot.webp', 'image/webp')}" x="0" y="0" width="1200" height="1200"/></g>
            <image href="{data('front.webp', 'image/webp')}" x="0" y="0" width="1200" height="1200"/>
            {numerals}
            <rect class="hit" x="{CX}" y="{VY}" width="{VX + VW - CX}" height="{VH}"/>
          </svg>"""

# ---------- agenda rows ----------
# DETAILS: anything you want to appear when someone points at a session. The two talks already have their titles.
# When the point/counterpoint topics, the panel line-up, etc. are known, add them here, keyed by the session's name.
DETAILS = {
    'Welcome and overview': '',
    'Hackathon presentations': '',
    'Coffee break': '',
    'Point / Counterpoint': '',
    'Unknown unknowns panel': '',
    'Pub quiz': '',
    'Awards and closing remarks': '',
}
rows = []
for (a, b, n, t) in SESSIONS:
    talk = isinstance(t, dict)
    shown = f"{t['name']}, {t['cred']}" if talk else n
    role = t['role'] if talk else ''
    detail = t['talk'] if talk else DETAILS.get(n, '')
    role_html = f'<span class="row__role">{esc(role)}</span>' if talk else ''
    rows.append(f'            <li class="row{" row--talk" if talk else ""}" data-start="{a}" data-end="{b}" data-name="{esc(shown)}" data-range="{clock(a)}\u2013{clock(b)}" data-role="{esc(role)}" data-detail="{esc(detail)}">'
                f'<span class="row__time"><time datetime="{iso(a)}">{clock(a)}</time>&ndash;<time class="row__end" datetime="{iso(b)}">{clock(b)}</time><span class="vh"> PM</span></span>'
                f'<span class="row__name">{role_html}{esc(shown)}</span></li>')

# ---------- speakers ----------
def speaker(sp):
    links = ''.join(f'<a href="{esc(u)}" target="_blank" rel="noopener noreferrer">{esc(t)}<span class="vh"> ({esc(sp["name"])}, opens in a new tab)</span></a>' for t, u in sp['links'])
    return f'''      <article class="speaker speaker--{sp['tone']}" aria-label="{sp['name']}">
        <div class="speaker__art">
          <img class="speaker__photo" src="{sp['photo']}" width="{sp['w']}" height="{sp['h']}" alt="Portrait of {sp['name']}">
        </div>
        <h2 class="speaker__name"><span class="speaker__role">{sp['role']}</span>{sp['name']}, {sp['cred'].replace(', ', ',&thinsp;')}</h2>
        <p class="speaker__talk">{sp['talk']}</p>
        <p class="speaker__links">{links}</p>
      </article>'''

page = open(os.path.join(HERE, 'template.html'), encoding='utf-8').read()
for token, value in {
    '%%FAVICON%%': FAVICON, '%%MAPS%%': esc(MAPS), '%%CAL%%': CAL, '%%ICON_EXT%%': ICON_EXT, '%%STAGE%%': STAGE, '%%ROWS%%': '\n'.join(rows),
    '%%SPEAKERS%%': '\n'.join([speaker(VALDES), speaker(GODLEY)]),
    '%%SPAN%%': str(SPAN), '%%A0%%': str(A0), '%%CX%%': str(CX), '%%CY%%': str(CY), '%%R%%': str(R), '%%VX%%': str(VX), '%%VY%%': str(VY), '%%VW%%': str(VW),
}.items():
    assert token in page, token
    page = page.replace(token, value)
assert '%%' not in page, 'unreplaced token'
open(OUT, 'w', encoding='utf-8').write(page)
print('wrote', OUT, f'{len(page.encode()) / 1024:.0f} KB')
