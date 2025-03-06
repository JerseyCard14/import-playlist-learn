#!/usr/bin/env python3
import os
import sys
import argparse
from spotify_client import SpotifyClient


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='将Spotify播放列表导出到Excel文件')
    parser.add_argument('--output', '-o', help='输出文件路径（可选，默认为"playlist_名称.xlsx"）')
    parser.add_argument('--id', '-i', help='播放列表ID（可选，如果不提供则显示用户的播放列表列表）')
    return parser.parse_args()


def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    
    try:
        # 连接到Spotify
        print("正在连接到Spotify...")
        spotify_client = SpotifyClient()
        
        # 如果没有提供播放列表ID，显示用户的播放列表列表
        if not args.id:
            print("获取用户播放列表...")
            playlists = spotify_client.get_user_playlists()
            
            if not playlists:
                print("未找到播放列表")
                sys.exit(0)
            
            print(f"\n找到 {len(playlists)} 个播放列表:")
            for i, playlist in enumerate(playlists):
                print(f"{i+1:3d}. {playlist['name']} ({playlist['tracks_total']} 首歌曲)")
            
            # 让用户选择一个播放列表
            try:
                choice = input("\n请选择要导出的播放列表 (1-{0}), 或输入 'q' 退出: ".format(len(playlists))).strip()
                if choice.lower() == 'q':
                    print("已取消导出")
                    sys.exit(0)
                
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(playlists):
                    playlist_id = playlists[choice_idx]['id']
                    playlist_name = playlists[choice_idx]['name']
                else:
                    print("无效的选择")
                    sys.exit(1)
            except ValueError:
                print("无效的输入")
                sys.exit(1)
        else:
            # 使用提供的播放列表ID
            playlist_id = args.id
            # 获取播放列表信息
            try:
                playlist = spotify_client.sp.playlist(playlist_id)
                playlist_name = playlist['name']
            except Exception:
                print(f"无法获取播放列表信息: {playlist_id}")
                sys.exit(1)
        
        # 确定输出文件路径
        if args.output:
            output_path = args.output
        else:
            # 创建一个有效的文件名
            safe_name = "".join([c if c.isalnum() or c in [' ', '-', '_'] else '_' for c in playlist_name])
            output_path = f"playlist_{safe_name}.xlsx"
        
        # 导出播放列表
        print(f"正在导出播放列表 '{playlist_name}' 到 '{output_path}'...")
        success = spotify_client.export_playlist_to_excel(playlist_id, output_path)
        
        if success:
            print(f"导出成功! 文件已保存到: {output_path}")
        else:
            print("导出失败")
            sys.exit(1)
        
    except Exception as e:
        print(f"错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 