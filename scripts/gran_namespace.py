"""Namespace licensed desktop sources without rewriting upstream URLs or credits."""
import json
import re


def rename(value):
    return value.replace('OMARCHY', 'GRAN').replace('Omarchy', 'Gran').replace('omarchy', 'gran')


def content(value):
    preserved = []

    def save(match):
        preserved.append(match.group())
        return f'@@UPSTREAM_{len(preserved) - 1}@@'

    value = re.sub(r'https?://[^\s\"\'<>`\\)]+', save, value)
    value = re.sub(r'(?im)^.*(?:copyright|SPDX-FileCopyrightText).*$', save, value)
    value = rename(value)
    for index, original in reversed(list(enumerate(preserved))):
        value = value.replace(f'@@UPSTREAM_{index}@@', original)
    return value


def json_content(value):
    original = json.loads(value)

    def walk(item):
        if isinstance(item, dict):
            return {rename(key): value if key in ('author', 'license', 'copyright') else walk(value)
                    for key, value in item.items()}
        if isinstance(item, list):
            return [walk(value) for value in item]
        return content(item) if isinstance(item, str) else item

    return json.dumps(walk(original), ensure_ascii=False, indent=2) + '\n'
