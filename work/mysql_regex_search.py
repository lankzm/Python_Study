#!urs/bin/env python
#coding:utf-8


import re
# from collections import Iterable
#Iterable并不能判断re模块finditer方法返回的对象是否可迭代，所有都是True
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, mapper
from sqlalchemy import Column, MetaData, Table
from sqlalchemy.types import Integer, TEXT, VARCHAR


DB_CONNECT_STRING = 'mysql+pymysql://root:123456@localhost/work?charset=utf8'
engine = create_engine(DB_CONNECT_STRING, 
#                        echo = True  #echo表示是否输出log
                       )
metadata = MetaData()   #跟踪表属性

minghui_table = Table(
    'minghui',
    metadata,
    Column('id', Integer, primary_key = True, autoincrement = True),
    Column('title', TEXT),
    Column('author', TEXT),
    Column('content', TEXT),
    Column('date', TEXT),
    Column('tags', TEXT),
    Column('others', TEXT)
)

minghui_table_filter = Table(
    'minghui_filter',
    metadata,
    Column('id', Integer, primary_key = True, autoincrement = True),
    Column('article_id', Integer),
    Column('information', VARCHAR(128)),
    Column('type', Integer)
)
# metadata.create_all(engine) #在数据库中生成表


class MingHui(object): pass     #创建一个映射类
class MingHuiFilter(object): pass

mapper(MingHui, minghui_table)  #把表映射到类
mapper(MingHuiFilter, minghui_table_filter)
Session = sessionmaker()        #创建一个自定义了的Session类
Session.configure(bind = engine)#将创建的数据库连接关联到这个session
session = Session()
    
phone_pattern = re.compile(r'((\d{11})|^((\d{7,8})|(\d{4}|\d{3})-(\d{7,8})|'\
                           '(\d{4}|\d{3})-(\d{7,8})-(\d{4}|\d{3}|\d{2}|\d{1})'\
                           '|(\d{7,8})-(\d{4}|\d{3}|\d{2}|\d{1}))$)'
                           )
email_pattern = re.compile(r'([_a-zA-Z0-9]+\.)*[_a-zA-Z0-9]+@([_a-zA-Z0-9]+\.)+[_a-zA-Z0-9]+(?<!\d)')
ip_pattern = re.compile(r'(((\d{1,2})|(1\d{2})|(2[0-4]\d)|(25[0-5]))\.){3}'\
                        '((\d{1,2})|(1\d{2})|(2[0-4]\d)|(25[0-5]))'
                        )
data = {}.fromkeys(['article_id', 'information', 'type'])

#数据映射关系
data_relation = {
    'phone' : 1,
    'email' : 2,
    'ip' : 3
}


def get_all():
    #简单的理解就是select()的支持ORM的替代方法，可以接受任意组合的class/column表达式
    query = session.query(MingHui)  
    index_ = 1
    while True: #连续的
        row = query.get(index_)
        if row:
            yield row
        else:
            break
        index_ += 1
        
def insert_result():
    #将结果插入新表
    global data
    print(data)
    f = MingHuiFilter()
    f.article_id = data['article_id']
    f.information = data['information']
    f.type = data['type']
    session.add(f)
    
def regex(row):
    def only_search(pattern):
        m = pattern.finditer(row.content)
        return m
        
    def assemble(info, key):
        #组装拼接数据
        try:
            flt = set()
            for one in info:
                information = one.group().strip()
                if information not in flt:
                    data['article_id'] = row.id
                    data['information'] = information
                    flt.add(information)
                    data['type'] = data_relation[key]
                    insert_result()
        except StopIteration:
            return
        
    global data
    phone_m = only_search(phone_pattern)
    email_m = only_search(email_pattern)
    ip_m = only_search(ip_pattern)
    assemble(phone_m, 'phone')
    assemble(email_m, 'email')
    assemble(ip_m, 'ip')
        

def main():
    #需要从minghui表中的content字段查找出电话，邮箱和IP。
    for row in get_all():
        regex(row)
    session.commit()
    print('提交完成！')
    
def test():
    email_pattern = re.compile(r'([a-zA-Z\d_].?)*@([_a-zA-Z0-9]+\.)+[_a-zA-Z0-9]+(?<!\d)')
    string = 'kycyjszx@public.km.yn.cn.1999年至今进行了73'
#     string = 'tuidang@epochtimes.com用翻墙软件登录http:'
#     string = '430042传真电话83234611电子邮箱83234611@163.com好99'
#     string = 'MSN免费即时消息给dtwip001@hotmail.com'
#     string = 'tdcs@minghui.org和weekly@'
#     string = ',用海外邮箱发表声明.tuidang@epochtimes.com'
    'freeget.ip@gmail.com发一个电子邮件('
    data = email_pattern.finditer(string)
    print(next(data).group())
    

if __name__ == '__main__':
    main()
#     test()