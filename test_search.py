#!/usr/bin/env python3
import sys
import argparse
from spotify_client import SpotifyClient


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='测试Spotify搜索功能')
    parser.add_argument('song', help='歌曲名称')
    parser.add_argument('--artist', '-a', help='艺术家名称（可选）')
    parser.add_argument('--verbose', '-v', action='store_true', help='显示详细信息')
    return parser.parse_args()


def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    
    try:
        # 连接到Spotify
        print("正在连接到Spotify...")
        spotify_client = SpotifyClient()
        
        # 搜索歌曲
        print(f"正在搜索: {args.song}" + (f" - {args.artist}" if args.artist else ""))
        
        if args.verbose:
            # 测试各种搜索策略
            print("\n测试不同的搜索策略:")
            
            # 清理输入
            song_name = spotify_client._clean_text(args.song)
            artist = spotify_client._clean_text(args.artist) if args.artist else ""
            
            print(f"清理后的输入: {song_name}" + (f" - {artist}" if artist else ""))
            
            # 策略1: 精确搜索
            print("\n策略1: 精确搜索")
            track_id = spotify_client._exact_search(song_name, artist)
            if track_id:
                print(f"找到歌曲! ID: {track_id}")
            else:
                print("未找到歌曲")
            
            # 策略2: 仅歌曲名搜索
            if artist:
                print("\n策略2: 仅歌曲名搜索")
                track_id = spotify_client._exact_search(song_name, "")
                if track_id:
                    print(f"找到歌曲! ID: {track_id}")
                else:
                    print("未找到歌曲")
            
            # 策略3: 关键词搜索
            print("\n策略3: 关键词搜索")
            track_id = spotify_client._keyword_search(song_name, artist)
            if track_id:
                print(f"找到歌曲! ID: {track_id}")
            else:
                print("未找到歌曲")
            
            # 策略4: 分词搜索
            print("\n策略4: 分词搜索")
            track_id = spotify_client._tokenized_search(song_name, artist)
            if track_id:
                print(f"找到歌曲! ID: {track_id}")
            else:
                print("未找到歌曲")
            
            # 策略5: 模糊匹配搜索
            print("\n策略5: 模糊匹配搜索")
            track_id = spotify_client._fuzzy_search(song_name, artist)
            if track_id:
                print(f"找到歌曲! ID: {track_id}")
            else:
                print("未找到歌曲")
        
        # 使用完整的搜索功能
        print("\n使用完整的搜索功能:")
        track_id = spotify_client.search_track(args.song, args.artist or "")
        
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
            print(f"ID: {track_id}")
        else:
            print("\n未找到歌曲")
        
    except Exception as e:
        print(f"错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 