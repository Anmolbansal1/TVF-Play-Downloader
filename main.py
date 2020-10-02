"""
	Usage: python main.py LINK_TO_EPISODE
"""

import os
import sys
import requests
import m3u8
import downloader
import slugify
DOWNLOADER = downloader.Downloader(download_dir='./download')

if len(sys.argv) < 2:
	print("Please provide URL of video to download")

url = sys.argv[1]

if not url.startswith("https://tvfplay.com/episode/"):
	print("Specified URL appears to be invalid or not supported.")
	sys.exit(0)

tvfapi_url = url.replace("https://tvfplay.com/", "https://tvfplay.com/api/")

tvfapi_response = requests.get(tvfapi_url)

if tvfapi_response.status_code != 200:
	print("Error: Unable to fetch ", url)
	sys.exit(0)

try:
	tvfapi_json = tvfapi_response.json()
	account_id = tvfapi_json['episode']['video_account_id']
	video_id = tvfapi_json['episode']['brightcove_video_id']
except:
	print("invalid response recieved.")
	sys.exit(0)

brightcove_url = "https://edge.api.brightcove.com/playback/v1/accounts/%s/videos/%s" % (account_id, video_id)

headers = {
	"Accept" : "application/json;pk=BCpkADawqM26dWgHi4x9Lu_uTkYQJxCTuCaHYLBE4aZP8Rt0mwH90-U1yNE95i08SZaACJN3ZIAsG0Jy8QkazZ8rgTc1\
	ySWLc8VG55XO42u92I2xwV1ObWXczNFBDZv8fXjZ9cIXZqKwocg_1dwa07eFUx3VQyXBEP5hz-WZt9pvog4edZMnUPKnuo2yJ_ZNWLRAMWjV_lTxIuSb0UoxWf9v\
	sfvOvcDVHWAucb5zFpUSLq8wZ7_HWtRj5_tgBVW8vG00k81rxc39Tu-WwB_q2bk6IDYQRh1ZNqpce2dvKl68lpL6mm080lz5zlmhlV7uWNOJWRJvJAFtr2TgUpEq\
	WHEsZah3vbafrc1mZcTlu_4KyzMgnHfZCHsP5ATD9saSiOCTjbzyB3ISMw6m7yGdPGQzRf5Y3bnmeWNKUi_kPGyBoOa6-ik3msfGBeey_PgI7X3YD19DvocW3sk3\
	188weIK5cxcebTpyMycQik6fPkt0jRIfXELfekgxz-WIqKCvGMGs0EnNLJRMSTE46aWSqGCRoAKXBRHNMktKBzM6SfGlTC2inesdzwXIqpxG8NqbnBUxSplboiOJ\
	bz-4MjS16YM_8Pj_UZFs3uFYtSgAyVvNjBnn9Vxv0GRf32U",
	"Origin": "https://tvfplay.com",
	"Referer" : url,
	"User-Agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36",
	}

brightcove_reponse = requests.get(brightcove_url, headers=headers)

video_streams = []

brightcove_json = brightcove_reponse.json()

# extract important data
filename = slugify.slugify(brightcove_json['name'])
for src in brightcove_json['sources']:
	video_streams.append(src)

print('My target is to extract files from this - ', video_streams[0])

m3u8_playlist = m3u8.load(video_streams[0]['src'])
m3u8_obj = m3u8_playlist.iframe_playlists[0]
print('Url to download - ', m3u8_obj.absolute_uri)
print('resolution of this video - ', m3u8_obj.iframe_stream_info.resolution)
print('In file - ', filename)
# for iframe_playlist in m3u8_obj.iframe_playlists:
# 	break

_http_headers = {
			'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/602.4.8 (KHTML, like Gecko)"
						  " Version/10.0.3 Safari/602.4.8"
		}

_http_session = requests.session()
filename += '.ts'
filename = os.path.join(os.getcwd(), filename)
print('Filename is - ', filename)
# resp = _http_session.get(m3u8_obj.absolute_uri, headers=_http_headers, stream=True)
# print(resp)
obj = m3u8.load(m3u8_obj.absolute_uri)
with open(filename, 'ab') as f:
	for i, segment in enumerate(obj.segments):
		segurl = segment.absolute_uri
		seg = requests.get(segurl, headers=_http_headers)
		f.write(seg.content)
		print('Completed segment no.', i)
		if i == 47:
			break
