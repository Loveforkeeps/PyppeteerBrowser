#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Erdog

import asyncio
from pyppeteer import launch
from pyppeteer import errors
import sys


class PyppeteerBrowser():
    def __init__(self, urls, maxtab=20, browserpath=None, timeout=1000 * 60):
        """
        PyppeteerBrowser

        Args:
            urls ([type]): [description]
            maxtab (int, optional): [description]. Defaults to 20.
            browserpath ([type], optional): [description]. Defaults to None.
            timeout ([type], optional): [description]. Defaults to 1000*60.
        """
        super().__init__()
        self.urls = urls
        self.timeout = timeout
        self.browser_path = browserpath
        self.max_tab = maxtab
        self.user_agent = "Mozilla/5.0 (Linux; Android 9; LM-Q720) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.116 Mobile Safari/537.36"
        self.window_size = "400,976"
        self.process_page = None  # Process Pyppeteer Page
        self.call_back = None
        self.headless = True
        self.screenshot = False
        self.loop = asyncio.get_event_loop()

    def headless_dis(self):
        self.headless = False

    async def web_browser(self):
        options = {
            'headless': self.headless,
            'ignoreHTTPSErrors': True,
            'userDataDir': 'data',
            'ignoreDefaultArgs': ['--enable-automation'],
            'autoClose': True,
            'defaultViewport': False,
            'loop': self.loop
        }
        if self.browser_path:
            options['executablePath'] = self.browser_path

        browser = await launch(
            options,
            args=[
                '--window-size=' + self.window_size, '--no-sandbox',
                '--disable-infobars', '--disable-extensions'
                # '--proxy-server=http://127.0.0.1:8080'
            ])
        return browser

    async def web_page(self, browser, url, sem):
        async with sem:
            print(f'Starting {url}')
            page = await browser.newPage()
            await page.setUserAgent(self.user_agent)
            # 逃避 window.navigator.webdriver 的检测
            await page.evaluateOnNewDocument(
                "() => {delete navigator.__proto__.webdriver;}")
            try:
                response = await page.goto(
                    url,
                    {
                        'timeout':
                        self.timeout,
                        'waitUntil': [
                            'load',  # 等待 “load” 事件触发
                            'domcontentloaded',  # 等待 “domcontentloaded” 事件触发
                            'networkidle0',  # 在 500ms 内没有任何网络连接
                            'networkidle2'  # 在 500ms 内网络连接个数不超过 2 个
                        ]
                    })

                if self.screenshot:
                    import os
                    # 判断文件位置是否存在，若不存在则创建
                    domainpath = ['archive']
                    for i in domainpath:
                        if not os.path.exists(i):
                            os.makedirs(i)
                            print(i + ' has been created!')
                    await page.screenshot(
                        {
                            'path': './archive/{}.png'.format(url.split('//')[-1].replace('/', '\\')),
                            'type': 'png',
                            'fullPage': True
                        }
                    )
                if self.process_page:
                    await self.process_page(url, response, page)
            except asyncio.CancelledError:
                print('Cancel the future.')
            except Exception as e:
                print(url, e)
            finally:
                await page.close()

    async def run_with_urls(self, urls):
        """
        Run with urls

        Args:
            urls ([list]): urls
        """
        try:
            browser = await self.loop.create_task(self.web_browser())
            sem = asyncio.BoundedSemaphore(self.max_tab)

            # futures = [
            #     self.loop.create_task(self.web_page(browser, url, sem))
            #     for url in urls
            # ]

            # for future in futures:
            #     if self.call_back:
            #         future.add_done_callback(self.callback)
            #     try:
            #         # pass
            #         await future
            #     except Exception as e:
            #         print(e)

            # 改用以下高级封装函数
            futures = asyncio.gather(
                *[self.web_page(browser, url, sem) for url in urls], loop=self.loop)
            if self.call_back:
                futures.add_done_callback(self.callback)
            await futures
        finally:
            # browser.close()
            pass

    def launch(self):
        """
        Launch the browser to browse the specified URLs
        """
        try:
            self.loop.run_until_complete(self.run_with_urls(self.urls))
        except RuntimeError:
            sys.exit(127)
        except Exception as e:
            print(e)
        finally:
            if self.loop.is_running():
                self.loop.close()

    def set_callback(self, callback):
        """
        Set Callback Func to Process future result

        Args:
            callback (function): function
        """
        self.call_back = callback

    def set_useragent(self, useragent):
        self.user_agent = useragent


if __name__ == "__main__":

    browserpath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

    urls = ['https://www.baidu.com', 'https://github.com/',
            'https://www.google.com', 'https://www.darknet.org.uk']
    pb = PyppeteerBrowser(
        urls, maxtab=3, browserpath=browserpath, timeout=10*1000)
    pb.screenshot = True
    pb.headless_dis()
    pb.launch()
