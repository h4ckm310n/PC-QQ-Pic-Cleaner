# PC-QQ-Pic-Cleaner
该工具用于清理电脑QQ上指定好友或群聊的聊天图片文件，只适用于非NT版本（旧版）。

建议运行之前做好备份工作，以免出现意外情况导致数据丢失。

## 操作步骤
建议每一步改动前都对数据库文件做一次备份。

### 1. 准备工作
QQ的聊天记录数据库（Msg3.0.db）是加密过的，需要先进行解密。

本工具不包含解密功能，请参考此处的[教程](https://github.com/QQBackup/qq-win-db-key/blob/master/%E6%95%99%E7%A8%8B%20-%20PCQQ%20(Windows).md)解密。

### 2. 解码
解码功能使用的是[qq_msg_decode](https://github.com/saucer-man/qq_msg_decode)的代码，在此基础上对于解码后的数据格式做了一点修改，方便解析图片路径。

运行如下命令，此处的“/path/to/db_file”指的是上面解密后的数据库文件的路径：
```shell
python3 decode.py "/path/to/db_file"
```

### 3. 运行
```shell
python3 clean.py --db /path/to/db_file --cp /path/to/message/folder \(-g GROUP_NUMBER | -f FRIEND_NUMBER | -t TABLE_NAME | -l | --scan \) [--dry-run]
```

#### 3.1. 运行参数
* -h, --help: 显示说明
* --db: 解码后的数据库文件的路径
* --cp, --chat-path: 聊天记录所在路径，如“C:\Users\XXX\Documents\Tencent Files\10000”
* -f, --friend: 指定的好友QQ号
* -g, --group: 指定的群号
* -t, --table: 指定的数据表名称
* -l, --list: 列出所有的数据表
* --scan: 扫描所有聊天记录中的图片文件，并按照图片文件占用空间的大小顺序输出结果
* --dry-run: 模拟运行，但不进行实际删除

#### 3.2. 示例
列出数据库中所有的表：

`python3 clean.py --db "C:\Users\XXX\Desktop\10000_decode.db" --cp "C:\Users\XXX\Documents\Tencent Files\10000" -l`

删除好友1234的聊天图片：

`python3 clean.py --db "C:\Users\XXX\Desktop\10000_decode.db" --cp "C:\Users\XXX\Documents\Tencent Files\10000" -f 1234`

模拟删除群聊1234的聊天图片（但实际并没有删除）：

`python3 clean.py --db "C:\Users\XXX\Desktop\10000_decode.db" --cp "C:\Users\XXX\Documents\Tencent Files\10000" -g 1234 --dry-run`

## 参考
1. <https://github.com/QQBackup/qq-win-db-key>
2. <https://github.com/saucer-man/qq_msg_decode>
