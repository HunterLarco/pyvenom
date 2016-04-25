'use strict';
(function (root) {
  
  root.addEventListener('load', Init);
  function Init(){
    var docContent = new DocContent();
    new RouteList(docContent);
    new Sidebar();
  }
  
})(window);