from django.utils.html import strip_tags
from haystack.utils import Highlighter


class SafeHighlighter(Highlighter):
    def highlight(self, text_block):
        """
        Highlighter uses `strip_tags`, which if there is no whitespace between
        paragraphs, will omit whitespace between sentences. Although we would
        like to keep paragraphs, the highlighter may leave paragraphs unclosed.
        """
        self.text_block = strip_tags(text_block.replace('</p><p>', '\n'))
        highlight_locations = self.find_highlightable_words()
        start_offset, end_offset = self.find_window(highlight_locations)
        return self.render_html(highlight_locations, start_offset, end_offset)
