'use strict';
(function (root) {
  
  root.addEventListener('load', Init);
  function Init(){
    var docContent = new DocContent();
    new RouteList(docContent);
    new Sidebar('.js-Sidebar-Routes', '.js-Layout');
    new Sidebar('.js-Sidebar-Explorer', '.js-Layout');
  }
  
})(window);