# GPT_Playground

One to explore what GPT can do with CodeX.

## Super Mario (Canvas Tribute)
A lightweight、纯前端的 FC 风格马里奥游戏，使用 HTML + CSS + 原生 Canvas 渲染，无需额外资源。

### 运行方式
1. 在仓库根目录启动本地服务器（任选其一）：
   - `python -m http.server 8000`
   - 或者使用任何静态服务器工具（如 `npx serve`）。
2. 打开浏览器访问 `http://localhost:8000/`。
3. 按 <kbd>←</kbd>/<kbd>→</kbd> 移动，<kbd>Z</kbd> 或 <kbd>空格</kbd> 跳跃，踩栗宝宝、顶问号方块、收集金币并冲向旗杆。

### 桌面版（Windows 可执行文件）
使用 Electron 打包，可在 Windows 上双击运行：

1. 安装依赖：`npm install`
2. 本地调试桌面版：`npm start`
3. 打包 Windows 便携版 exe：`npm run build:win`
   - 默认输出在 `dist/` 目录（例如 `dist/MarioCanvas.exe`）。
   - 在 macOS/Linux 上交叉编译 Windows 可执行文件需要预装 Wine（`brew install --cask wine-stable` 或对应发行版包管理器），如无需跨平台打包可在 Windows 直接运行同样命令。

### Release 下载（GitHub 一键获取 exe）
- 直接下载：在 GitHub 的 **Releases** 页面获取最新的 `MarioCanvas` 便携版 `.exe`（自动随标签发布）。
- 维护者发布步骤：
  1. 更新代码并推送。
  2. 创建版本标签并推送，例如：`git tag v1.0.1 && git push origin v1.0.1`。
  3. GitHub Actions 会在 Windows runner 上执行 `npm ci` 与 `npm run build:win`，构建出的 `dist/*.exe` 自动作为发布附件上传。
  4. 在发布页面即可下载可执行文件，无需本地打包。

### 特色
- 还原地面砖块、问号、金币、管道、旗杆和栗宝宝巡逻。
- 顶问号方块会喷出金币并计分，踩栗宝宝可反弹加分。
- HUD 展示分数、金币、世界和生命，支持掉坑、撞怪的生命惩罚与重置。
