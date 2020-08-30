DynamicCrawler
==

## 模块介绍 ##
DynamicCrawler是一个基于新浪微博安卓手机端破解API的简易分布式网络爬虫。实现本模块的编程语言是Python 2.7，其中应用的主要程序模块包括urllib2（http客户端）、json（数据解析）和sqlalchemy（ORM，数据持久化）等。本模块的输入是新浪微博用户的UID（User ID），输出则是对应用户所发布的微博内容（Timeline）以及其档案信息（Profile）。
## 模块功能 ##
DynamicCrawler的主要功能如下：

 1. 普通监控
 2. 强化监控 
 3. 档案获取
 4. 历史回溯
 5. 数据迁徙

### 普通监控 ###
普通监控是DynamicCrawler的基础功能，也是本模块的核心功能之一。

给定一组UID作为数据输入，爬虫在固定时间窗口内，对所有用户所发布的最新微博内容进行爬取。此过程不断重复，通过这种轮询机制，实现了对给定用户的微博监控。
### 强化监控 ###
作为普通监控数据输入的用户UID数目一般较大，一圈轮询可能导致系统获取数据的及时性降低，因此，我们引入了强化监控的机制。

在普通监控的过程中，如果爬虫发觉当前所监控的用户组，在短期内有事件爆发的趋势（即短时间内用户持续发布新微博），其就向主节点发起一个警报，部署了强化监控的子节点收到这个警报后，便开始增援发出警报的普通监控节点，即多个强化监控子节点将发出警报的普通监控子节点的监控用户均分，然后开始各自的小轮询。值得注意的是，强化监控的过程不是永续不断的，而是经过一段时间的衰减，当发出警报的普通监控节点解除了该警报后，强化节点则随之停止增援行动，进入等待模式，静候下一个警报。
### 档案获取 ###
档案获取是DynamicCrawler的一个附加功能，主要用来获取指定用户的档案信息（Profile Information），这个过程是一次性的。
### 历史回溯 ###
历史回溯主要是用来获取指定用户从某个时间点开始到当前时间的所有微博内容，其也是本爬虫的一个附属功能。
### 数据迁徙 ###
爬虫持续运行一段时间后，存储微博数据的数据表越来越大，由于索引的存在，写入效率与读取效率都将有所降低，因此，数据迁徙用来定时将“过气”的微博转移到数据备份表，使得数据表维持在一个固定的大小水平，保持数据库读写效率不致降低。
## 模块部署 ##
DynamicCrawler运行的具体行为主要由工程目录下的Configuration.py文件中的配置属性所定义。
### 初始化配置 ###

 - 计算环境配置：确保计算机安装有Python 2.7，推荐使用Anaconda，相关第三方类库，如bs4、pymysql以及sqlalchemy等，可以通过在运行具体脚本时解释器提示的Import Error来确定。
 - 数据库表结构：确保计算机安装有Mysql服务。target_users表是分配监控用户的数据表；uid确定用户身份；domain和subdomain是所分配爬虫的ID，比如某用户domain=2，subdomain=3，其就由2号普通监控爬虫监控，当触发了2号普通爬虫的警报之后，此用户又同时被3号强化监控爬虫监控。account_parameters表是存储新浪微博帐号数据的表，因为要利用破解的API访问新浪，所以在爬虫运行前，需要确保此表中有数据，其中i，s以及gsid决定一个微博帐号的唯一性，而domain是爬虫分配资源ID，即domain=i的帐号分配给i号爬虫使用。更多表结构以及字段说明在附表中给出。
 - 代码配置文件：Configuration.py是本爬虫的配置文件，DB_USER是数据库用户名，DB_PASSWD是数据库用户对应密码，DB_DATABASE是数据名称，DB_HOST是数据库主机IP地址。更多配置属性说明在附表中给出。

### 功能脚本配置 ###

 - 普通监控：在Configuration.py中，DOMAIN指定了节点作为普通监控的爬虫ID，同时其所分配得的新浪用户帐号资源也由DOMAIN指定，而monitor_targert_users.py是普通监控的启动脚本。
 - 强化监控：在Configuration.py中，DOMAIN2指定了强化监控爬虫分配的新浪微博帐号资源，而SUBDOMAIN则如上述的，指定了强化监控爬虫所监控的用户名单。reinforce_monitoring.py则是强化监控的启动脚本。
 - 档案获取：在Configuration.py中，DOMAIN3指定了新浪微博帐号资源，即其调用Domain=DOMAIN3的account_parameters进行用户档案信息的爬取。get_profiles.py是档案获取的启动脚本。
 - 历史回溯：在Configuration.py中，DOMAIN3指定了新浪微博帐号资源；MIN_DM和MAX_DM分别指定爬取用户domain的上下界，比如MIN_DM=2，MAX_DM=5，则爬虫爬取domain=2，3，4，5的用户的历史数据；TIMELINE_EARLIEST_DATETIME则指定了历史回溯的时间点。fetch_history_timelines.py是历史回溯的启动脚本。
 - 数据迁徙：在Configuration.py中，TIMELINE_LIVE_INTERVAL指定了两次迁徙操作的时间间隔；TIMELINE_MIGRATION_LIMIT指定了数据库记录批操作的数据量；TIMELINE_MIGRATION_CLOCK则指定了迁徙任务执行的时间。migrate_timelines_by_schedule.py是数据迁徙的启动脚本。
 
## 附表 ##
### 数据库表结构 ###
 - 表 account_parameters
<table>
<tbody>
<tr><td><em>属性</em></td><td><em>数据类型</em></td><td><em>描述</em></td></tr>
<tr><td>i</td><td>varchar(45)</td><td>帐号唯一性标识</td></tr>
<tr><td>s</td><td>varchar(45)</td><td>帐号唯一性标识</td></tr>
<tr><td>gsid</td><td>varchar(155)</td><td>帐号唯一性标识</td></tr>
<tr><td>domain</td><td>int(11)</td><td>所分配爬虫ID号</td></tr>
<tr><td>account</td><td>varchar(100)</td><td>主键，微博帐号名</td></tr>
<tr><td>passwd</td><td>varchar(100)</td><td>微博帐号密码</td></tr>
</tbody>
</table>
- 表 alarms
<table>
<tbody>
<tr><td><em>属性</em></td><td><em>数据类型</em></td><td><em>描述</em></td></tr>
<tr><td>domain</td><td>int(11)</td><td>主键，发出警报的爬虫ID</td></tr>
<tr><td>is_on</td><td>int(11)</td><td>警报是否开启，1表示开启，0表示关闭</td></tr>
<tr><td>launch_time</td><td>datetime</td><td>警报开启时间</td></tr>
</tbody>
</table>
- 表 target_users
<table>
<tbody>
<tr><td><em>属性</em></td><td><em>数据类型</em></td><td><em>描述</em></td></tr>
<tr><td>uid</td><td>varchar(45)</td><td>主键，新浪微博用户ID</td></tr>
<tr><td>weight</td><td>int(11)</td><td>用户权重，保留字段</td></tr>
<tr><td>domain</td><td>int(11)</td><td>普通监控分配ID</td></tr>
<tr><td>subdomain</td><td>int(11)</td><td>强化监控分配ID</td></tr>
</tbody>
</table>
- 表 timelines
<table>
<tbody>
<tr><td><em>属性</em></td><td><em>数据类型</em></td><td><em>描述</em></td></tr>
<tr><td>mid</td><td>bigint(20)</td><td>主键，微博ID</td></tr>
<tr><td>uid</td><td>bigint(20)</td><td>微博用户ID</td></tr>
<tr><td>name</td><td>varchar(30)</td><td>微博用户昵称</td></tr>
<tr><td>omid</td><td>bigint(20)</td><td>源微博ID</td></tr>
<tr><td>ouid</td><td>bigint(20)</td><td>源微博用户ID</td></tr>
<tr><td>oname</td><td>varchar(30)</td><td>源微博用户昵称</td></tr>
<tr><td>text</td><td>varchar(1024)</td><td>微博文本内容</td></tr>
<tr><td>pic_url</td><td>varchar(1024)</td><td>微博图片URL</td></tr>
<tr><td>app_source</td><td>varchar(45)</td><td>微博客户端</td></tr>
<tr><td>created_at</td><td>datetime</td><td>微博创建时间</td></tr>
<tr><td>repost_num</td><td>int(11)</td><td>微博转发数</td></tr>
<tr><td>favourite_num</td><td>int(11)</td><td>微博点赞数</td></tr>
<tr><td>comment_num</td><td>int(11)</td><td>微博评论数</td></tr>
<tr><td>geo_info</td><td>varchar(75)</td><td>地理位置信息</td></tr>
<tr><td>timestamp</td><td>datetime</td><td>爬取时间</td></tr>
</tbody>
</table>
- 表 users
<table>
<tbody>
<tr><td><em>属性</em></td><td><em>数据类型</em></td><td><em>描述</em></td></tr>
<tr><td>id</td><td>bigint(20)</td><td>主键，用户ID</td></tr>
<tr><td>screen_name</td><td>varchar(255)</td><td>用户昵称</td></tr>
<tr><td>avatar</td><td>varchar(255)</td><td>头像URL</td></tr>
<tr><td>description</td><td>varchar(1024)</td><td>用户描述信息</td></tr>
<tr><td>created_at</td><td>datetime</td><td>用户创建时间</td></tr>
<tr><td>gender</td><td>varchar(255)</td><td>性别</td></tr>
<tr><td>follower_num</td><td>int(11)</td><td>粉丝数</td></tr>
<tr><td>followee_num</td><td>int(11)</td><td>关注数</td></tr>
<tr><td>weibo_num</td><td>int(11)</td><td>微博数</td></tr>
<tr><td>level</td><td>int(255)</td><td>微博等级</td></tr>
<tr><td>location</td><td>varchar(255)</td><td>用户所在地区</td></tr>
<tr><td>credit_score</td><td>int(11)</td><td>信用积分</td></tr>
<tr><td>domain</td><td>varchar(255)</td><td>用户个性域名</td></tr>
<tr><td>vip_level</td><td>int(11)</td><td>VIP等级</td></tr>
<tr><td>verified</td><td>int(255)</td><td>是否认证用户</td></tr>
<tr><td>verified_reason</td><td>varchar(510)</td><td>认证原因</td></tr>
<tr><td>tags</td><td>varchar(510)</td><td>用户标签</td></tr>
<tr><td>badges</td><td>varchar(510)</td><td>用户徽章</td></tr>
<tr><td>name</td><td>varchar(255)</td><td>用户真实姓名，一般为昵称</td></tr>
<tr><td>json</td><td>text</td><td>全部备份信息</td></tr>
<tr><td>timestamp</td><td>datetime</td><td>爬取时间</td></tr>
</tbody>
</table>

### 配置文件属性 ###
Configuration.py
<table>
<tbody>
<tr><td><em>变量</em></td><td><em>默认值 </em></td><td><em>说明</em></td></tr>
<tr><td>TIME_WINDOW</td><td>10 mins</td><td>警报阈值时间窗口</td></tr>
<tr><td>LOOP_TIME</td><td>70 mins</td><td>轮询时间窗口</td></tr>
<tr><td>DECAY_TIME</td><td>3 * TIME_WINDOW</td><td>警报衰退时间</td></tr>
<tr><td>BUFFER_LIMIT</td><td>300</td><td>缓存微博条数</td></tr>
<tr><td>BUFFER_LIMIT_LARGE</td><td>3000</td><td>缓存微博条数（大）</td></tr>
<tr><td>BUFFER_LIMIT_MINI</td><td>600</td><td>缓存微博条数（小）</td></tr>
<tr><td>PROFILE_BUFFER_LIMIT</td><td>5000</td><td>缓存档案数目（普通监控）</td></tr>
<tr><td>PROFILE_LIMIT</td><td>100</td><td>缓存档案数目（档案获取）</td></tr>
<tr><td>ACCOUNT_LIMIT</td><td>15</td><td>最小运行帐号数目</td></tr>
<tr><td>TIMELINE_EARLIEST_DATETIME</td><td>NA</td><td>历史微博回溯时间点</td></tr>
<tr><td>TIMELINE_LIVE_INTERVAL</td><td>1</td><td>数据迁徙操作间隔时间（天）</td></tr>
<tr><td>TIMELINE_MIGRATION_LIMIT</td><td>5000</td><td>数据迁徙批处理微博数</td></tr>
<tr><td>TIMELINE_MIGRATION_CLOCK</td><td>1</td><td>数据迁徙脚本运行时间</td></tr>
<tr><td>ACCOUNT_NUM</td><td>20</td><td>初始化微博帐号数目</td></tr>
<tr><td>DOMAIN</td><td>NA</td><td>普通监控帐号以及目标分配ID</td></tr>
<tr><td>DOMAIN2</td><td>NA</td><td>强化监控帐号分配ID</td></tr>
<tr><td>SUBDOMAIN</td><td>NA</td><td>强化监控目标分配ID</td></tr>
<tr><td>DOMAIN3</td><td>NA</td><td>档案获取以及历史回溯帐号分配ID</td></tr>
<tr><td>MIN_DM</td><td>NA</td><td>历史回溯目标任务分配ID下界</td></tr>
<tr><td>MAX_DM</td><td>NA</td><td>历史回溯目标任务分配ID上界</td></tr>
<tr><td>ACCESS_LIMIT</td><td>800</td><td>微博帐号每小时最大访问次数</td></tr>
<tr><td>ACCESS_TIME_WINDOW</td><td>60 mins</td><td>帐号访问次数reset时间</td></tr>
<tr><td>THRESHOLD</td><td>150</td><td>报警阈值，即TIME_WINDOW内用户所发微博最大数</td></tr>
<tr><td>DB_USER</td><td>NA</td><td>数据库用户名</td></tr>
<tr><td>DB_PASSWD</td><td>NA</td><td>数据库用户密码</td></tr>
<tr><td>DB_DATABASE</td><td>NA</td><td>数据库数据库名</td></tr>
<tr><td>DB_HOST</td><td>NA</td><td>数据库主机IP地址</td></tr>
<tr><td>DB_CHARSET</td><td>utf8mb4</td><td>数据库字符集</td></tr>
<tr><td>DB_TABLES</td><td>NA</td><td>ORM对映数据库表名关系</td></tr>
</tbody>
</table>

## 注意事项 ##

 1. account_parameters中domain为0，意味着该帐号可用，所以，为了模块的正常运行，应保证domain为0的帐号资源充足，经验上讲，建议保障每个节点都能分到20个以上的帐号。
 2. 列出的所有配置文件属性中，默认值为NA的，需要根据实际情况填写，其余则建议暂时采用默认值，之后有了更多的运行经验再考虑调整。
 3. 运行一段时间后，有些帐号会被新浪封掉。被封的帐号主要分为两类：a）短期封禁和b）永久封禁。对于a）类帐号，程序会将其domain暂时设为403，一段时间后，自动转化为0，照常使用；而对于b）类帐号，程序会对其domain取负数，比如domain=7的变成domain=-7，其意味着该帐号永久性被封，除非你绑定手机。
 4. 关于DB_TABLES，其是一个python的字典，你主要通过修改不同key的value来实现对程序的操控：
 `DB_TABLES = {
    'account_parameters': 'account_parameters',
    'target_users': 'target_users',
    'timelines': 'timelines_live',
    'alarms': 'alarms',
    'test_merge': 'test_merge',
    'users': 'users',
    'history_timelines': 'timelines_161102'
}`
以此为例，DB_TABLES['account_parameters']指定微博帐号来源表，因此如果你数据库中将表account_parameters改名成accounts，此处则应对应改为'account_parameters': 'accounts'。值得注意的是key值'timelines'和'history_timelines'分别指定了微博输出表以及微博备份表。最后你应该删除'test_merge': 'test_merge'以及Database.py中TestMerge这个类，否则你必须在你的数据中建立对应的TestMerge表。
 5. 关于如何获取account_parameters的问题，可以查阅相关文档，此处不再赘述。
 6. 此模块设计尚存许多缺陷，在使用过程中如遇问题可以联系我[626058038@qq.com]，行文草率，恐难以周全，在此致歉。


  