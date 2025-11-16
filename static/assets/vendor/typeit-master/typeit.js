/* Local shim for TypeIt (UMD)
   Replace with the official minified/bundled file to serve locally.
*/
(function(){
  if(typeof window === 'undefined') return;
  try{ if(window.TypeIt) return; }catch(e){}
  var cdn = 'https://cdn.jsdelivr.net/npm/typeit@8.7.1/dist/typeit.umd.js';
  var s=document.createElement('script'); s.type='text/javascript'; s.async=true; s.src=cdn; document.head.appendChild(s);
})();
