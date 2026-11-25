from __future__ import annotations

import zipfile

from package_skills import package_all


def test_each_zip_has_skill_md_at_the_skill_root(tmp_path):
    archives = package_all(tmp_path)
    assert len(archives) == 6
    for archive_path in archives:
        with zipfile.ZipFile(archive_path) as archive:
            names = archive.namelist()
            skill = archive_path.stem
            assert f"{skill}/SKILL.md" in names
            assert all(name.startswith(f"{skill}/") for name in names)
            assert not any(name.endswith(".pyc") for name in names)
            info = archive.getinfo(f"{skill}/SKILL.md")
            assert info.date_time[:3] == (2026, 1, 1)
        assert archive_path.stat().st_size < 30 * 1024 * 1024
