// Optional authoring export: npm install sharp. No runtime dependency.
// Rasterize the SVG clip of the approved original; do not redraw the logo.
const fs = require('node:fs');
const path = require('node:path');
const sharp = require('sharp');
const root=path.resolve(__dirname,'..'), out=path.join(root,'webfrontend/htmlauth');
const original=fs.readFileSync(path.join(root,'icons/plx-logo-original.png'));
const svg=fs.readFileSync(path.join(root,'icons/favicon-mark.svg'),'utf8')
  .replace('xlink:href="plx-logo-original.png"',`xlink:href="data:image/png;base64,${original.toString('base64')}"`);
(async()=>{
 const frames=[];
 for(const size of [16,32,48,180]){
  const png=await sharp(Buffer.from(svg),{density:384}).resize(size,size).png().toBuffer();
  if(size===32)fs.writeFileSync(path.join(out,'favicon.png'),png);
  if(size===180)fs.writeFileSync(path.join(out,'apple-touch-icon.png'),png);
  if(size!==180)frames.push({size,png});
 }
 const header=Buffer.alloc(6+16*frames.length);header.writeUInt16LE(1,2);header.writeUInt16LE(frames.length,4);
 let offset=header.length;
 frames.forEach(({size,png},i)=>{const p=6+i*16;header[p]=size;header[p+1]=size;header.writeUInt16LE(1,p+4);header.writeUInt16LE(32,p+6);header.writeUInt32LE(png.length,p+8);header.writeUInt32LE(offset,p+12);offset+=png.length;});
 fs.writeFileSync(path.join(out,'favicon.ico'),Buffer.concat([header,...frames.map(f=>f.png)]));
})().catch(error=>{console.error(error);process.exitCode=1;});
