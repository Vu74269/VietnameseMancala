"""Tải tài nguyên ảnh cho pygame, có cơ chế fallback nếu thiếu file."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional, Tuple

import pygame


class AssetManager:
	def __init__(self, image_dir: Optional[Path] = None) -> None:
		root = Path(__file__).resolve().parents[3]
		self.image_dir = image_dir or (root / "assets" / "images")
		self._cache: Dict[Tuple[str, Optional[Tuple[int, int]]], Optional[pygame.Surface]] = {}

	def load_image(
		self, name: str, size: Optional[Tuple[int, int]] = None
	) -> Optional[pygame.Surface]:
		key = (name, size)
		if key in self._cache:
			return self._cache[key]

		file_path = self.image_dir / f"{name}.png"
		if not file_path.exists():
			self._cache[key] = None
			return None

		image = pygame.image.load(str(file_path)).convert_alpha()
		if size is not None:
			image = pygame.transform.smoothscale(image, size)
		self._cache[key] = image
		return image
