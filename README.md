# MetaWipe 🧹

**Office / PDF 文档元数据离线清理工具** —— 一拖即清，文件不出你的电脑。

把 Word、PPT、Excel、PDF 文件拖到工具上，即可清除其中的作者、公司、创建/修改时间、软件指纹等隐私元数据，生成一份「干净」的副本用于对外发送。**全程本地处理，零联网、零上传。**

---

## ✨ 功能特性

- **一键拖放**：把文件或整个文件夹拖到 `清理文档元数据.bat`（或直接拖到 exe）上即可
- **递归批量**：拖入文件夹会自动处理所有子目录中的文件，支持一次成百上千个
- **生成副本**：输出「原文件名_已清理元数据.扩展名」到原目录，**原文件绝不修改**
- **失败隔离**：损坏/加密/被占用的文件标记失败并继续，最后统一汇报，不中断批处理
- **智能跳过**：自动排除 Office 临时锁文件（`~$` 开头）和已清理的副本，重复拖放不会套娃
- **处理留痕**：日志写入同目录 `clean_log.txt`

## 🧽 清理范围

| 格式 | 清理内容 |
|---|---|
| `.docx` / `.pptx` / `.xlsx` | 标题、主题、作者、最后修改者、公司、创建/修改时间、修订号、自定义属性（含 WPS 的 `KSOProductBuildVer`、`KSOTemplateDocerSaveRecord`、`ICV` 内容指纹等）、缩略图 |
| `.pdf` | Info 字典（标题/作者/主题/关键词/创建修改时间/Creator/Producer）+ XMP 元数据流整体移除 |

> 正文内容零改动——只动元数据，不碰文档内容、排版、批注和修订。

## 📦 下载与使用

### 普通用户（免安装）

1. 下载 Release 中的 `cleanmeta.exe`（单文件，约 26 MB）；
2. 把 `.docx` / `.pptx` / `.xlsx` / `.pdf` 文件或整个文件夹**拖到 exe 上**；
3. 在原目录拿到「_已清理元数据」副本，直接发送即可。

也支持命令行：

```
cleanmeta.exe 文件1.docx 文件夹A ...
```

### 从源码运行（需 Python 3.8+，清理 PDF 需 pypdf）

```
python docx_metadata_cleaner.py 文件或文件夹 ...
```

### 从源码打包 exe（需 PyInstaller）

```
pip install pypdf pyinstaller
python -m PyInstaller --onefile --console --name cleanmeta docx_metadata_cleaner.py
```

## ⚠️ 使用注意

1. **清理后不要再经 WPS/Office 编辑保存**——WPS 保存时会重新写入 `KSOProductBuildVer`、`ICV` 指纹等属性。正确顺序：改完文档 → 拖入清理 → 直接发送；
2. 老格式 `.doc` / `.wps` / `.xls` / `.et` / `.dps` 不支持，请先在 WPS/Office 中「另存为」对应的 `.docx` / `.xlsx` / `.pptx` 新格式（另存本身就会甩掉大部分旧属性）；
3. PDF 采用整体重写策略，个别复杂排版 PDF 建议清理后翻看一眼再外发；
4. 嵌入图片自身的 EXIF（拍摄设备、GPS 等）暂不在清理范围内。

## 🛠 技术原理

- OOXML（docx/pptx/xlsx）本质是 zip 包：工具解包后清空 `docProps/core.xml`、`app.xml` 中的字段，**整块删除** `docProps/custom.xml` 与缩略图，再重新打包——不经过任何 Office 组件；
- PDF 使用 pypdf 整体重写，清空 Info 字典并移除 XMP 流，避免旧数据残留在文件尾部。

## 📄 许可证

[MIT](LICENSE)

## 免责声明

本工具按"现状"提供，使用前请自行备份重要文件。清理元数据不等于获得信息发布审批授权，请遵守所在单位的保密与外发管理规定。
