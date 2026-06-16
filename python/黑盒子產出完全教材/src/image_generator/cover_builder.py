from PIL import Image, ImageDraw, ImageFont  # 匯入 Pillow 影像處理核心模組，用於建立畫布、繪製文字與圖形
import os  # 匯入 os 模組用於路徑處理
from pathlib import Path  # 匯入 pathlib 進行跨平台路徑操作
import platform  # 匯入 platform 偵測作業系統種類


def _get_font(int_size):  # 整數參數：字型大小，跨平台搜尋並回傳適合的中文字型物件
    """依作業系統搜尋白名單中文字型；若找不到則回傳 Pillow 內建預設字型"""
    str_os = platform.system()  # 字串變數，偵測當前作業系統名稱（Windows / Darwin / Linux）

    if str_os == 'Darwin':  # macOS 字型目錄與候選清單
        list_search_dirs = [
            Path("/System/Library/Fonts"),
            Path("/Library/Fonts"),
            Path("/System/Library/Fonts/Supplemental"),
            Path.home() / "Library" / "Fonts"
        ]
        list_font_names = ["PingFang.ttc", "STHeiti Light.ttc", "Arial Unicode.ttf", "NotoSansCJK-Regular.ttc"]
    elif str_os == 'Windows':  # Windows 字型目錄與候選清單
        list_search_dirs = [
            Path(os.environ.get('WINDIR', 'C:/Windows')) / "Fonts",
            Path.home() / "AppData" / "Local" / "Microsoft" / "Windows" / "Fonts"
        ]
        list_font_names = ["msyh.ttc", "msjh.ttc", "simsun.ttc", "NotoSansCJK-Regular.ttc", "Arial Unicode.ttf"]
    else:  # Linux 字型目錄與候選清單
        list_search_dirs = [
            Path("/usr/share/fonts"),
            Path("/usr/local/share/fonts"),
            Path.home() / ".fonts",
            Path.home() / ".local" / "share" / "fonts"
        ]
        list_font_names = ["NotoSansCJK-Regular.ttc", "NotoSansSC-Regular.otf", "wqy-zenhei.ttc", "Arial Unicode.ttf"]

    for obj_dir in list_search_dirs:  # 物件變數，逐一走訪候選字型目錄
        if not obj_dir.exists():  # 若目錄不存在則跳過
            continue
        for str_font_name in list_font_names:  # 字串變數，逐一嘗試候選字型檔名
            obj_candidate = obj_dir / str_font_name  # 物件變數，組合目錄與檔名
            if obj_candidate.exists():
                try:
                    return ImageFont.truetype(str(obj_candidate), int_size)  # 載入並回傳
                except Exception:
                    continue

    return ImageFont.load_default()  # 所有路徑失敗時，回傳 Pillow 內建預設字型


def _draw_gradient_bg(obj_draw, int_width, int_height):  # 物件、整數參數：在畫布上繪製漸層背景
    """由上而下繪製深藍到深靛漸層背景，模擬簡報封面的專業視覺效果"""
    # 計算上下兩端的 RGB 顏色
    tuple_color_top = (18, 52, 99)  # 頂端：深海藍
    tuple_color_bottom = (12, 28, 60)  # 底端：深靛藍

    for int_y in range(int_height):  # 整數變數，逐行掃描計算漸層色值
        float_ratio = int_y / int_height  # 浮點數變數，當前行位置佔總高度的比例（0.0 ~ 1.0）
        int_r = int(tuple_color_top[0] + (tuple_color_bottom[0] - tuple_color_top[0]) * float_ratio)  # 整數：紅色分量
        int_g = int(tuple_color_top[1] + (tuple_color_bottom[1] - tuple_color_top[1]) * float_ratio)  # 整數：綠色分量
        int_b = int(tuple_color_top[2] + (tuple_color_bottom[2] - tuple_color_top[2]) * float_ratio)  # 整數：藍色分量
        obj_draw.line([0, int_y, int_width, int_y], fill=(int_r, int_g, int_b))  # 繪製當前行的漸層色橫線


def generate_cover_image(str_course_name, str_output_path, list_canonical_contents=None):  # 封面圖生成主函式
    """
    依課程名稱與教材內容生成一張 1280x720 的 JPG 課程封面圖。
    封面設計：漸層深藍背景、課程名稱主標題、副標題、以及從教材萃取的關鍵學習主題標籤。
    支援 Windows 與 macOS 跨平台中文字型自動搜尋。
    """
    int_width, int_height = 1280, 720  # 整數變數，定義封面圖的標準 16:9 寬高尺寸

    obj_img = Image.new('RGB', (int_width, int_height), color=(18, 52, 99))  # 物件變數，建立底色畫布（漸層函式會蓋過底色）
    obj_draw = ImageDraw.Draw(obj_img)  # 物件變數，建立繪圖器

    # ── 繪製漸層背景 ──
    _draw_gradient_bg(obj_draw, int_width, int_height)

    # ── 裝飾元素：頂部與底部橫條 ──
    obj_draw.rectangle([0, 0, int_width, 8], fill=(60, 140, 230))  # 頂部亮藍細條（品牌色條）
    obj_draw.rectangle([0, int_height - 8, int_width, int_height], fill=(60, 140, 230))  # 底部亮藍細條（對稱設計）

    # ── 裝飾元素：中央分隔線 ──
    int_center_y = int_height // 2 + 30  # 整數變數，中央分隔線的 Y 軸位置，略低於垂直中心
    obj_draw.line([80, int_center_y, int_width - 80, int_center_y], fill=(60, 140, 230, 120), width=1)  # 繪製細分隔線

    # ── 載入字型 ──
    obj_title_font = _get_font(76)   # 物件變數，課程名稱主標題用的大字型
    obj_sub_font = _get_font(36)     # 物件變數，副標題用的中字型
    obj_tag_font = _get_font(26)     # 物件變數，關鍵主題標籤用的小字型
    int_tag_font_size = getattr(obj_tag_font, 'size', 26)  # 整數變數，安全取得字型大小；預設字型無此屬性時回傳請求大小

    # ── 計算課程名稱寬高，使其水平置中 ──
    try:
        dict_title_bbox = obj_draw.textbbox((0, 0), str_course_name, font=obj_title_font)  # 字典變數，計算標題文字邊界框
        int_title_w = dict_title_bbox[2] - dict_title_bbox[0]  # 整數：文字寬度
        int_title_h = dict_title_bbox[3] - dict_title_bbox[1]  # 整數：文字高度
    except AttributeError:  # 舊版 Pillow 不支援 textbbox
        int_title_w, int_title_h = obj_draw.textsize(str_course_name, font=obj_title_font)  # 舊版 API 備案

    int_title_x = (int_width - int_title_w) // 2  # 整數變數：標題水平置中的 X 座標
    int_title_y = int(int_height * 0.22)  # 整數變數：標題位於畫面 22% 高度處

    # ── 繪製課程名稱（帶陰影效果） ──
    obj_draw.text((int_title_x + 3, int_title_y + 3), str_course_name,  # 先繪製陰影（偏移 3px，深色）
                  fill=(0, 0, 0, 100), font=obj_title_font)
    obj_draw.text((int_title_x, int_title_y), str_course_name,  # 再繪製主標題（白色）
                  fill=(255, 255, 255), font=obj_title_font)

    # ── 繪製副標題 ──
    str_subtitle = "完全教材摘要與試題"  # 字串變數，固定的副標題文字
    try:
        dict_sub_bbox = obj_draw.textbbox((0, 0), str_subtitle, font=obj_sub_font)  # 計算副標題邊界框
        int_sub_w = dict_sub_bbox[2] - dict_sub_bbox[0]
    except AttributeError:
        int_sub_w, _ = obj_draw.textsize(str_subtitle, font=obj_sub_font)

    int_sub_x = (int_width - int_sub_w) // 2  # 整數變數：副標題水平置中 X 座標
    int_sub_y = int_title_y + int_title_h + 22  # 整數變數：副標題位於主標題下方 22px
    obj_draw.text((int_sub_x, int_sub_y), str_subtitle, fill=(150, 195, 245), font=obj_sub_font)  # 淡藍色副標題

    # ── 從教材內容萃取關鍵學習主題，繪製標籤 ──
    list_topics = []  # 陣列變數，儲存要顯示的關鍵主題標籤文字
    if list_canonical_contents:  # 若有傳入教材內容
        for dict_content in list_canonical_contents[:3]:  # 最多取前三個教材區塊
            str_chapter = dict_content.get('chapter', '')  # 字串變數，取得章節名稱
            if str_chapter and str_chapter not in list_topics:  # 排除空值與重複
                list_topics.append(str_chapter[:18])  # 截斷過長的章節名稱（最多 18 字）
            list_objectives = dict_content.get('learning_objectives', [])  # 陣列變數，取得學習目標
            for str_obj in list_objectives[:2]:  # 每個區塊最多取 2 條學習目標
                str_short = str_obj[:20]  # 字串變數，截斷過長的目標文字
                if str_short and str_short not in list_topics:
                    list_topics.append(str_short)
        list_topics = list_topics[:5]  # 整體最多顯示 5 個標籤，防止畫面過於擁擠

    if list_topics:  # 若有關鍵主題可顯示
        int_tag_y = int(int_height * 0.72)  # 整數變數：標籤列的起始 Y 座標（畫面下方 72% 處）
        int_tag_padding_x, int_tag_padding_y = 16, 8  # 整數變數：標籤內邊距
        int_tag_gap = 18  # 整數變數：標籤之間的水平間隔
        int_tag_radius = 8  # 整數變數：標籤圓角矩形的圓角半徑（模擬標籤外形）

        # 計算所有標籤的總寬度，用於水平置中
        list_tag_widths = []  # 陣列變數，儲存各標籤的寬度
        for str_topic in list_topics:
            try:
                dict_tag_bbox = obj_draw.textbbox((0, 0), str_topic, font=obj_tag_font)
                int_tag_w = dict_tag_bbox[2] - dict_tag_bbox[0]
            except AttributeError:
                int_tag_w, _ = obj_draw.textsize(str_topic, font=obj_tag_font)
            list_tag_widths.append(int_tag_w + int_tag_padding_x * 2)  # 標籤總寬 = 文字寬 + 左右內邊距

        int_total_tags_w = sum(list_tag_widths) + int_tag_gap * (len(list_topics) - 1)  # 整數：所有標籤加間隔的總寬
        int_tags_start_x = (int_width - int_total_tags_w) // 2  # 整數：標籤列水平置中的起始 X 座標

        int_current_x = int_tags_start_x  # 整數變數：目前繪製到的 X 位置
        for int_i, str_topic in enumerate(list_topics):  # 整數、字串變數，逐一繪製每個標籤
            int_tag_w = list_tag_widths[int_i]  # 整數：當前標籤寬度

            # 繪製標籤背景（半透明深藍圓角矩形）
            list_tag_box = [int_current_x, int_tag_y,
                            int_current_x + int_tag_w, int_tag_y + int_tag_font_size + int_tag_padding_y * 2]  # 陣列：標籤邊界座標
            obj_draw.rounded_rectangle(list_tag_box, radius=int_tag_radius,
                                       fill=(40, 90, 160), outline=(80, 150, 230), width=1)  # 繪製帶邊框的圓角矩形

            # 繪製標籤文字
            obj_draw.text((int_current_x + int_tag_padding_x, int_tag_y + int_tag_padding_y),
                          str_topic, fill=(200, 225, 255), font=obj_tag_font)  # 以淡藍色繪製標籤文字

            int_current_x += int_tag_w + int_tag_gap  # 移動到下一個標籤的起始位置

    obj_img.save(str_output_path, 'JPEG', quality=95)  # 以 95% 品質儲存封面圖為 JPEG 格式
    return str_output_path  # 回傳產出的封面圖片完整路徑
