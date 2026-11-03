import * as THREE from 'three';
import { GLTFLoader } from './vendor/GLTFLoader.js';

const $=id=>document.getElementById(id);
const scene=new THREE.Scene();
scene.background=new THREE.Color('#66736c');
scene.fog=new THREE.FogExp2('#77847a',.026);
const distantForest=new THREE.TextureLoader().load('./assets/forest-panorama.png',texture=>{texture.mapping=THREE.EquirectangularReflectionMapping;texture.colorSpace=THREE.SRGBColorSpace;scene.background=texture;});
const camera=new THREE.PerspectiveCamera(67,innerWidth/innerHeight,.06,180);
camera.rotation.order='YXZ';
const renderer=new THREE.WebGLRenderer({antialias:true,powerPreference:'high-performance'});
renderer.setPixelRatio(Math.min(devicePixelRatio,1.6));
renderer.setSize(innerWidth,innerHeight);
renderer.toneMapping=THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure=1.25;
$('world').append(renderer.domElement);
scene.add(new THREE.HemisphereLight('#dce8e6','#38402a',2.2));
const sun=new THREE.DirectionalLight('#f7ecd2',3);sun.position.set(-8,18,-5);scene.add(sun);
const target=new THREE.WebGLRenderTarget(1,1);
const postScene=new THREE.Scene();
const postCamera=new THREE.OrthographicCamera(-1,1,1,-1,0,1);
const post=new THREE.ShaderMaterial({uniforms:{image:{value:target.texture},pixel:{value:new THREE.Vector2()},aspect:{value:1}},vertexShader:`varying vec2 vUv;void main(){vUv=uv;gl_Position=vec4(position.xy,0.,1.);}`,fragmentShader:`uniform sampler2D image;uniform vec2 pixel;uniform float aspect;varying vec2 vUv;
void main(){vec3 sharp=texture2D(image,vUv).rgb;vec3 blurred=vec3(0.);float total=0.;for(int x=-3;x<=3;x++){for(int y=-3;y<=3;y++){float w=exp(-float(x*x+y*y)/7.);blurred+=texture2D(image,vUv+vec2(float(x),float(y))*pixel*2.3).rgb*w;total+=w;}}vec2 q=abs(vUv-vec2(.5,.495))-vec2(.27,.225)+vec2(.018,.018*aspect);float d=length(max(q*vec2(aspect,1.),0.))+min(max(q.x*aspect,q.y),0.)-.018*aspect;float outside=smoothstep(-.002,.012,d);vec3 c=mix(sharp,blurred/total*.91,outside);float vignette=smoothstep(.25,.78,length((vUv-.5)*vec2(1.,.85)));gl_FragColor=vec4(c*(1.-vignette*.38),1.);}`});
postScene.add(new THREE.Mesh(new THREE.PlaneGeometry(2,2),post));
function resize(){renderer.setSize(innerWidth,innerHeight);camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();const size=renderer.getDrawingBufferSize(new THREE.Vector2());target.setSize(size.x,size.y);post.uniforms.pixel.value.set(1/size.x,1/size.y);post.uniforms.aspect.value=camera.aspect;clearInput();}
let distance=0,yaw=.25,pitch=.12,loaded=false,paused=false;
const keys=new Set();const move={x:0,y:0},look={x:0,y:0};
const sticks=[];
function clearInput(){keys.clear();for(const s of sticks)s.reset();}
function joystick(id,state){const el=$(id),knob=el.querySelector('.knob');let pointer=null;
 const reset=()=>{pointer=null;state.x=state.y=0;knob.style.transform='';};sticks.push({reset});
 function update(e){const r=el.getBoundingClientRect(),radius=r.width/2,dx=(e.clientX-r.left-radius)/radius,dy=(e.clientY-r.top-radius)/radius,len=Math.hypot(dx,dy),limit=Math.max(1,len);state.x=dx/limit;state.y=dy/limit;knob.style.transform=`translate(${state.x*radius*.62}px,${state.y*radius*.62}px)`;}
 el.onpointerdown=e=>{if(pointer!==null)return;pointer=e.pointerId;el.setPointerCapture(pointer);update(e);};el.onpointermove=e=>{if(pointer===e.pointerId)update(e);};el.onpointerup=el.onpointercancel=el.onlostpointercapture=e=>{if(pointer===e.pointerId)reset();};
}
joystick('move',move);joystick('look',look);
window.addEventListener('keydown',e=>{if(['ArrowUp','ArrowDown','ArrowLeft','ArrowRight','KeyW','KeyS'].includes(e.code)){e.preventDefault();keys.add(e.code);}if(e.code==='Escape')clearInput();});window.addEventListener('keyup',e=>keys.delete(e.code));window.addEventListener('blur',clearInput);document.addEventListener('visibilitychange',clearInput);window.addEventListener('resize',resize);
$('menu').onclick=()=>{clearInput();paused=true;$('panel').showModal();};$('resume').onclick=()=>$('panel').close();$('panel').onclose=()=>{paused=false;clearInput();};$('reset').onclick=()=>{distance=0;yaw=.25;pitch=.12;$('panel').close();};$('fullscreen').onclick=async()=>{try{await document.documentElement.requestFullscreen();await screen.orientation?.lock?.('landscape');}catch{} };
new GLTFLoader().load('./assets/forest.glb',gltf=>{const discard=[];gltf.scene.traverse(o=>{if(/^(Memory frame|Memory boundary|Memory interior|Memory volume|Time block|Spatial scan|Light bleeding from the memory frame|Far field)/.test(o.name))discard.push(o);});for(const o of discard)o.parent?.remove(o);scene.add(gltf.scene);loaded=true;$('caption').textContent='左で歩く　・　右で見回す';setTimeout(()=>{$('caption').textContent='';},7000);},e=>{if(e.total)$('caption').textContent=`森を読み込んでいます ${Math.round(e.loaded/e.total*100)}%`;},e=>{console.error(e);$('caption').textContent='森を読み込めませんでした。ページを再読み込みしてください。';});
const clamp=THREE.MathUtils.clamp;let last=performance.now();
function tick(now){requestAnimationFrame(tick);const dt=Math.min((now-last)/1000,.05);last=now;
 if(loaded&&!paused&&innerWidth>innerHeight){const input=move.y===0?0:move.y<0?1:-1;distance=clamp(distance+(input+(keys.has('KeyW')?1:0)-(keys.has('KeyS')?1:0))*dt*1.65,0,57.3);yaw-=(look.x+(keys.has('ArrowRight')?1:0)-(keys.has('ArrowLeft')?1:0))*dt*1.2;pitch=clamp(pitch-(look.y+(keys.has('ArrowDown')?1:0)-(keys.has('ArrowUp')?1:0))*dt*.85,-1.05,1.05);}
 const y=-14.6+distance;const forestRouteX=v=>.45*Math.sin(v*.17)+.22*Math.sin(v*.48);const routeX=v=>v<26.2?forestRouteX(v):-.4;const x=routeX(y)-routeX(-14.6)*Math.max(0,1-distance/3);const z=.1*Math.sin(x*.54+y*.19)+.055*Math.sin(y*.7-x*.27);
 camera.position.set(x,1.68+z,-y);camera.rotation.set(pitch,yaw,0);renderer.setRenderTarget(target);renderer.render(scene,camera);renderer.setRenderTarget(null);renderer.render(postScene,postCamera);
}
resize();requestAnimationFrame(tick);
// Read-only inspection for local QA.
window.gameState=()=>({distance,yaw,pitch,loaded,paused,position:camera.position.toArray(),move:{...move},look:{...look}});
