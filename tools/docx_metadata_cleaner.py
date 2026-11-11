# -*- coding: utf-8 -*-
"""Office/PDF 文档元数据离线清理工具（支持批量）
用法:
  1. 把 .docx / .pptx / .xlsx / .pdf 文件，或整个文件夹，拖到「清理文档元数据.bat」上
     （文件夹会递归处理所有子目录中的文件）
  2. 或命令行: python docx_metadata_cleaner.py 文件1.docx 文件夹A ...
效果:
  - Office(docx/pptx/xlsx): 清空作者/公司/创建修改时间/最后修改者,
    整块删除自定义属性(KSO*/ICV)和缩略图。
  - PDF: 清空 Info 字典(标题/作者/创建/修改时间等)并移除 XMP 元数据流。
正文内容零改动。原文件不覆盖, 输出「原文件名_已清理元数据.扩展名」到同目录。
注: Office 仅支持 OOXML 新格式; 老格式 .doc/.wps/.dps/.xls/.et 请先在 WPS 中
    "另存为"对应新格式再清理。PDF 清理为整体重写, 加密 PDF 会标记失败。
"""
import os
import re
import sys
import zipfile

try:
    from pypdf import PdfReader, PdfWriter
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

EMPTY_CORE = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\r\n'
    '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
    'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
    'xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
    '<dc:title></dc:title><dc:subject></dc:subject><dc:creator></dc:creator>'
    '<cp:keywords></cp:keywords><dc:description></dc:description>'
    '<cp:lastModifiedBy></cp:lastModifiedBy><cp:revision>1</cp:revision>'
    '</cp:coreProperties>'
)

EMPTY_APP = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\r\n'
    '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" '
    'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
    '<Application></Application><Company></Company>'
    '</Properties>'
)

SUPPORTED_EXTS = (".docx", ".pptx", ".xlsx", ".pdf")
SUFFIX = "_已清理元数据"
HERE = os.path.dirname(os.path.abspath(__file__))


def is_supported(path):
    name = os.path.basename(path)
    if name.startswith("~$"):          # Office 临时锁文件
        return False
    if os.path.splitext(name)[0].endswith(SUFFIX):
        return False                    # 已清理过的副本, 不重复处理
    return name.lower().endswith(SUPPORTED_EXTS)


def collect(paths):
    """展开文件/文件夹参数, 返回待处理文件列表(去重保序)"""
    files, seen = [], set()
    for p in paths:
        if os.path.isdir(p):
            for root, dirs, names in os.walk(p):
                dirs[:] = [d for d in dirs if not d.startswith(".")]
                for n in sorted(names):
                    full = os.path.join(root, n)
                    if is_supported(full) and full.lower() not in seen:
                        seen.add(full.lower())
                        files.append(full)
        elif os.path.isfile(p):
            if p.lower() not in seen:
                seen.add(p.lower())
                files.append(p)
    return files


def clean_pdf(src, dst):
    """清理 PDF 的 Info 字典与 XMP 元数据流, 返回说明文本"""
    if not HAS_PDF:
        return None, "缺少 pypdf 库, 无法清理 PDF(请重新部署工具)"
    writer = PdfWriter(clone_from=src)
    removed = []
    # 1) Info 字典: 已有键全部置空
    try:
        existing = list(writer.metadata.keys()) if writer.metadata else []
    except Exception:
        existing = []
    if existing:
        writer.add_metadata({k: "" for k in existing})
        removed.append("Info(%d项)" % len(existing))
    # 2) XMP 元数据流
    root = writer._root_object
    if "/Metadata" in root:
        del root["/Metadata"]
        removed.append("XMP")
    with open(dst, "wb") as f:
        writer.write(f)
    return ", ".join(removed) if removed else "无元数据", None


def clean_one(src):
    """返回 (状态, 说明)  状态: ok / skip / fail"""
    if not is_supported(src):
        return "skip", "不支持或已清理: " + os.path.basename(src)
    base, ext = os.path.splitext(src)
    dst = base + SUFFIX + ext
    if ext.lower() == ".pdf":
        try:
            removed, err = clean_pdf(src, dst)
        except Exception as e:
            if os.path.exists(dst):
                try:
                    os.remove(dst)
                except OSError:
                    pass
            return "fail", "%s -> %s" % (os.path.basename(src), e)
        if err:
            if os.path.exists(dst):
                os.remove(dst)
            return "fail", "%s -> %s" % (os.path.basename(src), err)
        return "ok", "%s -> %s  (清理: %s)" % (os.path.basename(src), os.path.basename(dst), removed)
    removed = []
    try:
        zin = zipfile.ZipFile(src, "r")
        names = zin.namelist()
        with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
            for name in names:
                lower = name.lower()
                if lower == "docprops/custom.xml" or lower.startswith("docprops/thumbnail"):
                    removed.append(os.path.basename(name))
                    continue
                data = zin.read(name)
                if name == "docProps/core.xml":
                    data = EMPTY_CORE.encode("utf-8")
                elif name == "docProps/app.xml":
                    data = EMPTY_APP.encode("utf-8")
                elif name == "[Content_Types].xml":
                    text = data.decode("utf-8")
                    text = re.sub(r'<Override[^>]*PartName="/docProps/custom\.xml"[^>]*/>', "", text)
                    text = re.sub(r'<Override[^>]*PartName="/docProps/thumbnail[^"]*"[^>]*/>', "", text)
                    data = text.encode("utf-8")
                elif name == "_rels/.rels":
                    text = data.decode("utf-8")
                    text = re.sub(r'<Relationship[^>]*Target="docProps/custom\.xml"[^>]*/>', "", text)
                    text = re.sub(r'<Relationship[^>]*Target="docProps/thumbnail[^"]*"[^>]*/>', "", text)
                    data = text.encode("utf-8")
                zout.writestr(name, data)
        zin.close()
    except Exception as e:                                   # 损坏/加密/被占用
        if os.path.exists(dst):
            try:
                os.remove(dst)
            except OSError:
                pass
        return "fail", "%s -> %s" % (os.path.basename(src), e)
    return "ok", "%s -> %s  (删除: %s)" % (os.path.basename(src), os.path.basename(dst),
                                          ", ".join(removed) if removed else "无自定义属性")


def main():
    argv = sys.argv[1:]
    args = [a for a in argv if not a.startswith("--")]
    noinput = any(a.startswith("--") for a in argv)
    if not args:
        print("用法: 把 .docx/.pptx/.xlsx/.pdf 文件或文件夹拖到 bat 上")
        print("      命令行: python docx_metadata_cleaner.py 文件或文件夹 ...")
        input("按回车退出...")
        return

    files = collect(args)
    total = len(files)
    print("待处理文件: %d 个\n" % total)
    if total == 0:
        print("未找到可处理的 docx/pptx/xlsx/pdf 文件。")
        if not noinput:
            input("按回车退出...")
        return

    ok, skipped, failed = [], [], []
    for i, f in enumerate(files, 1):
        status, msg = clean_one(f)
        if status == "ok":
            ok.append(msg)
        elif status == "skip":
            skipped.append(msg)
        else:
            failed.append(msg)
        print("[%d/%d] %s" % (i, total, msg))

    summary = "\n".join([
        "",
        "=" * 50,
        "批量处理完成: 共 %d 个 | 成功 %d | 跳过 %d | 失败 %d" % (total, len(ok), len(skipped), len(failed)),
        "=" * 50,
    ])
    if failed:
        summary += "\n失败明细:\n  " + "\n  ".join(failed)
    print(summary)

    log_path = os.path.join(HERE, "clean_log.txt")
    with open(log_path, "a", encoding="utf-8") as fp:
        fp.write("\n".join(["[批量] " + " | ".join(a for a in args)] + ok + skipped + [summary]) + "\n")

    if not noinput:
        input("按回车退出...")


if __name__ == "__main__":
    main()
