"""Repository conformance tests for the managed project definitions."""

import re
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).parents[1]
REQUIREMENT_PATTERN = re.compile(r"^\d{3}-[a-z][A-Za-z0-9]*\.md$")


def testDocumentationLinksResolve() -> None:
    """Ensure relative Markdown links resolve within repository-owned guides."""
    missingLinks = []

    for markdownPath in REPOSITORY_ROOT.rglob("*.md"):
        if any(part in {".git", ".pytest_cache"} for part in markdownPath.parts):
            continue
        if markdownPath.is_relative_to(REPOSITORY_ROOT / ".github"):
            continue

        content = markdownPath.read_text(encoding="utf-8")
        if content.startswith("<!-- deployed from Glawster/organiseMyProjects"):
            continue
        for target in re.findall(r"\[[^]]*\]\(([^)]+)\)", content):
            if "://" in target or target.startswith(("#", "mailto:")):
                continue
            targetPath = (markdownPath.parent / target.split("#", 1)[0]).resolve()
            if not targetPath.exists():
                missingLinks.append(
                    f"{markdownPath.relative_to(REPOSITORY_ROOT)}: {target}"
                )

    assert missingLinks == []


def testRequirementPathsAreStable() -> None:
    """Ensure feature records use permanent numeric Markdown filenames."""
    featuresPath = REPOSITORY_ROOT / "project" / "requirements" / "features"
    requirementNames = sorted(path.name for path in featuresPath.iterdir())

    assert requirementNames
    assert all(REQUIREMENT_PATTERN.fullmatch(name) for name in requirementNames)
    assert [int(name[:3]) for name in requirementNames] == list(
        range(1, len(requirementNames) + 1)
    )
