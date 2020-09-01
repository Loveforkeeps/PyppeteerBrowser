# PyppeteerBrowser
Use pyppeteer to Browse the URL andProcess the Response



## Deployment:



Python3.7+



## Install:



```shell
git clone git@github.com:Loveforkeeps/PyppeteerBrowser.git
```



## Using:

demo：

```python
browserpath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

with open('2020-08-01.txt') as f:
urls = f.read().splitlines()

pb = PyppeteerBrowser(urls,maxtab=20,browserpath=browserpath,timeout=1000*10)
# pb.process_page = parse_resp
pb.screenshot = True
# pb.headless_dis()
pb.launch()
```



## Update:

* None



### Issue Log:

* None



### Todo List:

* None



## Running  screenshot:

```shell
╰─ python PyppeteerBrowser.py
```

<img src="README.assets/2020-09-01%20at%2014.55.gif" alt="2020-09-01 at 14.55" style="zoom:50%;" />



## License:

This project is licensed under the [MIT license](http://opensource.org/licenses/mit-license.php) 

## Acknowledgments：

* None