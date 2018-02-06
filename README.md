# 天猫店铺爬虫
## 安装依赖包
```
pip install pyquery
pip install requests
```

## Usage
> get_shop_items.py
获取单个店铺所有商品
包含:
店铺基本信息
店铺所有商品
商品的基本信息
商品的评论(一页)
未办事项:
商品的图文信息


例如:
```
if __name__ == '__main__':
    url = 'https://xiaomi.m.tmall.com/'
    get_data(url)
```
然后运行即可, 结果保存在`data.json`中.
