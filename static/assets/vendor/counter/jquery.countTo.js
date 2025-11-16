/* Local shim for jquery.countTo
   Replace with the official minified file to serve locally.
*/
(function(){
  if(typeof window === 'undefined') return;
  try{ if(window.jQuery && jQuery.fn && jQuery.fn.countTo) return; }catch(e){}
  var cdn = 'https://cdnjs.cloudflare.com/ajax/libs/jquery-countto/1.2.0/jquery.countTo.min.js';
  var s=document.createElement('script'); s.type='text/javascript'; s.async=true; s.src=cdn; document.head.appendChild(s);
})();
