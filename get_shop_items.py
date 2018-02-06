import json
from concurrent import futures

import requests
from pyquery import PyQuery as pq


# 获取店铺名称, logo, url, 描述
def get_shop_detail(url):
    r = requests.get(url)
    doc = pq(r.text)
    data = {}
    data['shop_desc'] = doc("meta[name='description']").attr('content')
    data['shop_logo'] = doc("meta[property='og:image']").attr('content')
    data['shop_url'] = doc("meta[property='og:url']").attr('content')
    data['shop_title'] = doc("meta[property='og:title']").attr('content')
    data['shop_id'] = doc("#shop_id").attr('value')
    data['seller_id'] = doc('#sid').attr('value')
    return data


# 获取单页的商品
def get_page_items(url, page):
    url += '/shop/shop_auction_search.do?p={0}'.format(page)
    r = requests.get(url)
    data = r.json()
    items = data['items']
    return items


# 获取店铺所有商品
def get_shop_items(url):
    shop_url = url + '/shop/shop_auction_search.do'
    r = requests.get(shop_url)
    data = r.json()
    total_page = int(data['total_page'])
    items = []
    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        to_do_map = {}
        for page in range(1, total_page+1):
            future = executor.submit(get_page_items, url, page)
            to_do_map[future] = page

        done_iter = futures.as_completed(to_do_map)
        for future in done_iter:
            result = future.result()
            items += result
    return items


# 获取单个商品评论
def get_item_rate(item_id, seller_id):
    url = 'https://rate.tmall.com/list_detail_rate.htm?itemId={0}&sellerId={1}'.format(
        item_id, seller_id)
    try:
        data = requests.get(url).text.split(':', 1)[-1]
        data = json.loads(data)
        rate_list = data['rateList']
    except Exception as e:
        rate_list = []
        print(e)
    return rate_list


# 批量获取商品评价
def get_items_rate(items, seller_id):
    data = []
    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        to_do_map = {}
        for item in items:
            item_id = item['item_id']
            future = executor.submit(get_item_rate, item_id, seller_id)
            to_do_map[future] = item

        done_iter = futures.as_completed(to_do_map)
        for future in done_iter:
            result = future.result()
            item = to_do_map[future]
            item['rate'] = result
            data.append(item)
    return data


# 获取店铺信息整合
def get_data(url):
    data = {}
    shop_detail = get_shop_detail(url)
    data.update(shop_detail)
    items = get_shop_items(url)
    seller_id = data['seller_id']
    items = get_items_rate(items, seller_id)
    data['items'] = items
    # 保存为json格式稳文件
    with open('data.json', 'w') as f:
        json.dump(data, f)


if __name__ == '__main__':
    url = 'https://xiaomi.m.tmall.com/'
    get_data(url)
