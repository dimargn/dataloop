import aiohttp
import asyncio
import sys
import json
from bs4 import BeautifulSoup

from constants import Constants


class Crawler():
    def __init__(self, url, depth, data_type):
        self.url = url
        self.depth = depth
        self.data_type = data_type

    async def run(self):
        async with aiohttp.ClientSession() as session:
            crawled_data = await self.crawl_url(session, self.url, self.depth)

        with open('results.json', 'w') as outfile:
            json.dump({Constants.results.value: crawled_data}, outfile, indent=4)

        print(f"Crawling completed. Results saved to 'results.json'.")

    async def crawl_url(self, session, url, depth):
        try:
            async with session.get(url) as response:
                text = await response.text()
                soup = BeautifulSoup(text, Constants.htmlParser.value)
                image_tags = soup.find_all(self.data_type)

                results = []
                for img in image_tags:
                    image_url = img.get('src')
                    if image_url and not image_url.startswith('data:'):
                        results.append({
                            Constants.imageUrl.value: image_url,
                            Constants.sourceUrl.value: url,
                            Constants.depth.value: depth
                        })

                if depth > 0:
                    anchor_tags = soup.find_all('a')
                    tasks = [self.crawl_url(session, anchor.get('href'), depth - 1) for anchor in anchor_tags if
                             anchor.get('href') and anchor.get('href').startswith('http')]
                    sub_results = await asyncio.gather(*tasks)
                    results.extend(sub_results)

                return results

        except Exception as e:
            print(f"Error crawling {url}: {str(e)}")
            return []





if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python crawler.py <url: string> <depth: number>")
        sys.exit(1)

    start_url = sys.argv[1]
    crawl_depth = int(sys.argv[2])

    if crawl_depth < 0:
        print("Depth should be a non-negative integer.")
        sys.exit(1)

    crawler = Crawler(start_url, crawl_depth, 'img')
    asyncio.run(crawler.run())