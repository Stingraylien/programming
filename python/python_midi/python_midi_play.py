
# gmeini 所創作

from midiutil import MIDIFile
import random

def create_dramatic_intro():
    # 設定：2 個軌道 (0: 小提琴, 1: 管弦樂團), 速度 144 BPM
    midi = MIDIFile(2)
    track_violin = 0
    track_orchestra = 1
    time = 0    # 起始時間
    tempo = 144 # 快板
    
    # 設定兩個軌道的初始參數
    midi.addTempo(track_violin, time, tempo)
    midi.addTempo(track_orchestra, time, tempo)

    # 設定樂器 (Program Change)
    # 40 = Violin, 48 = String Ensemble 1 (用於模擬大樂團)
    midi.addProgramChange(track_violin, 0, 0, 40)
    midi.addProgramChange(track_orchestra, 0, 0, 48)

    # === 樂理結構 (C Minor: C, Eb, G) ===
    # 10秒 @ 144 BPM 大約是 6 個小節 (4/4拍)
    # 和弦進行: Cm -> Cm -> Fm -> G7 -> Cm (最後一擊)
    
    # 定義和弦音符 (MIDI Note Numbers)
    # C4=60, C5=72
    chord_cm_high = [72, 75, 79, 84] # C5, Eb5, G5, C6
    chord_fm_high = [77, 80, 84, 89] # F5, Ab5, C6, F6
    chord_g7_high = [79, 83, 86, 89] # G5, B5, D6, F6 (Dominant Tension)
    
    chord_cm_low = [36, 48, 60, 63]  # C1, C2, C3, Eb3 (Heavy Impact)
    chord_fm_low = [41, 53, 65, 68]  # F1, F2, F3, Ab3
    chord_g7_low = [43, 55, 67, 71]  # G1, G2, G3, B3

    # === Track 1: Virtuoso Violin Solo (16th notes / 16分音符) ===
    # 每個小節 16 個 16分音符 (duration = 0.25)
    
    current_time = 0
    bars = 6
    
    for bar in range(bars):
        # 決定當前小節的和弦
        if bar < 2: 
            notes = chord_cm_high
        elif bar < 4:
            notes = chord_fm_high
        elif bar < 5:
            notes = chord_g7_high # 第5小節張力最大
        else:
            notes = [84] # 第6小節收尾在 High C
        
        # 生成琶音樣式 (Up and Down Pattern)
        # 樣式：根-三-五-八-五-三-根-三...
        pattern_indices = [0, 1, 2, 3, 2, 1, 0, 1, 0, 1, 2, 3, 2, 1, 0, 1]
        
        for i in range(16): # 4 beats * 4 notes
            if bar == 5 and i > 0: break # 最後一小節只彈第一個音
            
            note_index = pattern_indices[i] % len(notes)
            note = notes[note_index]
            
            # 增加一點隨機力度 (Velocity) 讓聲音不那麼生硬
            velocity = random.randint(90, 110) 
            # 稍微調整 note 開始時間，製造一點點 "人味" (Humanize)
            human_offset = random.uniform(0, 0.02)
            
            midi.addNote(track_violin, 0, note, current_time + human_offset, 0.25, velocity)
            current_time += 0.25

    # === Track 2: Orchestral Hits (重擊伴奏) ===
    # 只在第 1 拍和第 3 拍演奏 (Staccato)
    
    orch_time = 0
    for bar in range(bars):
        if bar < 2: 
            chord = chord_cm_low
        elif bar < 4:
            chord = chord_fm_low
        elif bar < 5:
            chord = chord_g7_low
        else:
            chord = [36, 48, 60] # Final C Power Chord
            
        # 節奏模式：砰 (休) 砰 (休)
        # Beat 1
        velocity = 120 # 非常大聲
        duration = 0.4 # 短促 (Staccato)
        
        if bar == 5: # 最後一小節
             for note in chord:
                midi.addNote(track_orchestra, 0, note, orch_time, 4, 127) # 長音收尾
             break

        # Beat 1 Hit
        for note in chord:
            midi.addNote(track_orchestra, 0, note, orch_time, duration, velocity)
        
        # Beat 2 Rest
        
        # Beat 3 Hit (稍微輕一點點)
        for note in chord:
             midi.addNote(track_orchestra, 0, note, orch_time + 2, duration, velocity - 10)
             
        orch_time += 4 # Move to next bar

    # === 輸出檔案 ===
    with open("dramatic_intro.mid", "wb") as output_file:
        midi.writeFile(output_file)
    print("MIDI 檔案 'dramatic_intro.mid' 已生成！請匯入您的 DAW。")

if __name__ == "__main__":
    create_dramatic_intro()