import re, json
from PIL import Image
s=open('project/Main.dc.html').read()
helm=s[s.index('<helmet>')+8:s.index('</helmet>')]
css=helm[helm.index('<style>')+7:helm.index('</style>')]
body=s[s.index('</helmet>')+9:s.index('</x-dc>')].strip()
words=['Tap','Chip','Swipe','Credit','Debit','Mobile wallets','Tableside','Counter','Automated integration']
data={'marq':[{'t':w} for w in words+words],
'steps':[{'n':'1','title':'Send a recent statement','body':'One month of your current processing statement is enough to start.'},{'n':'2','title':'Get a side-by-side','body':'We mark every fee line and put our quote next to it, in plain numbers.'},{'n':'3','title':'Terminals arrive configured','body':'Devices show up set for your business and connected to your point of sale.'},{'n':'4','title':'Take your first tap','body':'We are there for the first service and reachable after it.'}]}
def loop(m):
    out=''
    for it in data[m.group(1)]:
        out+=re.sub(r'\{\{\s*'+m.group(2)+r'\.(\w+)\s*\}\}',lambda k:it[k.group(1)],m.group(3))
    return out
body=re.sub(r'<sc-for list="\{\{(\w+)\}\}" as="(\w+)"[^>]*>(.*?)</sc-for>',loop,body,flags=re.S)
assert '{{' not in body and 'sc-for' not in body
body=body.replace('/_blob/7f3cb7523529fe63220e6a1040ab3591','assets/logo.png').replace('/_blob/e01505bb1f090138734302c2bf98dfc4','assets/logo-anim.gif')
assert '_blob' not in body
# form wiring
def one(a,b):
    global body
    assert body.count(a)==1,(a,body.count(a)); body=body.replace(a,b)
one('<form style="','<form action="lead.php" method="post" style="')
one('id="f-name" type="text"','id="f-name" name="name" type="text" required maxlength="120"')
one('id="f-biz" type="text"','id="f-biz" name="business" type="text" required maxlength="160"')
one('id="f-email" type="email"','id="f-email" name="email" type="email" required maxlength="160"')
one('id="f-phone" type="tel"','id="f-phone" name="phone" type="tel" maxlength="40"')
one('<select id="f-vol"','<select id="f-vol" name="volume"')
one('<button type="button"','<div style="position: absolute; left: -9999px" aria-hidden="true"><label for="f-web">Leave this empty</label><input id="f-web" name="website" type="text" tabindex="-1" autocomplete="off"></div>\n<p style="margin: 0; font-size: 14px; color: #4A4F57">We use these details only to reply to your request.</p>\n<button type="submit"')
one('<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 4px 6px">','<div class="navlinks" style="display: flex; flex-wrap: wrap; align-items: center; gap: 4px 6px">')
one('clamp(46px, 6.6vw, 96px)','clamp(42px, 5.6vw, 80px)')
css+='\n@media (max-width:680px){.navlinks a:not(.btn-gold){display:none} }\nhtml{scroll-behavior:smooth}\n.no-intro .intro{display:none}\nimg{max-width:100%}\n'
head='''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<meta name="description" content="Paiment sets up card processing and point of sale for restaurants, shops and service businesses: terminals, tableside tap, automated integration and a rate review.">
<meta property="og:title" content="Paiment: card processing and point of sale">
<meta property="og:description" content="Terminals, tableside tap, automated integration and a rate reviewed against your current statement.">
<meta property="og:type" content="website">
<link rel="icon" type="image/png" href="assets/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400..700&family=Instrument+Sans:wght@400;500;600&display=swap">
<link rel="stylesheet" href="assets/site.css">
%s</head>
'''
ld='<link rel="canonical" href="https://paiment.cc/">\n<script type="application/ld+json">'+json.dumps({"@context":"https://schema.org","@type":"ProfessionalService","name":"Paiment","url":"https://paiment.cc/","logo":"https://paiment.cc/assets/logo.png","telephone":"+1-877-334-7570","email":"info@paiment.cc","description":"Card processing and point of sale setup for restaurants, shops and service businesses.","address":{"@type":"PostalAddress","streetAddress":"18 King St E, Suite 1400","addressLocality":"Toronto","addressRegion":"ON","postalCode":"M5C 1C4","addressCountry":"CA"},"areaServed":["CA","US"]})+'</script>\n'
open('site/sitemap.xml','w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n<url><loc>https://paiment.cc/</loc></url>\n</urlset>\n')
open('site/robots.txt','w').write('User-agent: *\nDisallow: /admin/\nSitemap: https://paiment.cc/sitemap.xml\n')
intro_js='<script>try{if(sessionStorage.getItem("paimentIntro")){document.documentElement.className+=" no-intro"}else{sessionStorage.setItem("paimentIntro","1")}}catch(e){}</script>\n'
open('site/assets/site.css','w').write(css.strip()+'\n')
open('site/index.html','w').write(head%('Paiment | Card processing and point of sale',ld+intro_js)+'<body>\n'+body+'\n</body>\n</html>\n')
# thanks page: reuse header + footer
hdr=body[body.index('<header '):body.index('</header>')+9].replace('href="#','href="index.html#')
ftr=body[body.index('<footer '):body.index('</footer>')+9].replace('href="#','href="index.html#')
root=body[:body.index('>')+1]
ty=root+'\n'+hdr+'''
<main style="max-width: 760px; margin: 0 auto; box-sizing: border-box; padding: 96px 24px 120px">
<h1 style="margin: 0 0 20px; font-family: 'Bricolage Grotesque', sans-serif; font-weight: 650; font-size: clamp(40px, 6vw, 72px); line-height: 1; letter-spacing: -0.03em">Request received.</h1>
<p style="margin: 0 0 32px; font-size: 20px; color: #4A4F57">Thanks. We will email you to ask for a recent processing statement, then come back with a side-by-side comparison.</p>
<a href="index.html" class="btn-gold" style="display: inline-block; background: linear-gradient(160deg, #FFD45C, #FF8A2A); color: #23262B; text-decoration: none; padding: 16px 26px; border-radius: 14px; font-weight: 600; font-size: 18px">Back to the homepage</a>
</main>
'''+ftr+'\n</div>'
open('site/thanks.html','w').write(head%('Request received | Paiment','<meta name="robots" content="noindex">\n')+'<body>\n'+ty+'\n</body>\n</html>\n')
im=Image.open('site/assets/logo.png').convert('RGBA').crop((0,0,575,727))
sq=Image.new('RGBA',(727,727),(0,0,0,255)); sq.paste(im,(76,0),im); sq.resize((128,128),Image.LANCZOS).save('site/assets/favicon.png')
print(len(body))
