import os
import time
from pathlib import Path
import pytest

# Expect daip_live.vcs.local to provide LocalVCS per LOCAL_VCS_MIN_SPEC.md
from daip_live.vcs.local import LocalVCS  # type: ignore

@pytest.mark.parametrize("use_git", [False])
def test_snapshot_triggers_and_aggregation(tmp_path: Path, use_git: bool):
    os.chdir(tmp_path)
    (tmp_path/"wiki").mkdir()
    vcs = LocalVCS(root=tmp_path, limit_mb=5, use_git=use_git, aggregate_seconds=1)

    p1 = tmp_path/"wiki"/"a.md"
    p1.write_text("a", encoding="utf-8")
    vcs.on_write(str(p1))
    time.sleep(0.2)
    p2 = tmp_path/"wiki"/"b.md"
    p2.write_text("b", encoding="utf-8")
    vcs.on_write(str(p2))

    vcs.flush()
    assert vcs.count_commits() >= 1


def test_daily_tag_and_lru_cleanup(tmp_path: Path):
    os.chdir(tmp_path)
    (tmp_path/"wiki").mkdir()
    vcs = LocalVCS(root=tmp_path, limit_mb=1, use_git=False, aggregate_seconds=0)
    for i in range(20):
        p = tmp_path/"wiki"/f"f{i}.md"
        p.write_text("x"*10000, encoding="utf-8")
        vcs.on_write(str(p))
        vcs.flush()
    vcs.daily_tag()
    vcs.enforce_quota()
    assert vcs.repo_size_mb() <= vcs.limit_mb
