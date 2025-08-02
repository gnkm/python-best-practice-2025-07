import re
from pathlib import Path

MARKDOWN_FILE = "Python-Best-Practice-2025-07.md"
OUTPUT_DIRECTORY = "output"


def slugify(text: str) -> str:
    """
    英語のテキストをスラグに変換します。
    例: "Modern Development Toolchain" -> "modern-development-toolchain"
    """
    # 英数字とハイフン以外を削除し、スペースをハイフンに置換
    slug = re.sub(r"[^a-zA-Z0-9\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "-", slug)


def split_markdown_file(input_path: str | Path, output_dir: str | Path):
    """
    マークダウンファイルをH2見出し(##)単位で分割します。
    H2見出しは英語で書かれていることを前提とします。

    :param input_path: 分割対象のマークダウンファイルパス
    :param output_dir: 分割後のファイルの出力先ディレクトリ
    """
    input_file = Path(input_path)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    print(f"'{input_file}' を読み込んでいます...")
    with input_file.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    # 1. フロントマターを抽出
    front_matter = []
    content_start_index = 0
    if lines and lines[0].strip() == "---":
        try:
            # '---' で終わる行を探す
            end_fm_index = lines.index("---\n", 1)
            front_matter = lines[: end_fm_index + 1]
            content_start_index = end_fm_index + 1
            print("フロントマターを抽出しました。")
        except ValueError:
            print("警告: フロントマターが正しく閉じられていません。")

    # 2. ## 単位でファイルを分割
    current_file_content = []
    current_filename = "00-introduction.md"
    file_count = 0

    # 最初のH2見出しが登場するまでの内容をイントロダクションとして保存
    initial_content = []

    for line in lines[content_start_index:]:
        if line.startswith("## "):
            # 前のセクションの内容があればファイルに書き出す
            if current_file_content:
                filepath = output_path / current_filename
                print(f"ファイルを作成中: {filepath}")
                with filepath.open("w", encoding="utf-8") as f:
                    if front_matter:
                        f.writelines(front_matter)
                    f.writelines(current_file_content)
            # 最初のH2の前の内容をイントロファイルに保存
            elif initial_content:
                filepath = output_path / current_filename
                print(f"ファイルを作成中: {filepath}")
                with filepath.open("w", encoding="utf-8") as f:
                    if front_matter:
                        f.writelines(front_matter)
                    f.writelines(initial_content)

            # 新しいファイル名と内容を準備
            title_full = line.strip().replace("## ", "")

            # "1. English Title" のような形式から番号とタイトルを抽出
            match = re.match(r"(\d+)\.\s*(.*)", title_full)
            if match:
                num = int(match.group(1))
                title = match.group(2)
                current_filename = f"{num:02d}-{slugify(title)}.md"
            else:
                # 番号がない見出しの場合
                file_count += 1
                current_filename = f"{file_count:02d}-{slugify(title_full)}.md"

            current_file_content = [line]
        else:
            if current_file_content:
                current_file_content.append(line)
            else:
                initial_content.append(line)

    # 最後のセクションをファイルに書き出す
    if current_file_content:
        filepath = output_path / current_filename
        print(f"ファイルを作成中: {filepath}")
        with filepath.open("w", encoding="utf-8") as f:
            if front_matter:
                f.writelines(front_matter)
            f.writelines(current_file_content)

    print("\n分割処理が完了しました。")


if __name__ == "__main__":
    if not Path(MARKDOWN_FILE).exists():
        print(f"エラー: ファイルが見つかりません: {MARKDOWN_FILE}")
    else:
        split_markdown_file(MARKDOWN_FILE, OUTPUT_DIRECTORY)
