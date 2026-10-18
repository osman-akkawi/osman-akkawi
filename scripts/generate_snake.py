"""Generate an animated SVG using the public GitHub contribution calendar."""
from html.parser import HTMLParser
from pathlib import Path
from datetime import date
import sys
import urllib.request

class Calendar(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells = []
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if 'data-date' in d and 'data-level' in d:
            _, row, col = d['id'].rsplit('-', 2)
            self.cells.append((int(col), int(row), int(d['data-level']), d['data-date']))

def generate(html):
    calendar = Calendar()
    calendar.feed(html)
    assert len(calendar.cells) >= 300, 'Incomplete calendar; keeping existing image'
    cols = max(c[0] for c in calendar.cells)+1
    route = [(c,r) for c in range(cols) for r in (range(7) if c%2==0 else range(6,-1,-1))]
    pts = [(20+c*15,38+r*15) for c,r in route]
    pts += [(20+cols*15,pts[-1][1]),(20+cols*15,24),(5,24),(5,38),pts[0]]
    dist = [0]
    for a,b in zip(pts,pts[1:]):dist.append(dist[-1]+abs(a[0]-b[0])+abs(a[1]-b[1]))
    path = 'M'+' L'.join(f'{x},{y}' for x,y in pts)
    palette = ['#161b22','#0e4429','#006d32','#26a641','#39d353']
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {35+cols*15} 166" role="img" aria-labelledby="title desc">',
      '<title id="title">Osman Akkawi contribution snake</title><desc id="desc">An animated green snake eats contribution squares, grows, and resets each loop.</desc>',
      '<rect width="100%" height="166" rx="14" fill="#0d1117"/>',f'<defs><path id="route" d="{path}"/></defs>',
      '<text x="15" y="16" fill="#8b949e" font-family="sans-serif" font-size="10">OSMAN AKKAWI / CONTRIBUTION SNAKE</text>']
    index = {p:i for i,p in enumerate(route)}
    for c,r,level,day in calendar.cells:
        t = max(.001,min(.97,(dist[index[(c,r)]]/dist[-1]-.025)%1))
        out.append(f'<rect x="{14.5+c*15}" y="{32.5+r*15}" width="11" height="11" rx="2" fill="{palette[level]}"><title>{day}: contribution level {level}</title>')
        if level:out.append(f'<animate attributeName="fill" values="{palette[level]};{palette[level]};#161b22;#161b22" keyTimes="0;{t:.5f};{t+.001:.5f};1" dur="60s" repeatCount="indefinite"/>')
        out.append('</rect>')
    for i in range(18):
        out.append(f'<circle r="{2.5+i*.18:.2f}" fill="{("#238636" if i<8 else "#3fb950")}"><animateMotion dur="60s" begin="{-1.5+(18-i)*.065:.3f}s" repeatCount="indefinite"><mpath xlink:href="#route"/></animateMotion>')
        if i<7:out.append(f'<animate attributeName="opacity" values="0;0;1;1" keyTimes="0;{.05+i*.035:.3f};{.06+i*.035:.3f};1" dur="60s" repeatCount="indefinite"/>')
        out.append('</circle>')
    out.append('<g><animateMotion dur="60s" begin="-1.5s" repeatCount="indefinite" rotate="auto"><mpath xlink:href="#route"/></animateMotion>')
    out.append('<path d="M5,0 H12 M10,0 L13,-2 M10,0 L13,2" stroke="#f97583" stroke-width="1.2" fill="none"><animate attributeName="opacity" values="0;1;0;0" dur="1.3s" repeatCount="indefinite"/></path><rect x="-6" y="-5.7" width="14" height="11.4" rx="5" fill="#7ee787" stroke="#238636"/><circle cx="3.4" cy="-3" r="1.8" fill="white"/><circle cx="3.4" cy="3" r="1.8" fill="white"/><circle cx="4" cy="-3" r=".9" fill="#0d1117"/><circle cx="4" cy="3" r=".9" fill="#0d1117"/></g>')
    out.append(f'<text x="15" y="155" fill="#8b949e" font-family="sans-serif" font-size="10">Public contribution snapshot / {date.today().isoformat()}</text></svg>')
    output = Path('assets/contribution-snake.svg')
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(''.join(out))
    print(f'Generated {len(calendar.cells)} contribution cells')

if __name__ == '__main__':
    if len(sys.argv)>1: html=Path(sys.argv[1]).read_text()
    else:
        req=urllib.request.Request('https://github.com/users/osman-akkawi/contributions',headers={'User-Agent':'contribution-snake-generator'})
        with urllib.request.urlopen(req,timeout=30) as response:html=response.read().decode()
    generate(html)
