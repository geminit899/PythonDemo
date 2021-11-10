该算法包用于，从数据库读取所有目标点，对每一个目标点构建15分钟可达区域，获取可达区域边界组成点，获取可达区域内所有目标点ID，并存入数据库。

主类是main.py，配置项在conf.py，如Oracle数据库配置、AK配置等。
使用命令 nohup python main.py & echo $! > service.pid 即可运行。
使用 cat service.pid 获取进程ID，使用 kill -9 进程ID 即可停止。

运行前准备：
一、python版本：3.6.0，需要安装依赖：
    pandas       0.25.3
    requests     2.26.0
    cx_oracle    8.2.1
    alphashape   1.3.1

二、python连接Oracle数据库，不仅要按照 cx_oracle 。还需要按照 Oracle 客户端。
    首先在 https://www.oracle.com/database/technologies/instant-client/downloads.html 下载对应包
    然后解压下载的包，并将其解压后路径加到环境变量中即可。

三、确认数据库中的表都已建好，且至少包含以下关键字段：
MAP_POINT表:
    ID:       VARCHAR2(64)       "存储点ID，唯一标识"
    LAT:      NUMBER(15,11)      "存储点经度"
    LNG:      NUMBER(15,11)      "存储点纬度"
    TYPE:     VARCHAR2(256)      "存储点类型，用于区分小区点和资源点"

BOUNDARY表:
    ID:       VARCHAR2(64)       "存储点ID"
    PATH:     CLOB               "组成存储点15分钟可达区域边界的所有点的经纬度"

REACHABLE_POINT表:
    ID:       VARCHAR2(64)       "存储点ID"
    POINTS:   CLOB               "存储点15分钟可达区域内所有的存储点ID"
