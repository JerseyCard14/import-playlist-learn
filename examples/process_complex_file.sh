#!/bin/bash

# 示例1: 使用列映射和跳过行处理复杂CSV文件
echo "示例1: 使用列映射和跳过行处理复杂CSV文件"
python import_playlist.py examples/complex_playlist.csv \
  --name "Ed Sheeran精选" \
  --description "Ed Sheeran的精选歌曲集合" \
  --column-mapping '{"歌曲名称":"song_name", "歌手":"artist"}' \
  --skip-rows 5 \
  --skip-empty \
  --preview

# 示例2: 处理包含多首歌曲的行
echo "示例2: 处理包含多首歌曲的行"
python import_playlist.py examples/complex_playlist.csv \
  --name "多艺术家精选" \
  --description "多位艺术家的精选歌曲" \
  --column-mapping '{"多首歌曲":"song_name", "歌手":"artist"}' \
  --skip-rows 16 \
  --skip-empty \
  --multi-song-separator " / " \
  --preview

# 示例3: 组合使用多个选项
echo "示例3: 组合使用多个选项"
python import_playlist.py examples/complex_playlist.csv \
  --name "完整播放列表" \
  --description "包含所有歌曲的播放列表" \
  --column-mapping '{"歌曲名称":"song_name", "多首歌曲":"song_name", "歌手":"artist"}' \
  --skip-rows 5 \
  --skip-empty \
  --multi-song-separator " / " \
  --interactive \
  --preview 