from haystack.utils import Highlighter

class SafeHighlighter(Highlighter):
    def highlight(self, text_block):
        """
        Highlighter uses `strip_tags`, which if there is no whitespace between
        paragraphs, will omit whitespace between sentences. All text is already
        safe, so we skip any tag stripping. Keeping paragraphs also makes sense.
        """
        self.text_block = text_block
        highlight_locations = self.find_highlightable_words()
        start_offset, end_offset = self.find_window(highlight_locations)
        return self.render_html(highlight_locations, start_offset, end_offset)
