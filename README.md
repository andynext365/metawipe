# 文档元数据清理项目仓库

本仓库只管理项目框架与工具，**不存放任何文档**（文档保留在桌面等原位置，不入库）。

| 分支 | 内容 |
|---|---|
| `main` | 主分支：README、.gitignore、`tools/` 元数据清理工具 |
| `office-docs` | 备用分支（当前与 main 相同，可用于后续 Office 文档相关的代码/脚本开发） |
| `pdf-docs` | 备用分支（当前与 main 相同） |

## 核心工具

`tools/清理文档元数据.bat` + `tools/docx_metadata_cleaner.py`：
离线清除 .docx / .pptx / .xlsx / .pdf 的元数据（作者、公司、创建/修改时间、KSO*/ICV 自定义属性、缩略图、XMP 等）。
使用方式：把文件或文件夹拖到 bat 上，原目录生成「_已清理元数据」副本。桌面 `文档元数据清理工具\` 下有同一套工具。

## 日常操作

```bash
git branch                 # 查看当前分支
git checkout main          # 切回主分支
git add <文件>             # 暂存改动
git commit -m "描述"       # 提交
git log --oneline          # 查看历史
```

## 注意

- 本仓库**不再提交任何 .docx/.xlsx/.pptx/.pdf 文档**，.gitignore 已按类型排除；
- `.workbuddy/` 目录为 WorkBuddy 运行数据，请勿手动删除；
- 对外发送文档前，先用 `tools/` 中的清理工具处理。
