import hid
import time
import sys
import json
import os
import subprocess

VID = 0x3434
RAW_USAGE_PAGE = 0xFF60
RAW_USAGE_ID = 0x0061
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, "state.json")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

def load_config():
    defaults = {
        "working_mode": 9,
        "input_mode": 14,
        "done_mode": 1,
        "idle_mode": 12,
        "done_duration": 15
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                defaults.update(data)
        except Exception:
            pass
    return defaults

def get_keyboard_device():
    for dev in hid.enumerate(VID):
        if dev.get('usage_page') == RAW_USAGE_PAGE and dev.get('usage') == RAW_USAGE_ID:
            if dev.get('product_id') == 0x0A04:
                try:
                    h = hid.device()
                    h.open_path(dev['path'])
                    return h
                except Exception:
                    continue
    return None

def send_cmd(h, cmd):
    packet = bytes([0x00] + list(cmd) + [0] * (32 - len(cmd)))
    h.write(packet)
    resp = h.read(32, timeout_ms=150)
    return list(resp)

def get_current_mode(h):
    try:
        resp = send_cmd(h, [0x08, 5, 2])
        if resp and len(resp) >= 4:
            return resp[3]
    except Exception:
        pass
    return None

def set_mode(mode, brightness=255, force=False):
    h = get_keyboard_device()
    if not h:
        return False
    try:
        if not force:
            cur = get_current_mode(h)
            if cur == mode:
                send_cmd(h, [0x07, 5, 1, brightness])
                h.close()
                return True

        send_cmd(h, [0x07, 5, 2, mode])
        send_cmd(h, [0x07, 5, 1, brightness])
        h.close()
        return True
    except Exception:
        try:
            h.close()
        except Exception:
            pass
        return False

def action_cue():
    cfg = load_config()
    working_m = cfg["working_mode"]
    h = get_keyboard_device()
    if not h:
        return False
    try:
        cur = get_current_mode(h)
        if cur != working_m:
            send_cmd(h, [0x07, 5, 2, working_m])
        
        # Quick dip in brightness without resetting animation
        send_cmd(h, [0x07, 5, 1, 0])
        time.sleep(0.08)
        send_cmd(h, [0x07, 5, 1, 255])
        h.close()
        return True
    except Exception:
        try:
            h.close()
        except Exception:
            pass
        return False

def record_state(state_name):
    try:
        data = {"state": state_name, "time": time.time()}
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception:
        pass

def get_last_state_time():
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("time", 0)
    except Exception:
        pass
    return 0

def start_solid_timer(seconds=None):
    cfg = load_config()
    if seconds is None:
        seconds = cfg.get("done_duration", 15)
    done_m = cfg.get("done_mode", 1)
    
    set_mode(done_m, 255, force=True)
    record_state("done")
    
    creation_flags = 0
    if sys.platform == "win32":
        creation_flags = 0x00000008 | 0x08000000
    
    subprocess.Popen(
        [sys.executable, os.path.abspath(__file__), "--hold-solid", str(seconds)],
        creationflags=creation_flags,
        close_fds=True
    )

def hold_solid_worker(seconds):
    cfg = load_config()
    idle_m = cfg.get("idle_mode", 12)
    start_time = get_last_state_time()
    time.sleep(seconds)
    current_time = get_last_state_time()
    if abs(current_time - start_time) < 0.5:
        set_mode(idle_m, 255, force=True)
        record_state("idle")

def handle_hook():
    cfg = load_config()
    payload = {}
    try:
        line = sys.stdin.read().strip()
        if line:
            payload = json.loads(line)
    except Exception:
        pass

    event = payload.get("hookEventName", "")

    if event == "PreInvocation":
        record_state("working")
        set_mode(cfg["working_mode"], 255)
        print(json.dumps({}))
        return

    elif event == "PreToolUse":
        tool_call = payload.get("toolCall", {})
        tool_name = tool_call.get("name", "")
        if tool_name == "ask_question":
            record_state("input")
            set_mode(cfg["input_mode"], 255)
        else:
            record_state("working")
            action_cue()
        print(json.dumps({"decision": "allow"}))
        return

    elif event == "Stop":
        transcript_path = payload.get("transcriptPath", "")
        needs_input = False
        if transcript_path and os.path.exists(transcript_path):
            try:
                with open(transcript_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    for line in reversed(lines[-10:]):
                        try:
                            item = json.loads(line)
                            calls = item.get("tool_calls", [])
                            for c in calls:
                                if c.get("name") == "ask_question":
                                    needs_input = True
                                    break
                            content = item.get("content", "")
                            if content and isinstance(content, str):
                                stripped = content.strip()
                                if stripped.endswith("?") or stripped.endswith("¿"):
                                    needs_input = True
                            if needs_input:
                                break
                        except Exception:
                            continue
            except Exception:
                pass

        if needs_input:
            record_state("input")
            set_mode(cfg["input_mode"], 255)
        else:
            start_solid_timer(cfg["done_duration"])

        print(json.dumps({}))
        return

    print(json.dumps({}))

def main():
    cfg = load_config()
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == "--hook":
            handle_hook()
            return
        elif arg == "--hold-solid":
            sec = int(sys.argv[2]) if len(sys.argv) > 2 else cfg["done_duration"]
            hold_solid_worker(sec)
            return
        elif arg in ("action", "cue"):
            record_state("working")
            action_cue()
            return
        elif arg in ("working", "work"):
            record_state("working")
            set_mode(cfg["working_mode"], 255)
            return
        elif arg in ("input", "ask", "confirm"):
            record_state("input")
            set_mode(cfg["input_mode"], 255)
            return
        elif arg in ("solid", "done"):
            start_solid_timer(cfg["done_duration"])
            return
        elif arg in ("idle", "default", "restore"):
            record_state("idle")
            set_mode(cfg["idle_mode"], 255)
            return
        elif arg.isdigit():
            m = int(arg)
            set_mode(m, 255, force=True)
            print(f"Modo fijado: {m}")
            return

    start_solid_timer(cfg["done_duration"])

if __name__ == "__main__":
    main()
