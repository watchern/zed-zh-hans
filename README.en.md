<!--Translate By GPT-4o-->
# 🌏 zed-loc (Zed Localization)

[简体中文](README.md)|**English**|[日本語](README.ja.md)|[한국어](README.ko.md)

## Project Overview

`zed-loc` is a tool for localizing the [Zed Editor](https://github.com/zed-industries/zed). It extracts strings from the source code and generates JSON files for translation and localization, while also supporting direct replacement and building of executable files.

## Features

- Automatically extracts strings from the source code
- Generates JSON files for easy translation
- GitHub Actions integration for automatic building and publishing
- Currently, manual localization builds are executed nightly

## Running
### Configuration
Ensure you have Python3 and Rust installed.

Run the following commands to clone the project, or click "Code" in the top right corner to download the zip file:

```bash
git clone https://github.com/tc999/zed-loc.git
cd zed-loc
```
### Extracting and Replacing Strings

> [!note]
>
> Note: Extracting and replacing strings can only be run on Windows systems. It will throw errors on Linux and MacOS.

First, you need to sync the Zed source code to your local machine:

```bash
git clone https://github.com/zed-industries/zed.git
```

Extract strings, which are saved by default to the `strings.json` file:
```bash
python3 step1-extract.py
```
Remove redundant strings according to the rules saved in the `del.yaml` file:
```bash
python3 step2-delete.py
```

> [!caution]
>
> Caution: The extraction script rule extracts all content within quotes. When translating, please refer to the Zed source code and be mindful of content that does not need translation.
> If there are strings that do not need translation, please delete them directly.

Then save the `strings.json` file with the target language code as the filename. After completing the translation of the strings, run the following command to replace the strings:
```bash
python3 step4-replace.py <path/to/lang.json>
```

### Building
If there are compilation errors, delete the Zed source code and clone it again.

```bash
cd zed
cargo run
```

Ensure it can compile and run normally.

# Acknowledgements

- [Zed](https://github.com/zed-industries/zed) - All contributors to the Zed Editor
- [deevus/zed-windows-builds](https://github.com/deevus/zed-windows-builds) - Reference for Zed Windows build scripts
- [Nriver/zed-translation](https://github.com/Nriver/zed-translation) - Provided ideas
- [GitHub Copilot](https://github.com/copilot) - Script writing

# License

This project is released under the [MIT License](LICENSE), allowing free use by any organization or individual.
