
import re

class ANSIParser:
    ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    COLORS = {'30': 'black', '31': 'red', '32': 'green', '33': 'yellow', '34': 'blue', '35': 'magenta', '36': 'cyan', '37': 'white', '90': 'grey'}

    @classmethod
    def strip(cls, text): return cls.ANSI_ESCAPE.sub('', text)

    @classmethod
    def parse(cls, text):
        parts, last_end = [], 0
        for match in cls.ANSI_ESCAPE.finditer(text):
            if match.start() > last_end: parts.append(('text', text[last_end:match.start()]))
            code = match.group()
            if code.endswith('m'):
                nums = re.findall(r'\d+', code)
                for n in nums:
                    if n in cls.COLORS: parts.append(('color', cls.COLORS[n]))
                    elif n == '0': parts.append(('reset', None))
            last_end = match.end()
        if last_end < len(text): parts.append(('text', text[last_end:]))
        return parts
