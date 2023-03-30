#!/usr/bin/env python3
import json
import time
import hashlib
import requests
import re
from html.parser import HTMLParser
import html

class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = set()

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for attr in attrs:
                if attr[0] == "href":
                    if 'bai-hat' in  attr[1]:   
                        self.hrefs.add(attr[1])



class Nct:
    def __init__(self, url, delay = 0) -> None:
        """
            url: input url to crawl
            delay: time to delay
        """
        self.__url = url
        self.__delay = delay
        self.__new_urls=[]

        time.sleep(self.__delay)

    def crawl_urls(self):
        """
            Return {
                success: Boolean,
                url: String,
                new_urls: List<String>
            }
            
            if failed, success = False, new_urls = []
        """

        result = None
        try:
            self.__set_song_key()
            res = requests.get(f"https://www.nhaccuatui.com/ajax/get-recommend-nextsmarty?key={self.__song_key}&type=song&deviceId=&ref_event=")
            parser = MyHTMLParser()
            parser.feed(json.loads(res.content)["data"]["html"])
            self.__new_urls = parser.hrefs
            result = {
                "success":True,
                "url":self.__url,
                "new_urls":self.__new_urls
            }
        except:
            result = {
                "success":False,
                "url":self.__url,
                "new_urls": []
            }

        return result


    def crawl_song(self):
        """
            Return {
                success: Boolean,
                url: String,
                song: {
                    id: String,
                    name: String,
                    artists: String,
                    thubnail:String,
                    lyric: String
                }
            }
            if Failed, success = False, song = {}
        """

        result = None
        try:
            self.__set_song_id()

            res = requests.get(self.__url)
            res_data = res.content.decode()
            title = re.search(f"<title>(.+)</title>", res_data).group(1)

            self.__song_name = title.split("-")[0].strip()
            self.__song_artists = title.split("-")[1][1:]

            lyric = re.findall(r'<br />(.+)\n', res_data)
            self.__song_lyric = html.unescape("\n".join(lyric))
            self.__song_thumbnail = re.search(r"(https://avatar.+jpg)", res_data).group(1)




            
            if self.__song_name == '':
                self.__song_name == "No name"
            if self.__song_artists == '':
                self.__song_artists == 'No artists'
            if self.__song_lyric == '':
                self.__song_lyric = "No lyric"
            if self.__song_thumbnail == '':
                self.__song_thumbnail = "No thumbnail"
            

            result = {
                "success": True,
                "url": self.__url,
                "song":{
                        "id": self.__song_id,
                        "name": self.__song_name,
                        "artists": self.__song_artists,
                        "thumbnail": self.__song_thumbnail,
                        "lyric": self.__song_lyric
                    }
            }
        except:
            result = {
                "success": False,
                "url": self.__url,
                "song":{}
            }

        
        return result
    
    
    def __set_song_id(self):
        self.__song_id = hashlib.md5(self.__url.encode()).hexdigest()

    def __set_song_key(self):
        self.__song_key = self.__url.split(".")[-2]

# result = Nct('https://www.nhaccuatui.com/bai-hat/vi-anh-dau-co-biet-madihu-ft-vu.8qjZjYGWp4U8.html').crawl_song()
# print(result)
