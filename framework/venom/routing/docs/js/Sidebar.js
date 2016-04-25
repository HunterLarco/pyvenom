'use strict';
(function (root) {
  
  function Sidebar (sidebar, drag_over) {
    this.init(sidebar, drag_over);
  }
  
  Sidebar.prototype = {
    init: function (sidebar, drag_over) {
      // Cache all the elements first on the instance
      this.$layout = $(drag_over);
      this.$sidebar = $(sidebar, this.$layout);
      this.$dragger = $('.js-SidebarDragger', this.$sidebar);
      
      this._onUp = this.handleMouseUp.bind(this);
      this._onMove = this.handleMouseMove.bind(this);
      this._mouseStartX = null;
      this._startOffset = null;
      
      this.bindEvents();
    },
    bindEvents: function () {
      this.$dragger.addEventListener('mousedown', this.handleMouseDown.bind(this));
    },
    handleMouseDown: function (event) {
      this._mouseStartX = event.pageX;
      this._startOffset = this.$sidebar.offsetWidth;
      
      classes.add('dragging', this.$layout);
      root.addEventListener('mouseup', this._onUp);
      root.addEventListener('mousemove', this._onMove);
    },
    handleMouseMove: function (event) {
      var diffX = event.pageX - this._mouseStartX;
      if(classes.has('right', this.$dragger))
        diffX *= -1;
      var width = this._startOffset + diffX;
      
      this.$sidebar.style.width = width + 'px';
    },
    handleMouseUp: function () {
      classes.remove('dragging', this.$layout);
      root.removeEventListener('mouseup', this._onUp);
      root.removeEventListener('mousemove', this._onMove);
    }
  };
  
  root.Sidebar = Sidebar;
  
})(window);