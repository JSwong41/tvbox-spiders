
import os
import json
from spider import Spider

class DemoSpider(Spider):
    def init(self, extend=""):
        self.extend = extend

    def loadSitesConfig(self):
        cache_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(cache_dir, 'assets', 'sites.json')
        if not os.path.exists(path):
            return {"sites": [], "categories": []}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def getSites(self):
        return self.loadSitesConfig().get("sites", [])

    def getCategories(self):
        return self.loadSitesConfig().get("categories", [])

    def homeContent(self):
        return {
            "sites": self.getSites(),
            "categories": self.getCategories()
        }

    def categoryContent(self, tid, pg, filter, extend):
        for site in self.getSites():
            if site['key'] == tid:
                return {
                    "list": [],  # TODO: API获取分类内容
                    "filters": site.get("filters", {})
                }
        return {"list": [], "filters": {}}

    def searchContent(self, key, quick, pg="1"):
        results = []
        for site in self.getSites():
            results.append({
                "site": site['name'],
                "title": f"{key} 示例视频",
                "vod_id": f"{site['key']}_{key}"
            })
        return {"list": results}
