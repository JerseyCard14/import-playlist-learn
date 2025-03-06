#!/usr/bin/env python3
import os
import sys
import argparse
from typing import List, Dict, Any
from tqdm import tqdm

from file_reader import get_reader
from spotify_client import SpotifyClient


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='将播放列表文件导入到Spotify')
    parser.add_argument('file', help='播放列表文件路径 (支持 Excel, CSV, JSON, TXT 格式)')
    parser.add_argument('--name', '-n', help='播放列表名称（可选，默认使用文件中的名称或文件名）')
    parser.add_argument('--description', '-d', help='播放列表描述（可选）')
    return parser.parse_args()


def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    
    # 检查文件是否存在
    if not os.path.exists(args.file):
        print(f"错误: 文件 '{args.file}' 不存在")
        sys.exit(1)
    
    try:
        # 获取适合的文件读取器
        print(f"正在读取文件 '{args.file}'...")
        try:
            reader = get_reader(args.file)
        except ValueError as e:
            print(f"错误: {str(e)}")
            sys.exit(1)
        
        # 读取播放列表数据
        try:
            songs = reader.read_playlist()
        except Exception as e:
            print(f"错误: {str(e)}")
            sys.exit(1)
        
        if not songs:
            print("错误: 文件中没有找到歌曲")
            sys.exit(1)
        
        print(f"找到 {len(songs)} 首歌曲")
        
        # 获取播放列表名称
        playlist_name = args.name if args.name else reader.get_playlist_name()
        playlist_description = args.description if args.description else f"从 {os.path.basename(args.file)} 导入的播放列表"
        
        # 连接到Spotify
        print("正在连接到Spotify...")
        spotify_client = SpotifyClient()
        
        # 创建播放列表
        print(f"正在创建播放列表 '{playlist_name}'...")
        playlist_id = spotify_client.create_playlist(playlist_name, playlist_description)
        
        # 搜索并添加歌曲
        print("正在搜索歌曲...")
        track_ids = []
        not_found = []
        
        for song in tqdm(songs, desc="处理歌曲"):
            song_name = song.get('song_name', '')
            artist = song.get('artist', '')
            
            if not song_name:
                continue
            
            track_id = spotify_client.search_track(song_name, artist)
            
            if track_id:
                track_ids.append(track_id)
            else:
                not_found.append(f"{song_name} - {artist}")
        
        # 添加歌曲到播放列表
        if track_ids:
            print(f"正在将 {len(track_ids)} 首歌曲添加到播放列表...")
            spotify_client.add_tracks_to_playlist(playlist_id, track_ids)
            print("完成!")
        else:
            print("没有找到任何歌曲")
        
        # 显示未找到的歌曲
        if not_found:
            print(f"\n未找到 {len(not_found)} 首歌曲:")
            for song in not_found:
                print(f"  - {song}")
        
    except Exception as e:
        print(f"错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 