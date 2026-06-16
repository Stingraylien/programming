import os
from datetime import datetime


def export_text_summary(str_course_name, list_canonical_contents, str_output_path):
    list_lines = []

    list_lines.append("=" * 50)
    list_lines.append(f"課程名稱：{str_course_name}")
    list_lines.append("=" * 50)
    list_lines.append("")

    list_lines.append("【課程目標】")
    int_obj_count = 1
    for dict_content in list_canonical_contents:
        for str_obj in dict_content.get('learning_objectives', []):
            list_lines.append(f"  {int_obj_count}. {str_obj}")
            int_obj_count += 1
    if int_obj_count == 1:
        list_lines.append("  （無法擷取課程目標）")
    list_lines.append("")

    list_lines.append("【課程大綱】")
    for int_idx, dict_content in enumerate(list_canonical_contents, 1):
        str_chapter = dict_content.get('chapter', '未命名章節')
        list_lines.append(f"  {int_idx}. {str_chapter}")
    if not list_canonical_contents:
        list_lines.append("  （無法擷取課程大綱）")
    list_lines.append("")

    list_lines.append("-" * 50)
    list_lines.append(f"產出時間：{datetime.now().strftime('%Y-%m-%d %H:%M')}")

    with open(str_output_path, 'w', encoding='utf-8') as obj_file:
        obj_file.write("\n".join(list_lines))
    return str_output_path
