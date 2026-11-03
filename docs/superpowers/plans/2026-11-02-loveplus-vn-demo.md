# LovePlus 风格 VN 短试玩 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 用 Ren'Py 做出可通关的现代校园短试玩：叶辰误入文艺社认识学姐苏念，经 3 次关键选择到达亲近结局或普通朋友结局。

**Architecture:** 标准 Ren'Py 工程；`characters.rpy` 定义角色与立绘映射；`script.rpy` 用 label + menu + 布尔旗标分支；AI 生成 PNG 放在 `game/images/`；无数值好感，亲近向选项计数 ≥2 进结局 A。

**Tech Stack:** Ren'Py 8.5.3（`/home/box/tools/renpy` / 命令 `renpy`）、Python 3（引擎内置）、Pillow（已装）、Git

## Global Constraints

- 语言与文风：简体中文，口语自然偏甜
- 女主：苏念；温柔学姐；棕发微卷；毛衣+百褶裙；日系
- 主角：叶辰（固定名）
- 立绘 5 表情文件名固定为：`sunian normal.png`、`sunian smile.png`、`sunian surprised.png`、`sunian shy.png`、`sunian worry.png`
- 背景至少：`bg campus.png`、`bg clubroom.png`、`bg hallway.png`（可选 `bg schoolgate.png`）
- 不做：好感数值 UI、多女主、日历养成、语音、自定义主角名
- 项目根：`/workspace/loveplus-game`
- 设计规格：`docs/superpowers/specs/2026-11-02-loveplus-vn-demo-design.md`

## File Structure

| 路径 | 职责 |
|------|------|
| `game/options.rpy` | 游戏名、版本、窗口标题 |
| `game/characters.rpy` | 角色 `s`/`n`、默认侧边位置、立绘 Layered 或 image 声明 |
| `game/script.rpy` | 开场→三选择→双结局全流程 |
| `game/images/*.png` | 立绘与背景 |
| `game/gui/` | Ren'Py 默认 GUI（由 launcher/generate 或复制 tutorial 默认） |
| `tools/check_flags.py` | 纯 Python 校验「≥2 亲近旗标 → ending_a」规则（可在引擎外跑） |
| `tools/test_check_flags.py` | 上述规则的单元测试 |

---

### Task 1: 脚手架 + 游戏元数据

**Files:**
- Create: `game/options.rpy`
- Create: `game/script.rpy`（仅占位 label）
- Create: `game/characters.rpy`（空壳角色）
- Ensure: Ren'Py 所需最小目录（可用 `renpy` 创建项目或手写最小集）

**Interfaces:**
- Consumes: Ren'Py 8.5.3 SDK
- Produces: 可被 `renpy /workspace/loveplus-game lint` 扫描的工程；`config.name` = `"苏念的文艺社"`；`config.version` = `"0.1.0"`

- [ ] **Step 1: 用 Ren'Py 创建空白工程（若手写则等价最小文件）**

在 `/workspace/loveplus-game` 下确保存在 `game/`。若尚无完整 GUI，从 SDK 示例复制默认 gui：

```bash
export PATH="$HOME/bin:$PATH"
# 若项目几乎为空：从 the_question 复制 gui 与必要骨架
cp -a /home/box/tools/renpy/the_question/game/gui /workspace/loveplus-game/game/
cp -a /home/box/tools/renpy/the_question/game/gui.rpy /workspace/loveplus-game/game/
cp -a /home/box/tools/renpy/the_question/game/screens.rpy /workspace/loveplus-game/game/
# 不要覆盖我们稍后写入的 script/options/characters
```

- [ ] **Step 2: 写入 `game/options.rpy`**

```renpy
define config.name = _("苏念的文艺社")
define config.version = "0.1.0"
define gui.show_name = True
define config.window_title = _("苏念的文艺社")
define config.save_directory = "SunianLiteraryClub-0.1.0"
define config.window_icon = None
define config.has_sound = True
define config.has_music = True
define config.has_voice = False
define config.enter_transition = dissolve
define config.exit_transition = dissolve
define config.after_load_transition = None
define config.end_game_transition = None
define config.window = "auto"
define config.window_show_transition = Dissolve(.2)
define config.window_hide_transition = Dissolve(.2)
define config.default_text_cps = 40
define config.default_afm_time = 15
define config.main_menu_music = None
define config.developer = True
define build.name = "SunianLiteraryClub"
```

（若从 the_question 复制了完整 `options.rpy`，则只改 `config.name` / `version` / `window_title` / `save_directory` / `build.name`，保留其余默认。）

- [ ] **Step 3: 写入最小 `game/characters.rpy` 与占位 `game/script.rpy`**

`characters.rpy`:

```renpy
define s = Character("苏念", color="#c48b9f")
define n = Character(None, kind=nvl)  # 若不用 nvl 可删
define narrator = Character(None)
```

`script.rpy`:

```renpy
label start:
    "脚手架已就绪。"
    return
```

- [ ] **Step 4: Lint 工程**

```bash
renpy /workspace/loveplus-game lint 2>&1 | tee /tmp/renpy-lint.txt
```

Expected: 无 error（warning 可接受）；若缺图相关 error，本 Task 仅占位脚本应无立绘引用。

- [ ] **Step 5: Commit**

```bash
cd /workspace/loveplus-game
git add game/options.rpy game/characters.rpy game/script.rpy game/gui game/gui.rpy game/screens.rpy
git commit -m "chore: scaffold Ren'Py project for Sunian demo"
```

---

### Task 2: 好感分支规则（引擎外可测）

**Files:**
- Create: `tools/check_flags.py`
- Create: `tools/test_check_flags.py`

**Interfaces:**
- Consumes: 三个布尔旗标 `helped: bool`, `honest: bool`, `closer: bool`（分别对应选择①②③的亲近向）
- Produces: `def ending_for(helped: bool, honest: bool, closer: bool) -> str` 返回 `"a"` 或 `"b"`；规则：亲近旗标个数 ≥ 2 → `"a"`，否则 `"b"`

- [ ] **Step 1: 写失败测试**

```python
# tools/test_check_flags.py
from check_flags import ending_for

def test_all_true_is_a():
    assert ending_for(True, True, True) == "a"

def test_two_true_is_a():
    assert ending_for(True, True, False) == "a"
    assert ending_for(True, False, True) == "a"
    assert ending_for(False, True, True) == "a"

def test_one_or_zero_is_b():
    assert ending_for(True, False, False) == "b"
    assert ending_for(False, False, False) == "b"
```

- [ ] **Step 2: 跑测试确认失败**

```bash
cd /workspace/loveplus-game/tools && python3 -m pytest test_check_flags.py -v
```

Expected: FAIL（`check_flags` 未定义或 import 失败）

若无 pytest：`python3 -c "import test_check_flags"` 会失败；安装 pytest 用：

```bash
python3 -m pip install --user pytest --break-system-packages
```

- [ ] **Step 3: 实现**

```python
# tools/check_flags.py
def ending_for(helped: bool, honest: bool, closer: bool) -> str:
    score = int(helped) + int(honest) + int(closer)
    return "a" if score >= 2 else "b"
```

- [ ] **Step 4: 跑测试确认通过**

```bash
cd /workspace/loveplus-game/tools && python3 -m pytest test_check_flags.py -v
```

Expected: 全部 PASS

- [ ] **Step 5: Commit**

```bash
git add tools/check_flags.py tools/test_check_flags.py
git commit -m "test: add ending flag rule (>=2 close flags -> ending A)"
```

---

### Task 3: AI 生成立绘与背景

**Files:**
- Create: `game/images/sunian normal.png`
- Create: `game/images/sunian smile.png`
- Create: `game/images/sunian surprised.png`
- Create: `game/images/sunian shy.png`
- Create: `game/images/sunian worry.png`
- Create: `game/images/bg campus.png`
- Create: `game/images/bg clubroom.png`
- Create: `game/images/bg hallway.png`
- Optional: `game/images/bg schoolgate.png`

**Interfaces:**
- Consumes: 设计文档外形描述；GenerateImage（或等价图像生成）
- Produces: 上述 PNG；立绘透明或可抠图的纯色底（若无法透明，用 Ren'Py `Image(..., mask=...)` 前先统一处理）；背景 1920×1080

- [ ] **Step 1: 生成苏念五表情（同一外貌提示词前缀）**

统一前缀（每次生成都带上）：

> Anime visual novel character sprite, Japanese high-school senpai girl, warm gentle older-sister vibe, wavy light-brown hair, soft sweater and pleated skirt, waist-up, clean flat lighting, consistent face and outfit, transparent or plain light-gray background, no text, no watermark

表情后缀分别追加：`neutral calm expression` / `gentle warm smile` / `slightly surprised` / `shy blush looking aside` / `worried soft frown`

用 Cursor `GenerateImage`（或当前环境可用的图像工具）各生成一张，保存到 `/workspace/loveplus-game/game/images/`，文件名必须与 Global Constraints 一致（Ren'Py 空格文件名：`sunian normal.png` 等）。

- [ ] **Step 2: 生成三张背景**

- campus：晴天高中招新广场，摊位横幅虚化，无文字可读
- clubroom：温馨文艺社教室，桌椅海报
- hallway：放学后走廊窗边逆光

保存为 `bg campus.png` 等；必要时用 Pillow 缩放到 1920×1080：

```bash
python3 - <<'PY'
from PIL import Image
from pathlib import Path
root = Path('/workspace/loveplus-game/game/images')
for p in root.glob('bg *.png'):
    im = Image.open(p).convert('RGB')
    im = im.resize((1920, 1080), Image.Resampling.LANCZOS)
    im.save(p)
    print('resized', p)
PY
```

- [ ] **Step 3: 目视抽查**

确认五张立绘发型服装一致；文件存在：

```bash
ls -la /workspace/loveplus-game/game/images/
```

Expected: 至少 8 个 png（5 立绘 + 3 背景）

- [ ] **Step 4: Commit**

```bash
git add game/images/*.png
git commit -m "assets: add Su Nian sprites and campus backgrounds"
```

---

### Task 4: 角色与图像声明

**Files:**
- Modify: `game/characters.rpy`
- Create or modify image defs in `game/characters.rpy`（或 `game/images.rpy`）

**Interfaces:**
- Consumes: Task 3 的 PNG 文件名
- Produces: `s` = Character("苏念")；可用 `show sunian smile` 等（Ren'Py 自动从 `sunian smile.png` 映射）；`show bg campus` 等

- [ ] **Step 1: 完善 `game/characters.rpy`**

```renpy
define s = Character("苏念", color="#c48b9f", who_outlines=[(1, "#00000055")])
define e = Character("叶辰", color="#6a8caf")  # 仅叶辰出声时用；多数用旁白

# 立绘默认位置
transform center_sprite:
    xalign 0.5
    yalign 1.0

# 文件名带空格时，显式声明更稳妥：
image sunian normal = "sunian normal.png"
image sunian smile = "sunian smile.png"
image sunian surprised = "sunian surprised.png"
image sunian shy = "sunian shy.png"
image sunian worry = "sunian worry.png"

image bg campus = "bg campus.png"
image bg clubroom = "bg clubroom.png"
image bg hallway = "bg hallway.png"
```

若 images 在 `game/images/` 下，路径写 `"images/sunian normal.png"` 或依赖 Ren'Py 自动搜索 `game/images/`（自动搜索时声明可为 `"sunian normal.png"`）。以 `renpy ... lint` 为准：缺图会报错。

- [ ] **Step 2: Lint**

```bash
renpy /workspace/loveplus-game lint 2>&1 | tee /tmp/renpy-lint2.txt
```

Expected: 无 missing image（若 script 仍未引用图，至少 characters 声明的路径在 compile 时可能不查；下一步 script 引用后必须通过）

- [ ] **Step 3: Commit**

```bash
git add game/characters.rpy
git commit -m "feat: define Su Nian character and image tags"
```

---

### Task 5: 完整剧情脚本（三选择 + 双结局）

**Files:**
- Modify: `game/script.rpy`（整文件替换为完整流程）

**Interfaces:**
- Consumes: `ending_for` 规则（在 script 内用相同逻辑：`if (helped + honest + closer) >= 2`）；`s` 角色；`sunian *` / `bg *` 图像
- Produces: `label start` → `label ending_a` / `label ending_b` → `return`；默认变量 `default helped = False` 等

- [ ] **Step 1: 写入完整 `game/script.rpy`**

```renpy
default helped = False
default honest = False
default closer = False

label start:
    scene bg campus
    with fade

    "高一的招新日，校园里到处是摊位和传单。"
    "我——叶辰——其实只是想找篮球社，结果拐错了弯。"

    show sunian smile at center_sprite
    with dissolve

    s "你好呀。文艺社这边，要不要看一看？"
    "面前的学姐棕发微卷，笑得很软。名牌上写着：苏念。"

    e "啊……文艺社？我好像走错了。"

    show sunian normal
    s "走错也没关系。要不要先帮我把这叠传单理一下？人手有点不够。"

    menu:
        "留下帮忙":
            $ helped = True
            show sunian smile
            e "……好啊，我来吧。"
            s "谢谢。你动作挺轻的，传单不容易皱。"
        "婉拒离开":
            $ helped = False
            show sunian worry
            e "我还是先去找篮球社好了。"
            s "嗯，那你小心别再走丢。门口那条路直走就到。"
            "我走了两步，还是忍不住回头。她仍站在摊位后，对我轻轻挥了挥手。"
            s "等等——传单你要不要拿一张？不当社员也没关系。"
            e "……那就一张。"

    scene bg clubroom
    with fade
    show sunian normal at center_sprite

    "几天后，我还是进了文艺社教室。说不清是传单的问题，还是她的问题。"
    s "叶辰同学，海报边缘可以再对齐一点吗？你看，这样会更舒服。"

    show sunian smile
    s "你今天看起来有点累。昨晚熬夜了？"

    menu:
        "坦诚说压力有点大":
            $ honest = True
            show sunian worry
            e "有一点。作业和社团凑在一起，有点喘不上气。"
            s "那就今天只做半小时。剩下的我来。累了要说，好吗？"
            show sunian shy
            "她把水杯推到我手边，指尖很轻。"
        "打趣掩饰":
            $ honest = False
            show sunian surprised
            e "没有啦，是被学姐的认真闪到了。"
            show sunian shy
            s "……你这张嘴。那海报还是对齐一下吧。"
        "逞强说没事":
            $ honest = False
            show sunian worry
            e "没事，我扛得住。"
            s "扛得住也不用一直扛。至少把肩膀放松一点点。"

    scene bg hallway
    with fade
    show sunian smile at center_sprite

    "活动当天结束后，走廊里只剩打扫的声音和窗外的晚风。"
    s "今天多亏你了。有你在，现场顺了很多。"

    menu:
        "说想继续靠近她":
            $ closer = True
            show sunian shy
            e "苏念学姐……以后还能这样，多待一会儿吗？"
            s "……可以。明天放学后，还在老地方。"
        "维持普通距离":
            $ closer = False
            show sunian normal
            e "社团的事，我还会继续帮忙的。"
            s "嗯。那就先做可靠的社员，也好。"
        "含糊带过":
            $ closer = False
            show sunian surprised
            e "啊，差不多该回去了。明天见？"
            show sunian smile
            s "明天见。路上慢一点。"

    if (int(helped) + int(honest) + int(closer)) >= 2:
        jump ending_a
    else:
        jump ending_b

label ending_a:
    scene bg hallway
    show sunian shy at center_sprite
    with dissolve
    s "叶辰。谢谢你没有在招新那天真的走开。"
    e "其实……我后来有点庆幸走错了路。"
    show sunian smile
    s "那条错路，就当是我们的秘密捷径吧。"
    "夕阳把她的发梢染成浅金色。我点头，第一次觉得校园的傍晚这么短。"
    "【结局：文艺社的秘密捷径】"
    return

label ending_b:
    scene bg hallway
    show sunian normal at center_sprite
    with dissolve
    s "今天也辛苦了。文艺社随时欢迎你来坐坐。"
    e "我会的。苏念学姐也……别太辛苦。"
    show sunian smile
    s "嗯。那，朋友见。"
    "我们在楼梯口分开。她的背影温柔，却停在刚好合适的距离。"
    "【结局：刚好合适的距离】"
    return
```

注意：`int(True)==1` 在 Ren'Py Python 中成立。若 lint 抱怨，改为：

```renpy
$ _score = (1 if helped else 0) + (1 if honest else 0) + (1 if closer else 0)
if _score >= 2:
    jump ending_a
else:
    jump ending_b
```

- [ ] **Step 2: Lint + 强制编译**

```bash
renpy /workspace/loveplus-game lint 2>&1 | tee /tmp/renpy-lint3.txt
renpy /workspace/loveplus-game compile 2>&1 | tee /tmp/renpy-compile.txt
```

Expected: lint 无 error；compile 成功

- [ ] **Step 3: 对照 Task 2 规则做手工路径检查（文档化）**

在 `/tmp/path-check.md` 写下并确认脚本一致：

- helped+honest+closer 全 True → ending_a
- 仅 helped → ending_b
- helped+closer → ending_a

- [ ] **Step 4: Commit**

```bash
git add game/script.rpy
git commit -m "feat: add full demo script with three choices and two endings"
```

---

### Task 6: 冒烟试玩与收尾

**Files:**
- Modify: 仅修 bug 时改 `game/script.rpy` / 图像
- Create: `README.md`（如何运行）

**Interfaces:**
- Consumes: 可编译工程
- Produces: README；可选无头试玩日志

- [ ] **Step 1: 写 README**

```markdown
# 苏念的文艺社（试玩 0.1.0）

## 运行

```bash
export PATH="$HOME/bin:$PATH"
renpy /workspace/loveplus-game
```

无显示器时至少执行：

```bash
renpy /workspace/loveplus-game lint
renpy /workspace/loveplus-game compile
```

## 内容

现代校园短试玩：叶辰误入文艺社，认识学姐苏念。三次选择，双结局。
```

- [ ] **Step 2: 最终 lint/compile**

```bash
renpy /workspace/loveplus-game lint && renpy /workspace/loveplus-game compile
```

Expected: 成功退出码 0

- [ ] **Step 3: 若有桌面，启动一次确认开场立绘**

```bash
renpy /workspace/loveplus-game run
```

（无 GUI 可跳过，以 lint/compile 为准。）

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: add run instructions for demo 0.1.0"
```

---

## Spec coverage check

| 规格项 | Task |
|--------|------|
| Ren'Py 标准 VN | 1, 5 |
| 苏念/叶辰/文艺社钩子 | 5 |
| 3 次关键选择 | 5 |
| 双结局、无数值、≥2 亲近 | 2, 5 |
| 5 表情 + 背景 AI | 3, 4 |
| 口语偏甜简中 | 5 文案 |
| 短试玩可通关 | 5, 6 |

## Placeholder scan

无 TBD/TODO；文件名与旗标名全文一致：`helped` / `honest` / `closer` / `ending_a` / `ending_b`。
