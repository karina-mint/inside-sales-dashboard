"""Build script to bundle src/ into main.py with AST-based analysis."""
import ast
from pathlib import Path
from typing import List, Tuple
import re


def generate_pep723_from_pyproject(pyproject_path: Path) -> str:
    """pyproject.tomlからPEP 723メタデータを生成

    pyproject.toml[project]セクションから依存関係を抽出し、
    PEP 723形式の文字列を生成する。

    Args:
        pyproject_path: pyproject.tomlへのパス

    Returns:
        PEP 723メタデータ文字列
    """
    try:
        import tomllib
    except ImportError:
        try:
            import tomli as tomllib
        except ImportError:
            print("Warning: tomllib/tomli not available, skipping PEP 723 metadata")
            return ""

    if not pyproject_path.exists():
        return ""

    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)

    project = data.get("project", {})
    requires_python = project.get("requires-python", ">=3.11")
    dependencies = project.get("dependencies", [])

    lines = ["# /// script"]
    lines.append(f'# requires-python = "{requires_python}"')

    if dependencies:
        lines.append("# dependencies = [")
        for dep in dependencies:
            lines.append(f'#     "{dep}",')
        lines.append("# ]")

    lines.append("# ///")

    return "\n".join(lines)


def collect_imports(file_path: Path) -> Tuple[List[str], List[str]]:
    """ファイルからimport文を収集（順序保持）

    Args:
        file_path: Pythonファイルへのパス

    Returns:
        (standard_imports, from_imports): import文とfrom文のリスト
    """
    with open(file_path) as f:
        content = f.read()
        tree = ast.parse(content)

    standard_imports = []
    from_imports = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                import_str = f"import {alias.name}"
                if alias.asname:
                    import_str += f" as {alias.asname}"
                if import_str not in standard_imports:
                    standard_imports.append(import_str)
        elif isinstance(node, ast.ImportFrom):
            # 内部モジュール（src、functions、agent）からのimportを除外
            # "agent"モジュール（1ファイル）と"agents"パッケージ（外部ライブラリ）を区別
            internal_modules = ("src.", "functions.", ".functions", ".agent")
            if node.module and not any(node.module.startswith(m) or node.module in ("agent",) for m in internal_modules):
                names = ", ".join([
                    f"{n.name}" + (f" as {n.asname}" if n.asname else "")
                    for n in node.names
                ])
                from_str = f"from {node.module} import {names}"
                if from_str not in from_imports:
                    from_imports.append(from_str)

    return standard_imports, from_imports


def extract_code_without_imports(file_path: Path) -> str:
    """import文とPEP 723メタデータを除いたコードを抽出

    Args:
        file_path: Pythonファイルへのパス

    Returns:
        import文とPEP 723メタデータを除いたコード
    """
    with open(file_path) as f:
        content = f.read()

    # PEP 723メタデータを削除
    content = re.sub(r'# /// script\n.*?\n# ///', '', content, flags=re.DOTALL)

    # import文を削除（AST使用）
    try:
        tree = ast.parse(content)
        lines = content.split("\n")

        # import文の行番号を収集
        import_lines = set()
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                import_lines.add(node.lineno - 1)  # 0-indexed

        # import文以外の行を抽出
        filtered_lines = [
            line for i, line in enumerate(lines)
            if i not in import_lines
        ]

        return "\n".join(filtered_lines).strip()
    except SyntaxError:
        # Fallback: 正規表現ベース
        lines = [
            line for line in content.split("\n")
            if not line.strip().startswith(("import ", "from "))
        ]
        return "\n".join(lines).strip()


def bundle_files(src_dir: Path, output_file: Path):
    """src/を単一ファイルに統合（AST解析ベース）

    Args:
        src_dir: src/ディレクトリへのパス
        output_file: 出力ファイル（main.py）へのパス
    """
    # 1. 依存順にファイル収集
    function_files = sorted(
        (src_dir / "functions").glob("*.py"),
        key=lambda p: p.name
    )
    function_files = [f for f in function_files if f.name != "__init__.py"]
    agent_file = src_dir / "agent.py"
    main_template = src_dir / "main_template.py"

    output_lines = []

    # 2. PEP 723メタデータを追加（pyproject.tomlから生成）
    pyproject_path = src_dir.parent / "pyproject.toml"
    pep723 = generate_pep723_from_pyproject(pyproject_path)
    if pep723:
        output_lines.append(pep723)
        output_lines.append("")

    # 3. Docstring
    output_lines.append('"""OpenAI Agents SDK-based agent (bundled)."""')
    output_lines.append("")

    # 4. 全ファイルからimport文を収集
    all_standard_imports = []
    all_from_imports = []

    for file in [*function_files, agent_file, main_template]:
        if not file.exists():
            continue
        std_imports, from_imports = collect_imports(file)
        all_standard_imports.extend(std_imports)
        all_from_imports.extend(from_imports)

    # 5. 重複排除（順序保持）
    unique_standard = []
    unique_from = []

    for imp in all_standard_imports:
        if imp not in unique_standard:
            unique_standard.append(imp)

    for imp in all_from_imports:
        if imp not in unique_from:
            unique_from.append(imp)

    # 6. Import文を追加
    if unique_standard:
        output_lines.extend(unique_standard)
        output_lines.append("")
    if unique_from:
        output_lines.extend(unique_from)
        output_lines.append("")

    # 7. Functions追加
    output_lines.append("# ========== Functions ==========")
    for file in function_files:
        if not file.exists():
            continue
        code = extract_code_without_imports(file)
        if code:
            output_lines.append(code)
            output_lines.append("")

    # 8. Agent追加
    output_lines.append("# ========== Agent ==========")
    if agent_file.exists():
        code = extract_code_without_imports(agent_file)
        if code:
            output_lines.append(code)
            output_lines.append("")

    # 9. Main追加
    output_lines.append("# ========== Main ==========")
    if main_template.exists():
        code = extract_code_without_imports(main_template)
        if code:
            output_lines.append(code)

    # 10. 出力
    output_file.write_text("\n".join(output_lines), encoding="utf-8")


if __name__ == "__main__":
    src_dir = Path(__file__).parent / "src"
    output_file = Path(__file__).parent / "main.py"

    if not src_dir.exists():
        print("✗ Error: src/ directory not found")
        exit(1)

    bundle_files(src_dir, output_file)
    print(f"✓ Built: {output_file}")
