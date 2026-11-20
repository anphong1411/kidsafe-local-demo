"""Build the reviewed, text-only sample taxonomy; never browse its domains."""
import csv
from pathlib import Path

GROUPS = {
    'education': '''khanacademy.org wikipedia.org wikibooks.org wikiversity.org wiktionary.org
    britannica.com nationalgeographic.com nasa.gov science.nasa.gov spaceplace.nasa.gov
    noaa.gov climate.gov weather.gov usgs.gov si.edu sierraclub.org
    loc.gov archives.gov gutenberg.org archive.org openlibrary.org
    mit.edu ocw.mit.edu scratch.mit.edu scratchjr.org code.org codingame.com
    python.org docs.python.org raspberrypi.org raspberrypi.com microbit.org
    arduino.cc tinkercad.com geogebra.org desmos.com wolframalpha.com
    mathisfun.com coolmath4kids.com funbrain.com abcya.com starfall.com
    pbskids.org pbslearningmedia.org sesamestreet.org wonderopolis.org
    nationalgeographickids.com kids.nationalgeographic.com dkfindout.com
    bbc.co.uk britishcouncil.org learnenglishkids.britishcouncil.org
    cambridge.org oxfordlearnersdictionaries.com merriam-webster.com
    dictionary.cambridge.org duolingo.com memrise.com busuu.com
    coursera.org edx.org futurelearn.com open.edu oercommons.org
    ck12.org brainpop.com brainpopjr.com discoveryeducation.com
    education.com scholastic.com readworks.org commonlit.org
    readingrockets.org storyweaver.org.in storyberries.com storylineonline.net
    tate.org.uk metmuseum.org moma.org britishmuseum.org louvre.fr
    nhm.ac.uk amnh.org exploratorium.edu calacademy.org
    worldwildlife.org iucn.org unicef.org unesco.org un.org
    who.int fao.org wfp.org worldbank.org ourworldindata.org
    gapminder.org ted.com teded.com ed.ted.com nrich.maths.org
    mathsisfun.com vietnamtourism.gov.vn vnu.edu.vn hust.edu.vn
    hcmus.edu.vn uit.edu.vn hcmut.edu.vn ctu.edu.vn hueuni.edu.vn
    ueh.edu.vn neu.edu.vn ftu.edu.vn hanu.vn hcmue.edu.vn
    moet.gov.vn hocmai.vn olm.vn vio.edu.vn violympic.vn
    ioe.vn vnedu.vn hoc10.vn hanhtrangso.nxbgd.vn''',
    'entertainment': '''youtube.com youtubekids.com netflix.com disneyplus.com
    spotify.com music.youtube.com soundcloud.com deezer.com pandora.com
    zingmp3.vn nhaccuatui.com vtv.vn vtvgo.vn fptplay.vn vieon.vn
    pops.vn pops.tv bilibili.com dailymotion.com vimeo.com twitch.tv
    lego.com disney.com nickelodeon.net cartoonnetwork.com boomerang.com''',
    'social': '''facebook.com instagram.com tiktok.com snapchat.com x.com twitter.com
    threads.net threads.com reddit.com discord.com discord.gg pinterest.com
    tumblr.com linkedin.com mastodon.social bsky.app zalo.me messenger.com
    whatsapp.com telegram.org signal.org viber.com wechat.com line.me''',
    'games': '''roblox.com minecraft.net chess.com lichess.org poki.com crazygames.com
    coolmathgames.com kongregate.com miniclip.com armor games.com
    itch.io store.steampowered.com epicgames.com gog.com ea.com ubisoft.com
    nintendo.com playstation.com xbox.com riotgames.com leagueoflegends.com
    playvalorant.com supercell.com brawlstars.com clashofclans.com''',
    'age_inappropriate': '''amazon.com ebay.com shopee.vn lazada.vn tiki.vn
    aliexpress.com alibaba.com temu.com etsy.com taobao.com''',
    'unclassified': '''github.com gitlab.com bitbucket.org stackoverflow.com
    superuser.com serverfault.com developer.mozilla.org w3.org ietf.org
    rfc-editor.org cloudflare.com microsoft.com apple.com google.com bing.com
    duckduckgo.com brave.com opera.com mozilla.org fastapi.tiangolo.com
    sqlalchemy.org sqlite.org pypi.org npmjs.com docker.com kubernetes.io''',
}
# A domain split by a prose space must not silently become two entries.
GROUPS['games'] = GROUPS['games'].replace('armor games.com', 'armorgames.com')


def build(root=Path('docs/data')):
    root.mkdir(parents=True, exist_ok=True)
    seen = set()
    rows = []
    for category, text in GROUPS.items():
        for domain in text.split():
            if domain in seen:
                raise ValueError(f'Duplicate {domain}')
            seen.add(domain)
            rows.append({'domain': domain, 'category': category,
                         'default_block_6_11': str(category in {'social', 'age_inappropriate'}).lower(),
                         'review_status': 'provisional_manual',
                         'rationale': 'Unsupervised purchasing' if category == 'age_inappropriate' else 'Sample category; parent can override'})
    with (root / 'domain_categories.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f'{len(rows)} unique entries, {len(GROUPS)} categories')


if __name__ == '__main__':
    build()
