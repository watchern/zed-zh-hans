# 🌏 zed-loc (Zed のローカライズ)

[简体中文](README.md)|[English](README.en.md)|**日本語**|[한국어](README.ko.md)

## 概要

`zed-loc` は Zed Editor のローカライズ（現地化）を行うためのツールです。ソースコードから文字列を抽出し、翻訳・ローカライズ用の JSON ファイルを生成します。また、実行ファイルの直接置換とビルドにも対応しています。

## 機能

- 自動でソースコードから文字列を抽出
- 翻訳しやすいように JSON ファイルを生成
- GitHub Actions による自動ビルドとデプロイ
- 現在、自動で毎晩ビルドを実行しています

## 実行

### 設定

Python 3 と Rust がインストール済みであることを確認してください。

以下のコマンドでプロジェクトをクローンするか、右上の「Code」ボタンから zip ファイルをダウンロードします。

```bash
git clone https://github.com/tc999/zed-loc.git
cd zed-loc
```

### 文字列の抽出と置換

> [!note]
>
> 注意：現在 Windows のみ対応です。Linux や MacOS ではエラーが発生します。

まず、Zed のソースコードをローカルにクローンしてください。

```bash
git clone https://github.com/zed-industries/zed.git
```

次に、以下のコマンドを実行し、文字列を抽出します（デフォルトでは `strings.json` に保存）。

```bash
python3 step1-extract.py
```

そして、`del.yaml` ファイル内のルールに従って冗長な文字列を削除します。

```bash
python3 step2-delete.py
```

> [!caution]
>
> 警告：抽出スクリプトは引用符内のテキストをすべて抽出します。翻訳する際には、Zed のソースコードを参照しながら翻訳不要な部分に注意してください。翻訳不要な箇所は削除してください。

翻訳方法：GPT で翻訳し、必要に応じて訳文を修正します。

最後に、`strings.json` を目標言語コードに合わせたファイル名に保存し、置換スクリプトを実行します。

```bash
python3 step4-replace.py ja/ja-JP.json
```

## ビルド

コンパイル時にエラーが発生した場合は、Zed のソースコードを削除し、再度クローンしてください。

```bash
cd zed
cargo run
```

正常にコンパイル・実行できるかどうかを確認してください。

# 謝辞

- [Zed](https://github.com/zed-industries/zed) — Zed エディタの貢献者
- [deevus/zed-windows-builds](https://github.com/deevus/zed-windows-builds) — Zed Windows ビルドスクリプトの参考
- [Nriver/zed-translation](https://github.com/Nriver/zed-translation) — アイデアの提供
- [GitHub Copilot](https://github.com/copilot) — スクリプト作成のサポート

## 貢献者全員への感謝

これらの素晴らしい貢献者に感謝します。

<a href="https://github.com/TC999" title="陈生杂物房">
  <img src="https://avatars.githubusercontent.com/u/88823709?v=4" width="42;" alt="陈生杂物房"/>
</a>
<a href="https://github.com/shenjackyuanjie" title="shenjack">
  <img src="https://avatars.githubusercontent.com/u/54507071?v=4" width="42;" alt="shenjack"/>
</a>
<a href="https://github.com/oper0" title="oper0">
  <img src="https://avatars.githubusercontent.com/u/204131036?v=4" width="42;" alt="oper0"/>
</a>

# ライセンス

本プロジェクトは MIT License で提供されており、いかなる組織や個人も無償で使用することができます。
