# SNNU Beamer Template

陕西师范大学 (Shaanxi Normal University) 风格的 LaTeX Beamer 演示文稿模板,
由 SUSTech Beamer 模板改写,配色与内容均已更换为陕师大主题。

## 使用

编辑 `slides.tex` 修改内容,所有图片放在 `figures` 目录。
校徽为 `figures/snnu-logo.png`:标题页自动缩放显示(高度为页面的 30%),
每页页眉固定 0.5cm 高,调整见 `slides.tex` 中的 `\titlegraphic` 与 `\logo` 两行。

编译(需要 XeLaTeX 与 ctex 宏包,用于中文支持):

```
make
```

生成 `out/slides.pdf` 后用任意 PDF 阅读器打开查看。

其他命令:

```
make view-xpdf      # Linux: xpdf
make view-okular    # Linux: okular
make view-acroread  # Linux: acroread
make clean
```

实时监听自动重编译可运行(Python 3):

```
python build-daemon.py     # 前台运行,每 1 秒检查并重建
python build-daemon.py -f  # Linux/macOS: 后台守护进程
python build-daemon.py -k  # 终止守护进程
```
