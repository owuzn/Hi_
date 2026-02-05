#Mr.asadflis
import aiohttp,asyncio,aiofiles,lxml,logging
from bs4 import BeautifulSoup
class Spiders:
	def __init__(self,url,headers,timeout,page_q):
		self.url=url
		self.page_q=page_q
		self.timeout=timeout or 10
		self.headers=headers or  {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
	async def fetch(self,s,u):
		try:
			async with s.get(
		u,
		headers=self.headers,
		timeout=self.timeout
		)as re:
				if re.status==200:
					return await re.text()
		except Exception as e:
			logging.error(f'来自 {u} 的错误 {e}')
		return None 
	async def worker(self,s,u):
		re=await self.fetch(s,u)
		if re:
			await self.page_q.put(re)
		
	async def run(self):
		async with aiohttp.ClientSession()as s:
			workers=[self.worker(s,u)for u in self.url]
			await asyncio.gather(*workers)
			await self.page_q.put(None)
class Parser:
	def __init__(self,page_q,item_q):
		self.page_q=page_q
		self.item_q=item_q
	async def run(self):
		while True:
			rs=await self.page_q.get()
			if rs is None:
				await self.item_q.put(None)
				logging.info('队列获取完成')
				break
			soup=BeautifulSoup(rs,'lxml')
			title=soup.title.text if soup.title else 'None'
			await self.item_q.put(title)
class Pipeline:
	def __init__(self,item_q,f):
		self.item_q=item_q
		self.f=f
	async def run(self):
		while True:
			rt=await self.item_q.get()
			if rt is None:
				logging.info('存档下载完成')
				break
			await self.f.write(f'{rt}\n')
async def main():
	logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
	async with aiofiles.open('box.txt','a',encoding='utf-8')as f:
		page_q=asyncio.Queue(maxsize=20)
		item_q=asyncio.Queue(maxsize=10)
		url=[
		'https://example.com',
		'https://baidu.com',
		'https://kugou.com',
		'https://weixin.com'
		]
		timeout=5
		headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
		spiders=Spiders(url,headers,timeout,page_q)
		parser=Parser(page_q,item_q)
		pipeline=Pipeline(item_q,f)
		logging.info('爬虫开始行动')
		await asyncio.gather(
	spiders.run(),
	parser.run(),
	pipeline.run()
	)
asyncio.run(main())