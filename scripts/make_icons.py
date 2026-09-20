"""LabOps-Agent 专属应用图标构建模块 (make_icons.py)

从前端界面品牌标识 SVG 渲染生成符合 Windows 标准的高品质多分辨率 .ico 图标
支持多阶分辨率：16x16, 32x32, 48x48, 64x64, 128x128, 256x256
并自动同步分发至开发工程、免安装便携包与 Inno Setup 安装向导工程中。
"""

import sys
import os
import shutil
import subprocess
from pathlib import Path
from PIL import Image

def get_logo_svg_content(svg_file_path: Path) -> str:
    """读取官方标准 SVG 标识内容"""
    if svg_file_path.exists():
        return svg_file_path.read_text(encoding="utf-8")
    raise FileNotFoundError(f"未找到前端 logo.svg 矢量文件: {svg_file_path}")

def render_svg_to_png(svg_str: str, out_png_path: Path):
    """
    使用 Windows 自带的 Edge 浏览器内核 (Headless 模式) 进行像素级保真的矢量渲染，
    生成 512x512 高清深色圆角现代桌面软件图标 (带有环境微光与软阴影)。
    """
    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html, body {{
    width: 512px;
    height: 512px;
    background: transparent;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
  }}
  .app-tile {{
    width: 460px;
    height: 460px;
    border-radius: 104px;
    background: linear-gradient(145deg, #1e1b4b 0%, #0f172a 60%, #090d16 100%);
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6), inset 0 2px 4px rgba(255, 255, 255, 0.25), inset 0 -2px 4px rgba(0, 0, 0, 0.4);
    border: 3px solid rgba(99, 102, 241, 0.35);
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
  }}
  .glow-ring {{
    position: absolute;
    width: 380px;
    height: 380px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(99, 102, 241, 0.22) 0%, rgba(56, 189, 248, 0.08) 50%, transparent 75%);
    pointer-events: none;
  }}
  .logo-svg {{
    width: 340px;
    height: 340px;
    filter: drop-shadow(0 8px 16px rgba(0, 0, 0, 0.45));
    position: relative;
    z-index: 1;
  }}
</style>
</head>
<body>
  <div class="app-tile">
    <div class="glow-ring"></div>
    <div class="logo-svg">
      {svg_str}
    </div>
  </div>
</body>
</html>"""

    temp_html = out_png_path.with_suffix(".render.html")
    temp_html.write_text(html_content, encoding="utf-8")

    edge_candidates = [
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        str(Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "Edge" / "Application" / "msedge.exe"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        str(Path(os.environ.get("LOCALAPPDATA", "")) / "Google" / "Chrome" / "Application" / "chrome.exe"),
    ]
    edge_exe = shutil.which("msedge") or shutil.which("chrome")
    if not edge_exe:
        for c in edge_candidates:
            if c and Path(c).is_file():
                edge_exe = c
                break

    if not edge_exe:
        if out_png_path.exists():
            print(f"[WARN] 未找到 Chromium 浏览器用于渲染，沿用现有母图缓存: {out_png_path}")
            if temp_html.exists():
                temp_html.unlink()
            return
        raise FileNotFoundError("未找到 Edge/Chrome 浏览器执行文件用于高保真渲染，且无可用母图缓存！")

    out_png_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        edge_exe,
        "--headless=new",
        "--disable-gpu",
        "--force-device-scale-factor=1",
        "--default-background-color=00000000",
        f"--screenshot={out_png_path.resolve()}",
        "--window-size=512,512",
        f"file:///{temp_html.resolve().as_posix()}"
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except Exception as e:
        if out_png_path.exists():
            print(f"[WARN] 浏览器渲染异常 ({e})，沿用现有母图缓存: {out_png_path}")
            return
        raise RuntimeError(f"渲染生成 PNG 失败: {e}")
    finally:
        if temp_html.exists():
            temp_html.unlink()

    if not out_png_path.exists():
        raise RuntimeError(f"渲染生成 PNG 失败: {out_png_path}")

def convert_png_to_multi_ico(png_path: Path, ico_path: Path):
    """
    使用 Pillow 将 512x512 PNG 转换为标准的 Windows 高清多分辨率 .ico 图标
    包含尺寸: 16x16, 32x32, 48x48, 64x64, 128x128, 256x256
    """
    img = Image.open(png_path).convert("RGBA")
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    ico_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(ico_path, format="ICO", sizes=icon_sizes)
    print(f"[*] 生成 Windows 多分辨率 ICO 图标: {ico_path} (文件大小: {ico_path.stat().st_size} 字节)")

def build_icons(workspace_dir: Path = None):
    """构建全套应用图标并同步分发至各工程目录"""
    if workspace_dir is None:
        workspace_dir = Path(__file__).resolve().parent.parent.parent

    dev_root = workspace_dir / "01-开发工程_LabOps-Dev"
    portable_root = workspace_dir / "02-免安装便携包_LabOps-Portable"
    setup_root = workspace_dir / "03-安装向导工程_LabOps-Setup"

    frontend_assets = dev_root / "frontend" / "src" / "assets"
    frontend_public = dev_root / "frontend" / "public"
    frontend_public.mkdir(parents=True, exist_ok=True)

    svg_file = frontend_assets / "logo.svg"
    svg_content = get_logo_svg_content(svg_file)

    # 1. 临时与主 PNG 渲染
    master_png = frontend_assets / "app.png"
    print(f"[*] 正在从 SVG 标识渲染 512x512 高清主图: {master_png}")
    render_svg_to_png(svg_content, master_png)

    # 2. 生成多分辨率 Windows ICO 文件
    master_ico = frontend_assets / "app.ico"
    print(f"[*] 正在生成多尺寸 Windows 图标: {master_ico}")
    convert_png_to_multi_ico(master_png, master_ico)

    # 3. 同步分发至前端静态目录 (浏览器 Favicon)
    shutil.copy2(master_ico, frontend_public / "favicon.ico")
    shutil.copy2(master_ico, frontend_public / "app.ico")
    shutil.copy2(svg_file, frontend_public / "logo.svg")
    shutil.copy2(master_png, frontend_public / "logo.png")
    print(f"[*] 已同步图标至前端 public 目录: {frontend_public}")

    # 4. 同步分发至免安装便携包目录
    if portable_root.exists():
        shutil.copy2(master_ico, portable_root / "app.ico")
        shutil.copy2(master_png, portable_root / "app.png")
        print(f"[*] 已同步图标至便携包工程: {portable_root / 'app.ico'}")

    # 5. 同步分发至安装向导工程目录
    if setup_root.exists():
        shutil.copy2(master_ico, setup_root / "app.ico")
        shutil.copy2(master_png, setup_root / "app.png")
        print(f"[*] 已同步图标至安装向导工程: {setup_root / 'app.ico'}")

    print("[SUCCESS] 全套 LabOps-Agent 应用图标构建并分发成功！")
    return master_ico

if __name__ == "__main__":
    build_icons()
