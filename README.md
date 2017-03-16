# tianmao_shop_spider

使用方式：
1. 单条店铺url修改 shop_url 的内容，例如shop_url = 'https://xiaomi.tmall.com'，输入想要获取的数目items，不输入默认获取所有条目，最后运行
TianmaoSpider().get_data(shop_url,items)
2. 多条店铺链接修改shop_urls的内容，例如shop_urls=[shop_url1,shop_url2]，获取条目修改
 result.append(pool.apply_async(TianmaoSpider().get_data,(url,items)))
 的items部分，例如
 result.append(pool.apply_async(TianmaoSpider().get_data,(url,2)))执行代码输出结果

