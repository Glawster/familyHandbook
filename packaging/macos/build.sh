#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd "${script_dir}/../.." && pwd)"
build_root="${project_root}/.build/macos"
venv_dir="${build_root}/venv"
pyinstaller_work="${build_root}/pyinstaller"
stage_root="${build_root}/pkg-root"
dist_dir="${project_root}/dist"

if [[ "$(uname -s)" != "Darwin" ]]; then
    echo "Error: the macOS package must be built on macOS." >&2
    exit 1
fi

python_bin="${PYTHON:-python3}"
if ! command -v "${python_bin}" >/dev/null 2>&1; then
    echo "Error: ${python_bin} is not available." >&2
    exit 1
fi

if ! command -v pkgbuild >/dev/null 2>&1; then
    echo "Error: pkgbuild is not available. Install the macOS command-line tools." >&2
    exit 1
fi

architecture="$(uname -m)"
macos_version="$(sw_vers -productVersion)"
macos_build="$(sw_vers -buildVersion)"
kernel_version="$(uname -r)"
python_path="$(command -v "${python_bin}")"
python_version="$("${python_bin}" --version 2>&1)"

if command -v xcode-select >/dev/null 2>&1 && xcode-select -p >/dev/null 2>&1; then
    developer_dir="$(xcode-select -p)"
else
    developer_dir="not available"
fi

if command -v pkgutil >/dev/null 2>&1; then
    clt_version="$(pkgutil --pkg-info=com.apple.pkg.CLTools_Executables 2>/dev/null | awk '/version:/ {print $2}' || true)"
else
    clt_version=""
fi
[[ -n "${clt_version}" ]] || clt_version="not reported"

cat <<EOF
Clann Eolas macOS build environment
----------------------------------
macOS version:        ${macos_version}
macOS build:          ${macos_build}
Architecture:         ${architecture}
Kernel:               ${kernel_version}
Python executable:    ${python_path}
Python version:       ${python_version}
Developer directory:  ${developer_dir}
Command Line Tools:   ${clt_version}
Project root:         ${project_root}
EOF

version="$(PROJECT_ROOT="${project_root}" "${python_bin}" - <<'PY'
import os
from pathlib import Path
import tomllib

project_root = Path(os.environ["PROJECT_ROOT"])
with (project_root / "pyproject.toml").open("rb") as handle:
    print(tomllib.load(handle)["project"]["version"])
PY
)"

package_name="ClannEolas-${version}-macos-${architecture}.pkg"

rm -rf "${build_root}"
mkdir -p "${build_root}" "${dist_dir}"

"${python_bin}" -m venv "${venv_dir}"
"${venv_dir}/bin/python" -m pip install --upgrade pip
"${venv_dir}/bin/python" -m pip install "${project_root}" "pyinstaller>=6,<7"

"${venv_dir}/bin/python" -m PyInstaller \
    --clean \
    --noconfirm \
    --distpath "${build_root}/dist" \
    --workpath "${pyinstaller_work}" \
    "${script_dir}/ClannEolas.spec"

mkdir -p "${stage_root}/usr/local/bin"
install -m 0755 "${build_root}/dist/eolas" "${stage_root}/usr/local/bin/eolas"

pkgbuild \
    --root "${stage_root}" \
    --identifier "com.clanneolas.cli" \
    --version "${version}" \
    --install-location "/" \
    "${dist_dir}/${package_name}"

checksum="$(shasum -a 256 "${dist_dir}/${package_name}" | awk '{print $1}')"

cat <<EOF
macOS verification package created:
  ${dist_dir}/${package_name}
  SHA-256: ${checksum}

This package is unsigned and intended for verification testing only.
It installs the self-contained 'eolas' command at /usr/local/bin/eolas.
EOF
