'use strict';
// Preserve ancestor pixels; retain only newly generated dark/light pigment.
const fs=require('node:fs'),crypto=require('node:crypto');
const {decodePNG,encodePNG,preview}=require('./finish_wall.js');
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const source='artifacts/line-1/wall-v17.png',destination='artifacts/line-1/wall-v18.png';
if(fs.existsSync('dist/line-1/36.json')) throw Error('record already exists');
const raw=fs.readFileSync(source),ancestor=decodePNG(source),donorRaw=fs.readFileSync(destination),donor=decodePNG(destination);
if(JSON.parse(fs.readFileSync('dist/line-1/35.json')).image!=='https://api.imd.fun/artifacts/'+hash(raw)) throw Error('ancestor pin mismatch');
if(!raw.equals(fs.readFileSync('artifacts/line-1/wall.png'))) throw Error('current ancestor mismatch');
if(ancestor.width!==1254||ancestor.height!==1254||ancestor.channels!==3||donor.width!==1254||donor.height!==1254) throw Error('unexpected image');
const out={...ancestor,pixels:Buffer.from(ancestor.pixels)},bounds=[422,522,508,578];
let charcoal=0,chalk=0;
for(let y=bounds[1];y<bounds[3];y++) for(let x=bounds[0];x<bounds[2];x++) {
 const a=(y*ancestor.width+x)*3,d=(y*donor.width+x)*donor.channels;
 const [r,g,b]=donor.pixels.subarray(d,d+3),[ar,ag,ab]=ancestor.pixels.subarray(a,a+3);
 const dark=r<130&&g<105&&b<75&&ar-r>20&&ag-g>15;
 const light=r>160&&g>140&&b>110&&r-g<55&&g-ag>16&&b-ab>16;
 if(!dark&&!light) continue;
 const feather=Math.min(1,(x-bounds[0])/3,(bounds[2]-1-x)/3,(y-bounds[1])/3,(bounds[3]-1-y)/3);
 if(feather<=0) continue;
 const alpha=.85*feather;
 for(let c=0;c<3;c++) out.pixels[a+c]=Math.round(ancestor.pixels[a+c]*(1-alpha)+donor.pixels[d+c]*alpha);
 if(dark) charcoal++;else chalk++;
}
let changed=0;
for(let y=0;y<out.height;y++) for(let x=0;x<out.width;x++) {
 const i=(y*out.width+x)*3;
 if(!out.pixels.subarray(i,i+3).equals(ancestor.pixels.subarray(i,i+3))) {
  changed++;
  if(x<bounds[0]||x>=bounds[2]||y<bounds[1]||y>=bounds[3]) throw Error('outside mutation');
 }
}
if(charcoal<250||chalk<20) throw Error('missing pigment');
const png=encodePNG(out),jpg=preview(out),digest=hash(png);
if(jpg.length>100000) throw Error('preview too large');
fs.writeFileSync(destination,png);fs.writeFileSync('artifacts/line-1/wall.png',png);
fs.writeFileSync('dist/line-1/36.jpg',jpg);
fs.writeFileSync('dist/line-1/36.json',JSON.stringify({name:'The Uncounted Pebble',image:'https://api.imd.fun/artifacts/'+digest,attributes:[
 {trait_type:'Cave',value:'Roots'},{trait_type:'Wall',value:'Line 1'},{trait_type:'Number',value:36},
 {trait_type:'Left behind',value:'Missing Bounds'},
 {trait_type:'Meaning',value:'Three charcoal pebbles and an open chalk arc keep an unknown outcome in the count.'},
 {trait_type:'One thing',value:'Reproducible benchmark evidence'}]},null,2)+'\n');
const review={wall:destination,width:1254,height:1254,format:'PNG RGB8',bytes:png.length,sha256:digest,
 preview:{path:'dist/line-1/36.jpg',width:512,height:512,format:'JPEG',bytes:jpg.length},
 ancestor:source,ancestor_sha256:hash(raw),generated_image_sha256:hash(donorRaw),bounds,changed_pixels:changed,
 charcoal_pixels:charcoal,chalk_pixels:chalk,all_pixels_outside_bounds_identical:true,
 process:'Installed image generator edited inherited wall. Only new darker charcoal and brighter chalk pixels from a bare-rock patch were transferred; generated full image overwritten by finished wall.',
 visual_review:{status:'pending inspection',unmet_visual_requirements:[]},
 preview_location_exception:'The task explicitly requires a numbered JPEG beside its JSON in dist/line-1.'};
fs.writeFileSync('line-1/wall-review-36.json',JSON.stringify(review,null,2)+'\n');
console.log(JSON.stringify(review));
