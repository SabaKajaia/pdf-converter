import os
import subprocess
import tempfile
import shutil
from flask import Flask, request, jsonify, send_file, render_template_string
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB máx

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}
FONTS_DIR = os.path.join(os.path.dirname(__file__), 'fonts')

HTML = '''<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Conversor PDF · Corporepol</title>
  <link href="https://fonts.googleapis.com/css2?family=Oswald:wght@700&family=DM+Sans:wght@400;500&family=DM+Mono&display=swap" rel="stylesheet"/>
  <style>
    *{box-sizing:border-box;margin:0;padding:0}
    :root{--bg:#0d0d0d;--surface:#161616;--surface2:#1e1e1e;--border:#2a2a2a;--border2:#333;--lime:#c8d400;--lime2:#a8b200;--white:#fff;--text:#e8e8e8;--text2:#888;--text3:#555;--success:#7ecb5f;--success-bg:rgba(126,203,95,0.08);--success-border:rgba(126,203,95,0.25);--error:#e05555;--error-bg:rgba(224,85,85,0.08);--error-border:rgba(224,85,85,0.25)}
    body{font-family:'DM Sans',sans-serif;background:var(--bg);color:var(--text);min-height:100vh;display:flex;flex-direction:column;align-items:center;padding:2rem 1rem 3rem}
    body::before{content:'';position:fixed;inset:0;z-index:0;background:radial-gradient(ellipse 60% 40% at 50% 0%,rgba(200,212,0,0.04) 0%,transparent 60%);pointer-events:none}
    .header{position:relative;z-index:1;width:100%;max-width:580px;text-align:center;padding:2rem 0 1.75rem;border-bottom:1px solid var(--border);margin-bottom:2rem}
    .logo-img{width:80px;height:80px;border-radius:50%;object-fit:cover;border:2.5px solid var(--lime);box-shadow:0 0 32px rgba(200,212,0,0.25);margin-bottom:1.25rem}
    h1{font-family:'Oswald',sans-serif;font-size:1.8rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--white);margin-bottom:.4rem}
    h1 span{color:var(--lime)}
    .header p{font-size:.86rem;color:var(--text2);line-height:1.65;max-width:440px;margin:0 auto}
    .main{position:relative;z-index:1;width:100%;max-width:580px;display:flex;flex-direction:column;gap:1.1rem}
    .dropzone{border:2px dashed var(--border2);border-radius:16px;padding:2.25rem 1.5rem;text-align:center;cursor:pointer;transition:all .25s;position:relative;background:var(--surface)}
    .dropzone:hover,.dropzone.over{border-color:var(--lime);background:rgba(200,212,0,0.03)}
    .dropzone input{position:absolute;inset:0;opacity:0;cursor:pointer;width:100%;height:100%}
    .dz-icon{width:54px;height:54px;margin:0 auto 1rem;background:linear-gradient(135deg,var(--lime),var(--lime2));border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:1.5rem;box-shadow:0 6px 24px rgba(200,212,0,0.25)}
    .dropzone h3{font-family:'Oswald',sans-serif;font-size:.95rem;font-weight:600;letter-spacing:.06em;text-transform:uppercase;margin-bottom:.3rem;color:var(--white)}
    .dropzone p{font-size:.82rem;color:var(--text2)}
    .dropzone em{color:var(--lime);font-style:normal;font-weight:500}
    .dz-note{margin-top:.45rem;font-size:.7rem;color:var(--text3);font-family:'DM Mono',monospace}
    .queue{display:flex;flex-direction:column;gap:.4rem}
    .queue-header{display:flex;align-items:center;justify-content:space-between;padding:.15rem 0}
    .queue-title{font-size:.73rem;font-weight:500;color:var(--text2);text-transform:uppercase;letter-spacing:.06em}
    .queue-clear{background:none;border:none;color:var(--text3);font-size:.73rem;cursor:pointer;font-family:'DM Sans',sans-serif;transition:color .15s}
    .queue-clear:hover{color:var(--error)}
    .file-item{display:flex;align-items:center;gap:.7rem;background:var(--surface2);border:1px solid var(--border);border-radius:10px;padding:.7rem .9rem;transition:border-color .2s}
    .file-item.done{border-color:rgba(126,203,95,0.3)}
    .file-item.processing{border-color:var(--lime);box-shadow:0 0 12px rgba(200,212,0,0.08)}
    .file-item.error{border-color:var(--error-border)}
    .fi-icon{width:32px;height:32px;flex-shrink:0;border-radius:7px;background:linear-gradient(135deg,#8b0000,#c0392b);display:flex;align-items:center;justify-content:center;font-size:.85rem}
    .fi-info{flex:1;min-width:0}
    .fi-name{font-size:.81rem;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:var(--white)}
    .fi-meta{font-size:.69rem;color:var(--text2);margin-top:.1rem;font-family:'DM Mono',monospace}
    .fi-status{font-size:.69rem;font-family:'DM Mono',monospace;white-space:nowrap;flex-shrink:0}
    .fi-status.waiting{color:var(--text3)}
    .fi-status.processing{color:var(--lime)}
    .fi-status.done{color:var(--success)}
    .fi-status.error{color:var(--error)}
    .fi-rm{background:none;border:none;color:var(--text3);cursor:pointer;font-size:.85rem;padding:.2rem;border-radius:4px;line-height:1;transition:color .15s;flex-shrink:0}
    .fi-rm:hover{color:var(--error)}
    .btn-go{width:100%;padding:.9rem;background:var(--lime);border:none;border-radius:12px;color:#0d0d0d;font-family:'Oswald',sans-serif;font-size:1rem;font-weight:700;cursor:pointer;letter-spacing:.08em;text-transform:uppercase;display:flex;align-items:center;justify-content:center;gap:.5rem;transition:background .2s,transform .1s,box-shadow .2s;box-shadow:0 4px 20px rgba(200,212,0,0.2)}
    .btn-go:hover:not(:disabled){background:#d4e000;transform:translateY(-1px);box-shadow:0 6px 28px rgba(200,212,0,0.3)}
    .btn-go:disabled{opacity:.3;cursor:not-allowed;box-shadow:none}
    .results{display:flex;flex-direction:column;gap:.5rem}
    .result-item{display:flex;align-items:center;gap:.7rem;padding:.75rem .9rem;border-radius:10px;border:1px solid}
    .result-item.ok{background:var(--success-bg);border-color:var(--success-border)}
    .result-item.err{background:var(--error-bg);border-color:var(--error-border)}
    .ri-ico{font-size:.95rem;flex-shrink:0}
    .ri-info{flex:1;min-width:0}
    .ri-name{font-size:.8rem;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    .result-item.ok .ri-name{color:var(--success)}
    .result-item.err .ri-name{color:var(--error)}
    .ri-meta{font-size:.7rem;color:var(--text2);margin-top:.1rem}
    .btn-dl-sm{padding:.35rem .75rem;border-radius:8px;background:var(--success-bg);border:1px solid var(--success-border);color:var(--success);font-family:'DM Sans',sans-serif;font-size:.73rem;font-weight:600;text-decoration:none;white-space:nowrap;flex-shrink:0;transition:background .15s;cursor:pointer}
    .btn-dl-sm:hover{background:rgba(126,203,95,0.15)}
    .btn-reset{width:100%;padding:.6rem;background:none;border:1px solid var(--border);border-radius:12px;color:var(--text2);font-family:'DM Sans',sans-serif;font-size:.82rem;cursor:pointer;transition:all .15s;margin-top:.5rem}
    .btn-reset:hover{border-color:var(--border2);color:var(--text)}
    .infobox{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:.9rem 1.1rem;display:flex;gap:.6rem}
    .infobox p{font-size:.76rem;color:var(--text2);line-height:1.7}
    .infobox strong{color:var(--lime);font-weight:500}
    .footer{margin-top:1.5rem;text-align:center;font-size:.7rem;color:var(--text3)}
    .spin{display:inline-block;width:9px;height:9px;border:1.5px solid var(--lime);border-top-color:transparent;border-radius:50%;animation:spin .65s linear infinite;vertical-align:middle}
    @keyframes spin{to{transform:rotate(360deg)}}
  </style>
</head>
<body>
<div class="header">
  <img class="logo-img" src="/static/logo.png" onerror="this.style.display='none'" alt="Corporepol"/>
  <h1>PDF <span>con Fuentes</span></h1>
  <p>Convierte tus documentos a PDF con las fuentes correctamente embebidas. El resultado se visualiza igual en todos los visores.</p>
</div>

<div class="main">
  <div class="dropzone" id="dz">
    <input type="file" id="fi" accept=".pdf,.docx,.doc" multiple/>
    <div class="dz-icon">📄</div>
    <h3>Arrastra tus archivos aquí</h3>
    <p>o <em>selecciona los archivos</em> desde tu ordenador</p>
    <p class="dz-note">PDF, DOCX, DOC · Múltiples archivos · Máx 50 MB por archivo</p>
  </div>

  <div id="queueWrap" style="display:none">
    <div class="queue-header">
      <span class="queue-title" id="queueTitle"></span>
      <button class="queue-clear" id="btnClear">✕ Limpiar todo</button>
    </div>
    <div class="queue" id="queue"></div>
  </div>

  <button class="btn-go" id="btnGo" disabled>🖨️ Convertir</button>

  <div id="resultsWrap" style="display:none">
    <div class="results" id="results"></div>
    <button class="btn-reset" id="btnReset">Convertir otros archivos</button>
  </div>

  <div class="infobox">
    <p>Utiliza <strong>LibreOffice</strong> en el servidor para la conversión, con la fuente <strong>Hey August</strong> instalada. Las fuentes quedan correctamente embebidas en el PDF resultante, sin convertir a imagen, manteniendo el texto seleccionable y el peso del archivo reducido.</p>
  </div>
</div>

<div class="footer">Corporepol · Herramienta interna · Powered by LibreOffice</div>

<script>
  let files = [], uid = 0;
  const dz = document.getElementById('dz'), fi = document.getElementById('fi');
  dz.addEventListener('dragover', e => { e.preventDefault(); dz.classList.add('over') });
  dz.addEventListener('dragleave', () => dz.classList.remove('over'));
  dz.addEventListener('drop', e => { e.preventDefault(); dz.classList.remove('over'); addFiles(Array.from(e.dataTransfer.files)) });
  fi.addEventListener('change', () => addFiles(Array.from(fi.files)));
  document.getElementById('btnClear').addEventListener('click', clearAll);
  document.getElementById('btnReset').addEventListener('click', clearAll);

  function addFiles(newFiles) {
    newFiles.forEach(f => files.push({ file: f, id: ++uid, status: 'waiting' }));
    renderQueue(); updateBtn();
  }
  function removeFile(id) { files = files.filter(f => f.id !== id); renderQueue(); updateBtn() }
  function clearAll() {
    files = []; renderQueue(); updateBtn();
    document.getElementById('resultsWrap').style.display = 'none';
    document.getElementById('results').innerHTML = '';
  }
  function renderQueue() {
    const wrap = document.getElementById('queueWrap'), queue = document.getElementById('queue');
    if (!files.length) { wrap.style.display = 'none'; return }
    wrap.style.display = 'block';
    document.getElementById('queueTitle').textContent = files.length + ' archivo' + (files.length > 1 ? 's' : '');
    const stMap = {
      waiting: '<span class="fi-status waiting">En espera</span>',
      processing: '<span class="fi-status processing"><span class="spin"></span> Procesando...</span>',
      done: '<span class="fi-status done">✓ Listo</span>',
      error: '<span class="fi-status error">✗ Error</span>'
    };
    queue.innerHTML = files.map(f =>
      '<div class="file-item ' + f.status + '">' +
      '<div class="fi-icon">📄</div>' +
      '<div class="fi-info"><div class="fi-name">' + esc(f.file.name) + '</div><div class="fi-meta">' + fmt(f.file.size) + '</div></div>' +
      stMap[f.status] +
      (f.status === 'waiting' ? '<button class="fi-rm" onclick="removeFile(' + f.id + ')">✕</button>' : '') +
      '</div>'
    ).join('');
  }
  function updateBtn() {
    const w = files.filter(f => f.status === 'waiting').length;
    document.getElementById('btnGo').disabled = !w;
  }
  function setStatus(id, status) {
    const i = files.findIndex(f => f.id === id); if (i < 0) return;
    files[i].status = status; renderQueue();
  }

  document.getElementById('btnGo').addEventListener('click', convertAll);
  async function convertAll() {
    const waiting = files.filter(f => f.status === 'waiting');
    if (!waiting.length) return;
    document.getElementById('btnGo').disabled = true;
    document.getElementById('resultsWrap').style.display = 'none';
    document.getElementById('results').innerHTML = '';

    for (const entry of waiting) {
      setStatus(entry.id, 'processing');
      try {
        const fd = new FormData();
        fd.append('file', entry.file);
        const resp = await fetch('/convert', { method: 'POST', body: fd });
        if (!resp.ok) {
          const err = await resp.json();
          throw new Error(err.error || 'Error del servidor');
        }
        const blob = await resp.blob();
        const outName = entry.file.name.replace(/[.](docx?|pdf)$/i, '_convertido.pdf');
        addResult(entry.file.name, outName, blob, null);
        setStatus(entry.id, 'done');
      } catch (err) {
        addResult(entry.file.name, null, null, err.message);
        setStatus(entry.id, 'error');
      }
    }
    document.getElementById('resultsWrap').style.display = 'block';
    updateBtn();
  }

  function addResult(name, outName, blob, err) {
    const r = document.getElementById('results');
    if (blob) {
      const url = URL.createObjectURL(blob);
      const size = fmt(blob.size);
      r.insertAdjacentHTML('beforeend',
        '<div class="result-item ok"><span class="ri-ico">✅</span>' +
        '<div class="ri-info"><div class="ri-name">' + esc(outName) + '</div><div class="ri-meta">' + size + ' · fuentes embebidas correctamente</div></div>' +
        '<a class="btn-dl-sm" href="' + url + '" download="' + esc(outName) + '">⬇️ Descargar</a></div>');
    } else {
      r.insertAdjacentHTML('beforeend',
        '<div class="result-item err"><span class="ri-ico">❌</span>' +
        '<div class="ri-info"><div class="ri-name">' + esc(name) + '</div><div class="ri-meta">' + esc(err) + '</div></div></div>');
    }
  }

  function fmt(b) { if (b < 1024) return b + ' B'; if (b < 1048576) return (b / 1024).toFixed(1) + ' KB'; return (b / 1048576).toFixed(1) + ' MB' }
  function esc(s) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;') }
</script>
</body>
</html>'''

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def install_fonts():
    """Instala las fuentes de la carpeta fonts/ en el sistema."""
    if not os.path.exists(FONTS_DIR):
        return
    font_dest = os.path.expanduser('~/.local/share/fonts')
    os.makedirs(font_dest, exist_ok=True)
    for font_file in os.listdir(FONTS_DIR):
        if font_file.lower().endswith(('.ttf', '.otf')):
            src = os.path.join(FONTS_DIR, font_file)
            dst = os.path.join(font_dest, font_file)
            if not os.path.exists(dst):
                shutil.copy2(src, dst)
    subprocess.run(['fc-cache', '-f', '-v'], capture_output=True)

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return jsonify({'error': 'No se ha enviado ningún archivo'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nombre de archivo vacío'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Formato no soportado. Usa PDF, DOCX o DOC'}), 400

    tmp_dir = tempfile.mkdtemp()
    try:
        filename = secure_filename(file.filename)
        input_path = os.path.join(tmp_dir, filename)
        file.save(input_path)

        # Convertir con LibreOffice
        result = subprocess.run(
            ['libreoffice', '--headless', '--convert-to', 'pdf',
             '--outdir', tmp_dir, input_path],
            capture_output=True, text=True, timeout=120
        )

        if result.returncode != 0:
            return jsonify({'error': 'Error en la conversión: ' + result.stderr}), 500

        # Buscar el PDF generado
        base = os.path.splitext(filename)[0]
        output_path = os.path.join(tmp_dir, base + '.pdf')

        if not os.path.exists(output_path):
            return jsonify({'error': 'No se generó el PDF'}), 500

        return send_file(
            output_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=base + '_convertido.pdf'
        )

    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Tiempo de conversión agotado'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

if __name__ == '__main__':
    install_fonts()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
