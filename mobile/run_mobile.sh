#!/data/data/com.termux/files/usr/bin/bash
# run_mobile.sh —— Termux 启动脚本（保持唤醒 + 后台常驻）
# 首次使用：
#   pkg update && pkg install python termux-api
#   export HITHINK_FINANCE_API_KEY=你的key        # 或写入 ~/.config/yaogu/key
#   bash run_mobile.sh
set -e
cd "$(dirname "$0")"

if [ -z "${HITHINK_FINANCE_API_KEY:-}" ] && [ ! -f "$HOME/.config/yaogu/key" ]; then
  echo "缺少 API Key：请 export HITHINK_FINANCE_API_KEY=... 或写入 ~/.config/yaogu/key"
  exit 1
fi

# 保持 CPU 唤醒（需 termux-api）
command -v termux-wake-lock >/dev/null 2>&1 && termux-wake-lock

echo "[启动] 妖股低吸 · 手机版 $(date '+%F %T')"
python -u live_mobile.py --interval 30 "$@"
