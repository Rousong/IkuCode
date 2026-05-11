#!/usr/bin/env bash
set -eu

script_dir="$(cd "$(dirname "$0")" && pwd)"
project_dir="$(cd "$script_dir/.." && pwd)"
voice_dir="$project_dir/voice"
requested_file="${1:?Usage: play_voice_macos.sh <mp3-file>}"

voice_file="$voice_dir/$requested_file"

if [ ! -f "$voice_file" ]; then
  echo "Voice file not found: $voice_dir/$requested_file" >&2
  exit 1
fi

if ! command -v afplay >/dev/null 2>&1; then
  echo "afplay is required on macOS." >&2
  exit 1
fi

nohup afplay "$voice_file" >/dev/null 2>&1 &
