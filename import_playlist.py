#!/usr/bin/env python3
import os
import sys
import argparse
import time
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
    parser.add_argument('--private', '-p', action='store_true', help='创建私有播放列表（默认为公开）')
    parser.add_argument('--verbose', '-v', action='store_true', help='显示详细信息')
    parser.add_argument('--preview', '-P', action='store_true', help='导入前预览歌曲列表')
    parser.add_argument('--no-preview', action='store_true', help='跳过预览直接导入')
    return parser.parse_args()


def display_preview(songs: List[Dict[str, Any]], playlist_name: str, spotify_client: SpotifyClient = None) -> List[Dict[str, Any]]:
    """
    显示歌曲预览并允许用户编辑
    
    Args:
        songs: 歌曲列表
        playlist_name: 播放列表名称
        spotify_client: Spotify客户端实例（可选，用于测试搜索）
        
    Returns:
        编辑后的歌曲列表
    """
    if not songs:
        print("没有找到歌曲")
        return []
    
    # 创建可编辑的歌曲列表副本
    edited_songs = songs.copy()
    
    while True:
        # 清屏
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # 显示播放列表信息
        print(f"\n===== 播放列表预览: {playlist_name} =====")
        print(f"共 {len(edited_songs)} 首歌曲\n")
        
        # 显示歌曲列表
        for i, song in enumerate(edited_songs):
            song_name = song.get('song_name', '')
            artist = song.get('artist', '')
            print(f"{i+1:3d}. {song_name} - {artist}")
        
        # 显示菜单
        print("\n===== 操作菜单 =====")
        print("1. 继续导入")
        print("2. 删除歌曲")
        print("3. 添加歌曲")
        print("4. 编辑歌曲")
        print("5. 测试搜索")
        print("6. 取消导入")
        
        # 获取用户选择
        choice = input("\n请选择操作 [1-6]: ").strip()
        
        if choice == '1':
            # 继续导入
            return edited_songs
        elif choice == '2':
            # 删除歌曲
            try:
                index = int(input("请输入要删除的歌曲编号: ").strip()) - 1
                if 0 <= index < len(edited_songs):
                    song = edited_songs.pop(index)
                    print(f"已删除: {song.get('song_name', '')} - {song.get('artist', '')}")
                else:
                    print("无效的歌曲编号")
                input("按Enter继续...")
            except ValueError:
                print("请输入有效的数字")
                input("按Enter继续...")
        elif choice == '3':
            # 添加歌曲
            song_name = input("请输入歌曲名: ").strip()
            artist = input("请输入艺术家名: ").strip()
            if song_name:
                edited_songs.append({'song_name': song_name, 'artist': artist})
                print(f"已添加: {song_name} - {artist}")
            else:
                print("歌曲名不能为空")
            input("按Enter继续...")
        elif choice == '4':
            # 编辑歌曲
            try:
                index = int(input("请输入要编辑的歌曲编号: ").strip()) - 1
                if 0 <= index < len(edited_songs):
                    song = edited_songs[index]
                    song_name = input(f"歌曲名 [{song.get('song_name', '')}]: ").strip()
                    artist = input(f"艺术家 [{song.get('artist', '')}]: ").strip()
                    if song_name:
                        song['song_name'] = song_name
                    if artist:
                        song['artist'] = artist
                    print(f"已更新: {song.get('song_name', '')} - {song.get('artist', '')}")
                else:
                    print("无效的歌曲编号")
                input("按Enter继续...")
            except ValueError:
                print("请输入有效的数字")
                input("按Enter继续...")
        elif choice == '5':
            # 测试搜索
            if spotify_client:
                try:
                    index = int(input("请输入要测试的歌曲编号: ").strip()) - 1
                    if 0 <= index < len(edited_songs):
                        song = edited_songs[index]
                        song_name = song.get('song_name', '')
                        artist = song.get('artist', '')
                        
                        print(f"\n正在搜索: {song_name} - {artist}")
                        track_id = spotify_client.search_track(song_name, artist)
                        
                        if track_id:
                            # 获取歌曲详情
                            track = spotify_client.sp.track(track_id)
                            track_name = track['name']
                            track_artists = ", ".join([a['name'] for a in track['artists']])
                            track_album = track['album']['name']
                            track_url = track['external_urls']['spotify']
                            
                            print(f"\n找到歌曲!")
                            print(f"歌曲名: {track_name}")
                            print(f"艺术家: {track_artists}")
                            print(f"专辑: {track_album}")
                            print(f"Spotify链接: {track_url}")
                        else:
                            print("\n未找到歌曲")
                    else:
                        print("无效的歌曲编号")
                except ValueError:
                    print("请输入有效的数字")
                input("按Enter继续...")
            else:
                print("无法测试搜索，Spotify客户端未初始化")
                input("按Enter继续...")
        elif choice == '6':
            # 取消导入
            if input("确定要取消导入吗? (y/n): ").lower() == 'y':
                return []
        else:
            print("无效的选择")
            input("按Enter继续...")


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
        
        # 预览歌曲列表
        show_preview = args.preview or (not args.no_preview and len(songs) > 5)
        if show_preview:
            print("正在准备预览...")
            songs = display_preview(songs, playlist_name, spotify_client)
            if not songs:
                print("导入已取消")
                sys.exit(0)
        
        # 创建播放列表
        print(f"正在创建{'私有' if args.private else '公开'}播放列表 '{playlist_name}'...")
        playlist_id = spotify_client.create_playlist(playlist_name, playlist_description, not args.private)
        
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
                if args.verbose:
                    print(f"找到: {song_name} - {artist}")
            else:
                not_found.append(f"{song_name} - {artist}")
                if args.verbose:
                    print(f"未找到: {song_name} - {artist}")
        
        # 添加歌曲到播放列表
        if track_ids:
            print(f"正在将 {len(track_ids)} 首歌曲添加到播放列表...")
            spotify_client.add_tracks_to_playlist(playlist_id, track_ids)
            print("完成!")
            print(f"成功率: {len(track_ids)}/{len(songs)} ({len(track_ids)/len(songs)*100:.1f}%)")
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