# weibo_data_crawler
# 新浪微博数据爬取
该项目使用mongodb进行数据存储，使用selenium，phantomjs,python进程，gevent协程技术来完成新浪微博数据爬取
## 环境配置
首先需要安装mongodb
进行项目目录下运行`./install.sh`完成环境配置
修改getuer.py中的用户名密码,运行即可完成新浪微博数据的爬取。
##局限性
新浪微博用户访问非自己的关注或粉丝的主页的时候，只能查看其五页的粉丝或关注，因此人物关系网不能完成获取，不过可以根据这暴露出来的用户id，继续爬取数据。