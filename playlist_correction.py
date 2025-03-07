#!/usr/bin/env python3
"""
播放列表修正工具

这个脚本提供了一系列功能，用于修正Spotify播放列表中的歌曲，包括：
1. 删除特定位置的歌曲
2. 交互式搜索并添加正确版本的歌曲

使用方法:
1. 删除特定位置的歌曲:
   python playlist_correction.py remove --playlist-id PLAYLIST_ID --indices 1,2,3

2. 交互式添加歌曲:
   python playlist_correction.py add --playlist-id PLAYLIST_ID --file songs.txt

版本: 1.2
"""

import os
import sys
import time
import argparse
from typing import List, Dict, Any

from spotify_client import SpotifyClient

def remove_songs(playlist_id: str, indices: List[int]):
    """
    从播放列表中删除特定位置的歌曲
    
    Args:
        playlist_id: 播放列表ID
        indices: 要删除的歌曲索引列表（从1开始）
    """
    # 初始化Spotify客户端
    spotify_client = SpotifyClient()
    
    try:
        # 获取播放列表信息
        print(f"正在获取播放列表信息...")
        sp = spotify_client.sp
        
        playlist = sp.playlist(playlist_id)
        playlist_name = playlist['name']
        print(f"正在处理播放列表: {playlist_name}")
        
        # 获取播放列表中的所有歌曲
        tracks = []
        results = sp.playlist_tracks(playlist_id)
        tracks.extend(results['items'])
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])
        
        print(f"播放列表中共有 {len(tracks)} 首歌曲")
        
        # 获取要删除的歌曲URI
        tracks_to_remove = []
        for idx in [i-1 for i in indices]:  # 转换为0-索引
            if 0 <= idx < len(tracks):
                track = tracks[idx]
                track_name = track['track']['name']
                artist_name = track['track']['artists'][0]['name']
                track_uri = track['track']['uri']
                
                print(f"将删除: {idx+1}. {track_name} - {artist_name}")
                tracks_to_remove.append({"uri": track_uri, "positions": [idx]})
        
        # 确认删除
        if not tracks_to_remove:
            print("没有找到要删除的歌曲")
            return
        
        confirm = input(f"确认从播放列表 '{playlist_name}' 中删除这 {len(tracks_to_remove)} 首歌曲? (y/n): ")
        if confirm.lower() != 'y':
            print("操作已取消")
            return
        
        # 删除歌曲
        try:
            sp.playlist_remove_specific_occurrences_of_items(playlist_id, tracks_to_remove)
            print(f"成功从播放列表 '{playlist_name}' 中删除 {len(tracks_to_remove)} 首歌曲")
        except Exception as e:
            print(f"删除歌曲时出错: {e}")
            
    except Exception as e:
        print(f"发生错误: {e}")

def add_songs_interactive(playlist_id: str, songs_file: str = None):
    """
    交互式搜索并添加歌曲到播放列表
    
    Args:
        playlist_id: 播放列表ID
        songs_file: 包含歌曲信息的文件路径（可选）
    """
    # 初始化Spotify客户端
    spotify_client = SpotifyClient()
    
    # 从文件加载歌曲或使用默认列表
    songs_to_add = []
    if songs_file and os.path.exists(songs_file):
        with open(songs_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and ' - ' in line:
                    song_name, artist = line.split(' - ', 1)
                    songs_to_add.append({"song_name": song_name.strip(), "artist": artist.strip()})
    
    if not songs_to_add:
        print("没有找到要添加的歌曲")
        return
    
    try:
        # 获取播放列表信息
        sp = spotify_client.sp
        playlist = sp.playlist(playlist_id)
        playlist_name = playlist['name']
        print(f"正在处理播放列表: {playlist_name}")
        
        # 搜索并添加歌曲
        track_ids = []
        not_found = []
        
        for i, song in enumerate(songs_to_add):
            song_name = song["song_name"]
            artist = song["artist"]
            print(f"正在搜索: {song_name} - {artist}")
            
            # 使用交互式搜索
            track_id = None
            search_results = spotify_client.get_search_results(song_name, artist, limit=10)
            
            if search_results:
                print(f"\n为 '{song_name}' - {artist} 找到多个结果:")
                for j, result in enumerate(search_results, 1):
                    result_name = result["name"]
                    result_artists = result["artists"]
                    result_album = result["album"]
                    result_url = result.get("url", "无链接")
                    print(f"{j}. {result_name} - {result_artists} ({result_album})")
                    print(f"   链接: {result_url}")
                
                choice = input(f"\n请选择一个结果 (1-{len(search_results)}), 或输入 'n' 跳过: ")
                if choice.isdigit() and 1 <= int(choice) <= len(search_results):
                    selected = search_results[int(choice) - 1]
                    track_id = selected["id"]
                    print(f"已选择: {selected['name']} - {selected['artists']}")
                else:
                    print(f"跳过: {song_name} - {artist}")
            else:
                print(f"未找到: {song_name} - {artist}")
                not_found.append(f"{song_name} - {artist}")
            
            if track_id:
                track_ids.append(track_id)
            
            # 添加延迟以避免API限制
            time.sleep(0.5)
        
        # 添加歌曲到播放列表
        if track_ids:
            print(f"\n正在将 {len(track_ids)} 首歌曲添加到播放列表 '{playlist_name}'...")
            success = spotify_client.add_tracks_to_playlist(playlist_id, track_ids)
            if success:
                print(f"成功添加 {len(track_ids)} 首歌曲到播放列表")
            else:
                print("添加歌曲失败")
        else:
            print("没有找到要添加的歌曲")
        
        # 显示未找到的歌曲
        if not_found:
            print("\n以下歌曲未找到:")
            for song in not_found:
                print(f"- {song}")
    
    except Exception as e:
        print(f"发生错误: {e}")

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="Spotify播放列表修正工具")
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # 删除歌曲子命令
    remove_parser = subparsers.add_parser("remove", help="从播放列表中删除特定位置的歌曲")
    remove_parser.add_argument("--playlist-id", required=True, help="播放列表ID")
    remove_parser.add_argument("--indices", required=True, help="要删除的歌曲索引，用逗号分隔")
    
    # 添加歌曲子命令
    add_parser = subparsers.add_parser("add", help="交互式搜索并添加歌曲到播放列表")
    add_parser.add_argument("--playlist-id", required=True, help="播放列表ID")
    add_parser.add_argument("--file", help="包含歌曲信息的文件路径")
    
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_arguments()
    
    if args.command == "remove":
        indices = [int(idx) for idx in args.indices.split(",")]
        remove_songs(args.playlist_id, indices)
    elif args.command == "add":
        add_songs_interactive(args.playlist_id, args.file)
    else:
        print("请指定子命令: remove 或 add")

if __name__ == "__main__":
    main() 