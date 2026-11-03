import { createServer } from 'node:http';
import { createReadStream, statSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { extname, relative, resolve, sep } from 'node:path';

const root = resolve(fileURLToPath(new URL('.', import.meta.url)));
const mime = { '.html':'text/html; charset=utf-8', '.js':'text/javascript; charset=utf-8', '.css':'text/css; charset=utf-8', '.glb':'model/gltf-binary', '.json':'application/json', '.wasm':'application/wasm' };
createServer((req,res)=>{
  let path;
  try { path=decodeURIComponent(new URL(req.url,'http://localhost').pathname); } catch { res.writeHead(400).end(); return; }
  const file=resolve(root,`.${path==='/'?'/index.html':path}`);
  const rel=relative(root,file);
  if(rel==='..'||rel.startsWith(`..${sep}`)){res.writeHead(403).end();return;}
  try { const size=statSync(file).size;res.writeHead(200,{'Content-Type':mime[extname(file)]||'application/octet-stream','Content-Length':size,'Cache-Control':'no-cache'});if(req.method==='HEAD')res.end();else createReadStream(file).pipe(res); }
  catch {res.writeHead(404).end('Not found');}
}).listen(8765,'127.0.0.1',()=>console.log('Forest game: http://127.0.0.1:8765'));
