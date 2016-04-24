'use strict';
(function (root) {
  
  function Route (path, method) {
    this.init(path, method);
  }
  
  Route.prototype = {
    init: function (path, method) {
      path = path.replace(/^\/api\/v{{ version }}/, '');
      
      // Cache all the elements first on the instance
      this.$elem = $new('div.Route');
      this.$pathLabel = $new('div.Route-Path', this.$elem, path);
      this.$methodLabel = $new('div.Route-Method', this.$elem, method);
      
      this.bindEvents();
    },
    bindEvents: function () {
      
    }
  };
  
  root.Route = Route;
  
})(window);