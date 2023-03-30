#!/usr/bin/env python
import json
import time
import hashlib
import hmac
import requests
import re

class Zing:
    def __init__(self, url, delay = 0) -> None:
        """
            url: input url to crawl
            delay: time to delay
        """
        self.__url = url
        self.__delay = delay
        self.__zing_version = '1.9.12'
        self.__secret_key = "acOrvUS15XRW2o9JksiK1KgQ6Vbds8ZW".encode()
        self.__api_key = 'X5BM3w8N7MKozC0B85o4KMlzLZKhV00y'
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
            self.__set_cookies()
            self.__set_ctime()
            self.__set_craw_url()
                
            res = requests.get(self.__crawl_url, cookies=self.__cookies)

            res_data = res.content.decode()
            items = json.loads(res_data)['data']['items']

            for item in items:
                if not f'https://zingmp3.vn{item["link"]}' in self.__new_urls:
                    self.__new_urls.append(f'https://zingmp3.vn{item["link"]}')

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
                    thumbnail: String,
                    lyric: String
                }
            }
            if Failed, success = False, song = {}
        """
        result = None
        try:
            self.__set_song_id()
            self.__set_cookies()
            self.__set_ctime()
            self.__set_song_key()
            self.__set_info_url()
            res = requests.get(self.__info_url, cookies=self.__cookies)
            res_data = json.loads(res.content)["data"]

            self.__song_name = res_data["title"]
            self.__song_artists = res_data["artistsNames"]
            self.__song_thumbnail = res_data["thumbnailM"]

            if "hasLyric" in res_data:
                self.__set_lyric_url()
                self.__song_lyric = ''
                res = requests.get(self.__lyric_url, cookies=self.__cookies)
                res_data = json.loads(res.content)["data"]["sentences"]
                
                for line in res_data:
                    for word in line["words"]:
                        self.__song_lyric += word["data"] + ' '
                    self.__song_lyric += '\n'
                self.__song_lyric = self.__song_lyric.strip()
            else:
                self.__song_lyric = "No lyric"
            
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

    def __set_cookies(self):
        res = requests.get("https://zingmp3.vn")
        self.__cookies = res.cookies.get_dict()

    def __set_ctime(self):
        self.__ctime = int(time.time())  

    def __set_song_key(self):
        self.__song_key = re.search( '[/]([a-zA-Z0-9]+).html',self.__url).group(1)


    def __set_info_url(self):
        msg = '/api/v2/page/get/song{}'.format(hashlib.sha256(f"ctime={self.__ctime}id={self.__song_key}version={self.__zing_version}".encode()).hexdigest())
        sig = hmac.new(self.__secret_key, msg.encode(), hashlib.sha512).hexdigest()
        self.__info_url = f"https://zingmp3.vn/api/v2/page/get/song?id={self.__song_key}&ctime={self.__ctime}&version={self.__zing_version}&sig={sig}&apiKey={self.__api_key}"



    def __set_lyric_url(self):
        msg = '/api/v2/lyric/get/lyric{}'.format(hashlib.sha256(f"ctime={self.__ctime}id={self.__song_key}version={self.__zing_version}".encode()).hexdigest())
        sig = hmac.new(self.__secret_key, msg.encode(), hashlib.sha512).hexdigest()
        self.__lyric_url = f"https://zingmp3.vn/api/v2/lyric/get/lyric?id={self.__song_key}&ctime={self.__ctime}&version={self.__zing_version}&sig={sig}&apiKey={self.__api_key}"

    
    def __set_craw_url(self):
        self.__set_song_key()
        msg = '/api/v2/recommend/get/songs{}'.format(hashlib.sha256(f"ctime={self.__ctime}id={self.__song_key}version={self.__zing_version}".encode()).hexdigest())
        sig = hmac.new(self.__secret_key, msg.encode(), hashlib.sha512).hexdigest()
        self.__crawl_url = f"https://zingmp3.vn/api/v2/recommend/get/songs?id={self.__song_key}&ctime={self.__ctime}&version={self.__zing_version}&sig={sig}&apiKey={self.__api_key}"


# result = Zing("https://zingmp3.vn/bai-hat/Anh-Chang-Sao-Ma-Khang-Viet/ZW9B7O0C.html").crawl_urls()
# print(result)