#!/usr/bin/env python3

import os
import re
import sys
import json
from glob import glob
import urllib.request

STRING_PATTERN = re.compile(r'L\[["\'](.*?)["\'"]\]')

ISSUE_TEMPLATE = '''
# This file is auto-generated!
name: Translation
description: Provide a translation for in-game strings.
title: 'Translation: '
labels:
  - translation
assignees:
  - {}
body:
  - type: dropdown
    id: locale
    attributes:
      label: Which locale are these translations for?
      options:
        - deDE (German)
        - esES (Spanish, Spain)
        - esMX (Spanish, Mexico)
        - frFR (French)
        - itIT (Italian)
        - koKR (Korean)
        - ptBR (Portuguese, Brazil)
        - ruRU (Russian)
        - zhCN (Chinese, Simplified, PRC)
        - zhTW (Chinese, Traditional, Taiwan)
    validations:
      required: true
  - type: markdown
    attributes:
      value: |
        Please translate each sentence below into the fields next to them.  

        ---
{}
'''

INPUT_TEMPLATE = '''
  - type: input
    attributes:
      label: {}
      placeholder: Translation here
    validations:
      required: true
'''

LOCALE_TEMPLATE = '''
-- This file is auto-generated
local L = select(2, ...).L('{}')

{}
'''

TRANSLATION_TEMPLATE = '''
L["{}"] = "{}"
'''

if sys.argv[1] == 'extract':
  url = f'{os.environ.get("GITHUB_API_URL")}/repos/{{}}/issues/{{}}'
  res = urllib.request.urlopen(url.format(os.environ.get('GITHUB_REPOSITORY'), os.environ.get('GITHUB_EVENT_ISSUE')))
  issue = json.loads(res.read())
  body = issue['body'].split('### ')[1:]
  lang = body[0].split('\n\n')[1].split(' ')[0]

  lines = []
  for block in body[1:]:
    orig, translation, *_ = block.split('\n\n')
    lines.append(TRANSLATION_TEMPLATE.format(orig.replace('"', r'\"'), translation.replace('"', r'\"')).strip())

  with open(os.path.join(os.getcwd(), 'locale/', lang + '.lua'), 'w') as f:
    f.write(LOCALE_TEMPLATE.format(lang, '\n'.join(sorted(lines))).strip() + '\n')

  # github action output
  with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
    print(f'lang={lang}', file=fh)
elif sys.argv[1] == 'template':
  strings = []

  for file in sorted(glob('**/*.lua', recursive=True)):
    with open(file) as f:
      for line in f:
        if line.find('bot-ignore') > 0:
          continue

        match = STRING_PATTERN.match(line)
        for match in STRING_PATTERN.finditer(line):
          for group in match.groups():
            if not group in strings:
              strings.append(group)

  inputs = []
  for s in sorted(strings):
    inputs.append(INPUT_TEMPLATE.format(s).rstrip().lstrip('\n'))

  with open(os.path.join(os.getcwd(), '.github/ISSUE_TEMPLATE/translate.yaml'), 'w') as f:
    f.write(ISSUE_TEMPLATE.format(os.environ.get('GITHUB_REPOSITORY_OWNER'), '\n'.join(inputs)).strip() + '\n')
