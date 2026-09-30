import httpx
import json
from pathlib import Path

species_wiki = [
    ('dorado', 'Salminus_brasiliensis'),
    ('surubi_pintado', 'Pseudoplatystoma_corruscans'),
    ('surubi_atigrado', 'Pseudoplatystoma_reticulatum'),
    ('tararira', 'Hoplias_malabaricus'),
    ('boga', 'Megaleporinus_obtusidens'),
    ('carpa', 'Cyprinus_carpio'),
    ('pati', 'Luciopimelodus_pati'),
    ('manduvi', 'Ageneiosus_inermis'),
    ('pacu', 'Piaractus_mesopotamicus'),
    ('bagre_amarillo', 'Pimelodus_maculatus')
]

out_dir = Path(__file__).resolve().parent.parent / "static" / "species"
out_dir.mkdir(parents=True, exist_ok=True)

headers = {'User-Agent': 'RemansoPescaApp/1.0 (https://remanso.app; pesca@remanso.ar)'}

with httpx.Client(headers=headers, timeout=15.0, follow_redirects=True) as client:
    for sp_id, wiki_title in species_wiki:
        # Check both en.wikipedia and es.wikipedia
        for lang in ['es', 'en']:
            url = f"https://{lang}.wikipedia.org/w/api.php?action=query&titles={wiki_title}&prop=pageimages&format=json&pithumbsize=800"
            try:
                r = client.get(url)
                data = r.json()
                pages = data.get("query", {}).get("pages", {})
                img_url = None
                for pid, pdata in pages.items():
                    if "thumbnail" in pdata:
                        img_url = pdata["thumbnail"]["source"]
                        break
                if img_url:
                    print(f"Found {sp_id} on {lang}.wiki -> {img_url}")
                    # Download image
                    ext = img_url.split(".")[-1].split("?")[0].lower()
                    if ext not in ["jpg", "jpeg", "png", "webp"]:
                        ext = "jpg"
                    file_path = out_dir / f"{sp_id}.{ext}"
                    img_resp = client.get(img_url)
                    if img_resp.status_code == 200 and len(img_resp.content) > 1000:
                        file_path.write_bytes(img_resp.content)
                        print(f"Saved {file_path.name} ({len(img_resp.content)} bytes)")
                        break
            except Exception as e:
                print(f"Error {sp_id} on {lang}: {e}")
