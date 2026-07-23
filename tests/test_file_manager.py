from pathlib import Path

from src.utils.file_manager import (
    load_text,
    load_word_list,
    save_text,
    save_word_list,
)


class TestFileManager:
    def test_save_and_load_text(self, tmp_path: Path):
        filepath = tmp_path / "test.txt"
        save_text("hello world", filepath)
        assert load_text(filepath) == "hello world"

    def test_load_text_missing(self):
        assert load_text(Path("/nonexistent/file.txt")) is None

    def test_save_and_load_word_list(self, tmp_path: Path):
        filepath = tmp_path / "words.txt"
        words = ["the", "of", "and", "to"]
        save_word_list(words, filepath)
        loaded = load_word_list(filepath)
        assert loaded == words

    def test_load_word_list_missing(self):
        assert load_word_list(Path("/nonexistent/words.txt")) is None
