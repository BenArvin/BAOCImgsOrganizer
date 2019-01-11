# BAOCImgsOrganizer

iOS工程Image Assets规范化工具

功能:
- 检查空Image set
- 检查重复的Image set
- 检查 1x 2x 3x 图片文件缺失，缺失文件默认使用已有图片中最清晰图片替代
- 规范化Image set内图片文件名，保持和文件夹同名
- 一键提取所有图片文件

使用:
1. python -o/-organize sourthPath targetPath

    检查、规范化所有Image set，并输出至目标文件夹

2. python -e/-extract sourthPath targetPath

    一键提取所有图片文件至目标文件夹