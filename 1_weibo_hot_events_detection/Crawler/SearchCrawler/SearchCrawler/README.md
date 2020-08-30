# SearchCrawler
---
## 模块介绍 ##
SearchCrawler是一个由Python 2.7编写的基于安卓手机端破解API的新浪微博网络爬虫。本爬虫程序以一组关键字作为程序输入，对每一个关键字，其调用新浪微博搜索引擎获取对应的热门微博。
## 模块功能 ##
本爬虫功能单一，仅致力于微博关键字的爬取，其算法逻辑主要封装在crawler.py文件中，main.py是其功能启动脚本。在数据库中配置好需要跟踪的关键字，正确启动爬虫之后，程序访问数据库获取爬取关键字列表，然后调用新浪微博搜索引擎对关键字逐个进行搜索，并获取对应的热门微博，解析提取数据后，持久化到数据库。对关键字列表轮询完一圈后，程序会检查数据库以更新关键字列表，并进入下一轮轮询。
## 模块部署 ##
### 服务器配置 ###
安装Python 2.7和MySQL服务，推荐使用Anaconda以及MySQL 5.6以上。
### 数据库配置 ###
 建立如下的表结构：
 
 - 表 accounts (新浪微博帐号信息表)
<table>
<tbody>
<tr><td><em>属性</em></td><td><em>数据类型</em></td><td><em>描述说明</em></td></tr>
<tr><td>username</td><td>varchar(30)</td><td>微博帐号用户名</td></tr>
<tr><td>password</td><td>varchar(30)</td><td>微博帐号密码</td></tr>
<tr><td>s</td><td>varchar(30)</td><td>微博帐号唯一性标识符</td></tr>
<tr><td>gsid</td><td>varchar(100)</td><td>微博帐号唯一性标识符</td></tr>
<tr><td>cid</td><td>int(11)</td><td>爬虫ID，Crawler ID</td></tr>
</tbody>
</table>
说明：s和gsid是构成API的核心参数，帐号的唯一性由这两个参数的组合决定；另一个重要的属性cid则指定了其工作爬虫的编号，如cid=2的帐号是为2号爬虫准备的。关于s和gsid的抽取方法在文末给出。

- 表 keywords
<table>
<tbody>
<tr><td><em>属性</em></td><td><em>数据类型</em></td><td><em>描述说明</em></td></tr>
<tr><td>keyword</td><td>varchar(50)</td><td>关键字内容</td></tr>
<tr><td>cid</td><td>int(11)</td><td>爬虫ID，Crawler ID</td></tr>
<tr><td>score</td><td>int(255)</td><td>突发分数</td></tr>
<tr><td>timestamp</td><td>datetime</td><td>检测时间</td></tr>
</tbody>
</table>
说明：cid的作用同account的cid一样，都是为了对应分配给正确的爬虫；score相当于关键字的权值，爬虫会优先轮询权值大的关键字；timestamp是关键字被检测出来的时间点。

- 表 timelines
<table>
<tbody>
<tr><td><em>属性</em></td><td><em>数据类型</em></td><td><em>描述说明</em></td></tr>
<tr><td>mid</td><td>bigint(20)</td><td>微博内容ID</td></tr>
<tr><td>encrypted_mid</td><td>varchar(20)</td><td>加密的微博ID</td></tr>
<tr><td>uid</td><td>bigint(20)</td><td>微博用户ID</td></tr>
<tr><td>screen_name</td><td>varchar(50)</td><td>用户昵称</td></tr>
<tr><td>text</td><td>varchar(2048)</td><td>微博内容</td></tr>
<tr><td>app_source</td><td>varchar(100)</td><td>微博客户端</td></tr>
<tr><td>created_at</td><td>datetime</td><td>微博发布日期</td></tr>
<tr><td>attitudes</td><td>int(11)</td><td>点赞数</td></tr>
<tr><td>comments</td><td>int(11)</td><td>评论数</td></tr>
<tr><td>reposts</td><td>int(11)</td><td>转发数</td></tr>
<tr><td>pic_urls</td><td>varchar(1024)</td><td>图片url</td></tr>
<tr><td>json</td><td>mediumtext</td><td>全部备份信息</td></tr>
<tr><td>timestamp</td><td>datetime</td><td>爬取时间</td></tr>
<tr><td>omid</td><td>bigint(20)</td><td>源微博内容ID</td></tr>
</tbody>
</table>
说明：encrypted_mid是合成该微博具体url的关键；json字段保留了爬取的所有内容，如有需求的字段属性不在本表中，可以考虑深入研究json数据包。

### 源代码配置 ###
由上述内容可知，accounts和keywords是爬虫的输入，而timelines是爬虫的输出。源代码的配置主要做两件事，一个是连接输入和输出，另一个是确立爬虫的具体行为。对于源代码的配置，出于封装性的考量，所有的定制行为都在configs.py(工程主目录下)中被定义。

连接输入输出主要是通过cid这个属性，所以为了使程序正确运行，要将configs.py中的CRAWLER_ID设置为其所分配到的account以及keywords的cid，同时通过将DB_TABLES['timelines']的值设为对应timelines的表名，来确定输出的数据表。值得注意的是，MONITOR_TIME_SPAN这个参数是关键字被监控的时间跨度，如MONITOR_TIME_SPAN = 7意味着该关键字在7日后，将不被爬虫爬取。

所有参数如下：
<table>
<tbody>
<tr><td><em>参数</em></td><td><em>默认值</em></td><td><em>描述说明</em></td></tr>
<tr><td>ACC_ACCESS_LIMIT</td><td>800</td><td>帐号固定时间内访问API次数</td></tr>
<tr><td>ACC_RESET_TIME</td><td>3600</td><td>单位秒，帐号访问限制固定时长</td></tr>
<tr><td>ACC_MIN_NUM</td><td>15</td><td>爬虫最小运行帐号数</td></tr>
<tr><td>ACC_MAX_NUM</td><td>20</td><td>爬虫最大运行账号数</td></tr>
<tr><td>MONITOR_TIME_SPAN</td><td>Null</td><td>关键字监控时长</td></tr>
<tr><td>CRAWLER_ID</td><td>Null</td><td>爬虫ID</td></tr>
<tr><td>DB_USER</td><td>Null</td><td>数据库用户名</td></tr>
<tr><td>DB_PASSWD</td><td>Null</td><td>数据库密码</td></tr>
<tr><td>DB_HOST</td><td>Null</td><td>数据库主机IP地址</td></tr>
<tr><td>DB_DATABASE</td><td>Null</td><td>数据库名称</td></tr>
<tr><td>DB_CHARSET</td><td>Null</td><td>数据库字符集</td></tr>
<tr><td>DB_TABLES</td><td>Null</td><td>数据库ORM映射关系</td></tr>
</tbody>
</table>
补充说明：

 - 默认值为Null表示该参数需根据具体需求指定；
 - 单帐号建议一小时访问API次数不要超过800次，默认参数已给出；
 - 本模块没有类似于DynamicCrawler中的帐号管理机制，所以需要手工管理帐号；
 - 经验上讲，一个关键字最多只有50页相关微博，且时间上只能回溯一个月。
 
### API破解 ###
 - 准备材料：
   - 抓包工具：charles、fiddler等
   - 微博帐号：[淘宝买吧][1]
   - 安卓微博客户端：使用安卓手机或者安卓虚拟机安装新浪微博
 
 - 抓包过程：用淘宝小号登录安卓客户端，模拟人类使用，使用抓包工具捕捉（[以charles为例，点击进入教程][2]）类似`http://wbapp.mobile.sina.cn/interface/f/ttt/v3/wbcontentad.php?c=android&i=613af9c&s=9363732e&ua=samsung-SAMSUNG-SM-N900A__weibo__6.3.0__android__android4.4.4&wm=2468_1001&aid=01AkhVappryyFI-Jda5ZBQExSpHqot5FKSVhhY01e3_iBKnck.&from=1063095010&gsid=_2A256ky58DeTxGeNH41YZ9CnNyTuIHXVXCSa0rDV6PUJbkdAKLW3MkWoIIOPCgpWS5Yrt-Wbeq3t1i8WWXQ..&lang=zh_CN&size=720&skin=normal&wifi=1&category=content&oldwm=2468_1001&sflag=1&platform=android`这样的url，提取其中的s和gsid。

  [1]: https://item.taobao.com/item.htm?spm=a230r.1.14.1.zNXAhX&id=533824091791&ns=1&abbucket=5#detail
  [2]: https://yq.aliyun.com/articles/36031
  
## 后记 ##
这个模块于DynamicCrawler之后被开发出来，功能较之前者略显单薄，但代码结构更加清晰。使用过程中如遇问题，可以联系我626058038@qq.com，我不知道你看到这个邮箱是不是习惯性地鄙视了下我😒噢吼吼～