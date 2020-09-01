import pymysql
pymysql.version_info = (1, 4, 13, "final", 0)
pymysql.install_as_MySQLdb()  # 使用pymysql代替mysqldb连接数据库

# python3 以上的使用pymysql 需要这样来配置  ，还有一个2.0的坑是关于MySQL连接的