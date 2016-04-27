'use strict';
(function (root) {
  
  function $ (el, context) {
    return (context || document).querySelector(el);
  }
  
  function $$ (el, context) {
    return (context || document).querySelectorAll(el);
  }
  
  root.$  = $;
  root.$$ = $$;

})(window);