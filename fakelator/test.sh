#!/usr/bin/env bash
set -xeuo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK_DIR=$(mktemp -d)
trap 'rm -rf "$WORK_DIR"' EXIT

SYSROOT_FLAG=""
if RISCV_SYSROOT=$(riscv64-linux-gnu-gcc -print-sysroot 2>/dev/null); then
    SYSROOT_FLAG="--sysroot=${RISCV_SYSROOT}"
fi

TOOLCHAIN_PATH="$WORK_DIR/toolchain"
mkdir -p "$TOOLCHAIN_PATH/bin"
ln -sf "$(which clang)"   "$TOOLCHAIN_PATH/bin/clang"
ln -sf "$(which ld.lld)"  "$TOOLCHAIN_PATH/bin/ld.lld"

DUMMY_BIN="$WORK_DIR/dummy.bin"
touch "$DUMMY_BIN"
cd "$WORK_DIR"

make_config() {
  local fakelator="$1"
cat > "$WORK_DIR/.simba.json" << EOF
{
  "verilator_path": "${fakelator}",
  "toolchain_base": {
    "path": "${TOOLCHAIN_PATH}",
    "cc": "clang",
    "ld": "ld.lld",
    "cflags": "--target=riscv64-unknown-linux-gnu -march=rv64gc -mcmodel=medany -fstack-protector ${SYSROOT_FLAG}"
  },
  "toolchain_extra": [
    { "cflags": "-O0" },
    { "cflags": "-O3" }
  ]
}
EOF
}

run_mode() {
    local mode="$1"
    shift

    echo "=== ${mode}: happy path ==="
    make_config "$REPO_DIR/fakelator/happy.sh"
    cd $WORK_DIR
    BENCH_JSON=$(simba run "$mode" "$@")
    if [ -z "$BENCH_JSON" ]; then
        echo "FAILED: expected JSON output, got nothing" >&2
        exit 1
    fi

    HTML_OUT=$(echo "$BENCH_JSON" | simba convert html)
    if [ -z "$HTML_OUT" ] && [ "$mode" != "executable" ]; then
        echo "FAILED: expected HTML output, got nothing" >&2
        exit 1
    fi
    echo "${mode} happy: OK"

    echo "=== ${mode}: sad path ==="
    make_config "$REPO_DIR/fakelator/sad.sh"
    cd $WORK_DIR
    SAD_OUTPUT=$(simba run "$mode" "$@" 2>/dev/null || true)
    if [ -n "$SAD_OUTPUT" ]; then
        echo "FAILED: expected no output on sad path, got: $SAD_OUTPUT" >&2
        exit 1
    fi
    echo "${mode} sad: OK"
}

run_mode executable "$DUMMY_BIN"
run_mode sources "$REPO_DIR/test/nopc/main.c"
run_mode miniproject "$REPO_DIR/test/nopc"
run_mode suite "$REPO_DIR/test"

echo "=== All tests passed ==="
