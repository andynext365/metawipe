# 文档版本管理仓库

用 Git 分支区分管理两类文档元数据版本：

| 分支 | 内容 |
|---|---|
| `main` | 项目框架：说明文件、.gitignore、元数据清理工具 |
| `office-docs` | Word / Excel / PPT 文档（.docx / .xlsx / .pptx） |
| `pdf-docs` | PDF 文档 |

## 日常操作

```bash
# 查看当前在哪个分支
git branch

# 切到 Office 文档版本
git checkout office-docs

# 切到 PDF 文档版本
git checkout pdf-docs

# 切回框架主线
git checkout main

# 添加/修改文档后提交
git add 文档库/
git commit -m "docs: 更新文档"

# 查看两个版本各自的提交历史
git log --oneline office-docs
git log --oneline pdf-docs
```

## 注意

- 两个文档分支里的 `文档库/` 内容互不相同，切换分支时文件会自动更换，请先关闭所有正在编辑的 Office 文件再切换；
- `.workbuddy/` 目录为 WorkBuddy 运行数据，已在 .gitignore 中排除，请勿手动删除；
- 对外发送前，请先用 `tools/` 中的清理工具处理文档（拖拽到 `清理文档元数据.bat`）。
