# -- encoding: UTF-8 --
import HTMLParser
import codecs

unescape = HTMLParser.HTMLParser().unescape


class FileProcessor(object):
    def __init__(self, input, output, encoding="UTF-8", **kwargs):
        self.encoding = encoding
        self.input = codecs.EncodedFile(input, encoding)
        self.output = output
        self.fp_init(**kwargs)

    def fp_init(self, **kwargs):
        # Convenience for subclasses
        pass

    def _write(self, line=""):
        if isinstance(line, str):
            line = line.decode(self.encoding)

        if self.output:
            line = (u"%s\n" % line).encode(self.encoding)
            self.output.write(line)

    def _read_lines(self):
        for line in self.input:
            line = line.strip()
            if not line:
                continue
            if line[0] in "#;":
                continue
            line = unescape(line)
            yield line
