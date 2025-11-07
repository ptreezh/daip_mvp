import os
import time
import shutil
from pathlib import Path

class LocalVCS:
    def __init__(self, root: Path, limit_mb: int = 500, use_git: bool = False, aggregate_seconds: float = 60.0):
        self.root = Path(root)
        self.vcs_dir = self.root/".daip_vcs"
        self.snap_dir = self.vcs_dir/"snapshots"
        self.vcs_dir.mkdir(exist_ok=True)
        self.snap_dir.mkdir(exist_ok=True, parents=True)
        self.limit_mb = limit_mb
        self.aggregate_seconds = aggregate_seconds
        self._pending: list[Path] = []
        self._last_flush = 0.0

    def on_write(self, path: str) -> None:
        p = Path(path)
        if p.exists():
            self._pending.append(p)
        if time.time() - self._last_flush >= self.aggregate_seconds:
            self.flush()

    def flush(self) -> None:
        if not self._pending:
            return
        ts = int(time.time())
        dst = self.snap_dir/str(ts)
        dst.mkdir(parents=True, exist_ok=True)
        seen = set()
        for p in self._pending:
            rel = p.relative_to(self.root) if self._is_subpath(p, self.root) else p.name
            target = dst/rel
            target.parent.mkdir(parents=True, exist_ok=True)
            if p.is_file() and str(p) not in seen:
                shutil.copy2(p, target)
                seen.add(str(p))
        self._pending.clear()
        self._last_flush = time.time()

    def count_commits(self) -> int:
        return sum(1 for _ in self.snap_dir.iterdir() if _.is_dir())

    def daily_tag(self) -> None:
        tag = self.vcs_dir/"daily_tags"
        tag.mkdir(exist_ok=True)
        today = time.strftime("%Y-%m-%d")
        (tag/today).touch(exist_ok=True)

    def repo_size_mb(self) -> float:
        total = 0
        for dirpath, _, filenames in os.walk(self.vcs_dir):
            for f in filenames:
                try:
                    total += os.path.getsize(os.path.join(dirpath, f))
                except FileNotFoundError:
                    pass
        return total/1024.0/1024.0

    def enforce_quota(self) -> None:
        while self.repo_size_mb() > self.limit_mb:
            snaps = sorted([p for p in self.snap_dir.iterdir() if p.is_dir()], key=lambda p: p.name)
            if not snaps:
                break
            shutil.rmtree(snaps[0], ignore_errors=True)

    def _is_subpath(self, p: Path, root: Path) -> bool:
        try:
            p.resolve().relative_to(root.resolve())
            return True
        except Exception:
            return False
