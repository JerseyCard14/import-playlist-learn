#!/usr/bin/env python3
import os
import sys
import argparse
import time
import json
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
    parser.add_argument('--interactive', '-i', action='store_true', help='启用交互式搜索（允许用户选择搜索结果）')
    parser.add_argument('--existing', '-e', help='导入到现有播放列表的ID（可选）')
    parser.add_argument('--cover', '-c', help='设置播放列表封面图片的文件路径（可选，JPEG格式）')
    parser.add_argument('--column-mapping', '-m', help='列映射JSON字符串或文件路径，例如：\'{"歌曲":"song_name", "歌手":"artist"}\'')
    parser.add_argument('--skip-rows', '-sr', type=int, help='跳过文件开头的行数（仅适用于Excel和CSV）')
    parser.add_argument('--skip-empty', '-se', action='store_true', help='跳过空行或缺少必要信息的行')
    parser.add_argument('--multi-song-separator', '-ms', help='多首歌曲分隔符（用于处理一行包含多首歌曲的情况）')
    parser.add_argument('--artist-column', '-ac', help='指定歌手列的名称（用于多列格式的表格）')
    parser.add_argument('--song-columns', '-sc', help='指定歌曲列的名称，多个列名用逗号分隔（用于多列格式的表格）')
    parser.add_argument('--count-column', '-cc', help='指定数量列的名称，用于确定每行实际的歌曲数量（用于多列格式的表格）')
    return parser.parse_args()


def load_column_mapping(mapping_str: str) -> Dict[str, str]:
    """
    加载列映射
    
    Args:
        mapping_str: 列映射JSON字符串或文件路径
        
    Returns:
        列映射字典
    """
    if not mapping_str:
        return None
        
    # 检查是否是文件路径
    if os.path.exists(mapping_str):
        try:
            with open(mapping_str, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"无法加载列映射文件: {str(e)}")
            return None
    
    # 尝试解析JSON字符串
    try:
        return json.loads(mapping_str)
    except Exception as e:
        print(f"无法解析列映射JSON: {str(e)}")
        return None


def select_playlist(spotify_client: SpotifyClient) -> str:
    """
    让用户选择一个现有的播放列表
    
    Args:
        spotify_client: Spotify客户端实例
        
    Returns:
        选择的播放列表ID，如果取消则返回空字符串
    """
    print("获取用户播放列表...")
    playlists = spotify_client.get_user_playlists()
    
    if not playlists:
        print("未找到播放列表")
        return ""
    
    print(f"\n找到 {len(playlists)} 个播放列表:")
    for i, playlist in enumerate(playlists):
        print(f"{i+1:3d}. {playlist['name']} ({playlist['tracks_total']} 首歌曲)")
    
    # 让用户选择一个播放列表
    try:
        choice = input("\n请选择要导入到的播放列表 (1-{0}), 或输入 'n' 创建新播放列表: ".format(len(playlists))).strip()
        if choice.lower() == 'n':
            return ""
        
        choice_idx = int(choice) - 1
        if 0 <= choice_idx < len(playlists):
            return playlists[choice_idx]['id']
        else:
            print("无效的选择，将创建新播放列表")
            return ""
    except ValueError:
        print("无效的输入，将创建新播放列表")
        return ""


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
                        track_id = spotify_client.search_track(song_name, artist, interactive=True)
                        
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
    if not args.file:
        print("错误: 必须提供文件路径")
        sys.exit(1)
    
    if not os.path.exists(args.file):
        print(f"错误: 文件 '{args.file}' 不存在")
        sys.exit(1)
    
    # 检查封面图片是否存在
    if args.cover and not os.path.exists(args.cover):
        print(f"错误: 封面图片文件 '{args.cover}' 不存在")
        sys.exit(1)
    
    # 加载列映射
    column_mapping = None
    if args.column_mapping:
        column_mapping = load_column_mapping(args.column_mapping)
        if column_mapping and args.verbose:
            print(f"使用列映射: {column_mapping}")
    
    # 处理歌手列和歌曲列参数
    artist_column = args.artist_column
    song_columns = None
    if args.song_columns:
        song_columns = [col.strip() for col in args.song_columns.split(',')]
        if args.verbose:
            print(f"使用歌曲列: {song_columns}")
    
    # 处理数量列参数
    count_column = args.count_column
    if count_column and args.verbose:
        print(f"使用数量列: {count_column}")
    
    try:
        # 获取适合的文件读取器
        print(f"正在读取文件 '{args.file}'...")
        try:
            reader_options = {
                'column_mapping': column_mapping,
                'skip_rows': args.skip_rows,
                'skip_empty': args.skip_empty,
                'multi_song_separator': args.multi_song_separator,
                'artist_column': artist_column,
                'song_columns': song_columns,
                'count_column': count_column
            }
            # 移除None值
            reader_options = {k: v for k, v in reader_options.items() if v is not None}
            
            reader = get_reader(args.file, **reader_options)
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
        
        # 确定播放列表ID
        playlist_id = ""
        if args.existing:
            # 使用指定的现有播放列表
            playlist_id = args.existing
            try:
                # 验证播放列表ID是否有效
                playlist = spotify_client.sp.playlist(playlist_id)
                playlist_name = playlist['name']
                print(f"将导入到现有播放列表: '{playlist_name}'")
            except Exception:
                print(f"错误: 无法获取播放列表信息: {playlist_id}")
                sys.exit(1)
        elif input("是否导入到现有播放列表? (y/n): ").lower() == 'y':
            # 让用户选择一个现有的播放列表
            playlist_id = select_playlist(spotify_client)
            if playlist_id:
                # 获取播放列表信息
                playlist = spotify_client.sp.playlist(playlist_id)
                playlist_name = playlist['name']
                print(f"将导入到现有播放列表: '{playlist_name}'")
        
        # 如果没有选择现有播放列表，则创建新的播放列表
        if not playlist_id:
            print(f"正在创建{'私有' if args.private else '公开'}播放列表 '{playlist_name}'...")
            playlist_id = spotify_client.create_playlist(playlist_name, playlist_description, not args.private)
        
        # 搜索并添加歌曲
        print("正在搜索歌曲...")
        track_ids = []
        not_found = []
        
        # 使用tqdm创建进度条，但在交互式模式下禁用
        progress_bar = songs if args.interactive else tqdm(songs, desc="处理歌曲")
        
        for song in progress_bar:
            song_name = song.get('song_name', '')
            artist = song.get('artist', '')
            
            if not song_name:
                continue
            
            if args.interactive:
                print(f"\n正在搜索: {song_name} - {artist}")
            
            track_id = spotify_client.search_track(song_name, artist, interactive=args.interactive)
            
            if track_id:
                track_ids.append(track_id)
                if args.verbose or args.interactive:
                    print(f"找到: {song_name} - {artist}")
            else:
                not_found.append(f"{song_name} - {artist}")
                if args.verbose or args.interactive:
                    print(f"未找到: {song_name} - {artist}")
        
        # 添加歌曲到播放列表
        if track_ids:
            print(f"正在将 {len(track_ids)} 首歌曲添加到播放列表...")
            spotify_client.add_tracks_to_playlist(playlist_id, track_ids)
            print("完成!")
            print(f"成功率: {len(track_ids)}/{len(songs)} ({len(track_ids)/len(songs)*100:.1f}%)")
        else:
            print("没有找到任何歌曲")
        
        # 设置播放列表封面图片
        if args.cover:
            print(f"正在设置播放列表封面图片...")
            if spotify_client.set_playlist_cover_image(playlist_id, args.cover):
                print("封面图片设置成功!")
            else:
                print("封面图片设置失败")
        
        # 显示未找到的歌曲
        if not_found:
            print(f"\n未找到 {len(not_found)} 首歌曲:")
            for song in not_found:
                print(f"  - {song}")
        
        # 显示播放列表链接
        playlist = spotify_client.sp.playlist(playlist_id)
        print(f"\n播放列表链接: {playlist['external_urls']['spotify']}")
        
    except Exception as e:
        print(f"错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 