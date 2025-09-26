import json
import requests
from com.github.catvod import Proxy
from abc import ABCMeta, abstractmethod
from lxml import etree

class Spider(metaclass=ABCMeta):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance:
            return cls._instance
        cls._instance = super().__new__(cls)
        return cls._instance

    @abstractmethod
    def init(self, extend=""):
        pass

    def fetch(self, url, params=None, headers=None, timeout=5):
        rsp = requests.get(url, params=params, headers=headers, timeout=timeout)
        rsp.encoding = 'utf-8'
        return rsp.text

    def typeMapping(self, t):
        mapping = {
            "动作片": "电影", "喜剧片": "电影", "爱情片": "电影",
            "科幻片": "电影", "恐怖片": "电影", "战争片": "电影",
            "纪录片": "电影", "动画片": "电影", "剧情片": "电影",
            "国产剧": "电视剧", "港台剧": "电视剧", "日韩剧": "电视剧",
            "欧美剧": "电视剧", "海外剧": "电视剧",
            "大陆综艺": "综艺", "港台综艺": "综艺", "日韩综艺": "综艺",
            "欧美综艺": "综艺",
            "国产动漫": "动漫", "日本动漫": "动漫", "欧美动漫": "动漫",
            "动画": "动漫"
        }
        return mapping.get(t, t)

class DemoSpider(Spider):
    def init(self, extend=""):
        # 指向你在 GitHub 上的 sites.json Raw URL
        self.sites_url = "https://raw.githubusercontent.com/JSwong41/tvbox-spiders/refs/heads/main/assets/sites.json"
        self.sites = json.loads(self.fetch(self.sites_url))['sites']

    def homeContent(self, filter=None):
        classes = []
        for site in self.sites:
            classes.append({"type_id": site['key'], "type_name": site['name']})
        return {"class": classes}

    def categoryContent(self, tid, pg, filter, extend):
        site = next((s for s in self.sites if s['key'] == tid), None)
        if not site:
            return {"list": []}
        url = site['api']
        try:
            data = json.loads(self.fetch(url))
            vods = []
            for item in data.get("list", []):
                vods.append({
                    "vod_id": f"{tid}${item['vod_id']}",
                    "vod_name": item.get("vod_name", ""),
                    "vod_pic": item.get("vod_pic", ""),
                    "vod_remarks": item.get("vod_remarks", "")
                })
            return {"list": vods}
        except:
            return {"list": []}

    def detailContent(self, ids):
        tid, vid = ids.split('$')
        site = next((s for s in self.sites if s['key'] == tid), None)
        if not site:
            return {}
        url = f"{site['api']}?ac=detail&ids={vid}"
        try:
            data = json.loads(self.fetch(url))
            info = data.get("list", [{}])[0]
            return {
                "vod_id": f"{tid}${info.get('vod_id','')}",
                "vod_name": info.get("vod_name",""),
                "vod_pic": info.get("vod_pic",""),
                "type_name": self.typeMapping(info.get("type_name","")),
                "vod_year": info.get("vod_year",""),
                "vod_area": info.get("vod_area",""),
                "vod_remarks": info.get("vod_remarks",""),
                "vod_actor": info.get("vod_actor",""),
                "vod_director": info.get("vod_director",""),
                "vod_content": info.get("vod_content",""),
                "vod_play_from": "播放",
                "vod_play_url": info.get("vod_play_url","")
            }
        except:
            return {}

    def searchContent(self, key, quick, pg="1"):
        results = []
        for site in self.sites:
            url = f"{site['api']}?ac=detail&wd={key}"
            try:
                data = json.loads(self.fetch(url))
                for item in data.get("list", []):
                    results.append({
                        "vod_id": f"{site['key']}${item['vod_id']}",
                        "vod_name": item.get("vod_name", ""),
                        "vod_pic": item.get("vod_pic", ""),
                        "vod_remarks": item.get("vod_remarks", "")
                    })
            except:
                continue
        return {"list": results}

    def playerContent(self, flag, id, vipFlags):
        tid, vid = id.split('$')
        site = next((s for s in self.sites if s['key'] == tid), None)
        if not site:
            return {}
        url = f"{site['api']}?ac=detail&ids={vid}"
        try:
            data = json.loads(self.fetch(url))
            info = data.get("list", [{}])[0]
            return {"parse": 1, "playUrl": info.get("vod_play_url","")}
        except:
            return {}
