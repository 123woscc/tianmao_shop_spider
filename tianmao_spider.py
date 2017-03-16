import requests
from bs4 import BeautifulSoup
import json
import multiprocessing
from multiprocessing.pool import ThreadPool


class TianmaoSpider():
    def __init__(self):
        # self.shop_url = url
        # self.goods_url = url + '/search.htm'
        # self.m_url = url.replace('tmall.com', 'm.tmall.com')
        self.shop_data = {}
        self.shop_data['goods'] = {}
        # manager = multiprocessing.Manager()
        # self.goods_id = manager.list()

    def get_soup(self, url):
        html = requests.get(url)
        return BeautifulSoup(html.content, 'lxml')

    def get_shop_smiple_data(self,url):
        soup = self.get_soup(url.replace('tmall.com', 'm.tmall.com'))
        shop_name = soup.find('span', class_='name').get_text()
        shop_logo = soup.find('a', class_='logo').img.get('src')
        shop_id = soup.find('input', id='shop_id').get('value')
        self.seller_id = soup.find('input', id='sid').get('value')
        self.shop_data['shop_name'] = shop_name
        self.shop_data['shop_logo'] = shop_logo
        self.shop_data['seller_id'] = self.seller_id
        self.shop_data['shop_id'] = shop_id


    def get_total_page(self,url):
        soup = self.get_soup(url + '/search.htm')
        goods_api_url = url + soup.find('input', id='J_ShopAsynSearchURL').get('value')
        html = requests.get(goods_api_url)
        soup = BeautifulSoup(str(html.text).replace(r'\"', ''), 'lxml')
        total_page = soup.find('b', class_='ui-page-s-len').get_text().split('/')[-1]
        urls = [goods_api_url + '&pageNo={0}'.format(x) for x in range(1, int(total_page) + 1)]
        return urls

    def get_page_id(self,url):
        id_list=[]
        html = requests.get(url)
        soup = BeautifulSoup(str(html.text).replace(r'\"', ''), 'lxml')
        goods = soup.find_all('dl', class_='item')
        for good in goods:
            good_id = str(good.get('data-id'))
            id_list.append(good_id)
        return id_list

    def get_goods_id(self,urls):
        pool = ThreadPool()
        id_list=pool.map(self.get_page_id,urls)
        pool.close()
        pool.join()
        return sum(id_list,[])

    def get_good_detail(self, id):
        try:
            print('start:', id)
            good_url = 'https://detail.m.tmall.com/item.htm?id={0}'.format(id)
            soup = self.get_soup(good_url)
            title = soup.find('section', id='s-title').div.h1.get_text()
            price = soup.find('span', class_='mui-price-integer').get_text()
            show_images = [image.get('data-src') for image in soup.find('section', id='s-showcase').find_all('img') if
                           image.get('data-src')]
            detail_images = [image.get('data-ks-lazyload') for image in soup.find_all('img', class_='lazyImg')]

            self.shop_data['goods'][id] = {}
            self.shop_data['goods'][id]['item_id'] = id
            self.shop_data['goods'][id]['title'] = title
            self.shop_data['goods'][id]['price'] = price
            self.shop_data['goods'][id]['show_images'] = show_images
            self.shop_data['goods'][id]['detail_images'] = detail_images
            self.shop_data['goods'][id]['rate_list'] = self.get_rate_list(id)
        except:
            pass

    def get_rate_list(self, id):
        try:
            rate_url = 'https://rate.tmall.com/list_detail_rate.htm?itemId={0}&sellerId={1}&currentPage=1'.format(
                id, self.seller_id)
            data = requests.get(rate_url).text.split(':', 1)[-1]

            dict = json.loads(data)
            rate_list = dict['rateList']
            new_rate_list = []
            for rate in rate_list:
                dict = {}
                dict['displayUserNick'] = rate['displayUserNick']
                dict['rateContent'] = rate['rateContent']
                dict['rateDate'] = rate['rateDate']
                dict['auctionSku'] = rate['auctionSku']
                dict['pics'] = rate['pics']
                dict['reply'] = rate['reply']
                new_rate_list.append(dict)
            return new_rate_list
        except:
            return []


    def get_data(self,url,count=-1):
        self.get_shop_smiple_data(url)
        urls=self.get_total_page(url)
        ids=self.get_goods_id(urls)
        pool = ThreadPool()
        pool.map(self.get_good_detail, ids[:count])
        pool.close()
        pool.join()
        return self.shop_data

    def get_datas(self,urls,count=-1):
        pool=multiprocessing.Pool()
        for url in urls:
            pool.apply_async(self.get_data,url,count)
        pool.close()
        pool.join()




if __name__ == '__main__':
    shop_url = 'https://xiaomi.tmall.com'
    shop_urls=[shop_url,shop_url]
    # data = TianmaoSpider().get_data(shop_url,3)
    result = []
    pool = multiprocessing.Pool()
    for url in shop_urls:
        result.append(pool.apply_async(TianmaoSpider().get_data,(url,2)))
    pool.close()
    pool.join()

    for rs in result:
        print(rs.get())
        print('=' * 50)


