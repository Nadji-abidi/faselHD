#! python
import requests
import os, sys
import re
from bs4 import BeautifulSoup as bs
import random
from vsdownload import vsdownload


soup = lambda url : bs(requests.get(url).content,"html.parser")

def random_user_agent(file=os.path.join(os.path.dirname(__file__),'user_agents.txt')):
	with open(file, "r") as f:
		lines = f.readlines()
		user_agent = random.choice(lines).replace("\n", "")
		f.close()
	return str(user_agent)

def search(user_input):
    search_URL = "https://www.faselhd.pro/?s=" + user_input.strip()
    search_result = soup(search_URL)
    results = search_result.select(".postDiv")
    tit_url = [(i.select_one(".h1").text, i.a["href"]) for i in results]
    return dict(tit_url)

def display_results(lists):
    choises = list(lists.keys())
    for i in range(len(choises)):
        print(f"{i + 1}. \x1b[33m{choises[i]}\x1b[0m")
    choise = int(input("\n\x1b[41m\x1b[37mChoose one \x1b[0m : "))
    return choises[choise - 1]

def seasons(seasonList):
    seasons_num = dict([(i.select_one(".title").text,i.div["data-href"]) for i in seasonList])
    choise = display_results(seasons_num)
    return "https://www.faselhd.pro/?p=" + seasons_num[choise]

def select_episodes(media_url):
    media_htm = soup(media_url)
    seasons_list = media_htm.select("#seasonList > div")
    if seasons_list : media_htm = soup(seasons(seasons_list))
    episodes = [ i["href"] for i in media_htm.select(".epAll a") ]
    if not(episodes) : return [media_url]
    else :
        pattern = r"[%d8%a7%d9%84%d8%ad%d9%84%d9%82%d8%a9]-(\d+)"
        try : episodes_num = [int("".join(re.findall(pattern,i))) for i in episodes]
        except ValueError : episodes_num = list(range(1,len(episodes) + 1))
        print(f"Episodes : {episodes_num[0]}-{episodes_num[-1]}")
        start,end = [ input(f"\n {i} EP : ") for i in ("Start on","End in") ]
        sel = lambda i,opt : opt if i == "" else episodes_num.index(int(i))
        return episodes[sel(start,0):sel(end,len(episodes))]

def getDirectLink(site) : 
    headers = {'User-Agent': f'{random_user_agent()}'}
    return requests.get(site,headers=headers).text
    
def download(links, folder):
    os.makedirs(folder)
    for link in links:
        link = soup(link)
        title = link.select_one(".h3").text
        title = " ".join(re.findall(r"\d+|\w+",title)) + ".mp4"
        print(f"\n\x1b[41m\x1b[37mDownloading \x1b[0m ===> {title}")
        link = getDirectLink(link.find("iframe")["src"])
        videoURL = re.findall("\"file\":\"(.*\.m3u8)\"",link)[0].replace("\\","")
        vsdownload.save(videoURL, output=f"{folder}/{title}", max_quality=True)

def main() :
    main_page = search(input("Search : "))
    while main_page == {} : 
        print("\n\n----- \x1b[41mNo Results\x1b[0m ----\n\n")
        main_page = search(input("Search : "))
    selected = display_results(main_page)
    episodes = select_episodes(main_page[selected])
    download(episodes, os.path.join(os.getcwd(),selected))

try : main()
except KeyboardInterrupt : 
    print("\n\nExit .....")
    sys.exit()
