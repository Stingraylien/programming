import unittest
from unittest.mock import patch, MagicMock
import os
import sys

str_sys_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, str_sys_path)

from src.video_generator.video_builder import generate_video

class TestVideoBuilder(unittest.TestCase):
    @patch('src.video_generator.video_builder.concatenate_videoclips')
    @patch('src.video_generator.video_builder.ImageClip')
    @patch('src.video_generator.video_builder.AudioFileClip')
    @patch('src.video_generator.video_builder._run_tts_sync')
    @patch('src.video_generator.video_builder._render_slide')
    def test_generate_video_codec(self, mock_render_slide, mock_run_tts, mock_audio_clip, mock_img_clip, mock_concat):
        # Setup mocks
        mock_final_clip = MagicMock()
        mock_concat.return_value = mock_final_clip

        mock_img_obj = MagicMock()
        mock_img_clip.return_value = mock_img_obj
        mock_img_obj.set_duration.return_value = mock_img_obj
        mock_img_obj.set_audio.return_value = mock_img_obj

        mock_audio_obj = MagicMock()
        mock_audio_obj.duration = 5.0
        mock_audio_clip.return_value = mock_audio_obj

        mock_render_obj = MagicMock()
        mock_render_slide.return_value = mock_render_obj

        # Test parameters
        str_course_name = "Mock Course"
        list_contents = [{"chapter": "Ch 1", "learning_objectives": ["Obj 1"]}]
        str_output_path = "mock_output.mp4"
        str_cover_path = "mock_cover.jpg"

        # Execute
        result = generate_video(str_course_name, list_contents, str_output_path, str_cover_path)

        # Verify h.264 codec was used
        mock_final_clip.write_videofile.assert_called_once()
        kwargs = mock_final_clip.write_videofile.call_args.kwargs
        self.assertEqual(kwargs.get('codec'), 'libx264', "Video must be encoded with h.264 (libx264)")
        self.assertEqual(result, str_output_path)

if __name__ == '__main__':
    unittest.main()
