#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from typing import List, Dict

def export_to_excel(list_questions: List[Dict], str_filename: str = "training_question_bank.xlsx"):
    """
    Export questions to XuLink compatible Excel format.
    Follows the format specified in test_rule.md
    """
    list_rows = []

    for dict_question in list_questions:
        # Add question header row
        dict_question_row = {
            "#Qtype": dict_question.get("type", ""),
            "Subject": dict_question.get("subject", ""),
            "Option": "",
            "Weight": dict_question.get("weight", 1),
            "Difficulty": dict_question.get("difficulty", 3),
            "Answer": "",
            "Option Limit Type": dict_question.get("option_limit_type", 0),
            "Option Limit Count": dict_question.get("option_limit_count", 0),
            "Analyze(for QBank)": dict_question.get("analyze", ""),
            "NoRandom(for QBank)": dict_question.get("no_random", 0)
        }
        list_rows.append(dict_question_row)

        # Add option rows
        if "options" in dict_question:
            for int_i, str_option in enumerate(dict_question["options"]):
                bool_is_correct = False
                
                if isinstance(dict_question.get("answer"), str):
                    bool_is_correct = (str_option == dict_question.get("answer"))
                elif isinstance(dict_question.get("answer"), list):
                    bool_is_correct = (str_option in dict_question.get("answer", []))
                
                str_answer_mark = "y" if bool_is_correct else ""
                
                dict_option_row = {
                    "#Qtype": "",
                    "Subject": "",
                    "Option": str_option,
                    "Weight": "",
                    "Difficulty": "",
                    "Answer": str_answer_mark,
                    "Option Limit Type": "",
                    "Option Limit Count": "",
                    "Analyze(for QBank)": "",
                    "NoRandom(for QBank)": ""
                }
                list_rows.append(dict_option_row)

    # Create DataFrame with correct column order
    df_excel = pd.DataFrame(list_rows, columns=[
        "#Qtype", "Subject", "Option", "Weight", "Difficulty", "Answer",
        "Option Limit Type", "Option Limit Count", "Analyze(for QBank)", "NoRandom(for QBank)"
    ])

    # Save to Excel
    df_excel.to_excel(str_filename, index=False, sheet_name='Questions')
    
    return str_filename
