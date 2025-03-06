#!/usr/bin/env python3
import pandas as pd
import json
import os

# 示例歌曲数据
songs = [
    {'song_name': 'Shape of You', 'artist': 'Ed Sheeran'},
    {'song_name': 'Blinding Lights', 'artist': 'The Weeknd'},
    {'song_name': 'Dance Monkey', 'artist': 'Tones and I'},
    {'song_name': 'Someone You Loved', 'artist': 'Lewis Capaldi'},
    {'song_name': 'Watermelon Sugar', 'artist': 'Harry Styles'},
    {'song_name': '七里香', 'artist': '周杰伦'},
    {'song_name': '晴天', 'artist': '周杰伦'},
    {'song_name': 'Dynamite', 'artist': 'BTS'},
    {'song_name': 'Bad Guy', 'artist': 'Billie Eilish'},
    {'song_name': 'Uptown Funk', 'artist': 'Mark Ronson ft. Bruno Mars'}
]

# 创建示例目录
examples_dir = 'examples'
os.makedirs(examples_dir, exist_ok=True)

# 1. 创建Excel示例文件
print("创建Excel示例文件...")
df = pd.DataFrame(songs)
excel_path = os.path.join(examples_dir, 'example_playlist.xlsx')
df.to_excel(excel_path, index=False)
print(f"已创建: {excel_path}")

# 2. 创建CSV示例文件
print("创建CSV示例文件...")
csv_path = os.path.join(examples_dir, 'example_playlist.csv')
df.to_csv(csv_path, index=False)
print(f"已创建: {csv_path}")

# 3. 创建JSON示例文件 (列表格式)
print("创建JSON示例文件 (列表格式)...")
json_list_path = os.path.join(examples_dir, 'example_playlist_list.json')
with open(json_list_path, 'w', encoding='utf-8') as f:
    json.dump(songs, f, ensure_ascii=False, indent=2)
print(f"已创建: {json_list_path}")

# 4. 创建JSON示例文件 (对象格式)
print("创建JSON示例文件 (对象格式)...")
json_obj_path = os.path.join(examples_dir, 'example_playlist_object.json')
playlist_obj = {
    'name': '我的示例播放列表',
    'description': 'JSON对象格式的示例播放列表',
    'songs': songs
}
with open(json_obj_path, 'w', encoding='utf-8') as f:
    json.dump(playlist_obj, f, ensure_ascii=False, indent=2)
print(f"已创建: {json_obj_path}")

# 5. 创建文本示例文件
print("创建文本示例文件...")
txt_path = os.path.join(examples_dir, 'example_playlist.txt')
with open(txt_path, 'w', encoding='utf-8') as f:
    f.write("# 我的示例播放列表\n")
    f.write("# 格式: 歌曲名 - 艺术家\n\n")
    for song in songs:
        f.write(f"{song['song_name']} - {song['artist']}\n")
print(f"已创建: {txt_path}")

print("\n所有示例文件已创建完成！")
print("使用方法示例:")
print(f"python import_playlist.py {excel_path}")
print(f"python import_playlist.py {csv_path}")
print(f"python import_playlist.py {json_list_path}")
print(f"python import_playlist.py {json_obj_path}")
print(f"python import_playlist.py {txt_path}") 