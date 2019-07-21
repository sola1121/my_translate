# https://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html

### NOTE: Basic Relationship Patterns ### 基本的关系模式
# 将会使用到的模块
from sqlalchemy import create_engine, Table, Column, Integer, ForeignKey
from sqlalchemy.orm import create_session, relationship
from sqlalchemy.ext.declarative import declarative_base

# 这里建立一个数据库关联引擎, 并创建了会话
engine = create_engine(create_engine('sqlite:///:memory:', echo=True))
session = create_session(bind=engine)
# 用于映射类的Declarative系统的基础类实例
Base = declarative_base()


### NOTE: One To Many ### 一对多
# 一个父表字段, 在子表中有多个引用.
# 一个一对多关系放置于一个引用父表的子表的外键中.
# relationship()接下来指定父表, 该父表将作为元素被子表引用的一个集合.
class Parent(Base):
    __tablename__ = "parent"
    id = Column(Integer, primary_key=True)
    children = relationship("Child")


class Child(Base):
    __tablename = "child"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("parent.id"))

# 在一对多中要建立一个双向关系, 其一对多的反面是多对一. 
# 这里建立一个双向关系需在子表中指定一个另外的relationship()并使用relationship.back_populates参数连接他们两个.
class Parent(Base):
    __tablename__ = "parent"
    id = Column(Integer, primary_key=True)
    children = relationship("Child", back_populates="parent")


class Child(Base):
    __tablename__ = "child"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("parent.id"))
    parent = relationship("Parent", back_populates="children")

# Child将会获得一个parent属性, 在多对一的情境下.


### NOTE: Many To One ### 多对一
# 多个父表字段, 引用一个子表字段.
# 多对以放置一个外键在引用子表的父表中.
# relationship()被在父表中声明, 这里一个新的标量保持属性将会被创建.
class Parent(Base):
    __tablename__ = "parent"
    id = Column(Integer, primary_key=True)
    child_id = Column(Integer, ForeignKey("child.id"))
    child = relationship("Child")


class Child(Base):
    __tablename__ = "child"
    id = Column(Integer, primary_key=True)

# 双向行为被通过在子表中添加第二个relationship()和同时在两方应用relationship.back_populates参数实现.
class Parent(Base):
    __tablename__ = "parent"
    id = Column(Integer, priamry_key=True)
    child_id = Column(Integer, ForeignKey("child.id"))
    child = relationship("Child", back_populates="parents")


class Child(Base):
    __tablename__ = "child"
    id = Column(Integer, primary_key=True)
    parent = relationship("Parent", back_populates="child")


### REVIEW: 总个结 ###
# 一对多和多对一互为相反关系. 
# 外键存在的表的字段是引用字段, 该表就为多的一方, 该字段是父表的字段数据的子集.
# 要想建立双向引用, 就必须要两头都写relationship()关系, 使用back_populates或类似的backref指定反向引用名.
# 在relationship()方法中还有很多有用的参数, 如cascade(级联), lazy(延迟加载方式)等.


### NOTE: One To One ### 一对一
# 一对一实质上是一个在两边都具有一个范围参数的双向关系.
# 要实现一对一关系, uselist标识符位置参数指明一个范围而不是一个在"多"关系那边的集合.
# 在一的那边, 指明引用的字段不使用列表, 多的那边不变.

# 转换一个一对多关系为一对一关系.
class Parent(Base):
    __tablename__ = "parent"
    id = Column(Integer, primary_key=True)
    child = relationship("Child", uselist=False, back_populates="parent")


class Child(Base):
    __tablename__ = "child"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("parent.id"))
    # parent = relationship("Parent", back_populates="child")

# 多对一关系转换为一对一
class Parent(Base):
    __tablename__ = "parent"
    id = Column(Integer, primary_key=True)
    child_id = Column(Integer, ForeignKey("child.id"))
    # child = relationship("Child", back_populates="parent")


class Child(Base):
    __tablename__ = "child"
    id = Column(Integer, primary_key=True)
    parent = relationship("Parent", uselist=False, back_populates="child")

# 若使用relationship()的backref参数
from sqlalchemy.orm import backref

# child = relationship("Parent", backref=backref("parent", uselist=False))


### NOTE: Many To Many ### 多对多
# 多对多关系需要添加一个协同表在两个类之间. 
# 协同表被relationship()的secondary参数指明.
# 通常, 对Table使用ForeignKey指令能找到需要连接的远端的表们.

association_table = Table("association", Base.metadata,
    Column("left_id", Integer, ForeignKey("left.id")),
    Column("right_id", Integer, ForeignKey("right.id"))
)


class Parent(Base):
    __tablename__ = "left"
    id = Column(Integer, primary_key=True)
    children = relationship("Child", secondary=association_table)


class Child(Base):
    __table__ = "right"
    id = Column(Integer, primary_key=True)
    parents = relationship("Parent", secondary=association_table)

# 对其构建双向关联的话, 两边的关系都需要包含一个集合.
# 指定使用relationship.back_populates, 和每一个relationship()指定一个共同的协同表.

association_table = Table("association", Base.metadata, 
    Column("left_id", Integer, ForeignKey("left.id")),
    Column("right_id", Integer, ForeignKey("right.id"))
)

class Parent(Base):
    __tablename__ = "lelt"
    id = Column(Integer, primary_key=True)
    children = relationship("Child", secondary=association_table, back_populates="children")


class Child(Base):
    __tablename__ = "right"
    id = Column(Integer, primary_key=True)
    parent = relationship("Parent", secondary=association_table, back_populates="parents")

# 使用backref代替back_populates, 只需要一边书写, 其会自动添加secondary到对立的一边.

# relationship()的secondary参数页支持使用一个最终返回是可执行的函数的函数, 这样的当映射对象被第一次使用时, 其将会对其评估. 
# 使用一个可返回函数的函数作为参数, 这样我们能在之后在定义association_table, 可以在所有模块都初始化后来完成它. (搞个工厂函数?)
# children = relationship("Child", secondary=lambda: association_table, backref="parents")

# 随着Declarative拓展的使用, 传统的"表对象名使用字符串描述"被完全接受, 和字串匹配的表名在 Base.metadata.tables 中可看.

# Deleting Rows from the Many To Many Table # 从多对多关联表中删除行
# 一个对relationship()的secondary参数是唯一的行为, 当在集合中添加或移除对象, 这里指定的Table自动地受INSERT和DELETE语句的约束.
# 这里不需要手动的从表中删除数据. 从集合中移除一条记录的行为将会有行在缓冲中被删除的效果.

# 行将会被从secondary表中自动的删除.
# myparent.children.remove(somechild)

# 一个经常被提的问题是当子对象被直接通过Session.delete()删除时应该怎样将"secondary"表中的对应行删除.
# session.delete(somechild)

# 这里有一些不同的可能性
# 1. 在父表和子表之间有一个relationship(), 但是他们没有一个特定的Child到每个Parent的连接的一个反向关系.
# 当删除这个特定Child对象, SQLAlchemy将不会有任何反应.
# 他需要维护连接到"secondary"表的Parent.
# 没有"secondary"表的删除将发生.

# 2. 存在一个关系连接一个特定Child到每个Parent, 假设他被叫为Child.parents.
# SQLAlchemy默认情况下将载入Child.parents集合中所有Parent对象, 并从"secondary"表中移除那些建立了连接的每一行.
# 注意, 这个关系不需要是双向的; SQLAlchemy严格的查看每个要删除Child对象相关联的relationship().

# 3. 在这里一个更高级的表现选择是使用由数据库操作的外键上ON DELETE CASECADE指令.
# 假设数据库支持这个特性, 数据库自身能自动删除作为引用行在"child"中已经删除了的"secondary"表中的行.
# 在这个实例使用relationship()上的passive_deletes指令, 让SQLALchemy能主动放弃载入Child.parents集合.

# 注意, 以上这些行为都只是相关的用于relationship()的secondary选项.
# 如果处理被显式的映射并且没有在一个相关的relationship()的secondary选项中存在的协同表的时候, 级联规则能被用于替代用于在反应中一个关联实例被删除时自动删除相关联的实例.
# cascade https://docs.sqlalchemy.org/en/latest/orm/cascades.html#unitofwork-cascades

