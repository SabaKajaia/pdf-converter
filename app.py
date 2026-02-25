import os, subprocess, tempfile, shutil
from flask import Flask, request, jsonify, send_file, render_template_string
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}
FONTS_DIR = os.path.join(os.path.dirname(__file__), 'fonts')

LOGO_B64 = "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"
LOGO_WHITE_B64 = "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"

HTML = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Conversor PDF · nabbu</title>
  <link href="https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600;700&display=swap" rel="stylesheet"/>
  <style>
    *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
    :root{
      --aqua:#00485d;--aqua2:#72cbc1;--orange:#f15f1c;--yellow:#f6de2a;
      --pink:#df1965;--paper:#efebe3;--paper2:#f8f6f2;--white:#fff;
      --ink:#00485d;--ink2:#3a6a7a;--ink3:#8aacb4;
      --border:rgba(0,72,93,0.13);--border2:rgba(0,72,93,0.22);
    }
    html{scroll-behavior:smooth}
    body{
      font-family:'Quicksand',sans-serif;background:var(--paper);
      color:var(--ink);min-height:100vh;overflow-x:hidden;
    }

    /* HERO */
    .hero{
      background:var(--aqua);
      padding:3rem 1.5rem 5rem;
      text-align:center;
      position:relative;
      overflow:hidden;
    }
    .hero::before{
      content:'';position:absolute;
      width:500px;height:500px;border-radius:50%;
      background:rgba(114,203,193,0.12);
      top:-200px;right:-150px;pointer-events:none;
    }
    .hero::after{
      content:'';position:absolute;
      width:300px;height:300px;border-radius:50%;
      background:rgba(246,222,42,0.07);
      bottom:-150px;left:-80px;pointer-events:none;
    }
    /* puntos decorativos */
    .dot1,.dot2,.dot3{position:absolute;border-radius:50%;pointer-events:none}
    .dot1{width:14px;height:14px;background:var(--pink);top:2.5rem;right:12%}
    .dot2{width:10px;height:10px;background:var(--yellow);top:4rem;right:14.5%}
    .dot3{width:18px;height:18px;background:var(--aqua2);bottom:3rem;left:8%}

    .logo-img{height:38px;margin-bottom:2.5rem;position:relative;z-index:1;filter:brightness(0) invert(1)}
    .hero h1{
      font-size:clamp(2rem,5vw,3rem);font-weight:700;
      color:var(--paper);letter-spacing:-.03em;
      line-height:1.1;margin-bottom:.9rem;
      position:relative;z-index:1;
    }
    .hero h1 span{
      color:var(--yellow);
      position:relative;
      display:inline-block;
    }
    .hero p{
      font-size:1rem;color:rgba(239,235,227,0.75);
      max-width:420px;margin:0 auto;line-height:1.7;
      font-weight:500;position:relative;z-index:1;
    }

    /* wave */
    .wave{display:block;margin-bottom:-2px;color:var(--paper)}

    /* MAIN CARD */
    .container{max-width:600px;margin:0 auto;padding:0 1.25rem 4rem}
    .card{
      background:var(--white);border-radius:24px;
      box-shadow:0 20px 60px rgba(0,72,93,0.1);
      padding:2rem;margin-top:-3rem;
      position:relative;z-index:2;
    }

    /* DROPZONE */
    .dropzone{
      border:2px dashed var(--border2);border-radius:18px;
      padding:2.5rem 1.5rem;text-align:center;cursor:pointer;
      transition:all .3s;position:relative;
      background:var(--paper2);
    }
    .dropzone:hover,.dropzone.over{
      border-color:var(--aqua2);background:rgba(114,203,193,0.08);
      transform:scale(1.01);
    }
    .dropzone input{position:absolute;inset:0;opacity:0;cursor:pointer;width:100%;height:100%}
    .dz-dots{display:flex;justify-content:center;gap:.5rem;margin-bottom:1.1rem}
    .dz-dot{
      width:48px;height:48px;border-radius:50%;
      display:flex;align-items:center;justify-content:center;font-size:1.3rem;
    }
    .dz-dot:nth-child(1){background:rgba(0,72,93,0.08)}
    .dz-dot:nth-child(2){background:var(--aqua);box-shadow:0 8px 20px rgba(0,72,93,0.25)}
    .dz-dot:nth-child(3){background:rgba(114,203,193,0.2)}
    .dropzone h3{font-size:1rem;font-weight:700;color:var(--aqua);margin-bottom:.35rem}
    .dropzone p{font-size:.84rem;color:var(--ink2);font-weight:500}
    .dropzone em{color:var(--orange);font-style:normal;font-weight:700}
    .dz-note{margin-top:.5rem;font-size:.71rem;color:var(--ink3)}

    /* QUEUE */
    .queue-wrap{margin-top:1.25rem}
    .queue-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:.5rem}
    .queue-title{font-size:.72rem;font-weight:700;color:var(--ink3);text-transform:uppercase;letter-spacing:.07em}
    .queue-clear{background:none;border:none;color:var(--ink3);font-size:.72rem;cursor:pointer;font-family:'Quicksand',sans-serif;font-weight:600;transition:color .15s}
    .queue-clear:hover{color:var(--pink)}
    .queue{display:flex;flex-direction:column;gap:.4rem}
    .file-item{
      display:flex;align-items:center;gap:.75rem;
      background:var(--paper2);border:1.5px solid var(--border);
      border-radius:14px;padding:.65rem .9rem;transition:all .2s;
    }
    .file-item.processing{border-color:var(--aqua2);background:rgba(114,203,193,0.05)}
    .file-item.done{border-color:rgba(114,203,193,0.5);background:rgba(114,203,193,0.05)}
    .file-item.error{border-color:rgba(223,25,101,0.3);background:rgba(223,25,101,0.04)}
    .fi-icon{width:36px;height:36px;flex-shrink:0;border-radius:10px;background:var(--aqua);display:flex;align-items:center;justify-content:center;font-size:.9rem}
    .fi-info{flex:1;min-width:0}
    .fi-name{font-size:.8rem;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:var(--aqua)}
    .fi-meta{font-size:.68rem;color:var(--ink3);margin-top:.1rem}
    .fi-status{font-size:.69rem;font-weight:700;white-space:nowrap;flex-shrink:0}
    .fi-status.waiting{color:var(--ink3)}
    .fi-status.processing{color:var(--aqua2)}
    .fi-status.done{color:#3aaa8a}
    .fi-status.error{color:var(--pink)}
    .fi-rm{background:none;border:none;color:var(--ink3);cursor:pointer;font-size:.85rem;padding:.2rem;border-radius:5px;transition:color .15s;flex-shrink:0}
    .fi-rm:hover{color:var(--pink)}

    /* BTN */
    .btn-go{
      width:100%;margin-top:1.25rem;padding:1rem;
      background:linear-gradient(135deg,var(--aqua) 0%,#006b87 100%);
      border:none;border-radius:100px;
      color:var(--paper);font-family:'Quicksand',sans-serif;
      font-size:1rem;font-weight:700;cursor:pointer;
      letter-spacing:.01em;
      display:flex;align-items:center;justify-content:center;gap:.5rem;
      transition:all .25s;
      box-shadow:0 8px 28px rgba(0,72,93,0.3);
      position:relative;overflow:hidden;
    }
    .btn-go::after{
      content:'';position:absolute;
      width:80px;height:200%;background:rgba(255,255,255,0.1);
      top:-50%;left:-100px;transform:skewX(-20deg);
      transition:left .5s ease;
    }
    .btn-go:hover:not(:disabled)::after{left:130%}
    .btn-go:hover:not(:disabled){transform:translateY(-2px);box-shadow:0 12px 36px rgba(0,72,93,0.35)}
    .btn-go:disabled{opacity:.35;cursor:not-allowed;box-shadow:none;transform:none}

    /* RESULTS */
    .results-wrap{margin-top:1.25rem}
    .results{display:flex;flex-direction:column;gap:.5rem}
    .result-item{
      display:flex;align-items:center;gap:.75rem;
      padding:.8rem 1rem;border-radius:14px;border:1.5px solid;
    }
    .result-item.ok{background:rgba(58,170,138,0.07);border-color:rgba(58,170,138,0.3)}
    .result-item.err{background:rgba(223,25,101,0.05);border-color:rgba(223,25,101,0.2)}
    .ri-ico{font-size:1rem;flex-shrink:0}
    .ri-info{flex:1;min-width:0}
    .ri-name{font-size:.8rem;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    .result-item.ok .ri-name{color:#2a8a6a}
    .result-item.err .ri-name{color:var(--pink)}
    .ri-meta{font-size:.69rem;color:var(--ink3);margin-top:.1rem}
    .btn-dl{
      padding:.4rem 1rem;border-radius:100px;
      background:var(--aqua);border:none;
      color:var(--paper);font-family:'Quicksand',sans-serif;
      font-size:.75rem;font-weight:700;text-decoration:none;
      white-space:nowrap;flex-shrink:0;transition:background .15s;cursor:pointer;
      box-shadow:0 4px 12px rgba(0,72,93,0.2);
    }
    .btn-dl:hover{background:#005a75}
    .btn-reset{
      width:100%;margin-top:.75rem;padding:.65rem;background:none;
      border:1.5px solid var(--border2);border-radius:100px;
      color:var(--ink2);font-family:'Quicksand',sans-serif;
      font-size:.83rem;font-weight:600;cursor:pointer;transition:all .15s;
    }
    .btn-reset:hover{border-color:var(--aqua);color:var(--aqua)}

    /* INFO PILLS */
    .pills{display:flex;gap:.6rem;flex-wrap:wrap;margin-top:1.5rem}
    .pill{
      display:flex;align-items:center;gap:.4rem;
      background:var(--paper2);border:1.5px solid var(--border);
      border-radius:100px;padding:.4rem .85rem;
      font-size:.75rem;font-weight:600;color:var(--ink2);
    }
    .pill-dot{width:7px;height:7px;border-radius:50%;flex-shrink:0}

    /* FOOTER */
    .footer-bar{
      background:var(--aqua);padding:1.5rem;text-align:center;
    }
    .footer-logo{height:22px;filter:brightness(0) invert(1);opacity:.7}
    .footer-txt{font-size:.72rem;color:rgba(239,235,227,0.5);margin-top:.5rem;font-weight:500}

    .spin{display:inline-block;width:9px;height:9px;border:1.5px solid var(--aqua2);border-top-color:transparent;border-radius:50%;animation:spin .65s linear infinite;vertical-align:middle}
    @keyframes spin{to{transform:rotate(360deg)}}

    @media(max-width:480px){
      .hero{padding:2rem 1rem 4.5rem}
      .card{padding:1.5rem;border-radius:20px}
    }
  </style>
</head>
<body>

<div class="hero">
  <div class="dot1"></div><div class="dot2"></div><div class="dot3"></div>
  <img class="logo-img" src="data:image/png;base64,""" + LOGO_WHITE_B64 + """" alt="nabbu"/>
  <h1>Convierte tus<br/><span>documentos PDF</span><br/>sin perder fuentes</h1>
  <p>Sube tus archivos y los convertimos con LibreOffice para que las fuentes queden perfectamente embebidas.</p>
</div>

<svg class="wave" viewBox="0 0 1440 60" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none" style="display:block;background:#00485d">
  <path d="M0,30 C360,60 1080,0 1440,30 L1440,60 L0,60 Z" fill="#efebe3"/>
</svg>

<div class="container">
  <div class="card">

    <div class="dropzone" id="dz">
      <input type="file" id="fi" accept=".pdf,.docx,.doc" multiple/>
      <div class="dz-dots">
        <div class="dz-dot">📎</div>
        <div class="dz-dot">📄</div>
        <div class="dz-dot">✨</div>
      </div>
      <h3>Arrastra tus archivos aquí</h3>
      <p>o <em>selecciona los archivos</em> desde tu ordenador</p>
      <p class="dz-note">PDF · DOCX · DOC &nbsp;·&nbsp; Múltiples archivos &nbsp;·&nbsp; Máx 50 MB</p>
    </div>

    <div class="queue-wrap" id="queueWrap" style="display:none">
      <div class="queue-header">
        <span class="queue-title" id="queueTitle"></span>
        <button class="queue-clear" id="btnClear">✕ Limpiar</button>
      </div>
      <div class="queue" id="queue"></div>
    </div>

    <button class="btn-go" id="btnGo" disabled>Convertir documentos</button>

    <div class="results-wrap" id="resultsWrap" style="display:none">
      <div class="results" id="results"></div>
      <button class="btn-reset" id="btnReset">Convertir otros archivos</button>
    </div>

  </div>

  <div class="pills">
    <div class="pill"><div class="pill-dot" style="background:#72cbc1"></div>Fuentes embebidas correctamente</div>
    <div class="pill"><div class="pill-dot" style="background:#f6de2a"></div>Texto seleccionable</div>
    <div class="pill"><div class="pill-dot" style="background:#df1965"></div>Peso reducido vs imagen</div>
    <div class="pill"><div class="pill-dot" style="background:#00485d"></div>100% privado · sin registro</div>
  </div>
</div>

<div class="footer-bar">
  <img class="footer-logo" src="data:image/png;base64,""" + LOGO_WHITE_B64 + """" alt="nabbu"/>
  <div class="footer-txt">Herramienta interna · Powered by LibreOffice</div>
</div>

<script>
  let files=[], uid=0;
  const dz=document.getElementById("dz"), fi=document.getElementById("fi");
  dz.addEventListener("dragover",e=>{e.preventDefault();dz.classList.add("over")});
  dz.addEventListener("dragleave",()=>dz.classList.remove("over"));
  dz.addEventListener("drop",e=>{e.preventDefault();dz.classList.remove("over");addFiles(Array.from(e.dataTransfer.files))});
  fi.addEventListener("change",()=>addFiles(Array.from(fi.files)));
  document.getElementById("btnClear").addEventListener("click",clearAll);
  document.getElementById("btnReset").addEventListener("click",clearAll);

  function addFiles(nf){nf.forEach(f=>files.push({file:f,id:++uid,status:"waiting"}));renderQueue();updateBtn()}
  function removeFile(id){files=files.filter(f=>f.id!==id);renderQueue();updateBtn()}
  function clearAll(){
    files=[];renderQueue();updateBtn();
    document.getElementById("resultsWrap").style.display="none";
    document.getElementById("results").innerHTML="";
  }
  function renderQueue(){
    const wrap=document.getElementById("queueWrap"),queue=document.getElementById("queue");
    if(!files.length){wrap.style.display="none";return}
    wrap.style.display="block";
    document.getElementById("queueTitle").textContent=files.length+" archivo"+(files.length>1?"s":"");
    const st={
      waiting:'<span class="fi-status waiting">En espera</span>',
      processing:'<span class="fi-status processing"><span class="spin"></span> Procesando...</span>',
      done:'<span class="fi-status done">✓ Listo</span>',
      error:'<span class="fi-status error">✗ Error</span>'
    };
    queue.innerHTML=files.map(f=>
      '<div class="file-item '+f.status+'">'+
      '<div class="fi-icon">📄</div>'+
      '<div class="fi-info"><div class="fi-name">'+esc(f.file.name)+'</div><div class="fi-meta">'+fmt(f.file.size)+'</div></div>'+
      st[f.status]+
      (f.status==="waiting"?'<button class="fi-rm" onclick="removeFile('+f.id+')">✕</button>':'')+
      '</div>'
    ).join("");
  }
  function updateBtn(){
    const w=files.filter(f=>f.status==="waiting").length;
    const btn=document.getElementById("btnGo");
    btn.disabled=!w;
    btn.textContent=w>1?"Convertir "+w+" documentos":"Convertir documento";
  }
  function setStatus(id,status){const i=files.findIndex(f=>f.id===id);if(i<0)return;files[i].status=status;renderQueue()}

  document.getElementById("btnGo").addEventListener("click",convertAll);
  async function convertAll(){
    const waiting=files.filter(f=>f.status==="waiting");
    if(!waiting.length)return;
    document.getElementById("btnGo").disabled=true;
    document.getElementById("resultsWrap").style.display="none";
    document.getElementById("results").innerHTML="";
    for(const entry of waiting){
      setStatus(entry.id,"processing");
      try{
        const fd=new FormData();fd.append("file",entry.file);
        const resp=await fetch("/convert",{method:"POST",body:fd});
        if(!resp.ok){const err=await resp.json();throw new Error(err.error||"Error del servidor")}
        const blob=await resp.blob();
        const outName=entry.file.name.replace(/[.](docx?|pdf)$/i,"_convertido.pdf");
        addResult(entry.file.name,outName,blob,null);
        setStatus(entry.id,"done");
      }catch(err){addResult(entry.file.name,null,null,err.message);setStatus(entry.id,"error")}
    }
    document.getElementById("resultsWrap").style.display="block";
    updateBtn();
    document.querySelector(".results-wrap").scrollIntoView({behavior:"smooth",block:"nearest"});
  }
  function addResult(name,outName,blob,err){
    const r=document.getElementById("results");
    if(blob){
      const url=URL.createObjectURL(blob);
      r.insertAdjacentHTML("beforeend",
        '<div class="result-item ok"><span class="ri-ico">✅</span>'+
        '<div class="ri-info"><div class="ri-name">'+esc(outName)+'</div><div class="ri-meta">'+fmt(blob.size)+' · fuentes embebidas</div></div>'+
        '<a class="btn-dl" href="'+url+'" download="'+esc(outName)+'">⬇ Descargar</a></div>');
    }else{
      r.insertAdjacentHTML("beforeend",
        '<div class="result-item err"><span class="ri-ico">❌</span>'+
        '<div class="ri-info"><div class="ri-name">'+esc(name)+'</div><div class="ri-meta">'+esc(err)+'</div></div></div>');
    }
  }
  function fmt(b){if(b<1024)return b+" B";if(b<1048576)return(b/1024).toFixed(1)+" KB";return(b/1048576).toFixed(1)+" MB"}
  function esc(s){return s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;")}
</script>
</body>
</html>"""

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def install_fonts():
    if not os.path.exists(FONTS_DIR): return
    font_dest = os.path.expanduser("~/.local/share/fonts")
    os.makedirs(font_dest, exist_ok=True)
    for font_file in os.listdir(FONTS_DIR):
        if font_file.lower().endswith((".ttf", ".otf")):
            src = os.path.join(FONTS_DIR, font_file)
            dst = os.path.join(font_dest, font_file)
            if not os.path.exists(dst): shutil.copy2(src, dst)
    subprocess.run(["fc-cache", "-f", "-v"], capture_output=True)

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/convert", methods=["POST"])
def convert():
    if "file" not in request.files: return jsonify({"error": "No se ha enviado ningún archivo"}), 400
    file = request.files["file"]
    if file.filename == "": return jsonify({"error": "Nombre de archivo vacío"}), 400
    if not allowed_file(file.filename): return jsonify({"error": "Formato no soportado. Usa PDF, DOCX o DOC"}), 400
    tmp_dir = tempfile.mkdtemp()
    try:
        filename = secure_filename(file.filename)
        input_path = os.path.join(tmp_dir, filename)
        file.save(input_path)
        result = subprocess.run(
            ["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", tmp_dir, input_path],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode != 0: return jsonify({"error": "Error en la conversión: " + result.stderr}), 500
        base = os.path.splitext(filename)[0]
        output_path = os.path.join(tmp_dir, base + ".pdf")
        if not os.path.exists(output_path): return jsonify({"error": "No se generó el PDF"}), 500
        return send_file(output_path, mimetype="application/pdf", as_attachment=True, download_name=base + "_convertido.pdf")
    except subprocess.TimeoutExpired: return jsonify({"error": "Tiempo de conversión agotado"}), 500
    except Exception as e: return jsonify({"error": str(e)}), 500
    finally: shutil.rmtree(tmp_dir, ignore_errors=True)

if __name__ == "__main__":
    install_fonts()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
