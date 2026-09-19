# =====================================================
# CAMPUSMIND AI - AUTOMATIC REAL-TIME GITHUB WATCHER & SYNC
# Automatically detects file changes, commits, and pushes to GitHub
# =====================================================

import os
import time
import subprocess
from datetime import datetime

WATCH_DIR = os.path.dirname(os.path.abspath(__file__))
SYNC_INTERVAL_SECONDS = 15  # Check every 15 seconds for changes


def run_cmd(cmd):
    try:
        res = subprocess.run(
            cmd,
            cwd=WATCH_DIR,
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        return res.returncode, res.stdout.strip(), res.stderr.strip()
    except Exception as e:
        return 1, "", str(e)


def auto_sync_loop():
    print("=" * 60)
    print(" 🚀 CampusMind AI - Real-Time GitHub Auto-Sync Engine Active")
    print(f" 📂 Watching: {WATCH_DIR}")
    print(f" ⏱️  Interval: Checking every {SYNC_INTERVAL_SECONDS} seconds")
    print("=" * 60)

    while True:
        try:
            # Check git status
            code, out, _ = run_cmd("git status --porcelain")

            if out:
                changed_files = [line.strip() for line in out.splitlines() if line.strip()]
                # Filter out untracked files that might be ignored
                if changed_files:
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"\n[{now_str}] 🔄 Changes detected ({len(changed_files)} files). Syncing to GitHub...")

                    # 1. Git add
                    run_cmd("git add .")

                    # 2. Git commit
                    commit_msg = "Update CampusMind AI"
                    code, c_out, _ = run_cmd(f'git commit -m "{commit_msg}"')
                    print(f"   ✓ Committed: {commit_msg}")

                    # 3. Git push
                    print("   ⬆️  Pushing to GitHub (origin main)...")
                    code, p_out, p_err = run_cmd("git push origin main")
                    if code != 0:
                        # Try force push if remote branch had diverged
                        code, p_out, p_err = run_cmd("git push origin main --force")

                    if code == 0:
                        print(f"   ✅ Successfully pushed to GitHub at {now_str}! 🎉")
                    else:
                        print(f"   ⚠️ Push notice: {p_err or p_out}")

            time.sleep(SYNC_INTERVAL_SECONDS)

        except KeyboardInterrupt:
            print("\n🛑 Auto-sync watcher stopped.")
            break
        except Exception as err:
            print(f"[Watcher Error] {err}")
            time.sleep(SYNC_INTERVAL_SECONDS)


if __name__ == "__main__":
    auto_sync_loop()
