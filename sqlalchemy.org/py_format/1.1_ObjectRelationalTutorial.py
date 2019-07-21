# https://docs.sqlalchemy.org/en/rel_1_2/orm/tutorial.html

# Engine 是连接数据库和映射类的连接纽带, 其指定使用的数据库引擎.
# Declarative Base类是创建映射类的基类, 通过对其进行继承, 子类便成为了一个映射类.基类在全应用中, 最好只出现一个.
# Session类是与数据库进行对话的会话类, 通过与Engine的绑定, 在其中完成对数据库的基本操作.


### NOTE: Connection ### 连接
# 使用连接, 我们使用create_engine()
from sqlalchemy import create_engine

# echo 参数, 使用了内建的logging库, 当为True的时候, 将会在终端打印生成的SQL语句, 为False将不会打印.
# create_engine() 是一个生成Engine实例的快捷方式, Engine实例代表了与不同数据库链接的接口集合.
# Engine实例被创建时并没有完成和数据库的真正的连接, 当使用如Engine.execute()或Engine.connect()时, Engine实例与数据库通过发送SQL发生连接.
# 通常我们不直接使用使用Engine实例, 而是通过ORM在间接的操作.
engine = create_engine('sqlite:///:memory:', echo=True)
# 更多的数据库 https://docs.sqlalchemy.org/en/rel_1_2/core/engines.html#database-urls


### NOTE: Declare a Mapping ### 声明一个映射
# 当使用ORM的时候, 配置的过程开始于声明一个我们将要处理的数据库, 然后定义我们自己的用于映射到表的类.
# 在现代的SQLAlchemy中, 使用一个叫为Declarative的系统, 这两个过程通常是一起执行的, 这个系统可以支持我们创建出包含描述被映射的实际数据库表的指令.
# 使用Declarative系统被映射的类是用基类定义的(就是继承一个基类), 这个基类会维护多个关联的类和表. 这个基类解释declarative base class.
# 我们的应用通常应该只有一个declarative base class, 通过导入来使用. 使用declaretive_base()来创建它.
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()   # 这样就有了一个base类, 我们可以通过他定义任何数量的映射类.

# 接下来我们定义一个User映射. 在这个映射中也是定义了数据库中详细的表结构.
from sqlalchemy import Column, Integer, String, Sequence

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, Sequence("user_id_seq"), primary_key=True)   # 在Firebird和Oracle中需要加入序列, 这里使用的sqlite, 加不加没影响.
    name = Column(String(64))
    fullname = Column(String(128))
    nickname = Column(String(64))

    def __repr__(self):
        return "<User %s name: %s, fullname: %s, nickname: %s>" \
                % (self.id, self.name, self.fullname, self.nickname)

# 一个使用Declarative的子类至少要有__tablename__和一个Column()是主键.
# 创建一个没有主键的表 https://docs.sqlalchemy.org/en/rel_1_2/faq/ormconfiguration.html#faq-mapper-primary-key
# SQLAlchemy从不对类引用的表做任何假设, 包阔默认的表名称, 数据类型或约束条件.
# 但这并不意味着需要样板; 相反, 我们鼓励用户使用辅助函数和mixin类创建自己的自动化任务.
# Mixin and Custom Base Classes. https://docs.sqlalchemy.org/en/rel_1_2/orm/extensions/declarative/mixins.html#declarative-mixins
# 当我们的映射类被创建后, Declarative将会使用一个被叫做descriptors的Python访问替换所有的Column对象, 这个进程叫做 instrumentation.
# 被"instrumented"的映射类将会提供我们在SQL上下文中引用我们的表以及执行和载入数据库中各列的值的方法.


### NOTE: Create a Schema ### 创建一个库
# 通过Declarative系统构建了我们的一个User类, 在此我们已经定义了我们的表的信息, 这叫做表的metadata(元数据).
# 被SQLAlchemy用来代表指定的表的元数据的信息的对象被称为Table对象. 可以从映射类的__table__属性中看到定义(这就是SQL执行语句).
print(User.__table__)

# 当我们声明了一个我们的类, 为了能在类声明完成时执行额外的动作, Declarative使用一个Python元类(metaclass); 在这阶段, 其之后会根据我们的指令创建一个Table对象并通过构建一个Mapper对象与之连接.
# Mapper对象是一个幕后对象, 通常我们都不用显式的处理他. 其中提供了大量的关于我们映射的信息.
# Table对象是大集合MetaData的一个成员. 当使用Declarative的时候, 这个对象是可以通过declarative base class中.meatadata属性获得的.
# MetaData是一个包含能够对数据库发出一个有限制的库创建命令集合的注册处.
# 当我们的SQLite数据库没有存在users表的时候, 可以使用MetadData来向数据库发出CREATE TABLE命令来创建没有存在的数据库.
# 可以执行MetaData.create_all()方法, 传入我们Engine作为数据库链接的来源. 
# 在这之后首先我们会看到一些特殊的命令被发出, 其将会检查users表的存在, 并在之后产生实际的CREATE TABLE指令.
print(Base.metadata.create_all(engine))   # 对连接引擎使用映射, 创建数据库


### NOTE:　Create an Instance of the Mapped Class ### 创建一个映射类实例
ed_user = User(name='ed', fullname='Ed Jones', nickname='edsnickname')
print(ed_user)   # 在这里可以看到id为None, 因为这里还没有发给数据库, 那么instrument通常会给个None, 之后在发送给数据库时生成.

# 我们使用Declarative系统定义的User类已经提供了一个构造函数（例如__init __（）方法），它自动接受与我们映射的列匹配的关键字名称。
# 我们可以自由地在我们的类上定义任何我们喜欢的显式__init __（）方法，它将覆盖Declarative提供的默认方法。

# 在这里创建的对象, 可以看到没有主键, 这不同于Python对错误属性的处理, 他没有raise AttributeError. 
# SQLAlchemy的instrumentation通常在第一次连接时提供默认的值给列映射属性. 
# 对于那些我们事实上分配了值的属性, instrumentation系统将追踪那些分配, 用来在最终向数据库发送INSERT语句.


### NOTE: Creating a Session ### 创建会话
# session三状态 transient, pending, persistent. 临时的, 待定的, 永久的.
# 我们已经准备好了和数据库进行交互. 处理ORM与数据库之间交流的是Session. 
# 在第一次创建应用时, 在同一层面上create_engine()语句发生时, 我们定义一个Session类, 其将会作为一个工厂函数服务于新的session对象.

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)

# 当还没有定义Engin对象的时候, 可以先创建一个会话对象, 然后在定义了Engine对象后在使用Session.configure()配置.
Session = sessionmaker()
Session.configure(bind=engine)
# 定制Session类将会创建一个新的session对象, 他是绑定到我们的数据库的.
# 当有和后端数据库进行相应的交流的时候, 可以实例化配置好的Session对象
session = Session()  # 使用配置好的Session对象创建会话实例.
# 当实例化的session对象第一次使用后, 其将会连接到一个由Engine对象维护的内存池中, 直到commit或者close会话.


### NOTE: Adding and Updating Objects ### 添加和升级对象
ed_user = User(name="ed", fullname="Ed Jones", nickname="edsnickname")
session.add(ed_user)   # ed_user 实例进入pending状态, 还并没有向数据库发出SQL语句, 所以也就没有真正的进入数据库
# Session将使用被称为flush(刷新?)的过程发出SQL以便在需要时尽快保留Ed Jsons.
# 当对Ed Jsons进行查询的时候, pending状态的信息将会首先flushed(被刷新), 而且查询在这之后被立刻执行.

# 创建一个新的载入了User的Query对象, 使用查询可以找到Ed Jsons的字段
the_user = session.query(User).filter_by(name="ed").first()
print(the_user, ed_user is the_user)   # 通过查询得到的对象和刚才添加到Session中的对象完全相同. 内存地址和内容.
# 事实上, Session已经确定返回的行与在其内部对象映射中已经表示的行相同, 因此我们实际上得到了与我们刚添加的相同的实例.

# 这里起作用的ORM概念是identity map和保证所有在一个Session操作中的一个具体行操作都使用同一个数据集.
# 当一个有特定主键的对象存在于Session, 所有的在Session上的SQL查询对这个特殊的主键将总是返回同样的Python对象.
# 并也会弹出一个错误如果尝试在会话中放置具有相同主键的第二个已经持久化的对象.

# 使用add_all()添加更多的User对象
session.add_all([
    User(name='wendy', fullname='Wendy Williams', nickname='windy'),
    User(name='mary', fullname='Mary Contrary', nickname='mary'),
    User(name='fred', fullname='Fred Flintstone', nickname='freddy')
])

# 可以在这个过程中更改User对象的内容
ed_user.nickname = "eddie"
# 当内容被修改了后, 将会引起session的关注, 可以使用session.dirty查看
print(session.dirty)
# 新添加的使用session.new查看
print(session.new)

# 当想要提交这些改变到数据库的时候, 可以通过commit()方法, session对象将会发出UPDATE语句对于修改的字段, INSERT语句对于新增的字段.
session.commit()
# commit()会刷新保存的更改到数据库, 并提交所有的事务.
# 会话引用的连接资源现在返回到连接池.
# 接下来通过这个session的操作将会发起一连串的new事务, 当再被需要时这将会在一次获得连接资源.

print(ed_user.id)   # 先前查看id属性, 其为None, 现在他有值了.
# 在session插入所有新行到数据库中后, 通过立刻地或负载优先访问, 所有新产生的标识符(id)和数据库产生的默认内容在实例上变得可用.
# 在这种情况下, 所有的行都在连接时被重载了, 因为一个新的事务将会在我们翻出commit()后被开启.
# 默认情况下, SQLAlchemy在第一次在新事务中访问时刷新先前事务中的数据, 以便最新状态可用.
# 重新载入的等级可以通过Session配置.


### NOTE: Rolling Back ### 事务回滚
# 当Session在事务中工作时, 可以使用roll back回到以前的工作.
ed_user.name = "Edwardo"
fake_user = User(name="fakeuser", fullname="Invalid", nickname="12345")   # 添加一个用于实验的用户
session.add(fake_user)
search_result = session.query(User).filter(User.name.in_(["Edwardo", "fakeuser"])).all()
print(search_result)   # 新的更改和用户被缓冲进了事务缓冲区
# 进行回退
session.rollback()
print(fake_user in session)   # 回退后, fake_user还在没有在会话中了
search_result = session.query(User).filter(User.name.in_(["ed", "fakeuser"])).all()
print(search_result)   # 再次查询是否存在相关更改和用户, 将会只显示更改前的Ed_user


### NOTE: Querying ### 查询
# 使用Session中的query()方法创建Query对象. 这个方法使用任意数量的参数, 这些参数可以是任何的类组合和instrumented类描述符.
# 下面我们指明一个载入了User实例的Query对象. 通过迭代User对象, 可以得到当前User对象的列表.
for instance in session.query(User).order_by(User.id):
    print(instance.name, instance.fullname)

# Query也可以接受ORM-instrumented描述符作为参数. 
# 任何时候当众多类实体或基于列的实体被作为参数传递给query()方法, 结果将会是一个tuple对象.
for name, fullname in session.query(User.name, User.fullname):
    print(name, fullname)

# 由Query对象返回的tuples是named tuples(collections.namedtuple对象?), 由KeyedTuple类提供支持, 并且可以向Python序列对象一样处理.
# 在namedtuple中的名字是属性的属性名相同, 类的类名相同. 
for row in session.query(User, User.name).all():
    print(row.User, row.name)

# 你可以使用labels()构造函数操纵各列的表达式的名称, 就如同使用sql中的as关键字自定名称.
# 这可用于来自任何ColumnElement驱动的对象, 就和其他有映射的类参数一样.
for row in session.query(User.name.label("name_label")).all():
    print(row.name_label)

# 假设多个实例当前在query()中了, 给予整个实例的名字如User可使用aliased()可以赋予一个完整的映射对象别名.
from sqlalchemy.orm import aliased
user_alias = aliased(User, name="user_alias")
for row in session.query(user_alias, user_alias.name).all():
    print(row.user_alias)

# 使用Query对象的基础操作, 如LIMIT, OFFSET等, 这些大多数可便利的使用Python数组切片和一般与ORDER BY结合的方式实现.
for u in session.query(User).order_by(User.id)[1:3]:
    print(u)
# 过滤结果, 可以使用根据关键字参数来完成的filter_by()方法来实现.
for name, in session.query(User.name).filter_by(fullname="Ed Jones"):
    print(name)
# 过滤结果也可以使用filter()方法, 其使用更灵活的SQL表达式语言构造. 
# 这些允许你在你的映射类中通过类层面上的属性使用通常的Python操作符.
for name, in session.query(User.name).filter(User.fullname=="Ed Jones"):
    print(name)

# Query对象是一个fully generative, 这意味着大多数方法的调用都将会返回一个新的Query对象, 在这之上可以添加其他标准.
# 比如, 通过name"ed"查询和通过fullname"Ed Jones"查询, 你可以使用filter两次, 其向标准中使用AND.
for user in session.query(User).filter(User.name=="ed").filter(User.fullname=="Ed Jones"):
    print(user)

### common Filter Operation ### 常见的filter()方法操作
query = session.query(User)

query.filter(User.name=="ed")   # 相等
query.filter(User.name!="ed")   # 不相等
query.filter(User.name.like("%ed%"))   # like
query.filter(User.name.ilike("%ed%"))  # 忽略大小写的like
query.filter(User.name.in_(["ed", "wendy", "jack"]))    # in
query.filter(User.name.in_(session.query(User.name).filter(User.name.like("%ed%"))))   # 使用in的联合查询
query.filter(~User.name.in_(["ed", "wendy", "jack"]))   # not in
query.filter(User.name==None)   # is null
query.filter(User.name.is_(None))   # is null
query.filter(User.name!=None)   # is not null
query.filter(User.name.isnot(None))   # is not null

from sqlalchemy import and_
query.filter(and_(User.name=="ed"), User.fullname=="Ed Jones")   # 使用特殊函数实现的and
query.filter(User.name=="ed", User.fullname=="Ed Jones")   # 直接通过多参数实现的and
query.filter(User.name=="ed").filter(User.fullname=="Ed Jones")   # 通过链式查询实现的and

from sqlalchemy import or_
query.filter(or_(User.name=="ed", User.name=="wendy"))   # 使用特殊函数实现的or

query.filter(User.name.match("wendy"))   # match, 其使用数据库特定的MATCH或者CONTAINS功能, 因各数据库平台而有差异

### Returning Lists and Scalars ### 返回列表和标量
# 许多在Query对象上的方法立刻发出SQL并返回从连接的数据库查询的值.

query = session.query(User).filter(User.name.like("%ed%")).order_by(User.id)

# all() 返回一个list
print(query.all())

# first() 返回范围内第一个值
print(query.first())

# one() 获取所有的行, 如果结果存在多行(即多个结果)或没有结果, 将会报不同的错
# print(query.one())

# one_or_none() 和one()类似, 但是当没有结果的时候, 不会报错, 而是返回None
# scalar() 调用one(), 成功时返回每行的第一列值

### Using Textual SQL ### 使用文本化的SQL
# Text() 文字串形式的查询能通过text()构造函数灵活的使用在Query()对象上, 这种方式被大多数Query方法接受.
from sqlalchemy import text

for user in session.query(User).filter(text("id<5")).order_by(text("id")).all():
    print(user.name)

# params() 可以使用基于字符串的SQL，使用冒号指定绑定参数。
search_result = session.query(User).filter(text("id<:value and name=:name")).params(value=224, name="fred").order_by(User.id).one()
print(search_result)

# from_statement() 要使用完全基于字符串的语句，可以将表示完整语句的text()构造传递给from_statement().
# 不需要额外指定, 通过名字对应, 在模型中的列将会和在字串形式中的列匹配.
search_result = session.query(User).from_statement(text("SELECT * FROM users where name=:name")).params(name="ed").all()
print(search_result)

# 通过名称匹配列适用于简单的情况, 在处理复杂的包含重复列名或在使用不易于匹配指定名称的匿名ORM构造语句时会变的难以处理.
# 另外的, 当处理结果行时在我们映射的列上进行类型行为,我们将会发现是必要的.
# 在这样的情景下, 对于这些情况, text()构造允许我们将其文本SQL按位置链接到核心或ORM映射的列的表达式上.
# 可以通过传递列表达式作为位置参数给TextClause.columns()来实现这个.
stmt = text("SELECT name, id, fullname, nickname FROM users where name=:name")
stmt = stmt.columns(User.name, User.id, User.fullname, User.nickname)   # text()对象的列对象, 通过位置与字符形式的SQL中的类对应.
search_result = session.query(User).from_statement(stmt).params(name="ed").all()
print(search_result)

# The TextClause.columns() method now accepts column expressions which will be matched positionally to a plain text SQL result set, 
# eliminating the need for column names to match or even be unique in the SQL statement.

# 当使用text()构造进行查询，Query也许仍然可以指定要返回哪些列和实体; 也可以单独请求这些列，而不是query(User)，就像在任何其他情况下一样
stmt = text("SELECT name, id FROM users where name=:name")
stmt = stmt.columns(User.name, User.id)
search_result = session.query(User.id, User.name).from_statement(stmt).params(name="ed").all()

### Count ### 计数
# Query对象的计数方法count()
count_num = session.query(User).filter(User.name.like("%ed")).count()
print(count_num)
# count()方法被用来判断有多少行通过SQL语句返回.
# 通过上面的观察, SQLAlchemy总是将我们查询过的任何内容放入子查询中, 然后计数.
# 但是现代版本的SQLAlchemy不会尝试猜测何时计数合适, 应为可以使用更明确的方法发出确切的SQL.

# 需要独立使用count功能的时候可以从func中取引入, 可以单独对某一列进行统计
from  sqlalchemy import func

count_num = session.query(func.count(User.name), User.name).group_by(User.name).all()
print(count_num)   # 统计每个名字有多少重名的

# SELECT count(*) FROM table;
count_num = session.query(func.count("*")).select_from(User).scalar()
print(count_num)
# 如果直接指定计数主键, 以上select_from可以被省略
count_num = session.query(func.count(User.id)).scalar()
print(count_num)


### NOTE: Building a Relationship ### 创建一个关联关系
# 创建一个和User相关联的邮件地址映射表, 我们系统中的Users通过关联的用户名能存储任何数量的邮件地址.
# 这里将建立一个一对多的关系, User 1 -- Address 多
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class Address(Base):
    __tablename__ = "addresses"
    id = Column(Integer, primary_key=True)
    email_address = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    user = relationship("User", back_populates="addresses")

    def __repr__(self):
        return "<Address email_address: %s; user: %s>" % (self.email_address, self.user.name) 


User.addresses = relationship("Address", order_by=Address.id, back_populates="user")

# 上面的类介绍了ForeignKey构造函数, 它是一个应用于Column的指令, 表明此列中的值应该被constrained(限制), 其值代表了远端相同名字的列.
# 这在关系型数据库中是一个核心功能, 并作为一种粘合剂将相反的没有连接的表集合相互交叠形成丰富的联系.
# ForeignKey表明在addresses.user_id列中的值应该也包含在users.id列中. 即作为user.id的外键.

# orm.relationship()方法告诉ORM使用Address.user属性将Address类和User类相互连接.
# 在Address中的relationship()使用外键关联了两个表, 决定连接的性质, 定义了Address.user是一个many to one的关系.
# 另一个relationship()在User.addresses中, 可以看到在定义完address后, 紧接着动态的向User中添加了一个新的relationship关联列.
# 在两个relationship()指令中, 参数relationship.back_populates被分配附加的属性名给该列, 通过这个, 每一个relationship()可以做出与反向表达的相同关系的智能决策.
# 在另一方面Address.user引用一个User的实例, 同时User.address也引用了一个Address实例的列表.

# 也有个和relationship.back_populates相似的参数, 是relationship.backref, 前者对后者做了一些优化, 这两者将会共存.

# 站在多对一关系相反面的是一对多关系. 
# 这两种互补关系Address.user和User.addresses被引用为双向关系, 这也是SQLAlchemy ORM的关键特征.
# 若Declarative系统在使用时, relationship()的有关远端的类的参数能使用字符串指定.
# 一旦当所有映射完成, 这些字符串的参数将被作为Python表达式, 为了产生实际的参数, 在上面的例子中是User类.
# 在此评估期间允许使用的名称包括根据声明的base创建的所有类的名称.

# FOREIGN KEY 约束在大多数关系型数据库中只能连接到一个主键列或一个UNIQUE约束列
# FOREIGN KEY 约束引用了多个主键列并且本身也有多列, 被叫做复合外键
# FOREIGN KEY 列可以根据自己引用的列或行的变动而自动更新. 这被叫为CASCADE referential action(级联操作), 并且这是由关系型数据库的内建函数完成.
# FOREIGN KEY 可以引用自己所在的表. 这叫做自关联

# 创建addresses表, 将跳过存在的表而创建没有的
Base.metadata.create_all(engine)


### NOTE: Working with Related Objects ### 使用关联表
jack = User(name="jack", fullname="Jack Bean", nickname="gjffdd")
print(jack.addresses)   # 默认返回是一个Python list对象

# 可以自由的将Address对象加入User对象
jack.addresses = [
    Address(email_address="jack@google.com"),
    Address(email_address="j25@yahoo.com")
]

# 当使用双向关联, 元素自动添加并在其定义的其他地方可见.
# 这个行为基于属性on-change事件并由Python完成, 没有使用任何SQL.
print(jack.addresses[1])
print(jack.addresses)

# 让我们使用使用commit添加Jack Bean到数据库. jack和他的两个Address成员同时被添加到了会话中, 使用了一个叫做cascading的进程.
session.add(jack)
session.commit()

# 如果此时使用查询来查找jack, 将会得到jack对象, 不会有sql发出到jack的addresses.
# 当连接到addresses集合, SQL语句将会立刻发出. 这就是lazy loading关系的一个例子. 
# addresses集合当前被载入并表现的像一个有序列表. 
jack_search = session.query(User).filter_by(name="jack").one()
print(jack_search, jack_search.addresses)


### NOTE: Querying with Joins ### 联合查询
# 构建一个简单的隐式的join在User和Address之间, 可以使用Query.filter()连接两者的列.
# 这个就像nature join
for u, a in session.query(User, Address).\
                         filter(User.id==Address.user_id).\
                         filter(Address.email_address.ilike("%jack%")).all():
    print(u, a)


# 使用Query.join() 显示的构建联合查询
search_result = session.query(User).join(Address).\
                        filter(Address.email_address.ilike("%jack%")).all()
print(search_result)

# Query.join()方法知道如何去join User和Address表, 因为User和Address之间是用一个外键进行关联的. 
# 如果没有外键, 或者是多个外键, Query.join(), 直接在join中指定关系连接将会更好.
query = session.query(User)

query.join(Address, User.id==Address.user_id)   # 显示的指定关联关系
query.join(User.addresses)                      # 从左到右指定关系, 左连接?
query.join(Address, User.addresses)             # 显示的指定关联关系
query.join("addresses")                         # 显示指定关联关系就, 使用字符串

# 使用outer join, 使用Query.outerjoin()方法
query.outerjoin(User.addresses)   # 左外部连接 left outer join

# 如果有多个实体, Query将如何选择?
# Query.join()方法一般都会从在实例列表中最左边的项进行join, 当 ON语句被省略, 或 ON语句是一个纯SQL表达式.
# 想要控制第一个join的实例, 使用Query.select_from()方法, 即控制谁作为左连接.
query = session.query(User, Address).select_from(Address).join(User)

# Using Aliases # 
# 使用别名
# 在跨多个表进行查询时，如果需要多次引用同一个表，则SQL通常要求使用其他名称对该表进行别名，以便可以将该表与该表的其他实例区分开来。
# Query支持显式的使用aliased构造.
from sqlalchemy.orm import aliased
adalias1 = aliased(Address)
adalias2 = aliased(Address)
for username, email1, email2 in \
    session.query(User.name, adalias1.email_address, adalias2.email_address).\
    join(adalias1, User.addresses).\
    join(adalias2, User.addresses).\
    filter(adalias1.email_address=="jack@google.com").\
    filter(adalias2.email_address=="j25@yahoo.com"):

    print(username, email1, email2)

""" 
SELECT users.name AS users_name, 
       addresses_1.email_address AS addresses_1_email_address, 
       addresses_2.email_address AS addresses_2_email_address
FROM users 

JOIN addresses AS addresses_1 ON users.id = addresses_1.user_id
JOIN addresses AS addresses_2 ON users.id = addresses_2.user_id

WHERE addresses_1.email_address = ?
AND addresses_2.email_address = ?; 
"""

# Using Subqueries # 
# 使用子查询
# Query对象适用于生成可作为子查询的语句. 
# 支持我们想要的载入User对象统计属于一个每个用户有多少Adress记录计数.
"""
SELECT user.*, adr_count.address_count FROM users

LEFT OUTER JOIN 
   (SELECT user_id, count(*) AS address_count FROM address GROUP By user_id) AS adr_count
ON users.id = adr_count.user_id;
"""
# 使用Query, 从内到外创建一个语句. 
# statement 访问器返回有一个由通常的Query产生的SQL表达式的语句, 这是一个select()构造.
from sqlalchemy import func

stmt = session.query(Address.user_id, func.count("*").label("address_count")).\
               group_by(Address.user_id).\
               subquery()

# func关键字产生SQL方法, Query对象上subquery()方法生成一个SQL表达式构造, 该构造表示嵌入在别名中的SELECT语句(实际上其是query().statement.alias()的缩写)
# 当拥有了我们的语句, 其行为和Table构造相似, 就像一个users表的实例对象.
# 在语句中的列可以通过语句中的c属性进行调取.
for u, count in session.query(User, stmt.c.address_count).\
                        outerjoin(stmt, User.id==stmt.c.user_id).\
                        order_by(User.id):
    print(u, count)
"""
SELECT users.id AS users_id,
        users.name AS users_name,
        users.fullname AS users_fullname,
        users.nickname AS users_nickname,
        anon_1.address_count AS anon_1_address_count
FROM users 

LEFT OUTER JOIN
    (SELECT addresses.user_id AS user_id, count(?) AS address_count
            FROM addresses GROUP BY addresses.user_id) AS anon_1
    ON users.id = anon_1.user_id
ORDER BY users.id;
"""

# Selecting Entities from Subqueries #
# 子查询中的selecting实体
# 在上面的例子中, 只是选择了一个从子查询中包含一列的结果. 如果想要子查询映射到一个实体呢?
# 对于此, 我们使用aliased()来连接一个"alias"作为一个映射类到一个子查询.
stmt = session.query(Address).filter(Address.email_address!="j25@yahoo.com").subquery()
adalias = aliased(Address, alias=stmt)
for user, address in session.query(User, adalias).\
                             join(adalias, User.addresses):
    print(user, address, sep="\n")

"""
SELECT users.id AS users_id,
        users.name AS users_name,
        users.fullname AS users_fullname,
        users.nickname AS users_nickname,
        anon_1.id AS anon_1_id,
        anon_1.email_address AS anon_1_email_address,
        anon_1.user_id AS anon_1_user_id
FROM users 

JOIN
    (SELECT addresses.id AS id,
            addresses.email_address AS email_address,
            addresses.user_id AS user_id
    FROM addresses
    WHERE addresses.email_address != ?) AS anon_1
    ON users.id = anon_1.user_id
"""

# Using EXISTS # 
# 使用EXISTS语句
# 在SQL中的EXISTS关键字是一个布尔操作符, 当给予的表达式包含行时, 将会返回True.
# 其可能会被用在许多的场景中, 例如joins语句中, 查找列是否在关联的表中有值.
from sqlalchemy.sql import exists   # 显式的exists构造

stmt = exists().where(Address.user_id==User.id)
for name, in session.query(User.name).filter(stmt):
    print(name)

"""
SELECT users.name AS users_name FROM users
WHERE EXISTS (SELECT * FROM addresses WHERE addresses.user_id = users.id);
"""

# 一些在Query对象中的操作会自动的使用EXISTS. 例如 any(), has()
# 上个例子就可以使用如下的表达方式.
for name, in session.query(User.name).\
                     filter(User.addresses.any()):
    print(name)

# any()中也可使用查询条件来限制匹配的行
for name, in session.query(User.name).\
                     filter(User.addresses.any(Address.email_address.like("%google%"))):
    print(name)

# has()对多对一关系是一个和any()很相似的操作符(其也适用 ~ , 取反) 
isHas = session.query(Address).filter(~Address.user.has(User.name=="jack")).all()   # address中的user是否有不是用户jack的数据
print(isHas)   # []

# Common Relationship Operators #
# 这些都是建立在关联关系之上的操作符.
query = session.query(Address)
user_object = session.query(User).filter(User.name == "jack")
address_object = session.query(Address).filter(Address.user.name == "jack").first()

# __eq__()   多对一 相等比较
query.filter(Address.user == user_object)
# __ne__()   多对一 不相等比较
query.filter(Address.user != user_object)
# IS NULL   多对一比较, 同样使用 __eq__()
query.filter(Address.user == None)
# contains()   一对多集合
query.filter(User.address.contains(address_object))
# any()   用于集合
query.filter(User.addresses.any(Address.email_address == "bar"))
query.filter(User.addresses.any(email_address = "bar"))   # 使用关键字参数
# has()   用于范围查询
query.filter(Address.user.has(name="ed"))
# Query.with_parent() 用于关联
session.query(Address).with_parent(user_object, "addresses")


### NOTE: Eager Loading ### 贪婪加载
# 在访问User.addresses集合并发出SQL时, 当时说明了一个延迟加载操作.
# 如果想要减少查询的次数, 可以在查询操作中使用一个eager loading(贪婪加载).
# SQLAlchemy提供了三种不同类型的贪婪加载模式. 其中两个是自动的, 另一个涉及自定义一些行为.
# 所有的这三个模式通常通过查询选项的方法进行启用, 贪婪加载会添加额外的指示到Query, 让我们载入我们所希望的不同的属性, 通过Query.options()方法.

# Subquery Load #
# 子查询载入
# 在这个示例中, 想要表明User.addresses应该被贪婪加载.
# 一个对于加载一个对象集合以及他们相关联的集合的好的选择是orm.subqueryload()选项, 其会再次发出SELECT语句用以在已经加载的结果中寻找结果.
# "subquery"的名字来自于SELECT语句构造实际是直接通过Query的再使用, 作为一个子查询被再一次嵌套进一个针对关联表SELECT中.
from sqlalchemy.orm import subqueryload

jack = session.query(User).\
               options(subqueryload(User.addresses)).\
               filter_by(name="jack").one()
print(jack, "\n", jack.addresses)
# 当subqueryload 用于关联限制比如Query.first(), Query.limit()或Query.offset()为了保证正确的结果, 应该同样包含Query.order_by()在一个unique列中

# Joined Load #
# 关联载入
# 另一个更常用的会自动贪婪加载的方法是orm.joinedload(). 
# 该方法的将会发出一个JOIN, 通常是LEFT OUTER JOIN, 所以载入的对象同时和关联的对象或者集合都在一个步骤中被载入.
# 我们用此方法演示相同的载入addresses集合.
# 即使插槽的User.addresses集合在刚刚已被填充, 查询都将发出额外的join
from sqlalchemy.orm import joinedload

jack = session.query(User).\
               options(joinedload(User.addresses)).\
               filter_by(name="jack").one()
print(jack, "\n", jack.addresses)
# 注意, 即使OUTER JOIN 得到的两行结果, 也只返回了一个User对象实例. 这是因为Query将使用"uniquing"策略在返回实体上, 该策略是基于对象身份认证的.
# 这尤其是在关联的贪懒加载时能在没有影响查询结果时被应用.
# joinedload()已经存在了很长时间, subqueryload()是从贪懒加载中新加的.
# 当joinedload()尝试在多对一关系上表现得更好时, subqueryload()尝试更多的链接来载入关联集合, 因为事实上只有一行引导和关联对象被载入.

# joinedload()不能取代join()
# join是由joinedload()创造, 这是一个匿名的别名, 以至于其没有影响查询的结果. 一个Query.order_by()或Query.filter()的调用不能引用这些别名表, 所以调用由Query.join()构成的"user space"(名称空间)joins.
# 这个理由就是为什么joinedload()只能为了影响关联对象或数据集合之间作为一个优化细节被应用, 其在被加入或被移除时是对结果没有影响的.

# Explicit Join + Eagerload # 
# 显式联合+贪婪载入
# 第三种风格的贪懒加载在为了定位主键行显式构建JOIN, 并将会额外使用外部表用以在主键对象上的一个被关联对象或数据集.
# 这个特性通过orm.contains_eager()方法提供, 是对于在一个需要在同一个对象上过滤预加载多对一对象时最典型有用的.
# 以下示例, 我们演示同时载入Address行和关联的User对象, 从User对象的name="jack"上过滤, 并使用orm.contains_eager()来对Address.user属性使用"user"列
from sqlalchemy.orm import contains_eager

jacks_addresses = session.query(Address).\
                          join(Address.user).\
                          filter(User.name=="jack").\
                          options(contains_eager(Address.user)).all()
print(jacks_addresses, "\n", jacks_addresses[0].user)


### NOTE: Deleting ### 删除
# 让我们试着删除jack来看看这是怎么运行的.
# 在session中用deleted标记对象, 然后发出一个count查询直到看见没有结果存在
session.delete(jack)
session.query(User).filter_by(name="jack").count() # 0
# 再来看看jack的Address对象们
session.query(Address).filter(Address.email_address.in_(["jack@google.com", "j25@yahoo.com"])).count() # 2
# 从结果来看, 这些地址是依然存在的, 对应的user_id将会被设置为NULL. 
# SQLAlchemy不会默认采取级联删除, 除非显式的告诉SQLAlchemy.

# Configuring delete/delete-orphan Cascade # 
# 配置删除/删除孤立级联
# 我们将会在User.addresses关系上配置cascade(级联)选项来改变默认的删除方案.
# SQLAlchemy允许动态的在映射关系上添加新的属性, 在这里的例子中需要将存在的表间关系移除, 所以我们需要彻底的移除映射关系并重启. 我们要关闭Session.
session.close()   # 关闭session
Base = declarative_base()   # 使用一个新的Declarative base class

# 在定义User类, 向addresses关联关系加入包含cascade配置的属性.
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    nickname = Column(String)

    addresses = relationship("Address", back_populates="user", cascade="all, delete, delete-orphan")   # 配置级联, 删除孤立数据

    def __repr__(self):
        return "<User(name=%s, fullname=%s, nickname=%s)>" % (self.name, self.fullname, self.nickname)


# 重新创建Address. 通过已有的User类创建Address.user
class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True)
    email_address = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"))   # 外键

    user = relationship("User", back_populates="addresses")

    def __repr__(self):
        return "<Address(email_address=%s)>" % self.email_address

# 这样当删除User中的记录的时候, 对应的Address中的用户记录也会一同删除
jack = session.query(User). get(5)   # 通过主键载入jack
del jack.addresses[1]   # 移除一个Address(延迟负载触发)

search_result = session.query(Address).filter(Address.email_address.in_(["jack@google.com", "j25@yahoo.com"])).count()
print(search_result)   # 1, 将会只有一个存在

# 删除jack将会同时删除Jack和存在关联的Address.
session.delete(jack)
search_result = session.query(User).filter_by(name=="jack").count()
print(search_result)   # 0
search_result = session.query(Address).filter(Address.email_address.in_(["jack@google.com", "j25@yahoo.com"])).count()
print(search_result)   # 0

# 更多关于级联 https://docs.sqlalchemy.org/en/rel_1_2/orm/cascades.html#unitofwork-cascades
# 级联功能也能通过关系数据库的ON DELETE CASCADE功能顺利整合.

# 使用all, delete-orphan, 不会删除对应的相关数据, 但是在查询中将会不可见.


### NOTE: Bulding a Many To Many Relationship ### 建立一个多对多关系
# 接下来我们将会来创建一个博客应用, 用户们可以书写多个BlogPost(博客文章, 多对一), 并且这些BlogPost有多个Keyword(标签)项和他相连(多对多).
# 对于一个简单的多对多关系, 需要创建一个没有映射Table构造用以连接表.
from sqlalchemy import Table, Text
# 博客标签对应表, 用以和博客文章相关联, 联合主键
post_keywords = Table('post_keywords', Base.metadata,
    Column("post_id", ForeignKey("postd.id"), primary_key=True),
    Column("keyword_id", ForeignKey("keywords.id"), primary_key=True)
)
# 通过以上直接声明一个Table, 可以看出这和声明一个映射类有所不同. 
# Table是一个构造函数, 所以每一个独立的Column参数数都被逗号分割. 
# Column对象也被显式的命名, 而不是用指定的变量的名称.

# 接下来使用另外的relationship()构造函数定义BlogPost和Keyword, 每一个引用到post_keywords表的, 都将作为一个连接表.
class BlogPost(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    headline = Column(String(255), nullable=False)
    body = Column(Text)

    # 多对多 Blog <-> Keyword
    keywords = relationship("Keyword",
                            secondary=post_keywords,   # relationship中使用secondary
                            back_populates="posts")

    def __init__(self, headline, body, author):
        self.author = author
        self.headline = headline
        self.body = body

    def __repr__(self):
        return "BlogPost(%r, %r, %r)" % (self.headline, self.body, self.author)


class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True)
    keyword = Column(String(50), nullable=False, unique=True)
    posts = relationship("BlogPost",
                         secondary=post_keywords,   # relationship中使用secondary
                         back_populates="keywords")
    
    def __init__(self, keyword):
        self.keyword = keyword
# 以上两个类的声明都显式的使用了__init__方法. 记住, 当使用Declarative的时候, 这是可选的.

# 多对多关系是BlogPost.keywords. 一个多对多关系定义的特征是使用secondary关键字参数, 其可以应用一个代表连接表的Table对象.
# 这个表只单单包含关系两边表各自引用到的列; 如果其有任何其他的列, 比如其自身的主键或者其他表的外键, SQLAlchemy需要一个不同的使用模式叫做"association object".
# association Object https://docs.sqlalchemy.org/en/rel_1_2/orm/basic_relationships.html#association-pattern

# 我们同样需要我们的BlogPost类有一个author字段.
# 我们将添加这个字段作为另一个双向连接关系, 排除了这个问题, 我们的一个用户就可以有多个博客帖.
# 当我们连接到User.posts时, 我们将会能够进一步的过滤结果, 这样就不用载入完整的实例.
# 对于这个目的, 我们使用一个relationship()的设置叫做lazy="dynamic", 通过这个参数配置一个可选的载入策略.
BlogPost.author = relationship(User, back_populates="posts")
User.posts = relationship(BlogPost, back_populates="author", lazy="dynamic")

Base.metadata.create_all(engine)

# 向其中添加数据
wendy = session.query(User).filter_by(name="wendy").one()
post = BlogPost("Wendy's Blog", "This is the body", wendy)
session.add(post)

# 向标签表中创建数据
post.keywords.append(Keyword("wendy"))
post.keywords.append(Keyword("firstpost"))

# 产看是否有博客具有firstpost标签
search_result = session.query(BlogPost).\
    filter(BlogPost.keywords.any(Keyword="firstpost")).all()
print(search_result)

# 查看wnedy的有firstpost标签博客
search_result = session.query(BlogPost).\
                        filter(BlogPost.author==wendy).\
                        filter(BlogPost.keywords.any(Keyword="firstpost")).all()
print(search_result)

search_result = wendy.posts.filter(BlogPost.keywords.any(keyword="firstpost")).all()
print(search_result)

