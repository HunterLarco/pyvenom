'use strict';
(function (root) {
  
  function Route (routeList, path, method) {
    this.init(routeList, path, method);
  }
  
  Route.prototype = {
    init: function (routeList, path, method) {
      path = path.replace(/^\/api\/v{{ version }}/, '');
      this.path = path;
      this.method = method;
      
      this.routeList = routeList;
      
      // Cache all the elements first on the instance
      this.$elem = $new('div.Route');
      
      path = path.replace(/\:([^/]+)/g, '<div class="UrlParameter">$1</div>');
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
      this.triggerLoadMeta();
    },
    triggerDeactivate: function () {
      classes.remove('active', this.$elem);
    },
    triggerLoadMeta: function () {
      var path = '/meta/v{{ version }}' + this.path + '?method=' + this.method;
      fetch(path).then(function(response){
        return response.json();
      }).then(this.renderMeta.bind(this));
    },
    renderMeta: function (meta){
      if (meta.routes.length == 1)
        this.routeList.docContent.render(meta.routes[0]);
    }
  };
  
  root.Route = Route;
  
})(window);