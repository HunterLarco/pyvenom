'use strict';
(function (root) {
  
  function DocContent () {
    this.init();
  }
  
  DocContent.prototype = {
    init: function () {
      // Cache all the elements first on the instance
      this.$content = $('.js-DocContent');
      this.$methodLabel = $('.js-Method', this.$content);
      this.$pathLabel = $('.js-Path', this.$content);
      
      this.bindEvents();
    },
    bindEvents: function () {
      
    },
    render: function (route) {
      this.renderHeader(route);
    },
    renderHeader: function (route) {
      this.$methodLabel.innerHTML = route.methods[0];
      
      var path = route.path.replace(/^\/api\/v{{ version }}/, '');
      path = path.replace(/\:([^/]+)/g, '<div class="UrlParameter">$1</div>');
      this.$pathLabel.innerHTML = path;
    }
  };
  
  root.DocContent = DocContent;
  
})(window);