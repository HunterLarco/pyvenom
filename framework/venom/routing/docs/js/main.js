'use strict';
(function (root) {
  
  root.addEventListener('load', Init);
  function Init(){
    new RouteList();
    new Sidebar();
  }
  
})(window);