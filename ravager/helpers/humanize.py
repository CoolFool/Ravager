import collections


def humanize(size):
    humanized = collections.namedtuple("humanized", ["original", "size", "unit"])
    original = size
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB']
    suffix_index = 0
    while size >= 1024 and suffix_index < 4:
        suffix_index += 1
        size /= 1024
    size = round(size, 2)
    humanized = humanized(original=original, size=size, unit=suffixes[suffix_index])
    return humanized
