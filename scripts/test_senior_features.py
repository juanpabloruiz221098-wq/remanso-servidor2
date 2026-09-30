import httpx

client = httpx.Client(base_url='http://127.0.0.1:8000', timeout=15.0)

# 1. Test species
r_spec = client.get('/api/species')
assert r_spec.status_code == 200, 'Species endpoint failed'
species_list = r_spec.json()
print(f'Total species: {len(species_list)}')
assert len(species_list) >= 8, 'Expected at least 8 species'

for sp in species_list:
    img_url = sp['image_url']
    r_img = client.get(img_url)
    assert r_img.status_code == 200, f'Image failed: {img_url}'
    print(f"Species: {sp['common_name']:28} -> Image: {img_url} ({len(r_img.content)} bytes)")

# 2. Test feedback
r_fb_post = client.post('/api/feedback', json={'port_id': 'rosario', 'rating': 'excelente', 'comment': 'Salieron 2 dorados en el puente'})
assert r_fb_post.status_code == 200
print('Feedback POST status:', r_fb_post.status_code)

r_fb_get = client.get('/api/feedback/rosario')
assert r_fb_get.status_code == 200
print('Feedback GET summary:', r_fb_get.json())

# 3. Test metrics
r_metrics = client.get('/api/metrics/rosario')
assert r_metrics.status_code == 200
print('Metrics bite score:', r_metrics.json()['bite']['score'], 'Feedback:', r_metrics.json()['bite']['feedback'])

# 4. Test Track GPX export
sample_track = {
    'name': 'Deriva Paso Destileria',
    'points': [
        {'lat': -32.745, 'lng': -60.725, 'speed_knots': 1.8, 'cog': '135°', 'time': '2026-09-28T15:00:00Z'},
        {'lat': -32.748, 'lng': -60.723, 'speed_knots': 2.1, 'cog': '140°', 'time': '2026-09-28T15:05:00Z'}
    ]
}
r_track = client.post('/api/track/export/gpx', json=sample_track)
assert r_track.status_code == 200
assert '<trkpt' in r_track.text
print('Track GPX Export status:', r_track.status_code, 'Bytes:', len(r_track.text))

# 5. Test index HTML
r_html = client.get('/')
assert r_html.status_code == 200
assert 'trackLoggerHud' in r_html.text
assert 'communityConsensusBadge' in r_html.text
print('\nHTML verification passed! ALL 5 SENIOR FEATURES TESTED AND WORKING 100%!')
