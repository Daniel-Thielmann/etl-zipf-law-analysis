from src.data.preprocessing import (
    clean_text,
    extract_n_words,
    preprocess_gutenberg,
    strip_gutenberg_header,
)


class TestCleanText:
    def test_lowercase_and_punctuation(self):
        assert clean_text("Hello, WORLD! 123") == "hello world"

    def test_multiple_spaces(self):
        assert clean_text("word    word") == "word word"

    def test_non_ascii_removed(self):
        assert clean_text("café naïve") == "caf na ve"

    def test_empty_string(self):
        assert clean_text("") == ""

    def test_only_special_chars(self):
        assert clean_text("!!! 123 @@@") == ""


class TestStripGutenbergHeader:
    def test_removes_header_and_footer(self):
        text = (
            "preamble\n"
            "*** START OF THE PROJECT GUTENBERG EBOOK SOME BOOK ***\n"
            "main content here\n"
            "*** END OF THE PROJECT GUTENBERG EBOOK SOME BOOK ***\n"
            "license"
        )
        result = strip_gutenberg_header(text)
        assert "preamble" not in result
        assert "license" not in result
        assert result.strip() == "main content here"

    def test_no_markers_returns_unchanged(self):
        text = "just some text without markers"
        assert strip_gutenberg_header(text) == text

    def test_partial_markers(self):
        text = "*** START OF THE PROJECT GUTENBERG EBOOK ***"
        assert strip_gutenberg_header(text) == text


class TestExtractNWords:
    def test_enough_words(self):
        assert extract_n_words("a b c d e", 3) == ["a", "b", "c"]

    def test_insufficient_words(self):
        assert extract_n_words("a b", 3) is None

    def test_exact_count(self):
        words = "a b c"
        assert extract_n_words(words, 3) == ["a", "b", "c"]

    def test_empty_string(self):
        assert extract_n_words("", 5) is None


class TestPreprocessGutenberg:
    def test_full_pipeline(self):
        raw = (
            "*** START OF THE PROJECT GUTENBERG EBOOK TEST ***\n"
            "Hello, World! This is a test.\n"
            "*** END OF THE PROJECT GUTENBERG EBOOK TEST ***\n"
        )
        result = preprocess_gutenberg(raw, 6)
        assert result is not None
        assert result == ["hello", "world", "this", "is", "a", "test"]

    def test_insufficient_after_clean(self):
        raw = (
            "*** START OF THE PROJECT GUTENBERG EBOOK ***\n"
            "short\n"
            "*** END OF THE PROJECT GUTENBERG EBOOK ***\n"
        )
        result = preprocess_gutenberg(raw, 10)
        assert result is None
