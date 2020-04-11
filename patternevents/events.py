"""Monitor changes to patterns within files and expose those change events as generators"""
import watch
from regexutils import *
from pathlib import Path
from config import *

def changes(pattern, *abs_paths, yield_sames=False):
    """a generator for detecting changes to regex patterns
    within a set of files

    Args:
        param1 (str): the regex pattern to match
        *abs_paths (pathlib.Path): the absolute paths to the files to be monitored
        yield_sames (bool): if True a match appearing in the same
            place (relative to other matches) will be treated as a
            'none' change. This way there will be one yield for every
            match in a file each time the file is written to

    Yields:
        a tuple of one of the following forms

            - `('added', match_number, match_text, groups)`
            - `('removed', previous_match_number, match_text, groups)`
            - `('moved', (previous_match_number, match_number), match_text, groups)`
            - `('none', match_number, match_text, groups)`

        where:
            - `match_number (int)`: index of match within the list of all matches
            - `previous_match_number (int)`: the index of the match
                in the list of all matches , prior to the change
            -  `match_text (str)`: the text which was changed
            - `groups ([groups], {named_groups})` the groups from
            the regex match
    """

    def group(m):
        return ([g for g in m.groups() if g not in m.groupdict().values()], m.groupdict())

    # cache the matches
    for p in abs_paths:
        matches = match(pattern, p.read_text())
        cache_file(p).write_text('\n'.join([m.group(0) for m in matches]))

    for updated in watch.writes(*abs_paths):
        # collect cached matches
        cached_groups = {m.group(0):group(m) for m in
                match(pattern, cache_file(updated).read_text())}

        cached  = cached_groups.keys()
        # find matches in the updated file
        groups  = {m.group(0):group(m) for m in match(pattern, updated.read_text())}
        matches = groups.keys()

        # associate each match to it's index in the list of matches
        cached_index = {match:i+1 for i, match in enumerate(cached)}
        new_index    = {match:i+1 for i, match in enumerate(matches)}

        added   = set(matches) - set(cached)
        removed = set(cached)  - set(matches)
        still   = set(cached)  & set(matches)

        moved = set([match for match in still
            if cached_index[match] != new_index[match]])

        same    = [('none', new_index[match], match, groups[match]) for match in (still - moved)]
        moved   = [('moved', (cached_index[match], new_index[match]), match, groups[match])
                for match in moved]
        added   = [('added', new_index[match], match, groups[match]) for match in added]
        removed = [('removed', cached_index[match], match, cached_groups[match])
                for match in removed]

        changes = sorted(added + removed + moved)
        if yield_sames: changes += sorted(same)
        yield from changes

        cache_file(updated).write_text("\n".join(matches))
