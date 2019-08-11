import os
import ssl
import sys
import os.path
import urllib
import urllib.request
from importlib import reload
from bs4 import BeautifulSoup

web_prefix = "https://www.ibiblio.org/eldritch/ac/jr/"
num_stories = 202
for story_id in range(1,num_stories):
	
	url = web_prefix+"{:03d}.htm".format(story_id)
	print(f"I: .. opening the site \"{url}\"")

	myssl = ssl.SSLContext()
	html = urllib.request.urlopen(url,context=myssl).read()
	soup = BeautifulSoup(html,'html.parser',from_encoding="iso-8859-1")
	
	the_text = soup.get_text()
	if not the_text:
		print(f"E: .. Could not read anything from story id {story_id}")
		continue

	the_text = the_text.strip()
	split_text = the_text.split('\n')

	text_title = str(story_id)
	
	if not os.path.isdir('my_stories'):
		os.mkdir('my_stories')
	file_name = os.path.join('my_stories',text_title+".txt")

	try:
		print(f'I: .. creating file {file_name}')
	except:
		file_name = os.path.join('my_stories',f"{story_id}.txt")
		print(f"I: .. unable to decode title so setting name to {file_name}")
	the_text = '\n'.join(split_text)

	# if os.path.isfile(file_name):
	#     print(f"I: .. File {file_name} is already there, please verify before overwriting. Skipping for now")
	#     continue
	print(f'I: .. writing to file {file_name}')
	with open(file_name,'wb') as outfile:
		outfile.write(the_text.encode('ascii','ignore'))
