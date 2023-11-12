import feedparser 
from bs4 import BeautifulSoup
import time
import xml.etree.ElementTree as ET



def get_rss_urls(opml_file_path='Feeds.opml',category=[]):

    tree = ET.parse(opml_file_path)
    root = tree.getroot()

    body = root.find('body')

    opml_data = []  # 用于存储字典格式的OPML数据

    for outline in body.findall('outline'):
        if outline.get("title") in category or not category:
            # 提取outline元素的属性，例如text、type、xmlUrl等
            for line in outline.findall("outline"):
                outline_dict = {
                    'text': line.get('text'),
                    'type': line.get('type'),
                    'xmlUrl': line.get('xmlUrl')
                    # 添加其他属性，如果有的话
                }
                
                # 将每个outline元素的属性字典添加到opml_data列表中
                opml_data.append(outline_dict)

    # 现在opml_data包含了字典格式的OPML数据
    # 您可以根据需要进一步处理或访问这些数据
    return opml_data


def get_feeds(rss_source:list=[],publish_limit:int = 60):
    waitlist=[]
    for rss in rss_source:
        rss_url=rss.get("xmlUrl")
        if rss_url:
            response = feedparser.parse(rss_url)
            for entry in response.get('entries',[]):
                if time.mktime(entry.get("published_parsed",time.strptime("2020-09-09 19:00:00", "%Y-%m-%d %H:%M:%S")))< time.mktime(time.gmtime())-publish_limit*60: #只看publish_limit分钟内发布的内容
                   # print(f"{rss.get('text')}:out-to-date news")
                    break
                elif entry.get("id") not in waitlist:
                    summary_raw = entry.get("summary")
                    if summary_raw:
                        # 使用Beautiful Soup解析HTML
                        soup = BeautifulSoup(summary_raw, 'html.parser')

                        # 查找<div>标签
                        div_tag = soup.find('div')

                        # 提取<div>中的文本内容
                        summary_text = div_tag.text if div_tag else entry.get("title")

                    waitlist.append({
                        "id":entry.get("id"),
                        "title":entry.get("title"),
                        "link":entry.get("link"),
                        "date":entry.get("published_parsed"),
                        "description":summary_text,
                        "content":entry.get("content"),
                    })

                 #   print(f"{rss.get('text')} \n {entry.get('title')}")
                    break
                else:
                    break
    sorted_waitlist=sorted(waitlist,key=lambda x: x['date'],reverse=True)
    return sorted_waitlist