import os.path
import sqlite3
import argparse
import re


def parse_args():
    parser = argparse.ArgumentParser(description="PC QQ（非NT）聊天记录图片删除工具")
    parser.add_argument("--db", type=str, required=True, help="数据库文件路径")
    parser.add_argument("--dry-run", action="store_true", help="模拟运行，不进行删除")
    parser.add_argument("--cp", "--chat-path", type=str, required=True, help="聊天记录根目录")
    group_or_friend = parser.add_mutually_exclusive_group(required=True)
    group_or_friend.add_argument("-g", "--group", type=str, default="", help="群号")
    group_or_friend.add_argument("-f", "--friend", type=str, default="", help="好友账号")
    group_or_friend.add_argument("-t", "--table", type=str, default="", help="数据表名")
    group_or_friend.add_argument("-l", "--list", action="store_true", help="列出所有数据表")
    group_or_friend.add_argument("--scan", action="store_true", help="扫描图片文件")
    args = parser.parse_args()
    return args


def read_database(db_path):
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"数据库文件{db_path}不存在")
    uri = f"file:{db_path}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    cur = conn.cursor()
    cur.execute("PRAGMA mmap_size = 10240000")
    return conn, cur


def list_tables(cur):
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    for table in cur.fetchall():
        print(table[0])


def scan(cur, root_path):
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    result = {}
    for table in cur.fetchall():
        table_name = table[0]
        cur.execute(f"SELECT * FROM {table_name} limit 1")
        col_name_list = [i[0] for i in cur.description]
        if "DecodedMsg" not in col_name_list:
            continue
        size, count = clean_img(cur, table_name, root_path, True, True)
        result[table_name] = (size, count)
    sorted_result = dict(sorted(result.items(), key=lambda item: item[1][0], reverse=True))
    for table, (size, count) in sorted_result.items():
        print(table, convert_bytes_size(size), count)


def find_table(cur, name, mode):
    if mode == 1:
        prefix = "group_"
    elif mode == 2:
        prefix = "buddy_"
    else:
        prefix = ""
    table_name = prefix + name
    query = f"SELECT count(*) FROM sqlite_master WHERE type=\"table\" AND name = \"{table_name}\""
    cur.execute(query)
    if cur.fetchone()[0] == 0:
        return ""
    return table_name


def get_img_path_from_msg(msg):
    pattern = r"\[t:img,path=\|UserDataImage\:(?P<path>[^|]+)\|,hash=(?P<hash>[0-9a-f]{32})\]"
    matches = re.finditer(pattern, msg)
    results = []
    for match in matches:
        results.append((match.group('path'), match.group('hash')))
    return results


def convert_bytes_size(bytes_size):
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    size = float(bytes_size)

    for unit in units:
        if size < 1024.0 or unit == units[-1]:
            return f"{size:.2f} {unit}"
        size /= 1024.0


def delete_img(path, dry_run):
    file_size = os.path.getsize(path)
    if not dry_run:
        os.remove(path)
    return file_size


def clean_img(cur, table_name, root_path, dry_run, is_scan):
    root_path = os.path.join(root_path, "image")
    print(table_name)
    query = f"SELECT DecodedMsg FROM {table_name}"
    cur.execute(query)
    try:
        rows = cur.fetchall()
    except Exception as e:
        print(f"读取数据库失败 {e}")
        return -1, -1

    total_size = 0
    delete_count = 0
    for row in rows:
        msg = row[0]
        img_paths = get_img_path_from_msg(msg)
        if not img_paths:
            continue
        for path, hash_ in img_paths:
            path = os.path.join(root_path, path)
            is_exist = False
            if os.path.exists(path):
                is_exist = True
                try:
                    file_size = delete_img(path, dry_run)
                    total_size += file_size
                    delete_count += 1
                except:
                    pass
            ext = path.rfind(".")
            if ext != -1:
                gif_path = path[:ext] + ".gif"
                if os.path.exists(gif_path):
                    is_exist = True
                    try:
                        file_size = delete_img(gif_path, dry_run)
                        total_size += file_size
                        delete_count += 1
                    except:
                        pass
                tmb_path = path[:ext] + "_tmb" + path[ext:]
                if os.path.exists(tmb_path):
                    is_exist = True
                    try:
                        file_size = delete_img(tmb_path, dry_run)
                        total_size += file_size
                        delete_count += 1
                    except:
                        pass
            if not is_exist and not is_scan:
                print(path)
    return total_size, delete_count
    #print(convert_bytes_size(total_size), delete_count)


def main():
    args = parse_args()
    db_path = args.db
    try:
        conn, cur = read_database(db_path)
    except Exception as e:
        e.with_traceback()
        return

    if args.list:
        list_tables(cur)
        return
    if args.scan:
        scan(cur, args.cp)
        return
    if args.table:
        table_name = find_table(cur, args.table, 0)
    elif args.group:
        table_name = find_table(cur, args.group, 1)
    else:
        table_name = find_table(cur, args.friend, 2)
    if not table_name:
        print("找不到数据表")
        return
    size, count = clean_img(cur, table_name, args.cp, args.dry_run, False)
    print(convert_bytes_size(size), count)

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()