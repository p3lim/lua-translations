# Lua Translation Utility

A hacky python script that handles some of the menial tasks regarding translations for my Lua projects.

It has two functionalities and a bunch of requirements, and the function keyword is the only argument it takes.

### Function: extract

This function will do the following:

1. It will read a specific issue
  - Which issue is defined by two environment variables:
    - `GITHUB_REPOSITORY`, expected format: `<repo_owner>/<repo_name>`, e.g. `p3lim/lua-translations`
    - `GITHUB_EVENT_ISSUE`, expected format: `<issue_id>`, e.g. `10`
2. It will parse the issue body as expected from the template created by the "extract" function
  - From this it will find the language submitted in the issue, and each string with their translations
3. It will generate translation files in Lua at `locale/<lang>.lua`
  - The format of each string is `L["original english string"] = "translated string"`
  - It will define a header using [World of Warcraft Lua AddOn namespace](https://warcraft.wiki.gg/wiki/Using_the_AddOn_namespace), specific to a [library](https://github.com/p3lim-wow/Dashi/wiki/namespace#namespacellocalestring) I use

This is _really_ specific to a certain usecase (mine), so if you want to use this for yourself it's recommended to fork the project and adjust these templates yourself (or use my library).

Using it in a [GitHub workflow](https://docs.github.com/en/actions) with an action to auto-create pull requests (or auto-commit directly) is recommended, see below for an example.

### Function: template

This function will do the following:

1. It will read all Lua files in the working directory
2. It will look for any localization strings
  - unless they have `bot-ignore` anywhere on the line
3. It will update a [GitHub issue template](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/configuring-issue-templates-for-your-repository) with the strings, to act as a form for people to submit translations

It has some very specific requirements:

1. The strings will be matched using a regex pattern: `L\[["'](.*)["']\]`
  - Example Lua object: `L["This is the string"]`
  - Example output string: `This is the string`
2. It expects a [GitHub issue label](https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/managing-labels) named `translation` to exist
3. It auto-assigns the issue from the issue form to the GitHub repository owner

Using it in a [GitHub workflow](https://docs.github.com/en/actions) with an action to auto-create pull requests (or auto-commit directly) is recommended.

## Example workflow

These are two example workflows using both functions of this project:

```yaml
name: Update translation issue template

on:
  push:
    branches:
      - master
    tags-ignore:
      - '**'

jobs:
  template:
    runs-on: ubuntu-latest
    steps:
      - name: Clone project
        uses: actions/checkout@v4

      - name: Update issue template
        uses: p3lim/lua-translations@v1
        with:
          action: template

      - name: Create pull request
        uses: peter-evans/create-pull-request@v7
        with:
          title: Update translation issue template
          body:
          commit-message: Update translation issue template
          branch: translation-issue-template
          delete-branch: true
```

```yaml
name: Create pull request from translation form

on:
  issues:
    types: [labeled]

env:
  GITHUB_EVENT_ISSUE: ${{ github.event.issue.number }}

jobs:
  extract:
    if: ${{ github.event.label.name == 'translation' }}
    runs-on: ubuntu-latest

    steps:
      - name: Clone project
        uses: actions/checkout@v4

      - name: Extract translations
        uses: p3lim/lua-translations@v1
        with:
          action: extract
        id: extract

      - name: Create pull request
        uses: peter-evans/create-pull-request@v7
        with:
          title: Update ${{ steps.extract.outputs.lang }} translation
          body:
          commit-message: |
          	Update ${{ steps.extract.outputs.lang }} translation

          	Fixes #${{ github.event.issue.number }}
          branch: update-translation-${{ github.event.issue.number }}
          delete-branch: true
```
