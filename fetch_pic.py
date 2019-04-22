#!/usr/bin/python3
# -*-codig=utf8-*-

'''
https://eviloh.github.io/2018/08/05/headless-chrome-pptr%E5%88%9D%E6%8E%A2/
https://miyakogi.github.io/pyppeteer/reference.html#request-class
https://zhaoqize.github.io/puppeteer-api-zh_CN/#/

'''

from pyppeteer import launch
import asyncio
from urllib.parse import quote
import DataFile
import datetime
import os
import time

url_prefix = "http://10.142.77.135/web?query="

wordlist = DataFile.read_file_into_list("./vr_1")

err_str = "前端不支持VR模板"


def gen_result_dir(dirstr):
    try:
        if "/" in dirstr:
            os.makedirs(dirstr)
        else:
            os.mkdir(dirstr)
    except FileExistsError:
        print('[gen_result_dir] Dir exists: %s. remove dir, mkdir again' % (dirstr))
        shutil.rmtree(dirstr)
        if "/" in dirstr:
            os.makedirs(dirstr)
        else:
            os.mkdir(dirstr)

    
async def action_get_page_content(page):
    content = await page.evaluate('document.documentElement.outerHTML', force_expr=True)
    return content


async def action_remove_all_element(page, div_selector_to_remove):
    await page.evaluate('''(sel) => {
        var elements = document.querySelectorAll(sel);
        for(var i=0; i< elements.length; i++){
            elements[i].parentNode.removeChild(elements[i]);
        }
    }''', div_selector_to_remove)
    return True


async def action_remove_right_debugxml(page):
    await page.evaluate('''{
        var tmp_ss = document.querySelectorAll('#right>div'); //选取右边下属所有div
        for(var i=0;i<tmp_ss.length;i++){  //遍历查找
            if(tmp_ss[i].innerText.indexOf("XML源码") >= 0){  //包括xml源码则移除
                tmp_ss[i].parentNode.removeChild(tmp_ss[i]);
            }
        }
    }''')
    return True

async def main():
    #mychrome = "C:\\Users\\yinjingjing\\AppData\\Local\\pyppeteer\\pyppeteer\\local-chromium\\575458\\chrome-win32\\chrome.exe"
    time_now = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    gen_result_dir(time_now + "/pic/")
    gen_result_dir(time_now + "/html/")

    index = 1

    for word in wordlist:

        print("开始处理第%d个词条" % index)

        try:
            browser = await launch({"executablePath": "chromium-browser", "args": ["--no-sandbox"]})
            page = await browser.newPage()

            url = url_prefix + quote(word) + "&wxc=on"
            await page.goto(url)

            # 获取页面源码
            content = await action_get_page_content(page)
            file_name = "./" + time_now + "/html/" + word + ".html"
            if err_str in content:
                print("word=%s\terr=%s\turl=%s\n" % (word, err_str, url))

            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(content)

            #截图,部分debgu信息太长,导致截图太小,先去掉这部分debug信息再截图
            await action_remove_all_element(page, ".stDocID")   #DEBUG_INFO过长，导致页面过宽
            await action_remove_right_debugxml(page)            #右侧vr xml过长，导致页面过长

            await page.setViewport({"width": 1920, "height": 1080})
            await page.screenshot({"path": "./" + time_now + "/pic/" + word + ".png", "fullPage": "True"})

            index = index + 1
            time.sleep(0.5)
            await browser.close()
            time.sleep(0.5)

        except Exception as err:
            print("word=%s\terr=%s" % (word, err))
            index = index + 1
            continue


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())

