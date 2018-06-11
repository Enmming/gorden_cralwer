# -*- coding: utf-8 -*-
from pymongo import MongoClient
from pymongo.mongo_replica_set_client import MongoReplicaSetClient
from gorden_crawler.bee_queue.client import BeeQueueClient
from gorden_crawler.bee_queue.bee_queue import Job
from pymongo.read_preferences import ReadPreference
import copy
import time

def not_set(string):
    """ Check if a string is None or ''
    :returns: bool - True if the string is empty
    """
    if string is None:
        return True
    elif string == '':
        return True
    return False

class YelpPipeline(object):

    config = {
        'uri': 'mongodb://localhost:27017',
        'mongodb_database': 'shiji_navigation',
        'replica_set': None,
        'fsync': False,
        'write_concern': 0,
        'image_handle_queue_redis_host': 'localhost',
        'image_handle_queue_redis_port': 6379,
    }

    def load_spider(self, spider):
        self.settings = spider.settings

    def configure(self):
        """ Configure the MongoDB """
        # Set all regular options
        options = [
            ('uri', 'YELP_MONGODB_SERVER'),
            ('fsync', 'MONGODB_FSYNC'),
            ('write_concern', 'MONGODB_REPLICA_SET_W'),
            ('replica_set', 'MONGODB_REPLICA_SET'),  
            ('image_handle_queue_redis_host', 'IMGAE_HANDLE_QUEUE_REDIS_HOST'),
            ('image_handle_queue_redis_port', 'IMGAE_HANDLE_QUEUE_REDIS_PORT'),
            ('image_handle_queue_redis_password', 'IMGAE_HANDLE_QUEUE_REDIS_PASSWORD'),
        ]

        for key, setting in options:
            if not not_set(self.settings[setting]):
                self.config[key] = self.settings[setting]

    def open_spider(self, spider):
        self.load_spider(spider)
        self.configure()
        
        if self.config['replica_set'] is not None:
            connection = MongoReplicaSetClient(
                self.config['uri'],
                replicaSet=self.config['replica_set'],
                w=self.config['write_concern'],
                fsync=self.config['fsync'],
                read_preference=ReadPreference.PRIMARY_PREFERRED) 
        else:
            # Connecting to a stand alone MongoDB
            connection = MongoClient(
                self.config['uri'],
                fsync=self.config['fsync'],
                read_preference=ReadPreference.PRIMARY)
            
        # Set up db
        self.db = connection[self.config['mongodb_database']]
        if 'image_handle_queue_redis_password' in self.config.keys():
            self.image_hamdle_queue = BeeQueueClient("yelp:crawler_handle_image:", host=self.config['image_handle_queue_redis_host'], port=self.config['image_handle_queue_redis_port'], password=self.config['image_handle_queue_redis_password'])
        else:
            self.image_hamdle_queue = BeeQueueClient("yelp:crawler_handle_image:", host=self.config['image_handle_queue_redis_host'], port=self.config['image_handle_queue_redis_port'])
        
    def process_item(self, item, spider):
        
    	item_type = item.get('type')
        
    	if item_type == 1:
            item_detail = {
                'scan_time': int(time.time()),
                'scan_date': time.strftime('%Y-%m-%d',time.localtime(time.time())),
                'mall': item.get('mall'),
                'status': item.get('status'),
                'from_site': item.get('from_site'),
                'type': item.get('type'),
                'shop_id': item.get('shop_id'),
                'name': item.get('name'),
                'address': item.get('address'),
                'telephone': item.get('telephone'),
                'introduction': item.get('introduction'),
                'city': '',
                'crawl_country': item.get('country'),
                'coordinate': item.get('coordinate'),
                'crawl_url': item.get('crawl_url'),
                'shop_url': item.get('shop_url'),
                'area': '',
                'category': item.get('category'),
                'cover': item.get('cover'),
                'cover_bak': item.get('cover'),
                'price_range': item.get('price_range'),
                'rating': item.get('rating'),
                'coordinate_zoom': item.get('coordinate_zoom'),
                'open_time_item': item.get('open_time_item'),
                'categories_item': item.get('categories_item'),
                'country_item': '',#item.get('country_item'),
                'city_item': '',#item.get('city_item'),
                'images_item': item.get('images_item')
            }

            item_detail_copy = copy.deepcopy(item_detail)
            del item_detail_copy['open_time_item']
            del item_detail_copy['categories_item']
            del item_detail_copy['country_item']
            del item_detail_copy['city_item']
            del item_detail_copy['images_item']
            
            query_condition={'shop_id': item_detail_copy['shop_id'], 'from_site':item_detail_copy['from_site']}
            collection_name = 'shop'
            
            shop_mongo = self.db[collection_name].find_one(query_condition)
            need_push = False
            
            if len(item_detail['cover']) > 0:
                if not shop_mongo:
                    need_push=True
                elif 'handle_image' not in shop_mongo:
                    need_push=True
                elif shop_mongo['handle_image']!=2:
                    need_push=True

            if shop_mongo:
                del item_detail_copy['mall']
                del item_detail_copy['status']
                del item_detail_copy['city']
                del item_detail_copy['area']

                if 'handle_image' in shop_mongo and shop_mongo['handle_image'] == 2:
                    del item_detail_copy['cover']
                    
                if 'user_modify' in shop_mongo.keys() and shop_mongo['user_modify'] == 2:
                    del item_detail_copy['name']
                    del item_detail_copy['introduction']
                
                if shop_mongo['category'] != item_detail_copy['category'] and 'category_ids' in shop_mongo.keys():
                    item_detail_copy['category_change'] = '1'

            self.update_one_doc(collection_name, item_detail_copy, query_condition)

            open_time_item_list = item_detail.get('open_time_item')
            for open_time_item in open_time_item_list:
                query_condition = {'shop_id': open_time_item['shop_id'], 'day':open_time_item['day']}
                collection_name = 'open_time'
                self.update_one_doc(collection_name ,open_time_item, query_condition)

            #country_item
#             country_item = item_detail.get('country_item')
#             query_condition = {'from_site': country_item['from_site'], 'name':country_item['name']}
#             collection_name = 'crawl_country'
            #self.update_one_doc(collection_name ,country_item, query_condition)

            #city_item
#             city_item = item_detail.get('city_item')
#             query_condition = {'from_site': city_item['from_site'], 'name':city_item['name']}
#             collection_name = 'crawl_city'
            '''oss do,so ignore'''
            #self.update_one_doc(collection_name ,city_item, query_condition)

            #categories_item
            categoriesItem_list = item_detail.get('categories_item')
            for categoryItem in categoriesItem_list:
                query_condition = {'from_site': categoryItem['from_site'], 'category':categoryItem['category']}
                collection_name = 'crawl_shop_category'
                self.update_one_doc(collection_name ,categoryItem, query_condition)

            # imageItem
            images_item = item_detail.get('images_item')
            # print images_item
            for imageItem in images_item:
                query_condition={'shop_id': imageItem['shop_id'], 'from_site':imageItem['from_site'], 'url':imageItem['url']}
                collection_name = 'shop_image'
                self.update_one_doc(collection_name, imageItem, query_condition)

            if need_push:
                self.push_handle_image_to_queue('c', item_detail)
        return item

    def push_handle_image_to_queue(self, type, detail):
        if type == 'c':
            data = {"t": "c", 'from_site': detail['from_site'], 's_id':detail['shop_id']} 
        self.image_hamdle_queue.pushJob(Job(data, options={"timeout":10000,"retries":2}))

    def update_one_doc(self, collection_name, item_detail, query_condition):
        self.db[collection_name].update_one(
                    query_condition,
                    {'$set': item_detail},
                    upsert = True
                )