"""Unit tests for read_file path parsing with spaces."""
import shlex

import pytest


def parse_read_cmd(read_cmd: str) -> tuple[str, str, int | None, int | None]:
    """
    Parse read command and extract path, command, and optional line numbers.
    This mirrors the logic in tools.py read_file function.

    Returns:
        (command, path, start_line, end_line)
    """
    parts = shlex.split(read_cmd.strip())
    if not parts:
        raise ValueError("Empty command")

    start_line = None
    end_line = None

    if parts[0] in ["cat", "less"]:
        command = parts[0]
        if len(parts) < 2:
            raise ValueError(f"Missing file path for {command}")

        # Handle unquoted paths with spaces
        path_parts = []
        remaining_parts = []

        for i, part in enumerate(parts[1:], 1):
            try:
                int(part)
                remaining_parts = parts[i:]
                break
            except ValueError:
                path_parts.append(part)

        path = " ".join(path_parts)

        if remaining_parts:
            if len(remaining_parts) >= 1:
                start_line = int(remaining_parts[0])
            if len(remaining_parts) >= 2:
                end_line = int(remaining_parts[1])
    else:
        command = "cat"

        path_parts = []
        remaining_parts = []

        for i, part in enumerate(parts):
            try:
                int(part)
                remaining_parts = parts[i:]
                break
            except ValueError:
                path_parts.append(part)

        path = " ".join(path_parts) if path_parts else parts[0]

        if remaining_parts:
            if len(remaining_parts) >= 1:
                start_line = int(remaining_parts[0])
            if len(remaining_parts) >= 2:
                end_line = int(remaining_parts[1])

    return command, path, start_line, end_line


class TestReadFilePathParsing:
    """Test suite for read_file path parsing with various scenarios."""

    def test_simple_cat(self):
        """Test simple cat command without spaces."""
        cmd, path, start, end = parse_read_cmd("cat /workspace/file.txt")
        assert cmd == "cat"
        assert path == "/workspace/file.txt"
        assert start is None
        assert end is None

    def test_simple_less(self):
        """Test simple less command without spaces."""
        cmd, path, start, end = parse_read_cmd("less /workspace/file.txt")
        assert cmd == "less"
        assert path == "/workspace/file.txt"
        assert start is None
        assert end is None

    def test_no_command_defaults_to_cat(self):
        """Test that omitting command defaults to cat."""
        cmd, path, start, end = parse_read_cmd("/workspace/file.txt")
        assert cmd == "cat"
        assert path == "/workspace/file.txt"
        assert start is None
        assert end is None

    def test_cat_with_start_line(self):
        """Test cat command with start line number."""
        cmd, path, start, end = parse_read_cmd("cat /workspace/file.txt 10")
        assert cmd == "cat"
        assert path == "/workspace/file.txt"
        assert start == 10
        assert end is None

    def test_cat_with_start_and_end_lines(self):
        """Test cat command with start and end line numbers."""
        cmd, path, start, end = parse_read_cmd("cat /workspace/file.txt 10 20")
        assert cmd == "cat"
        assert path == "/workspace/file.txt"
        assert start == 10
        assert end == 20

    def test_no_command_with_line_numbers(self):
        """Test path without command but with line numbers."""
        cmd, path, start, end = parse_read_cmd("/workspace/file.txt 10 20")
        assert cmd == "cat"
        assert path == "/workspace/file.txt"
        assert start == 10
        assert end == 20

    def test_unquoted_path_with_spaces(self):
        """Test unquoted path containing spaces."""
        cmd, path, start, end = parse_read_cmd("less /path/Procare Oct25 cash transactions.md")
        assert cmd == "less"
        assert path == "/path/Procare Oct25 cash transactions.md"
        assert start is None
        assert end is None

    def test_unquoted_path_with_one_space(self):
        """Test unquoted path with single space."""
        cmd, path, start, end = parse_read_cmd("cat /workspace/my file.txt")
        assert cmd == "cat"
        assert path == "/workspace/my file.txt"
        assert start is None
        assert end is None

    def test_no_command_unquoted_spaces(self):
        """Test path without command containing spaces."""
        cmd, path, start, end = parse_read_cmd("/workspace/my file with spaces.txt")
        assert cmd == "cat"
        assert path == "/workspace/my file with spaces.txt"
        assert start is None
        assert end is None

    def test_spaces_with_line_numbers(self):
        """Test unquoted path with spaces AND line numbers."""
        cmd, path, start, end = parse_read_cmd("cat /workspace/my file.txt 1 100")
        assert cmd == "cat"
        assert path == "/workspace/my file.txt"
        assert start == 1
        assert end == 100

    def test_spaces_with_start_line_only(self):
        """Test unquoted path with spaces and start line."""
        cmd, path, start, end = parse_read_cmd("less /path/Procare Oct25 transactions.md 50")
        assert cmd == "less"
        assert path == "/path/Procare Oct25 transactions.md"
        assert start == 50
        assert end is None

    def test_no_command_spaces_and_lines(self):
        """Test no command with spaces and line numbers."""
        cmd, path, start, end = parse_read_cmd("/workspace/my file.txt 5 15")
        assert cmd == "cat"
        assert path == "/workspace/my file.txt"
        assert start == 5
        assert end == 15

    def test_quoted_path_with_spaces(self):
        """Test quoted path with spaces (backwards compatibility)."""
        cmd, path, start, end = parse_read_cmd('cat "/workspace/my file.txt"')
        assert cmd == "cat"
        assert path == "/workspace/my file.txt"
        assert start is None
        assert end is None

    def test_quoted_complex_path(self):
        """Test quoted path with complex filename."""
        cmd, path, start, end = parse_read_cmd('less "/path/Procare Oct25 cash transactions.md"')
        assert cmd == "less"
        assert path == "/path/Procare Oct25 cash transactions.md"
        assert start is None
        assert end is None

    def test_quoted_path_with_line_numbers(self):
        """Test quoted path with line numbers."""
        cmd, path, start, end = parse_read_cmd('"/workspace/my file.txt" 10 20')
        assert cmd == "cat"
        assert path == "/workspace/my file.txt"
        assert start == 10
        assert end == 20

    def test_virtual_parsed_file(self):
        """Test virtual _parsed.{ext}.md file path."""
        cmd, path, start, end = parse_read_cmd("cat /path/file_parsed.pdf.md")
        assert cmd == "cat"
        assert path == "/path/file_parsed.pdf.md"
        assert start is None
        assert end is None

    def test_long_tenant_path_with_spaces(self):
        """Test long tenant/user path with spaces in filename."""
        input_cmd = "less /tenant:smooth-flame-13/user:xxx/workspace/ws_personal_b37483e0b292/Procare Oct25 cash transactions 9.28-11.1.25_parsed.xlsx.md"
        cmd, path, start, end = parse_read_cmd(input_cmd)
        assert cmd == "less"
        assert path == "/tenant:smooth-flame-13/user:xxx/workspace/ws_personal_b37483e0b292/Procare Oct25 cash transactions 9.28-11.1.25_parsed.xlsx.md"
        assert start is None
        assert end is None

    def test_empty_command_raises_error(self):
        """Test that empty command raises ValueError."""
        with pytest.raises(ValueError, match="Empty command"):
            parse_read_cmd("")

    def test_cat_without_path_raises_error(self):
        """Test that cat without path raises ValueError."""
        with pytest.raises(ValueError, match="Missing file path"):
            parse_read_cmd("cat")

    def test_less_without_path_raises_error(self):
        """Test that less without path raises ValueError."""
        with pytest.raises(ValueError, match="Missing file path"):
            parse_read_cmd("less")
