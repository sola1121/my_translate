# sqlalchemy quick start
# https://docs.sqlalchemy.org/en/rel_1_2/orm/tutorial.html

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import create_session
from sqlalchemy import MetaData, Table, String, Integer

# 数据库来自MySQL官方练习数据库, 雇员数据库employees
db_engine = sqlalchemy.create_engine("mysql+pymysql://leimilia:leimilia@localhost/employees?charset=utf8mb4")

# 普通的pymysql式的使用
results = db_engine.execute("select * from departments limit 10")
for result in results.fetchall():
    print(result)


Model = declarative_base()
metadata = MetaData(bind=db_engine)

class Departments(Model):
    """映射已有的数据库，传入三个参数：数据库名称、metadata（绑定接口）、autoload=True"""
    __table__ = Table("departments", metadata, autoload=True)

# 创建事务(会话)
session = create_session(bind=db_engine)
results = session.query(Departments).order_by("dept_no").all()

for result in results:
    print("部门号: ", result.dept_no, "   部门名: ", result.dept_name)