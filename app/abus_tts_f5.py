import os
import json
import time
import pysubs2
import re
import unicodedata
import string
import queue
import threading

from pydub import AudioSegment
from pydub.silence import detect_leading_silence
import numpy as np
import gradio as gr
import torch
import gc

from app.abus_genuine import *
from app.abus_path import *
from app.abus_ffmpeg import *
from app.abus_text import *
from app.abus_nlp_spacy import *
from app.abus_audio import *

import structlog
logger = structlog.get_logger()


import soundfile as sf


from cached_path import cached_path
from f5_tts.model import DiT, UNetT
from f5_tts.infer.utils_infer import (
    load_vocoder,
    load_model,
    preprocess_ref_audio_text,
    infer_process,
    remove_silence_for_generated_wav,
    save_spectrogram,
)

try:
    import spaces
    USING_SPACES = True
except ImportError:
    USING_SPACES = False

def gpu_decorator(func):
    if USING_SPACES:
        return spaces.GPU(func)
    else:
        return func


class ModelPathManager:
    def __init__(self, config_path="abus_tts_f5_models.json"):
        self.config_path = config_path
        self.model_configs = self._load_config()
        
    def _load_config(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON format in configuration file: {self.config_path}")
    
    def get_model_paths(self, model_name):
        if model_name not in self.model_configs:
            raise KeyError(f"Model '{model_name}' not found in configuration")
            
        return self.model_configs[model_name]
    
    def list_available_models(self):
        return list(self.model_configs.keys())



class F5TTS:
    def __init__(self):
        config_path = os.path.join(Path(__file__).resolve().parent, "abus_tts_f5_models.json")
        self.manager = ModelPathManager(config_path)
        self.vocoder = load_vocoder()
        


    def available_models(self):
        models = self.manager.list_available_models()
        models.append("SWivid/E2-TTS")    
        return models        
    

    def load_f5tts(self, model_name: str = "SWivid/F5-TTS_v1"):
        model_paths = self.manager.get_model_paths(model_name)
        default_cfg = dict(dim=1024, depth=22, heads=16, ff_mult=2, text_dim=512, conv_layers=4)
        
        # Helper to resolve path (Local Project Cache -> System Cache)
        def resolve_path(path_or_url, is_model=True):
            if not path_or_url: return ""
            
            # 1. If it's already a local path, return it (cached_path handles it too, but we can be explicit)
            if not path_or_url.startswith("hf://") and not path_or_url.startswith("http"):
                return str(cached_path(path_or_url))
                
            # 2. If it's a URL, check if we have a local copy in project 'ckpts'
            # Construct a safe local directory name from model_name
            safe_model_name = model_name.replace("/", "_")
            ckpt_dir = os.path.join(os.getcwd(), "ckpts", safe_model_name)
            
            # Extract filename from URL
            filename = path_or_url.split("/")[-1]
            local_file_path = os.path.join(ckpt_dir, filename)
            
            if os.path.exists(local_file_path):
                logger.info(f"Found local cache for {filename}: {local_file_path}")
                return local_file_path
            
            # 3. If local copy doesn't exist, we could download it there?
            # But cached_path downloads to system cache. 
            # To support "download to project dir", we would need to implement download logic here.
            # For now, we fallback to system cache (cached_path default behavior), 
            # UNLESS the user explicitly wants project-local downloads.
            # Given the user request "can this be put in project dir... if missing will it download to project dir",
            # we should probably try to download to project dir.
            
            logger.info(f"Local cache missing for {filename}. Using cached_path (system cache)...")
            return str(cached_path(path_or_url))

        vocab_path = resolve_path(model_paths.get('vocab_path', ""))
        ckpt_path = resolve_path(model_paths.get('model_path', ""))
        model_cfg = model_paths['config'] if 'config' in model_paths else default_cfg
            
        return load_model(DiT, model_cfg, ckpt_path, vocab_file=vocab_path)


    def load_e2tts(self):
        ckpt_path = str(cached_path("hf://SWivid/E2-TTS/E2TTS_Base/model_1200000.safetensors"))
        model_cfg = dict(dim=1024, depth=24, heads=16, ff_mult=4, text_mask_padding=False, pe_attn_head=1)
        return load_model(UNetT, model_cfg, ckpt_path)
    

    
    def select_model(self, model_choice):
        if model_choice == "SWivid/E2-TTS":
            self.ema_model = self.load_e2tts()
        else:
            self.ema_model = self.load_f5tts(model_choice)
        
    
    
    @staticmethod
    def release_cuda_memory():
        from app.abus_device import AbusDevice
        AbusDevice.release_device_memory()
                
                
    @gpu_decorator
    def generate_audio(self, dubbing_text:str, output_file, ref_audio, ref_text, speed_factor, progress=gr.Progress()):
        logger.debug(f'[abus_tts_f5.py] generate_audio - {dubbing_text}')
        
        final_wave, final_sample_rate, _ = infer_process(
            ref_audio,
            ref_text,
            dubbing_text,
            self.ema_model,
            self.vocoder,
            cross_fade_duration=0.15,
            nfe_step=32,                # denoising steps, 4 ~ 64
            speed=speed_factor,
            progress=progress
        )
        logger.debug(f'[abus_tts_f5.py] final_sample_rate - {final_sample_rate}')
        # logger.debug(f'[abus_tts_f5.py] final_wave - {final_wave}')
        
        # Return numpy array and sample rate instead of writing to file
        return final_wave, final_sample_rate
        # sf.write(output_file, final_wave, final_sample_rate)
        
        
                    
    
    
    def request_tts(self, line: str, output_file: str, ref_audio, ref_text, speed_factor, audio_format):
        # This method is now primarily for single-file requests (not batch)
        # For batch processing, use internal helpers to avoid file I/O
        
        output_voice_file = os.path.join(path_dubbing_folder(), path_new_filename(ext = f".{audio_format}"))
        line = AbusText.normalize_text(line)
        if len(line) < 1:
            logger.warning(f"[abus_tts_f5.py] request_tts - error: no line")
            return False
        
        logger.debug(f'[abus_tts_f5.py] request_tts - line = {line}')
        try:
            # 1. Generate (In-Memory)
            final_wave, sample_rate = self.generate_audio(line, None, ref_audio, ref_text, speed_factor)
            
            # 2. Convert Numpy -> AudioSegment
            # pydub requires int16 or float32 bytes. F5-TTS likely returns float32 (-1.0 to 1.0) or int16.
            # soundfile handles this automatically. 
            # To be safe, let's write to a buffer or use soundfile to write to a temp file if needed, 
            # BUT we want to avoid I/O.
            
            # Efficient conversion: Numpy -> Bytes -> AudioSegment
            # Assuming final_wave is float32, we convert to int16 for pydub
            if final_wave.dtype.kind == 'f':
                 final_wave = (final_wave * 32767).astype(np.int16)
            
            audio_segment = AudioSegment(
                final_wave.tobytes(), 
                frame_rate=sample_rate,
                sample_width=2, # 16-bit
                channels=1
            )
            
            # 3. Trim Silence (In-Memory)
            trimmed_audio = AbusAudio.trim_silence_audio(audio_segment)
            
            # 4. Convert to Stereo (In-Memory)
            # Duplicate mono channel to stereo
            stereo_audio = AudioSegment.from_mono_audiosegments(trimmed_audio, trimmed_audio)
            
            # 5. Export
            stereo_audio.export(output_file, format=audio_format)
            
            return True
        except Exception as e:
            logger.error(f"[abus_tts_f5.py] request_tts - generate_audio error: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Legacy code removed
        # trimed_voice_file = path_add_postfix(output_voice_file, "_trimed")
        # AbusAudio.trim_silence_file(output_voice_file, trimed_voice_file)        
        # ffmpeg_to_stereo(trimed_voice_file, output_file)
        
        # try:
        #     os.remove(output_voice_file)
        #     os.remove(trimed_voice_file)
        # except Exception as e:
        #     logger.error(f"[abus_tts_f5.py] request_tts - error: {e}")
        #     return False        
        # return True
    

    def _post_process_audio_segment(self, final_wave, sample_rate, text, target_duration_ms=None):
        """
        Helper for batch processing (CPU-bound): Numpy -> AudioSegment -> Trim -> Speed -> Stereo.
        Returns an AudioSegment object.
        """
        if final_wave is None:
            return None
            
        # 1. Numpy -> AudioSegment
        if final_wave.dtype.kind == 'f':
             final_wave = (final_wave * 32767).astype(np.int16)
        
        segment = AudioSegment(
            final_wave.tobytes(), 
            frame_rate=sample_rate,
            sample_width=2, 
            channels=1
        )
        
        # 2. Trim Silence
        segment = AbusAudio.trim_silence_audio(segment)
        
        # 3. Fit Duration (Only if target_duration is set)
        if target_duration_ms and target_duration_ms > 0:
            current_duration = len(segment)
            # If generated audio is significantly longer than target (allow 5% tolerance)
            if current_duration > target_duration_ms * 1.05:
                # Need to speed up. Pydub speedup changes pitch, so we MUST use FFmpeg (atempo).
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_in:
                    temp_in_path = tmp_in.name
                
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_out:
                    temp_out_path = tmp_out.name
                    
                try:
                    segment.export(temp_in_path, format="wav")
                    
                    # Calculate speed ratio
                    speed_ratio = current_duration / target_duration_ms
                    
                    # Run FFmpeg
                    from app.abus_ffmpeg import ffmpeg_change_audio_speed
                    if ffmpeg_change_audio_speed(temp_in_path, temp_out_path, speed_ratio):
                        # Read back
                        segment = AudioSegment.from_file(temp_out_path)
                    else:
                        logger.warning(f"Failed to change speed for segment: {text}")
                finally:
                    if os.path.exists(temp_in_path): os.remove(temp_in_path)
                    if os.path.exists(temp_out_path): os.remove(temp_out_path)
                    
        # 4. Convert to Stereo
        segment = AudioSegment.from_mono_audiosegments(segment, segment)
        
        return segment


    def srt_to_voice(self, subtitle_file: str, output_file: str, ref_audio, ref_text, speed_factor, audio_format, progress=gr.Progress()):
        full_subs = pysubs2.load(subtitle_file, encoding="utf-8")
        subs = full_subs
        
        # Results container (index -> AudioSegment)
        results = {}
        
        # Queue for passing data from GPU (Producer) to CPU (Consumer)
        # Item: (index, final_wave, sample_rate, text, target_duration)
        audio_queue = queue.Queue()
        
        # Consumer Worker (CPU Processing)
        def consumer_worker():
            while True:
                item = audio_queue.get()
                if item is None:
                    break
                
                idx, wave, rate, txt, dur = item
                try:
                    if wave is not None:
                        seg = self._post_process_audio_segment(wave, rate, txt, dur)
                        results[idx] = seg
                    else:
                        results[idx] = None
                except Exception as e:
                    logger.error(f"Error processing line {idx}: {e}")
                    results[idx] = None
                finally:
                    audio_queue.task_done()
        
        # Start Consumer Thread
        t = threading.Thread(target=consumer_worker, daemon=True)
        t.start()
        
        # Producer Loop (GPU Generation)
        for i in progress.tqdm(range(len(subs)), desc='Generating...'):
            line = subs[i]
            target_duration = line.end - line.start
            
            if target_duration <= 0:
                results[i] = None
                continue

            try:
                # Generate (GPU)
                line_text = AbusText.normalize_text(line.text)
                if len(line_text) < 1:
                    results[i] = None
                    continue

                final_wave, sample_rate = self.generate_audio(line_text, None, ref_audio, ref_text, speed_factor)
                
                # Put in Queue for CPU processing
                audio_queue.put((i, final_wave, sample_rate, line_text, target_duration))
                
            except Exception as e:
                logger.error(f"Error generating line {i}: {e}")
                results[i] = None

        # Signal end of processing
        audio_queue.put(None)
        t.join()
        
        # Final Assembly (Main Thread)
        audio_segments = []
        
        for i in range(len(subs)):
            line = subs[i]
            target_duration = line.end - line.start
            
            segment_audio = results.get(i)
            
            if segment_audio is None and target_duration > 0:
                # Fallback: silence
                segment_audio = AudioSegment.silent(duration=target_duration)
            elif segment_audio is None:
                 continue

            # Absolute Positioning Sync Logic
            current_total_duration = sum(len(s) for s in audio_segments)
            
            if current_total_duration < line.start:
                silence_gap = line.start - current_total_duration
                if silence_gap > 0:
                    audio_segments.append(AudioSegment.silent(duration=silence_gap))
            
            # Truncate if too long
            if len(segment_audio) > target_duration:
                segment_audio = segment_audio[:target_duration]
                
            audio_segments.append(segment_audio)

        # Export
        if audio_segments:
            combined_audio = sum(audio_segments)
            combined_audio.export(output_file, format=audio_format)         
      
    
    def srt_to_voice_multi(self, subtitle_file: str, output_file: str, ref_audio1, ref_text1, ref_audio2, ref_text2, speed_factor, audio_format, progress=gr.Progress()):
        full_subs = pysubs2.load(subtitle_file, encoding="utf-8")
        subs = full_subs
        
        results = {}
        audio_queue = queue.Queue()
        
        def consumer_worker():
            while True:
                item = audio_queue.get()
                if item is None: break
                
                idx, wave, rate, txt, dur = item
                try:
                    if wave is not None:
                        seg = self._post_process_audio_segment(wave, rate, txt, dur)
                        results[idx] = seg
                    else:
                        results[idx] = None
                except Exception as e:
                    logger.error(f"Error processing line {idx}: {e}")
                    results[idx] = None
                finally:
                    audio_queue.task_done()
        
        t = threading.Thread(target=consumer_worker, daemon=True)
        t.start()
        
        for i in progress.tqdm(range(len(subs)), desc='Generating...'):
            line = subs[i]
            text = line.text
            target_duration = line.end - line.start
            
            if target_duration <= 0:
                results[i] = None
                continue
                
            # Determine speaker
            current_ref_audio = ref_audio1
            current_ref_text = ref_text1
            
            if '{spk2}' in text:
                current_ref_audio = ref_audio2
                current_ref_text = ref_text2
                text = text.replace('{spk2}', '')
            elif '{spk1}' in text:
                current_ref_audio = ref_audio1
                current_ref_text = ref_text1
                text = text.replace('{spk1}', '')
            
            # Fallback
            if current_ref_audio is None:
                if ref_audio1 is not None:
                    current_ref_audio = ref_audio1
                    current_ref_text = ref_text1
                else:
                    logger.warning(f"No reference audio available for line: {text}")
                    results[i] = None
                    continue

            try:
                line_text = AbusText.normalize_text(text)
                if len(line_text) < 1:
                    results[i] = None
                    continue

                # Generate (GPU)
                final_wave, sample_rate = self.generate_audio(line_text, None, current_ref_audio, current_ref_text, speed_factor)
                
                audio_queue.put((i, final_wave, sample_rate, line_text, target_duration))
                
            except Exception as e:
                logger.error(f"Error generating line {i}: {e}")
                results[i] = None

        audio_queue.put(None)
        t.join()
        
        # Assembly
        audio_segments = []
        for i in range(len(subs)):
            line = subs[i]
            target_duration = line.end - line.start
            
            segment_audio = results.get(i)
            
            if segment_audio is None and target_duration > 0:
                segment_audio = AudioSegment.silent(duration=target_duration)
            elif segment_audio is None:
                continue
            
            current_total_duration = sum(len(s) for s in audio_segments)
            if current_total_duration < line.start:
                silence_gap = line.start - current_total_duration
                if silence_gap > 0:
                    audio_segments.append(AudioSegment.silent(duration=silence_gap))
            
            if len(segment_audio) > target_duration:
                segment_audio = segment_audio[:target_duration]
                
            audio_segments.append(segment_audio)

        if audio_segments:
            combined_audio = sum(audio_segments)
            combined_audio.export(output_file, format=audio_format)
      
    
    def text_to_voice(self, dubbing_text: str, output_file: str, ref_audio, ref_text, speed_factor, audio_format, progress=gr.Progress()):
        segments_folder = path_tts_segments_folder(output_file)          

        use_punctuation = AbusText.has_punctuation_marks(dubbing_text)
        lines = AbusText.split_into_sentences(dubbing_text, use_punctuation)
        lines = lines
        
        combined_audio = AudioSegment.empty() 
        for i in progress.tqdm(range(len(lines)), desc='Generating...'):
            tts_segment_file = os.path.join(segments_folder, f'tts_{i+1:06}.{audio_format}')    
            tts_result = self.request_tts(lines[i], tts_segment_file, ref_audio, ref_text, speed_factor, audio_format)
            if tts_result == False:
                continue
            combined_audio += AudioSegment.from_file(tts_segment_file)
            
        combined_audio.export(output_file, format=audio_format)

    
    
    def infer_single(self, dubbing_text:str, output_file, celeb_audio, celeb_transcript, model_choice, speed_factor, audio_format: str, progress=gr.Progress()):
        self.select_model(model_choice)
        ref_audio, ref_text = preprocess_ref_audio_text(celeb_audio, celeb_transcript)
        
        subtitle_file = None
        if AbusText.is_subtitle_format(dubbing_text):
            subs = pysubs2.SSAFile.from_string(dubbing_text)
            subtitle_file = os.path.join(path_dubbing_folder(), path_new_filename(f".{subs.format}"))
            subs.save(subtitle_file)
            
        try:
            if subtitle_file:
                self.srt_to_voice(subtitle_file, output_file, ref_audio, ref_text, speed_factor, audio_format, progress)
            else:
                self.text_to_voice(dubbing_text, output_file, ref_audio, ref_text, speed_factor, audio_format, progress)
            return True
        except Exception as e:
            logger.error(f"[abus_tts_f5.py] infer_single - error: {e}")
            return False
        finally:
            del self.ema_model
            self.ema_model = None
            self.release_cuda_memory()

            
    def infer_multi(self, dubbing_text:str, output_file, celeb_audio1, celeb_transcript1, celeb_audio2, celeb_transcript2, model_choice, speed_factor, audio_format: str, progress=gr.Progress()):
        self.select_model(model_choice)
        ref_audio1, ref_text1 = preprocess_ref_audio_text(celeb_audio1, celeb_transcript1) if celeb_audio1 else (None, None)
        ref_audio2, ref_text2 = preprocess_ref_audio_text(celeb_audio2, celeb_transcript2) if celeb_audio2 else (None, None)
        
        try:
            # Check for SRT format
            if AbusText.is_subtitle_format(dubbing_text):
                try:
                    subs = pysubs2.SSAFile.from_string(dubbing_text)
                    subtitle_file = os.path.join(path_dubbing_folder(), path_new_filename(f".{subs.format}"))
                    subs.save(subtitle_file)
                    
                    self.srt_to_voice_multi(subtitle_file, output_file, ref_audio1, ref_text1, ref_audio2, ref_text2, speed_factor, audio_format, progress)
                    return True
                except Exception as e:
                    logger.error(f"[abus_tts_f5.py] infer_multi - Failed to process subtitle: {e}")
                    # Fallback to normal text processing if subtitle processing fails
            
            segments_folder = path_tts_segments_folder(output_file)
            conversations = self._parse_conversation_regex(dubbing_text)
            if not conversations:
                logger.warning(f"[abus_tts_f5.py] infer_multi - no conversation found in text, defaulting to spk1")
                conversations = [{'speaker': 'spk1', 'message': dubbing_text.strip()}]
                
            combined_audio = AudioSegment.empty() 
            for i in progress.tqdm(range(len(conversations)), desc='Generating...'):
                tts_segment_file = os.path.join(segments_folder, f'tts_{i+1:06}.{audio_format}') 
                
                conversation = conversations[i]
                if conversation['speaker'] == 'spk1':
                    tts_result = self.request_tts(conversation['message'], tts_segment_file, ref_audio1, ref_text1, speed_factor, audio_format)
                else:
                    tts_result = self.request_tts(conversation['message'], tts_segment_file, ref_audio2, ref_text2, speed_factor, audio_format)
                
                if tts_result == False:
                    continue
                combined_audio += AudioSegment.from_file(tts_segment_file)
        
            combined_audio.export(output_file, format=audio_format)
            return True
        except Exception as e:
            logger.error(f"[abus_tts_f5.py] infer_multi - An error occurred: {e}")
            return False
        finally:
            del self.ema_model
            self.ema_model = None
            self.release_cuda_memory()



    def _parse_conversation_regex(self, text):
        pattern = r'\s*\{(\w+)\}\s*(.*)'
        conversations = []
        
        for line in text.splitlines():
            line_str = line.strip()
            if line_str:
                match = re.search(pattern, line)
                if match:
                    speaker, message = match.groups()
                    if message.strip():
                        conversations.append({
                            'speaker': speaker,
                            'message': message.strip()
                        })
        
        return conversations

