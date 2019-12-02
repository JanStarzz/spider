import time
import lxml
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import matplotlib.pyplot as plt
import openpyxl
ur = "https://xm.58.com/shichang/pn{}/?key=%E5%B8%82%E5%9C%BA%E8%90%A5%E9%94%80&cmcskey=%E5%B8%82%E5%9C%BA%E8%90%A5%E9%94%80&final=1&jump=1&specialtype=gls&PGTID=0d303651-0025-e1d0-8406-cff4529e87ce&ClickID=2"  # 58中销售专员的招聘信息
txt_name = "./薪酬.txt"
csv_name = "./薪酬.csv"
xlsx_name = "./薪酬.xlsx"


def get_wages(url):
    requests.packages.urllib3.disable_warnings()

    contents = []  # 装入每个工作的列表
    for i in range(6):
        req = requests.get(url.format(str(i+1)))  # 请求网站
        req.encoding = "utf-8"  # 请求编码
        soup = BeautifulSoup(req.text, "lxml")  # 整理数据
        items = soup.select("li.job_item")  # 获得每个工作的数据 列表类型
        for item in items:  # 遍历工作元素
            now = []  # 装入每个工作的三个元素（名称，地址，工资）
            if not item.select("div.item_con p.job_salary"):  # 数据清洗，去掉工资为空的元素
                continue
            if not item.select("div.item_con span.address"):  # 数据清洗，去掉地址为空的元素
                continue
            if not item.select("div.item_con span.name"):  # 数据清洗，去掉名称为空的元素
                continue
            wages = item.select("div.item_con p.job_salary")[0].text.strip("元/月") # 数据清洗，去掉元/每月，方便获得平均值和绘制饼状图
            address = item.select("div.item_con span.address")[0].text.strip()  # select()返回的是list类型
            name = item.select("div.item_con span.name")[0].text
            now.append(name)
            now.append(address)
            now.append(wages)
            contents.append(now.copy())
            print(now)
        time.sleep(3)  # 休眠，防止网站反爬虫响应
    return contents


def write_csv(file_name, content_str):  # 用panda库写入csv
    name = ["职业名", "地址", "薪资"]  # 三列元素，列名分别为职业名，地址，薪资
    salary = pd.DataFrame(columns=name, data=content_str)
    salary.to_csv(file_name)


def write_txt(file_name, content_str):   # 写入txt的函数
    with open(file_name, "w", encoding='utf-8', ) as f:
        for i in content_str:   # 第一层for循环获得每个工作的样本
            for j in i:       # 第二层获得工资的样本
                f.write(j)    # 写入文本
            f.write('\n')  # 换行
        f.close


def make_pie(contents):
    negotiable = 0   # 面议的工作的数目
    low = 0   # 0-3000
    mid = 0   # 3000-6000
    high = 0  # 6000-9000
    ex = 0  # 大于9000
    for i in contents:  # 遍历工作元素
        if '面议' in i:  # 如果工资面议
            negotiable += 1
            continue
        n_lst = re.split(r'[-]', i[2])  # 去掉-
        avg = sum(list(map(int, n_lst))) / 2
        if 0 < avg < 3000:  # 判断工资范围
            low += 1
        elif 3001 < avg < 6000:
            mid += 1
        elif 6001 < avg < 9000:
            high += 1
        else:
            ex += 1
    lst = [negotiable, low, mid, high, ex]
    labels = ['negotiable', '0-3000', '3001-6000', '6001-9000', '9000+']
    plt.pie(lst, labels=labels, autopct='%1.2f%%')  # 画饼图（数据，数据对应的标签，百分数保留两位小数点）
    plt.title("wages")  # 设置标题
    plt.show()
    plt.savefig("wages.png")  # 保存


def write_excel(file_name, list_content):
    wb = openpyxl.Workbook()  # 新建Excel工作簿
    st = wb.active
    st['A1'] = "薪资"  # 修改为自己的标题
    second_row = ["名称", "地址", "工资"]  # 根据实际情况写属性
    st.append(second_row)
    for row in list_content:
        st.append(row)
    wb.save(file_name)  # 新工作簿的名称


if __name__ == '__main__':
    content = get_wages(ur)
    write_csv(csv_name, content)
    write_txt(txt_name, content)
    write_excel(xlsx_name, content)
    make_pie(content)
