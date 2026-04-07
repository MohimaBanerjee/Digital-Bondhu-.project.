"""Digital Bandhu — Flask Backend"""
import os, logging
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from detection import (detect_message, detect_url, detect_upi, detect_news,
                       detect_email, detect_voice, detect_bank, detect_media,
                       detect_transaction)

app = Flask(__name__, static_folder=".")
CORS(app)
logging.basicConfig(level=logging.INFO)
START = datetime.utcnow()

def ok(r, inp):
    return {"success":True,"input":str(inp)[:120],"score":r["score"],
            "level":r["level"],"reasons":r["reasons"],"action":r.get("action",""),
            "timestamp":datetime.utcnow().isoformat()+"Z"}

def err(msg, code=400):
    return jsonify({"success":False,"error":msg}), code

def field(b, k, n=3):
    v=b.get(k,"")
    if not isinstance(v,str): return None,f"'{k}' must be string"
    v=v.strip()
    if len(v)<n: return None,f"'{k}' too short"
    return v,None

@app.route("/")
def index(): return send_from_directory(".","index.html")

@app.route("/health")
def health():
    return jsonify({"status":"ok","service":"Digital Bandhu","version":"2.0",
                    "uptime":int((datetime.utcnow()-START).total_seconds()),
                    "timestamp":datetime.utcnow().isoformat()+"Z"})

@app.route("/api/message",methods=["POST"])
@app.route("/message",methods=["POST"])
def api_msg():
    b=request.get_json(silent=True) or {}
    v,e=field(b,"text",5)
    if e: return err(e)
    return jsonify(ok(detect_message(v),v))

@app.route("/api/url",methods=["POST"])
@app.route("/url",methods=["POST"])
def api_url():
    b=request.get_json(silent=True) or {}
    v,e=field(b,"url",4)
    if e: return err(e)
    return jsonify(ok(detect_url(v),v))

@app.route("/api/upi",methods=["POST"])
@app.route("/upi",methods=["POST"])
def api_upi():
    b=request.get_json(silent=True) or {}
    v,e=field(b,"upi_id",3)
    if e: return err(e)
    return jsonify(ok(detect_upi(v),v))

@app.route("/api/news",methods=["POST"])
@app.route("/news",methods=["POST"])
def api_news():
    b=request.get_json(silent=True) or {}
    v,e=field(b,"text",10)
    if e: return err(e)
    return jsonify(ok(detect_news(v),v))

@app.route("/api/email",methods=["POST"])
@app.route("/email",methods=["POST"])
def api_email():
    b=request.get_json(silent=True) or {}
    v,e=field(b,"text",5)
    if e: return err(e)
    return jsonify(ok(detect_email(v),v))

@app.route("/api/voice",methods=["POST"])
@app.route("/voice",methods=["POST"])
def api_voice():
    b=request.get_json(silent=True) or {}
    v,e=field(b,"transcript",10)
    if e: return err(e)
    return jsonify(ok(detect_voice(v),v))

@app.route("/api/bank",methods=["POST"])
@app.route("/bank",methods=["POST"])
def api_bank():
    b=request.get_json(silent=True) or {}
    v,e=field(b,"sms",5)
    if e: return err(e)
    return jsonify(ok(detect_bank(v),v))

@app.route("/api/media",methods=["POST"])
def api_media():
    if request.files:
        f=next(iter(request.files.values()))
        c=f.read()
        return jsonify(ok(detect_media(f.filename or "",f.content_type or "",len(c)),f.filename))
    b=request.get_json(silent=True) or {}
    ft=b.get("filetype","")
    if not ft: return err("provide filetype")
    return jsonify(ok(detect_media(b.get("filename","file"),ft,int(b.get("filesize",0))),b.get("filename","file")))

@app.route("/api/transaction",methods=["POST"])
def api_txn():
    b=request.get_json(silent=True) or {}
    if not any(b.get(k) for k in ["message","upi_id"]): return err("provide message or upi_id")
    return jsonify(ok(detect_transaction(b),str(b.get("upi_id") or b.get("message",""))[:80]))

@app.errorhandler(404)
def nf(e): return err("Not found",404)
@app.errorhandler(405)
def ma(e): return err("Use POST",405)

if __name__=="__main__":
    port=int(os.environ.get("PORT",5000))
    print(f"\n🛡 Digital Bandhu → http://localhost:{port}\n")
    app.run(host="0.0.0.0",port=port,debug=False)
