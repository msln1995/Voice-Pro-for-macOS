import os
import platform
import gradio as gr
from yt_dlp import YoutubeDL
from yt_dlp.postprocessor import PostProcessor

from app.abus_path import cmd_rename_file, path_shorten

import structlog
logger = structlog.get_logger()


class FilenameCollectorPP(PostProcessor):
    def __init__(self):
        super(FilenameCollectorPP, self).__init__(None)
        self.filenames = []

    def run(self, information):
        self.filenames.append(information["filepath"])
        return [], information
    

class ExceededMaximumDuration(Exception):
    def __init__(self, videoDuration, maxDuration, message):
        self.videoDuration = videoDuration
        self.maxDuration = maxDuration
        super().__init__(message)    
    
    
class YoutubeDownloader:
    def __init__(self):
        self.progress = gr.Progress()         
        
    def validate_path(self, path):
        try:
            shortened_path = path_shorten(path)
            cmd_rename_file(path, shortened_path)
        except ValueError as e:
            shortened_path = path
            logger.error(f"validate_path - Error: {e}")    

        return shortened_path
        
        
    def dl_progress_hook(self, d):
        if ('status' not in d):
            return
        if ('total_bytes' not in d) and ('total_bytes_estimate' not in d):
            return
        
        try:
            total_bytes = d["total_bytes"] if 'total_bytes' in d else (d["total_bytes_estimate"] if 'total_bytes_estimate' in d else 0)     
            downloaded_bytes = d["downloaded_bytes"]
            
            if d["status"] == "downloading" and total_bytes > 0:
                self.progress(int(downloaded_bytes / total_bytes * 100) / 100.0, desc="YouTube Downloader")
        except Exception as e:
            logger.error(f"[abus_downloader.py] dl_progress_hook - An error occurred: {e}")

   
    def yt_download(self, url: str, download_folder: str, quality: str = "good", maxDuration: int = None):       
        ydl_opts = {}
        ydl_opts['keepvideo'] = False
        ydl_opts['progress_hooks'] = [self.dl_progress_hook]
        ydl_opts['playlist_items'] = '1'
        ydl_opts['retries'] = 20
        ydl_opts['fragment_retries'] = 20
        ydl_opts['nocheckcertificate'] = True
        ydl_opts['socket_timeout'] = 30
        ydl_opts['ignoreerrors'] = True
        
        # 설정 초기화 및 사용자 성공 사례 기반 옵션 구성
        ydl_opts['merge_output_format'] = 'mp4'
        
        # Cookie 설정
        cookiefile_path = os.path.join(os.getcwd(), 'cookies.txt')
        is_valid_cookie_file = False
        
        if os.path.exists(cookiefile_path):
            try:
                with open(cookiefile_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(512)
                    if "# Netscape" in content or "\t" in content:
                        is_valid_cookie_file = True
            except Exception:
                pass

        if is_valid_cookie_file:
            ydl_opts['cookiefile'] = cookiefile_path
            logger.info(f"Using valid cookie file: {cookiefile_path}")
        else:
            # 브라우저에서 쿠키 추출 (사용자 성공 사례 기반)
            try:
                ydl_opts['cookiesfrombrowser'] = ('chrome',) 
                logger.info("Setting cookiesfrombrowser to chrome...")
            except Exception as e:
                logger.warning(f"Failed to set cookiesfrombrowser: {e}")
                
        
        # 포맷 설정 (사용자 성공 사례 기반: bestvideo+bestaudio/best)
        if quality == "best":
            ydl_opts['format'] = 'bestvideo+bestaudio/best'
        elif quality == "good":            
            ydl_opts['format'] = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/best'
        elif quality == "low":
            ydl_opts['format'] = 'bestvideo[height<=720]+bestaudio/best[height<=720]/best'

        ydl_opts['outtmpl'] = download_folder + '/%(title)s.f%(format_id)s.%(ext)s'

        filename_collector = FilenameCollectorPP()
        with YoutubeDL(ydl_opts) as ydl:
            if maxDuration and maxDuration > 0:
                info = ydl.extract_info(url, download=False)
                entries = "entries" in info and info["entries"] or [info]
                total_duration = 0

                # Compute total duration
                for entry in entries:
                    total_duration += float(entry["duration"])

                if total_duration >= maxDuration:
                    raise ExceededMaximumDuration(videoDuration=total_duration, maxDuration=maxDuration, message="Video is too long")

            ydl.add_post_processor(filename_collector)
            ydl.download([url])

        if len(filename_collector.filenames) <= 0:
            raise Exception("Cannot download " + url)
        
        target_file = filename_collector.filenames[0]
        if not os.path.exists(target_file):
            # Check for partial files to provide better error message
            if os.path.exists(target_file + ".part"):
                raise Exception(f"Download was interrupted. Only .part file exists: {target_file}")
            raise Exception(f"Download failed. File not found: {target_file}")
            
        valid_path = self.validate_path(target_file)
        return valid_path
                

                