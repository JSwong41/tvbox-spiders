import json
import requests
from com.github.catvod import Proxy
from abc import ABCMeta, abstractmethod

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

class DemoSpider(Spider):
    def init(self, extend=""):
        # 你的 sites.json raw 地址
        self.sites_url = "https://raw.githubusercontent.com/JSwong41/tvbox-spiders/refs/heads/main/assets/sites.json"
        self.sites = json.loads(self.fetch(self.sites_url))['sites']

    # 首页分类，支持 filters
    def homeContent(self, filter=None):
        classes = []
        for site in self.sites:
            filters = [
                {
                    "key": "type_name",
                    "name": "类型",
                    "value": [{"n": t, "v": t} for t in ["动作片","喜剧片","爱情片","科幻片","恐怖片","剧情片","纪录片","动画片"]]
                },
                {
                    "key": "year",
                    "name": "年份",
                    "value": [{"n": str(y), "v": str(y)} for y in range(2025, 2015, -1)]
                }
            ]
            classes.append({"type_id": site['key'], "type_name": site['name'], "filters": filters})
        return {"class": classes}

    # 分类内容
    def categoryContent(self, tid, pg, filter, extend):
        site = next((s for s in self.sites if s['key'] == tid), None)
        if not site:
            return {"list": []}
        params = {}
        if filter:
            for f in filter:
                params[f['key']] = f['value']
        try:
            data = json.loads(self.fetch(site['api'], params=params))
            vods = []
            for item in data.get("list", []):
                vods.append({
                    "vod_id": f"{tid}${item['vod_id']}",
                    "vod_name": item.get("vod_name",""),
                    "vod_pic": item.get("vod_pic",""),
                    "vod_remarks": item.get("vod_remarks","")
                })
            return {"list": vods}
        except:
            return {"list": []}

    # 详情
    def detailContent(self, ids):
        tid, vid = ids.split('$')
        site = next((s for s in self.sites if s['key'] == tid), None)
        if not site:
            return {}
        try:
            data = json.loads(self.fetch(f"{site['api']}?ac=detail&ids={vid}"))
            info = data.get("list",[{}])[0]
            return {
                "vod_id": f"{tid}${info.get('vod_id','')}",
                "vod_name": info.get("vod_name",""),
                "vod_pic": info.get("vod_pic",""),
                "vod_remarks": info.get("vod_remarks",""),
                "vod_play_from": "播放",
                "vod_play_url": info.get("vod_play_url","")
            }
        except:
            return {}

    # 搜索
    def searchContent(self, key, quick, pg="1"):
        results = []
        for site in self.sites:
            try:
                data = json.loads(self.fetch(f"{site['api']}?ac=detail&wd={key}"))
                for item in data.get("list", []):
                    results.append({
                        "vod_id": f"{site['key']}${item['vod_id']}",
                        "vod_name": item.get("vod_name",""),
                        "vod_pic": item.get("vod_pic",""),
                        "vod_remarks": item.get("vod_remarks","")
                    })
            except:
                continue
        return {"list": results}

    # 播放
    def playerContent(self, flag, id, vipFlags):
        tid, vid = id.split('$')
        site = next((s for s in self.sites if s['key'] == tid), None)
        if not site:
            return {}
        try:
            data = json.loads(self.fetch(f"{site['api']}?ac=detail&ids={vid}"))
            info = data.get("list",[{}])[0]
            return {"parse":1,"playUrl":info.get("vod_play_url","")}
        except:
            return {}
