import re

def clean_songname(query):
    """Clean a Youtube video title so it's shorter and easier to read."""
    to_remove = (
        "1080", "1080p", "4k", "720", "720p", "album", "amv", "audio", "avi",
        "creditless", "dvd", "edition", "eng", "english", "from", "full", "hd",
        "jap", "japanese", "lyrics", "mix", "mp3", "mp4", "music", "new",
        "nightcore", "official", "original", "original sound track",
        "original soundtrack", "ost", "raw", "size", "soundtrack", "special",
        "textless", "theme", "tv", "ver", "version", "video", "with lyrics"
    )

    replacers = (
        # replace common indicators for the artist with a simple dash
        ((r"[\|:\/]", r"(^|\W)by(\W|$)"), " - "),
        # remove all parentheses and their content and remove "opening 5" stuff
        ((r"\(.*\)", r"(?:^|\b)op(?:ening)?(?:\s+\d{1,2})?(?:\b|$)"), " "),
        # replace several artist things with &
        ((r"(?:^|\b)(?:feat|ft)(?:\b|$)", ), " & "),
        # replace w/ with with
        ((r"w\/",), "with")
    )

    special_regex = (
        (r"\b([\w\s]{3,})\b(?=.*\1)", ""),
        (r"\(f(?:ea)?t\.?\s?([\w\s\&\-\']{2,})\)", r" & \1"),
    )
    special_regex_after = (
        # make sure that everything apart from [',] has space ("test -test"
        # converts to "test - test")
        (r"(\s)([^\w\s\',])(\w)", r"\1 \2 \3"),
        (r"(\w)([^\w\s\',])(\s)", r"\1 \2 \3"),
        (r"[^\w\s]\s*[^\w\s]", " ")
    )

    for target, replacement in special_regex:
        query = re.sub(target, replacement, query, flags=re.IGNORECASE)

    for targets, replacement in replacers:
        for target in targets:
            query = re.sub(target, replacement, query, flags=re.IGNORECASE)

    for key in to_remove:
        # mainly using \W over \b because I want to match "[HD]" too
        query = re.sub(r"(^|\W)" + key + r"(\W|$)",
                       " ", query, flags=re.IGNORECASE)

    for target, replacement in special_regex_after:
        query = re.sub(target, replacement, query, flags=re.IGNORECASE)

    # remove everything apart from the few allowed characters
    query = re.sub(r"[^\w\s\-\&\',]", " ", query)
    # remove unnecessary whitespaces
    query = re.sub(r"\s+", " ", query)

    no_capitalisation = ("a", "an", "and", "but", "for", "his",
                         "my", "nor", "of", "or", "s", "t", "the", "to", "your", "re", "my")

    # title everything except if it's already UPPER because then it's probably
    # by design. Also don't title no-title words (I guess) if they're not in
    # first place
    word_elements = []
    parts = re.split(r"(\W+)", query)
    for sub_ind, part in enumerate(parts):
        word_elements.append(part if (part.isupper() and len(part) > 2) or (
            part.lower() in no_capitalisation and sub_ind != 0) else part.title())

    query = "".join(word_elements)

    return query.strip(" -&,")