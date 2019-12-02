import time
import lxml
import requests
from bs4 import BeautifulSoup
import pandas as pd
url = "https://sz.58.com/tech/pn{0}/pve_5363_245/?PGTID=0d303655-0000-494e-03a8-eda59e7a49ff&ClickID=3 "  # 58中人力资源的招聘信息
it = []


def get_wages():
    for i in range(8):
        req = requests.get(url.format(str(i+1)))
        req.encoding = "utf-8"
        soup = BeautifulSoup(req.text, "lxml")
        items = soup.select("li.job_item")
        for item in items:
            now = []
            print(item.select("div.item_con p.job_salary"))
            if not item.select("div.item_con p.job_salary"):
                continue
            if not item.select("div.item_con span.address"):
                continue
            if not item.select("div.item_con span.name"):
                continue
            wages = item.select("div.item_con p.job_salary")[0].text
            address = item.select("div.item_con span.address")[0].text.strip()  # select()返回的是list类型
            name = item.select("div.item_con span.name")[0].text
            now.append(name)
            now.append(address)
            now.append(wages)
            it.append(now.copy())
            print(now)
        time.sleep(3)

    return it


def nice(its):
    name = ["职业名", "地址", "薪资"]
    salary = pd.DataFrame(columns=name, data=its)
    salary.to_csv("F:/pythonspace/人力资源/计算机软件-深圳.csv")


if __name__ == '__main__':
    nice(get_wages())
