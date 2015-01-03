# -- encoding: UTF-8 --
import HTMLParser
import codecs

unescape = HTMLParser.HTMLParser().unescape


class FileProcessor(object):

    def __init__(self, input, output, encoding="UTF-8", **kwargs):
        self.input = codecs.EncodedFile(input, encoding)
        if output:
            self.output = codecs.EncodedFile(output, encoding)
        else:
            self.output = None
        self.fp_init(**kwargs)

    def fp_init(self, **kwargs):
        # Convenience for subclasses
        pass

    def _write(self, line=""):
        if self.output:
            self.output.write("%s\n" % line)

    def _read_lines(self):
        for line in self.input:
            line = line.strip()
            if not line:
                continue
            if line[0] in "#;":
                continue
            line = unescape(line)
            yield line
