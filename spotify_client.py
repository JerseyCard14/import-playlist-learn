import os
import time
import re
from typing import List, Dict, Any, Optional, Tuple
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
from difflib import SequenceMatcher


class SpotifyClient:
    """用于与Spotify API交互的客户端类"""
    
    def __init__(self):
        """初始化Spotify客户端并进行认证"""
        # 加载环境变量
        load_dotenv()
        
        # 获取Spotify API凭证
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI')
        
        if not all([client_id, client_secret, redirect_uri]):
            raise ValueError("缺少Spotify API凭证。请在.env文件中设置SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET和SPOTIFY_REDIRECT_URI")
        
        # 设置权限范围
        scope = "playlist-modify-public playlist-modify-private"
        
        # 创建Spotify客户端
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=scope
        ))
        
        # 获取当前用户信息
        self.user_id = self.sp.current_user()['id']
    
    def create_playlist(self, name: str, description: str = "", public: bool = True) -> str:
        """
        创建新的Spotify播放列表
        
        Args:
            name: 播放列表名称
            description: 播放列表描述
            public: 是否公开播放列表
            
        Returns:
            新创建的播放列表ID
        """
        playlist = self.sp.user_playlist_create(
            user=self.user_id,
            name=name,
            public=public,
            description=description
        )
        return playlist['id']
    
    def search_track(self, song_name: str, artist: str = "") -> Optional[str]:
        """
        在Spotify上搜索歌曲，使用增强的搜索算法
        
        Args:
            song_name: 歌曲名称
            artist: 艺术家名称（可选）
            
        Returns:
            歌曲ID，如果未找到则返回None
        """
        # 清理和标准化输入
        song_name = self._clean_text(song_name)
        artist = self._clean_text(artist)
        
        # 尝试多种搜索策略
        track_id = self._try_search_strategies(song_name, artist)
        if track_id:
            return track_id
            
        # 如果所有策略都失败，返回None
        return None
    
    def _clean_text(self, text: str) -> str:
        """
        清理和标准化文本，移除特殊字符和多余空格
        
        Args:
            text: 要清理的文本
            
        Returns:
            清理后的文本
        """
        if not text:
            return ""
            
        # 移除括号及其内容，如 "(Live Version)", "[Remix]" 等
        text = re.sub(r'\([^)]*\)|\[[^\]]*\]', '', text)
        
        # 移除特殊字符，保留字母、数字、空格和一些基本标点
        text = re.sub(r'[^\w\s\'-]', ' ', text, flags=re.UNICODE)
        
        # 将多个空格替换为单个空格并去除首尾空格
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _try_search_strategies(self, song_name: str, artist: str) -> Optional[str]:
        """
        尝试多种搜索策略
        
        Args:
            song_name: 清理后的歌曲名称
            artist: 清理后的艺术家名称
            
        Returns:
            歌曲ID，如果未找到则返回None
        """
        # 策略1: 精确搜索 (歌曲名 + 艺术家)
        track_id = self._exact_search(song_name, artist)
        if track_id:
            return track_id
            
        # 策略2: 仅歌曲名搜索
        if artist:
            track_id = self._exact_search(song_name, "")
            if track_id:
                return track_id
                
        # 策略3: 关键词搜索 (不使用field限定符)
        track_id = self._keyword_search(song_name, artist)
        if track_id:
            return track_id
            
        # 策略4: 分词搜索 (处理歌曲名可能包含艺术家的情况)
        track_id = self._tokenized_search(song_name, artist)
        if track_id:
            return track_id
            
        # 策略5: 模糊匹配搜索 (获取多个结果并比较相似度)
        return self._fuzzy_search(song_name, artist)
    
    def _exact_search(self, song_name: str, artist: str) -> Optional[str]:
        """
        使用精确字段进行搜索
        
        Args:
            song_name: 歌曲名称
            artist: 艺术家名称
            
        Returns:
            歌曲ID，如果未找到则返回None
        """
        if not song_name:
            return None
            
        # 构建搜索查询
        query = f"track:{song_name}"
        if artist:
            query += f" artist:{artist}"
        
        # 搜索歌曲
        try:
            results = self.sp.search(q=query, type='track', limit=1)
            if results['tracks']['items']:
                return results['tracks']['items'][0]['id']
        except Exception:
            pass
            
        return None
    
    def _keyword_search(self, song_name: str, artist: str) -> Optional[str]:
        """
        使用关键词搜索，不使用field限定符
        
        Args:
            song_name: 歌曲名称
            artist: 艺术家名称
            
        Returns:
            歌曲ID，如果未找到则返回None
        """
        if not song_name:
            return None
            
        # 构建搜索查询
        query = song_name
        if artist:
            query += f" {artist}"
        
        # 搜索歌曲
        try:
            results = self.sp.search(q=query, type='track', limit=1)
            if results['tracks']['items']:
                return results['tracks']['items'][0]['id']
        except Exception:
            pass
            
        return None
    
    def _tokenized_search(self, song_name: str, artist: str) -> Optional[str]:
        """
        分词搜索，处理歌曲名可能包含艺术家的情况
        
        Args:
            song_name: 歌曲名称
            artist: 艺术家名称
            
        Returns:
            歌曲ID，如果未找到则返回None
        """
        if not song_name:
            return None
            
        # 如果艺术家名在歌曲名中，尝试分离
        if artist and artist.lower() in song_name.lower():
            # 从歌曲名中移除艺术家名
            clean_song_name = re.sub(re.escape(artist), '', song_name, flags=re.IGNORECASE).strip()
            clean_song_name = re.sub(r'^-\s+|\s+-\s*$', '', clean_song_name).strip()
            
            if clean_song_name:
                # 使用清理后的歌曲名和艺术家进行搜索
                track_id = self._exact_search(clean_song_name, artist)
                if track_id:
                    return track_id
        
        # 如果歌曲名包含 " - "，可能是 "艺术家 - 歌曲名" 格式
        if " - " in song_name and not artist:
            parts = song_name.split(" - ", 1)
            if len(parts) == 2:
                potential_artist, potential_song = parts
                
                # 尝试这种组合
                track_id = self._exact_search(potential_song.strip(), potential_artist.strip())
                if track_id:
                    return track_id
                    
                # 尝试反向组合
                track_id = self._exact_search(potential_artist.strip(), potential_song.strip())
                if track_id:
                    return track_id
        
        return None
    
    def _fuzzy_search(self, song_name: str, artist: str) -> Optional[str]:
        """
        模糊匹配搜索，获取多个结果并比较相似度
        
        Args:
            song_name: 歌曲名称
            artist: 艺术家名称
            
        Returns:
            最匹配的歌曲ID，如果未找到则返回None
        """
        if not song_name:
            return None
            
        # 构建搜索查询
        query = song_name
        if artist:
            query += f" {artist}"
        
        # 搜索更多结果
        try:
            results = self.sp.search(q=query, type='track', limit=10)
            tracks = results['tracks']['items']
            
            if not tracks:
                return None
                
            # 如果只有一个结果，直接返回
            if len(tracks) == 1:
                return tracks[0]['id']
                
            # 计算每个结果的相似度得分
            scored_tracks = []
            for track in tracks:
                track_name = track['name']
                track_artists = ", ".join([a['name'] for a in track['artists']])
                
                # 计算歌曲名相似度
                name_similarity = SequenceMatcher(None, song_name.lower(), track_name.lower()).ratio()
                
                # 计算艺术家相似度
                artist_similarity = 0.0
                if artist:
                    artist_similarity = SequenceMatcher(None, artist.lower(), track_artists.lower()).ratio()
                
                # 综合得分 (歌曲名权重更高)
                score = name_similarity * 0.7 + artist_similarity * 0.3
                
                scored_tracks.append((track['id'], score, track_name, track_artists))
            
            # 按得分排序
            scored_tracks.sort(key=lambda x: x[1], reverse=True)
            
            # 返回得分最高的歌曲ID
            if scored_tracks and scored_tracks[0][1] > 0.5:  # 设置一个最低相似度阈值
                return scored_tracks[0][0]
                
        except Exception:
            pass
            
        return None
    
    def add_tracks_to_playlist(self, playlist_id: str, track_ids: List[str]) -> bool:
        """
        将歌曲添加到播放列表
        
        Args:
            playlist_id: 播放列表ID
            track_ids: 歌曲ID列表
            
        Returns:
            是否成功添加
        """
        # Spotify API限制一次最多添加100首歌曲
        chunk_size = 100
        
        for i in range(0, len(track_ids), chunk_size):
            chunk = track_ids[i:i + chunk_size]
            self.sp.playlist_add_items(playlist_id, chunk)
            
            # 添加短暂延迟以避免API限制
            if i + chunk_size < len(track_ids):
                time.sleep(1)
        
        return True 