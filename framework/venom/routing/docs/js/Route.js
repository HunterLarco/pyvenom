'use strict';
(function (root) {
  
  function Route (routeList, path, method) {
    this.init(routeList, path, method);
  }
  
  Route.prototype = {
    init: function (routeList, path, method) {
      path = path.replace(/^\/api\/v{{ version }}/, '');
      path = path.replace(/\:([^/]+)/g, '<div class="UrlParameter">$1</div>')
      
      this.routeList = routeList;
      
      // Cache all the elements first on the instance
      this.$elem = $new('div.Route');
      this.$pathLabel = $new('div.Route-Path', this.$elem, path);
      this.$methodLabel = $new('div.Route-Method', this.$elem, method);
      
      this.bindEvents();
    },
    bindEvents: function () {
      this.$elem.addEventListener('click', this.handleClick.bind(this));
    },
    handleClick: function () {
      this.routeList.triggerActivateRoute(this)
    },
    triggerActivate: function () {
      classes.add('active', this.$elem);
    },
    triggerDeactivate: function () {
      classes.remove('active', this.$elem);
    }
  };
  
  root.Route = Route;
  
})(window);