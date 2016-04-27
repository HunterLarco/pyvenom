'use strict';
(function (root) {
  
  function $new (elstring, parentElement, html) {
    var elstring = elstring || ''
    
    if (elstring.indexOf(' ') > -1){
      var elstring = elstring.replace(/\s+/g, ' ');
      var selectors = elstring.split(' ');
      var original = $new(selectors[0], parentElement)
      var last = original;
      for(var i=1; i<selectors.length; i++){
        var selector = selectors[i];
        last = $new(selector, last);
      }
      if(!!html) last.innerHTML = html;
      return original;
    }
    
    var classes = elstring.split('.');
    var elem = document.createElement(classes[0] || 'div');
    var classlist = classes.slice(1).join(' ');
    elem.setAttribute('class', classlist);
    if(!!parentElement) parentElement.appendChild(elem);
    if(!!html) elem.innerHTML = html;
    return elem;
  }
  
  window.$new  = $new;

})(window);