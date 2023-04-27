

# Fastapi 巡轨系统后台
提供两种方式，开发请用源码运行，部署使用打包的exe
## 源码运行

### Prerequisites

- Python 3.8.6 or higher
- FastAPI
- Docker

### Project setup

```sh
# move to the project folder
$ cd DogeAPImetro
```

### Dependencies
安装python依赖

```sh

# install all dependencies
$ pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

```

### Running the Application
启动后台服务
```sh
# Running the application using uvicorn
$ python main.py
```

### Configuration
修改.env文件

```
#服务器ip
HOST=127.0.0.1  
#服务器端口
PORT=8800
#redis 地址
REDIS_URL=192.168.50.165
#redis 端口
REDIS_PORT=6379
#使用mysql设置为True
MYSQL=False
#mysql地址 root为账号 123456为密码 3306为数据库端口
BASE_MYSQL='mysql+pymysql://root:123456@localhost:3306/'
```
最后重新运行
```sh
$ python main.py
```
数据库配置
添加索引
ALTER TABLE meas_hz10_002  ADD UNIQUE(timestamp);
删除重复行
SELECT * FROM abnorm_hz10_002 GROUP BY timestamp HAVING  COUNT(timestamp)>1;
导出数据库表
https://product.pconline.com.cn/itbk/wlbg/office/1709/9955096.html
    mysqldump -uroot -padmin pan_std meas_hz10_002 --where="timestamp>1675220345000" >q2.sql
     mysqldump -uroot -padmin pan_std train_info  >q2.sql

DELETE t1 FROM abnorm_hz10_002 t1 INNER JOIN abnorm_hz10_002 t2 WHERE t1.timestamp = t2.timestamp;

delete from abnorm_hz10_002 where id not in (
    select t.max_id from
    (select max(id) as max_id from abnorm_hz10_002 group by timestamp) as t
    );

## package exe
python -m nuitka --standalone --mingw64 --show-memory --show-progress --nofollow-imports --include-package=uvicorn --include-package=click --include-package=h11 --include-package=starlette --include-package=fastapi --include-data-files=.env=.env --include-data-dir=static=static --include-data-dir=templates=templates --include-data-files=hz4_anchor_dl.csv=hz4_anchor_dl.csv --include-data-files=hz4_anchor_ul.csv=hz4_anchor_ul.csv  --windows-icon-from-ico=metro.ico --output-dir=out main.py


python -m nuitka --standalone  --mingw64 --show-memory --show-progress --nofollow-import-to=sqlalchemy --nofollow-import-to=numpy --nofollow-import-to=pandas --nofollow-import-to=scipy --include-package=uvicorn --include-package=click --include-package=h11 --include-package=starlette --include-package=fastapi --include-data-files=.env=.env --include-data-dir=static=static --include-data-dir=templates=templates --include-data-files=anchor_dl.csv=anchor_dl.csv --include-data-files=anchor_ul.csv=anchor_ul.csv  --windows-icon-from-ico=metro.ico --output-dir=out main.py

## exe运行

exe文件夹：outs/main.dist

### 方法
拷贝exe文件夹到目标电脑，配置.env 文件内容
主要是Mysql数据库的配置
BASE_MYSQL='mysql+pymysql://root:123456@localhost:3306/standard'