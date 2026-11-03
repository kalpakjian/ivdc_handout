// 把 REPORT.md 渲染成 Pages 用的 report.html（marked + 與 index.html 同一個深色主題）
const fs = require("fs");
const path = require("path");
const { marked } = require("marked");

const REPO = "/home/kalpakjian/Projects/ivdc_handout";
const md = fs.readFileSync(path.join(REPO, "REPORT.md"), "utf-8");
const body = marked.parse(md);

const html = `<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>IVDC Lesson 8 · 25 頁教材逐頁核對報告</title>
<style>
  :root { --bg:#0a0e14; --panel:#111823; --line:#1e2a3a; --fg:#e6edf3; --mut:#8b9bb0;
          --cyan:#2dd4bf; --mag:#e83e8c; }
  * { box-sizing: border-box; }
  body { margin:0; background:var(--bg); color:var(--fg); line-height:1.72;
         font-family:"Noto Sans TC","Segoe UI",system-ui,-apple-system,"Helvetica Neue",Arial,sans-serif; }
  .wrap { max-width: 900px; margin:0 auto; padding: 44px 22px 90px; }
  a { color: var(--cyan); text-decoration:none; border-bottom:1px solid rgba(45,212,191,.35); }
  a:hover { color:#fff; }
  h1 { font-size:1.75rem; margin:.2em 0 .5em; }
  h2 { font-size:1.2rem; margin:2em 0 .6em; padding-left:10px; border-left:3px solid var(--mag); }
  h3 { font-size:1.02rem; margin:1.6em 0 .5em; color:var(--cyan); }
  p, li { font-size:.95rem; }
  blockquote { margin:1em 0; padding:.6em 1em; border-left:3px solid var(--line);
               background:var(--panel); color:var(--mut); border-radius:0 8px 8px 0; }
  code { background:#0f1621; border:1px solid var(--line); border-radius:4px;
         padding:1px 5px; font-size:.86em; color:#b6e3ff; }
  pre { background:#0f1621; border:1px solid var(--line); border-radius:10px;
        padding:14px 16px; overflow-x:auto; }
  pre code { border:0; background:none; padding:0; color:#cfe3f5; }
  table { border-collapse:collapse; width:100%; margin:1em 0; font-size:.88rem; display:block; overflow-x:auto; }
  th, td { border:1px solid var(--line); padding:8px 10px; text-align:left; vertical-align:top; }
  th { background:#131c28; color:var(--cyan); white-space:nowrap; }
  tr:nth-child(even) td { background:#0d141d; }
  hr { border:0; border-top:1px solid var(--line); margin:2.2em 0; }
  .back { display:inline-block; margin-bottom:18px; font-size:.86rem; }
  footer { margin-top:46px; padding-top:16px; border-top:1px solid var(--line);
           color:var(--mut); font-size:.8rem; }
</style>
</head>
<body>
<div class="wrap">
  <a class="back" href="./">← 回索引</a>
  ${body}
  <footer>MIT License ｜ 課程簡報著作權屬匯縱專業發展中心，本 repo 只還原程式碼結構與實測筆記。</footer>
</div>
</body>
</html>
`;

fs.writeFileSync(path.join(REPO, "report.html"), html);
console.log("wrote report.html", Buffer.byteLength(html), "bytes");
