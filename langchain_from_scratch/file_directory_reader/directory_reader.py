import logging
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Generator, List, Set

logger = logging.getLogger(__name__)

@dataclass
class Document:
    content: str
    metadata: dict


class DirectoryReader:
    DEFAULT_IGNORE: Set[str] = {'.git', '.idea', '.venv', 'venv', '__pycache__', 'uv.lock', 'node_modules', 'dist', 'build', '__init__.py'}

    SUPPORTED_EXTENSIONS: Set[str] = {'.py', '.md', '.txt', '.json', '.yaml', '.yml', '.js', '.ts', '.html', '.css', '.sql'}

    def __init__(self, root_dir: str, ignore_list: Set[str] = None):
        self.root_dir = Path(root_dir)
        self.ignore_list = self.DEFAULT_IGNORE.union(ignore_list or set())

    def read_files(self) -> Generator[Document, None, None]:
        """
        Reads files from the specified root directory, ignoring specified directories and files.

        :return: yields Document objects containing file content and metadata.
        """
        for root, directoriess, files in os.walk(self.root_dir):
            # Prune ignored directories in-place to prevent os.walk from descending into them
            directoriess[:] = [directory for directory in directoriess if directory not in self.ignore_list and not directory.endswith('.egg-info')]

            for filename in files:
                file_path = Path(root) / filename

                if filename in self.ignore_list or file_path.suffix not in self.SUPPORTED_EXTENSIONS:
                    continue
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().strip()

                    if not content:
                        continue

                    # Relative path makes metadata cleaner and portable
                    relative_path = file_path.relative_to(self.root_dir)

                    yield Document(
                        content=content,
                        metadata={
                            "file_path": str(relative_path),
                            "file_name": filename,
                            "extension": file_path.suffix,
                            "char_count": len(content)
                        }
                    )
                except Exception as e:
                    logger.exception(f"Skipping {file_path} due to error: {e}")

    def chunk_files(self, chunk_size: int = 1000, overlapping_character: int = 100) -> Generator[Document, None, None]:
        """
        Chunks documents using a fixed sliding window with consistent overlap.

        :param chunk_size: The size of each chunk in characters.
        :param overlapping_character: The number of characters that overlap between consecutive chunks.

        :return: yields Document objects containing chunked content and updated metadata.
        """
        if overlapping_character >= chunk_size:
            raise ValueError("overlapping_character must be smaller than chunk_size.")

        stride = chunk_size - overlapping_character

        for document in self.read_files():
            content = document.content
            metadata = document.metadata
            total_chars = len(content)

            chunk_idx = 0
            for start_idx in range(0, total_chars, stride):
                end_idx = min(start_idx + chunk_size, total_chars)
                chunk_content = content[start_idx:end_idx]

                yield Document(
                    content=chunk_content,
                    metadata={
                        **metadata,
                        "chunk_index": chunk_idx,
                        "char_start": start_idx,
                        "char_end": end_idx,
                        "chunk_char_count": len(chunk_content)
                    }
                )
                chunk_idx += 1

                # Stop if this chunk reaches the end of the file
                if end_idx >= total_chars:
                    break

    def embedding_files(self, chunk_size: int = 1000, overlapping_character: int = 100) -> List[Document]:
        """
        Embeds documents using a fixed sliding window with consistent overlap.

        :param chunk_size: The size of each chunk in characters.
        :param overlapping_character: The number of characters that overlap between consecutive chunks.

        :return: A list of Document objects containing chunked content and updated metadata.
        """
        return list(self.chunk_files(chunk_size=chunk_size, overlapping_character=overlapping_character))

DirectoryReader(root_dir=r'C:\Users\hengl\OneDrive\Documents\GitHub\LangChain-Project').read_files()