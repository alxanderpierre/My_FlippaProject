# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import mysql.connector

class FlippaPipeline:
    def __init__(self):
        self.create_connection()
        self.create_table()

    def create_connection(self):
        self.conn = mysql.connector.connect(
            host = 'localhost',
            user = 'root',
            passwd = 'D6608t253agam.',
            database = 'MyEmpire'
        )
        self.curr = self.conn.cursor()
    def create_table(self):
            self.curr.execute(""" drop table if exists Flippa_tb """ )
            self.curr.execute("""create table Flippa_tb(
                title text,
                type_ text,
                monetization text,
                net int,
                price int,
                monthly_net int,
                age_of_site int,
                site_type text,
                multiple dec, 
                platform text)""")
            

    def process_item(self, item, spider):
        if "type_" in item:
            self.store_db(item)
        return item

    def store_db(self, item):
        for j in range(len(item["net"])):
            self.curr.execute("""insert into Flippa_tb values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",(
                item['title'][j],
                item['type_'][j],
                item['monetization'][j],
                item['net'][j],
                item['gross_rev'][j],
                item['unique_visits'],
                item['page_views'],
                item['price'][j],
                item['multiple'][j],
                item['monthly_net'][j], 
                item['age_of_site'][j],
                item['site_type'][j],  
                item['platform'][j]))
            
            self.conn.commit()
