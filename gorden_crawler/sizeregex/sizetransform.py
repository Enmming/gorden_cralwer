# -*-coding:utf-8-*-
from ..sizeregex.strategyfactory import StrategyFactory
from ..bee_queue.bee_queue import Job
import logging, re


class Batchtransform():
    def batchtransform(self, site, shop_db, size_transform_list, size_transform_flag):
        from ..pipelines.mongodb import SingleMongodbPipeline
        if size_transform_flag == 3:
            return
        if re.findall('item_', site):
            site = re.sub('item_', '', site)
        if site in size_transform_list:
            strategy = StrategyFactory().getStrategy(site)()
            siteRes = strategy.getReMap()
            logging.warning("Transforming")
            sizelist = shop_db['skus'].find({'from_site': site, 'handle_size': '1'}).distinct('size')
            if siteRes:
                for reg in siteRes:
                    k = siteRes.index(reg)
                    logging.warning("one group start ---- " + reg)
                    for size in sizelist:
                        if strategy.transform(size, reg, site, k) is None:
                            continue

                        [sizeType, standardSize] = strategy.transform(size, reg, site, k)
                        if re.findall('^\D+$', size):
                            sizeType = 'Size'
                        if type(size_transform_flag) != int:
                            size_transform_queue = size_transform_flag
                            size_transform_queue.pushJob(Job(
                                {'site': site, 'size': size, 's_z': standardSize, 's_t': sizeType},
                                options={"timeout": 10000, "retries": 2}))
                        elif size_transform_flag == 1 or size_transform_flag == 4:
                            logging.warning("updating mongodb")
                            shop_db['skus'].update({'from_site': site, 'size': size, 's_z': {'$exists': False}},
                                                   {'$set': {'s_z': standardSize, 's_t': sizeType}}, multi=True)
                        elif size_transform_flag == 2:
                            pass

                        logging.warning(size + '--' + sizeType + '---' + standardSize)
                    logging.warning("one group end")
            logging.warning("not-handled size start")
            smp = SingleMongodbPipeline()
            if site in smp.currency_country_map.keys():
                country_id = smp.currency_country_map[site]['country_id']
                country_type = smp.country_sizetype_map[country_id]
            else:
                country_type = 'us'

            if type(size_transform_flag) != int:
                for size in sizelist:
                    if re.findall('^\D+$', size):
                        size = re.sub(' ', '', size)
                        sizeType = 'Size'
                    else:
                        sizeType = country_type
                    size_transform_queue = size_transform_flag
                    size_transform_queue.pushJob(Job({'site': site, 'size': size, 's_t': sizeType, 's_z': size},
                                                     options={"timeout": 10000, "retries": 2}))
            elif size_transform_flag == 1 or size_transform_flag == 4:
                if re.findall('^\D+$', size):
                    sizeType = 'Size'
                else:
                    sizeType = country_type
                shop_db['skus'].update({'from_site': site, 's_t': {'$exists': False}}, {'$set': {'s_t': sizeType}},
                                       multi=True)
            elif size_transform_flag == 2:
                pass
            logging.warning("not-handled size end")
            logging.warning("success")


class Singletransform():
    def singletransform(self, from_site, sku_detail, size_transform_list):
        if from_site in size_transform_list:
            strategy = StrategyFactory().getStrategy(from_site)()
            siteRes = strategy.getReMap()
            if siteRes:
                for reg in siteRes:
                    k = siteRes.index(reg)
                    size = sku_detail['size']
                    st = strategy.transform(size, reg, from_site, k)
                    if st:
                        logging.warning("**Transforming size with " + reg + "**")
                        [sizeType, standardSize] = st
                        sku_detail['s_z'] = standardSize
                        sku_detail['s_t'] = sizeType
                        logging.warning(size + '--' + sizeType + '---' + standardSize)
                        logging.warning("**Transformed successfully**")
