import requests
from bs4 import BeautifulSoup
import jieba
import jieba.analyse
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import urllib.parse
import os
import time
import random

# 获取百度搜索结果HTML
def get_html(keyword, page):
    """获取百度搜索结果 HTML"""
    pn = (page - 1) * 10  # 每页10条
    url = f"https://www.baidu.com/s?wd={urllib.parse.quote(keyword)}&pn={pn}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0",
        "Referer": "https://www.baidu.com/",
        "Accept": "text/html,application/xhtml+xml,application/xml;"
                  "q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive"
    }

    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = 'utf-8'
        return res.text
    except Exception as e:
        print(f"[ERROR] 请求第 {page} 页出错: {e}")
        return ""

# 解析网页
def parse_html(html):
    """解析搜索结果标题与摘要"""
    soup = BeautifulSoup(html, "html.parser")

    # 标题在 h3 a 标签中
    titles = [t.get_text(strip=True) for t in soup.select("h3 a")]

    # 摘要匹配 class 中含 summary-text
    summaries = [s.get_text(strip=True) for s in soup.select("span[class*='summary-text']")]

    return titles, summaries

# 3. 循环抓取多页
def crawl(keyword, max_pages=5):
    """循环抓取百度搜索多页结果"""
    all_text = ""
    for page in range(1, max_pages + 1):
        html = get_html(keyword, page)
        if not html:
            print(f"️[WARNING] 第{page}页获取失败")
            continue

        titles, summaries = parse_html(html)
        if len(titles) == 0:
            print(f"[WARNING] 第{page}页未获取到结果")
            continue

        for t, s in zip(titles, summaries):
            all_text += t + " " + s + "\n"

        print(f"[INFO] 第{page}页爬取完成，共获取 {len(titles)} 条结果")
        time.sleep(random.uniform(1, 2))  # 随机延迟 1~2 秒

    return all_text

# 生成词云
def generate_wordcloud(text, keyword, topK=100, mask_path=None):
    """生成中文词云，可选自定义形状"""
    # TF-IDF 提取关键词
    keywords = jieba.analyse.extract_tags(text, topK=topK, withWeight=True)
    freq_dict = {word: weight for word, weight in keywords}

    # 设置中文字体，解决中文显示问题
    font_path = "C:/Windows/Fonts/simhei.ttf"  # 黑体，可换成微软雅黑 msyh.ttc

    mask = None
    if mask_path:
        import numpy as np
        from PIL import Image
        mask = np.array(Image.open(mask_path))

    wc = WordCloud(
        font_path=font_path,
        width=800,
        height=600,
        background_color="white",
        max_words=topK,
        mask=mask,
        contour_width=2,
        contour_color="steelblue"
    ).generate_from_frequencies(freq_dict)

    # 保存词云
    save_dir = "txt_data"
    os.makedirs(save_dir, exist_ok=True)
    filename = os.path.join(save_dir, f"词云图_{keyword}.png")
    wc.to_file(filename)
    print(f"[INFO] 词云图已保存: {filename}")

    # Matplotlib 中文显示设置，避免警告
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    # 显示词云
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.title(f"{keyword} 词云图")
    plt.show()

# 主程序
if __name__ == "__main__":
    keyword = input("请输入关键词：")
    text = crawl(keyword, max_pages=5)

    # 自动创建 txt_data 文件夹
    save_dir = "txt_data"
    os.makedirs(save_dir, exist_ok=True)

    # 保存爬取结果到 txt_data 文件夹
    txt_path = os.path.join(save_dir, f"{keyword}_result.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"[INFO] 百度搜索结果已保存到 {txt_path}")

    # 生成词云
    generate_wordcloud(text, keyword, topK=100, mask_path='cloud.png')
