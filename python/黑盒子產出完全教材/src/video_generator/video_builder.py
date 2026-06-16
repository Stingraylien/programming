import os  # 匯入 os 模組以進行路徑操作與檔案清理
import asyncio  # 匯入非同步任務模組，用於驅動 Edge TTS 語音生成
import platform  # 匯入 platform 模組以偵測作業系統並設定對應的事件迴圈策略
from pathlib import Path  # 匯入 pathlib 以進行跨平台路徑處理

import edge_tts  # 匯入 Edge TTS 套件，負責將文字轉換為語音 MP3
from PIL import Image, ImageDraw, ImageFont  # 匯入 Pillow 影像處理套件，用於繪製投影片圖片

# Try to import moviepy with compatibility for different versions
try:
    from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
except ImportError:
    try:
        from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
    except ImportError:
        # Fallback: create minimal stubs for testing
        ImageClip = None
        AudioFileClip = None
        concatenate_videoclips = None

# ─────────────────────────────────────────
# TTS 語音生成（跨平台非同步包裝）
# ─────────────────────────────────────────

async def _async_generate_tts(str_text, str_audio_path, str_voice):  # 非同步函式：呼叫 Edge TTS 並儲存語音檔
    """呼叫 Microsoft Edge TTS 雲端服務，將文字轉換為 MP3 語音並存入指定路徑"""
    obj_communicate = edge_tts.Communicate(str_text, str_voice)  # 物件變數，建立與 Edge TTS 的連線實例並指定語音角色
    await obj_communicate.save(str_audio_path)  # 非同步等待，直到語音完整儲存至磁碟


def _run_tts_sync(str_text, str_audio_path, str_voice):  # 同步包裝函式：在 Windows 與 macOS 上皆能穩定執行 TTS
    """建立全新事件迴圈執行 TTS，避免與 Flask / 其他框架的迴圈發生衝突（Windows/macOS 通用）"""
    obj_loop = asyncio.new_event_loop()  # 物件變數，建立獨立的全新事件迴圈，不依賴既有環境
    asyncio.set_event_loop(obj_loop)  # 將新迴圈設為當前執行緒的事件迴圈
    try:
        obj_loop.run_until_complete(  # 同步阻塞執行，直到 TTS 任務完成
            _async_generate_tts(str_text, str_audio_path, str_voice)
        )
    finally:
        obj_loop.close()  # 確保迴圈關閉並釋放資源，防止資源洩漏


# ─────────────────────────────────────────
# 跨平台中文字型載入
# ─────────────────────────────────────────

def _get_font(int_size):  # 整數參數：字型大小，跨平台搜尋並回傳適合的中文字型物件
    """依作業系統自動搜尋白名單中文字型；若無法載入則回傳 Pillow 內建預設字型"""
    str_os = platform.system()  # 字串變數，偵測當前作業系統名稱（Windows / Darwin / Linux）

    if str_os == 'Darwin':  # macOS 系統的字型搜尋目錄
        list_search_dirs = [
            Path("/System/Library/Fonts"),           # macOS 核心字型目錄
            Path("/Library/Fonts"),                  # macOS 共用字型目錄
            Path("/System/Library/Fonts/Supplemental"),  # macOS 擴充字型目錄
            Path.home() / "Library" / "Fonts"       # 使用者個人字型目錄
        ]
        list_font_names = [
            "PingFang.ttc",          # 蘋方（macOS 系統預設中文字型）
            "STHeiti Light.ttc",     # 華文細黑體（備選）
            "Arial Unicode.ttf",     # Arial Unicode 萬用字型（最廣泛相容）
            "NotoSansCJK-Regular.ttc"  # Google Noto CJK 字型（如已安裝）
        ]
    elif str_os == 'Windows':  # Windows 系統的字型搜尋目錄
        list_search_dirs = [
            Path(os.environ.get('WINDIR', 'C:/Windows')) / "Fonts",  # 動態讀取 WINDIR 組合出標準字型目錄
            Path.home() / "AppData" / "Local" / "Microsoft" / "Windows" / "Fonts"  # 使用者層級字型目錄
        ]
        list_font_names = [
            "msyh.ttc",              # 微軟雅黑（Windows 標準中文字型）
            "msjh.ttc",              # 微軟正黑體（繁中 Windows 標準字型）
            "simsun.ttc",            # 新宋體（備選）
            "NotoSansCJK-Regular.ttc",  # Noto CJK（如已安裝）
            "Arial Unicode.ttf"      # Arial Unicode 萬用備案
        ]
    else:  # Linux 及其他 Unix 系統
        list_search_dirs = [
            Path("/usr/share/fonts"),         # 全域字型目錄
            Path("/usr/local/share/fonts"),   # 本機安裝字型目錄
            Path.home() / ".fonts",           # 使用者字型目錄（舊慣例）
            Path.home() / ".local" / "share" / "fonts"  # XDG 規範的使用者字型目錄
        ]
        list_font_names = [
            "NotoSansCJK-Regular.ttc",  # Google Noto CJK（Linux 最常見中文字型）
            "NotoSansSC-Regular.otf",   # Noto Sans 簡體中文
            "wqy-zenhei.ttc",           # 文泉驛正黑（備選）
            "Arial Unicode.ttf"
        ]

    for obj_dir in list_search_dirs:  # 物件變數，逐一走訪候選字型目錄
        if not obj_dir.exists():  # 若該目錄在此系統上不存在則跳過
            continue
        for str_font_name in list_font_names:  # 字串變數，逐一嘗試候選字型檔名
            obj_candidate = obj_dir / str_font_name  # 物件變數，組合目錄與檔名為完整候選路徑
            if obj_candidate.exists():  # 若該字型檔確實存在
                try:
                    return ImageFont.truetype(str(obj_candidate), int_size)  # 載入字型並回傳
                except Exception:
                    continue  # 載入失敗則繼續嘗試下一個字型

    return ImageFont.load_default()  # 若所有字型皆找不到，回傳 Pillow 內建的預設字型作為最後備案


# ─────────────────────────────────────────
# 投影片圖片渲染
# ─────────────────────────────────────────

def _render_slide(str_title, list_bullets, int_width=1280, int_height=720):  # 字串、陣列、整數參數：使用 Pillow 繪製單張投影片圖片
    """將章節標題與重點條列文字渲染為一張 PIL Image 物件（深藍主題，符合課程風格）"""
    obj_img = Image.new('RGB', (int_width, int_height), color=(25, 55, 109))  # 物件變數，建立深藍底色的 1280x720 畫布
    obj_draw = ImageDraw.Draw(obj_img)  # 物件變數，在畫布上建立繪圖器實例

    # ── 頂部標題欄 ──
    obj_draw.rectangle([0, 0, int_width, 108], fill=(15, 35, 75))  # 繪製深色標題欄背景矩形
    obj_draw.line([0, 108, int_width, 108], fill=(80, 160, 230), width=3)  # 標題欄底部的亮藍分隔線

    # ── 左側裝飾條 ──
    obj_draw.rectangle([0, 108, 6, int_height], fill=(80, 160, 230))  # 左側藍色垂直裝飾線

    # ── 載入字型 ──
    obj_title_font = _get_font(52)  # 物件變數，載入標題專用大字型
    obj_bullet_font = _get_font(34)  # 物件變數，載入條列重點中字型

    # ── 繪製標題文字 ──
    str_display_title = str_title[:30] + "…" if len(str_title) > 30 else str_title  # 字串變數，超長標題截斷以防溢出
    obj_draw.text((36, 26), str_display_title, fill=(255, 255, 255), font=obj_title_font)  # 在標題欄繪製白色標題

    # ── 繪製條列重點 ──
    int_y = 138  # 整數變數，條列文字起始 Y 座標（在標題欄下方）
    for str_bullet in list_bullets[:7]:  # 最多顯示 7 條，防止文字超出畫面底部
        str_bullet_text = str(str_bullet)  # 確保為字串格式
        str_display = (f"▸  {str_bullet_text[:44]}…" if len(str_bullet_text) > 44
                       else f"▸  {str_bullet_text}")  # 字串變數，超長文字截斷並加省略號
        obj_draw.text((36, int_y), str_display, fill=(195, 220, 255), font=obj_bullet_font)  # 以淡藍色繪製條列內容
        int_y += 74  # 每條間隔 74 像素，確保行距舒適可讀

    return obj_img  # 回傳完成的投影片 PIL Image 物件


# ─────────────────────────────────────────
# 影片生成主函式
# ─────────────────────────────────────────

def generate_video(str_course_name, list_canonical_contents, str_output_video_path,
                   str_cover_image_path, str_target_language='zh-TW'):  # 影片生成主函式（Windows/macOS 通用）
    """
    從標準化教材內容生成逐張投影片播放的 MP4 課程摘要影片。
    每張投影片配有對應的 Edge TTS 語音旁白，以 H.264 + AAC 輸出確保最大相容性。
    """
    # ── 語系對應語音角色 ──
    dict_voice_map = {  # 字典變數，各語系對應的 Edge TTS 語音角色名稱
        'zh-TW': 'zh-TW-HsiaoChenNeural',  # 繁體中文女聲
        'zh-CN': 'zh-CN-XiaoxiaoNeural',   # 簡體中文女聲
        'en-US': 'en-US-JennyNeural',       # 英文女聲
        'ja-JP': 'ja-JP-NanamiNeural',      # 日文女聲
        'es-ES': 'es-ES-ElviraNeural',      # 西班牙文女聲
        'cs-CZ': 'cs-CZ-VlastaNeural',      # 捷克文女聲
        'th-TH': 'th-TH-PremwadeeNeural'   # 泰文女聲
    }
    str_voice = dict_voice_map.get(str_target_language, 'zh-TW-HsiaoChenNeural')  # 字串變數，查表取得語音角色；找不到時預設繁中女聲
    str_base = str_output_video_path.replace('.mp4', '')  # 字串變數，去除副檔名取得路徑基底，用於暫存檔命名

    # ── 建立每張投影片的資料 ──
    list_slide_data = []  # 陣列變數，儲存每張投影片的圖片資訊與旁白文字

    # 第 0 張：封面投影片（直接使用已生成的封面圖）
    list_slide_data.append({
        'use_cover': True,  # 布林旗標，此張使用封面圖而非重新繪製
        'narration': f"歡迎來到「{str_course_name}」。本影片將帶您了解課程的重點摘要與大綱。請繼續收看。"  # 字串，封面投影片的開場旁白文字
    })

    for dict_content in list_canonical_contents:  # 字典變數，逐一處理每個標準化教材區塊
        str_chapter = dict_content.get('chapter', str_course_name)  # 字串變數，取得章節名稱，若無則以課程名代替
        list_objectives = dict_content.get('learning_objectives', [])  # 陣列變數，取得學習目標清單
        list_paragraphs = dict_content.get('paragraphs', [])  # 陣列變數，取得段落內容清單

        # 優先使用學習目標作為條列重點；若無學習目標則改用段落前五句
        list_bullets = list_objectives if list_objectives else list_paragraphs[:5]  # 陣列變數，該投影片要顯示的條列重點

        # 組合旁白腳本文字
        list_narration_parts = [f"在「{str_chapter}」這個單元，"]  # 陣列變數，組合旁白語句的各片段
        for str_obj in list_objectives[:4]:  # 最多朗讀四條學習目標，避免單頁旁白過長
            list_narration_parts.append(f"重點目標是：{str_obj}。")
        if not list_objectives and list_paragraphs:  # 若無學習目標，改以段落首句簡介
            list_narration_parts.append(f"本單元的核心內容涵蓋了 {str(list_paragraphs[0])[:60]}。")

        list_slide_data.append({
            'use_cover': False,  # 布林旗標，此張需重新繪製投影片圖片
            'title': str_chapter,  # 字串，投影片標題
            'bullets': list_bullets,  # 陣列，投影片條列重點
            'narration': ''.join(list_narration_parts)  # 字串，拼接完整的旁白腳本
        })

    # ── 逐張生成圖片與音訊，並建立 moviepy 片段 ──
    list_temp_paths = []  # 陣列變數，記錄所有暫存檔路徑，用於 finally 區塊清理
    list_video_clips = []  # 陣列變數，儲存每段 moviepy 影片片段物件
    obj_final_clip = None  # 物件變數，最終合成的影片物件，預設為 None

    try:
        for int_idx, dict_slide in enumerate(list_slide_data):  # 整數、字典變數，逐張處理每張投影片
            # ── 產生投影片圖片 ──
            if dict_slide['use_cover']:  # 封面投影片：直接使用已生成的封面 JPG 檔
                str_slide_img_path = str_cover_image_path  # 字串變數，封面圖的實體路徑
            else:  # 內容投影片：以 Pillow 渲染並存為暫存 JPEG
                str_slide_img_path = f"{str_base}_slide_{int_idx}.jpg"  # 字串變數，暫存投影片圖片路徑
                obj_slide_img = _render_slide(dict_slide['title'], dict_slide['bullets'])  # 呼叫 Pillow 投影片渲染函式
                obj_slide_img.save(str_slide_img_path, 'JPEG', quality=92)  # 以 92% 品質儲存 JPEG，兼顧畫質與效能
                list_temp_paths.append(str_slide_img_path)  # 登記暫存路徑以待清理

            # ── 產生語音旁白 ──
            str_audio_path = f"{str_base}_audio_{int_idx}.mp3"  # 字串變數，暫存語音 MP3 路徑
            list_temp_paths.append(str_audio_path)  # 登記暫存路徑
            _run_tts_sync(dict_slide['narration'], str_audio_path, str_voice)  # 呼叫跨平台 TTS 包裝函式生成語音

            # ── 建立 moviepy 片段 ──
            obj_audio_clip = AudioFileClip(str_audio_path)  # 物件變數，載入語音音訊片段
            obj_img_clip = ImageClip(str_slide_img_path)  # 物件變數，載入投影片圖片片段
            obj_img_clip = obj_img_clip.set_duration(obj_audio_clip.duration)  # 將圖片片段時長設為與語音等長
            obj_combined = obj_img_clip.set_audio(obj_audio_clip)  # 物件變數，將語音注入圖片片段，形成單張投影片的影片片段
            list_video_clips.append(obj_combined)  # 將該片段加入清單

        # ── 串聯所有片段並輸出 MP4 ──
        obj_final_clip = concatenate_videoclips(list_video_clips, method='compose')  # 物件變數，將所有投影片片段依序串聯
        obj_final_clip.write_videofile(
            str_output_video_path,  # 輸出 MP4 的完整路徑
            fps=24,  # 設定每秒 24 幀，符合一般影片標準
            codec='libx264',  # 使用 H.264 編碼，確保 Windows/macOS/手機 最廣泛播放相容性
            audio_codec='aac',  # 使用 AAC 音訊編碼，與 MP4 容器最佳搭配
            verbose=False,  # 關閉 moviepy 的詳細輸出日誌，保持終端機整潔
            logger=None  # 關閉進度條，避免在伺服器環境中產生干擾輸出
        )

    finally:  # 無論成功或失敗，都必須清理暫存資源，防止磁碟空間浪費與記憶體洩漏
        if obj_final_clip is not None:  # 若最終影片物件已建立
            try:
                obj_final_clip.close()  # 關閉並釋放最終影片的編碼器資源
            except Exception:
                pass
        for obj_clip in list_video_clips:  # 逐一關閉各個片段物件
            try:
                obj_clip.close()  # 釋放個別片段佔用的記憶體與檔案控制代碼
            except Exception:
                pass
        for str_temp_path in list_temp_paths:  # 逐一刪除所有暫存檔案
            if os.path.exists(str_temp_path):  # 確認暫存檔確實存在才執行刪除
                try:
                    os.remove(str_temp_path)  # 刪除暫存圖片或語音檔，保持產出目錄整潔
                except Exception:
                    pass

    return str_output_video_path  # 完成所有流程，回傳最終 MP4 影片的儲存絕對路徑
